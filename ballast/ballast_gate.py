#!/usr/bin/env python3
"""
Ballast - Risk Gate (v2.2)

This is the "Risk/Exit independent verifier with full veto power" from the
manual, implemented as plain arithmetic rather than as instructions to a
language model.

Why arithmetic: rules 2-7 of the Constitution are pure maths (percentages,
limits, dates). A model asked to remember ten rules will follow them most of
the time. A function that computes them follows them every time. The veto in
Part 4 is only meaningful if nothing can talk it out of a veto.

Usage:
    python ballast_gate.py --asset SOL-USD --direction long \
        --entry 200 --stop 188 --target 224 --hold-days 3

    python ballast_gate.py --status          # show desk state and any freezes
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_PATH = HERE / "desk_state.json"

# ---------------------------------------------------------------------------
# Part 4 hard rules. These are the numbers from the manual.
# Loosening a number here is the same as breaking the rule. Don't.
# ---------------------------------------------------------------------------
RULES = {
    "main_desk": {
        "max_risk_per_trade_pct": 2.5,
        "max_risk_per_trade_pct_drawdown": 1.5,   # after -20% from peak
        "max_total_open_risk_pct": 6.0,
        "max_hold_days": 5,
        "daily_loss_limit_pct": 5.0,
        "weekly_loss_limit_pct": 12.0,
        "drawdown_reduce_risk_pct": 20.0,
        "drawdown_full_pause_pct": 30.0,
        "full_pause_days": 14,
        "max_satellite_pct_of_equity": 20.0,
    },
    "experimental_sleeve": {
        # The manual says the sleeve runs "its own tighter limits" without
        # naming them. These are tighter than the Main Desk. Set your own
        # numbers in desk_state.json if you want different ones - but set
        # them once, in advance, not mid-drawdown.
        "max_risk_per_trade_pct": 2.0,
        "max_risk_per_trade_pct_drawdown": 1.0,
        "max_total_open_risk_pct": 4.0,
        "max_hold_days": 5,
        "daily_loss_limit_pct": 4.0,
        "weekly_loss_limit_pct": 10.0,
        "drawdown_reduce_risk_pct": 15.0,
        "drawdown_full_pause_pct": 25.0,
        "full_pause_days": 7,
        "max_satellite_pct_of_equity": 20.0,
    },
}

CORE_UNIVERSE = {"BTC-USD", "ETH-USD", "SOL-USD"}


class Veto(Exception):
    """Raised when a hard rule refuses the trade outright."""


def load_state() -> dict:
    if not STATE_PATH.exists():
        sys.exit(
            f"No desk state found at {STATE_PATH}\n"
            "Copy desk_state.example.json to desk_state.json and fill in your numbers."
        )
    with STATE_PATH.open() as fh:
        return json.load(fh)


def save_state(state: dict) -> None:
    with STATE_PATH.open("w") as fh:
        json.dump(state, fh, indent=2)
        fh.write("\n")


def require_numbers(desk: dict, desk_name: str) -> None:
    """Part 1 of the manual: the numbers must exist before anything runs."""
    missing = [
        key
        for key in ("current_equity", "peak_equity", "day_start_equity", "week_start_equity")
        if desk.get(key) in (None, "", 0)
    ]
    if missing:
        raise Veto(
            f"{desk_name}: these values are not filled in yet: {', '.join(missing)}. "
            "Open desk_state.json and set them before sizing any trade."
        )


def check_freezes(desk: dict, rules: dict, desk_name: str, today: date) -> list[str]:
    """Daily, weekly, and drawdown freezes. Returns notes; raises Veto to stop."""
    notes: list[str] = []

    frozen_until = desk.get("frozen_until")
    if frozen_until:
        until = datetime.strptime(frozen_until, "%Y-%m-%d").date()
        if today <= until:
            raise Veto(
                f"{desk_name} is frozen until {until.isoformat()} "
                f"(reason: {desk.get('freeze_reason', 'not recorded')})."
            )
        notes.append(f"Freeze expired on {until.isoformat()}; desk is live again.")

    equity = float(desk["current_equity"])
    peak = float(desk["peak_equity"])
    day_start = float(desk["day_start_equity"])
    week_start = float(desk["week_start_equity"])

    day_change_pct = (equity - day_start) / day_start * 100
    week_change_pct = (equity - week_start) / week_start * 100
    drawdown_pct = (peak - equity) / peak * 100

    if day_change_pct <= -rules["daily_loss_limit_pct"]:
        raise Veto(
            f"NO TRADE - DAILY LIMIT HIT. Down {abs(day_change_pct):.2f}% on the day "
            f"(limit {rules['daily_loss_limit_pct']}%). Frozen for the rest of the day."
        )

    if week_change_pct <= -rules["weekly_loss_limit_pct"]:
        raise Veto(
            f"NO TRADE - WEEKLY LIMIT HIT. Down {abs(week_change_pct):.2f}% on the week "
            f"(limit {rules['weekly_loss_limit_pct']}%). Frozen for the rest of the week."
        )

    if drawdown_pct >= rules["drawdown_full_pause_pct"]:
        raise Veto(
            f"NO TRADE - {drawdown_pct:.1f}% below peak equity "
            f"(threshold {rules['drawdown_full_pause_pct']}%). "
            f"Full pause for {rules['full_pause_days']} days, then a written review. "
            "Set frozen_until in desk_state.json now."
        )

    notes.append(
        f"Day {day_change_pct:+.2f}% | Week {week_change_pct:+.2f}% | "
        f"Drawdown from peak {drawdown_pct:.2f}%"
    )
    return notes


def allowed_risk_pct(desk: dict, rules: dict) -> tuple[float, str]:
    """2.5% normally; 1.5% once you are 20% below peak, until a new peak."""
    equity = float(desk["current_equity"])
    peak = float(desk["peak_equity"])
    drawdown_pct = (peak - equity) / peak * 100

    if drawdown_pct >= rules["drawdown_reduce_risk_pct"]:
        return (
            rules["max_risk_per_trade_pct_drawdown"],
            f"reduced to {rules['max_risk_per_trade_pct_drawdown']}% - "
            f"{drawdown_pct:.1f}% below peak, restores at a new equity high",
        )
    return rules["max_risk_per_trade_pct"], "standard"


def evaluate(args: argparse.Namespace) -> int:
    state = load_state()
    desk_key = "experimental_sleeve" if args.sleeve else "main_desk"
    desk_name = "Experimental Sleeve" if args.sleeve else "Main Desk"
    desk = state[desk_key]
    rules = {**RULES[desk_key], **state.get("rule_overrides", {}).get(desk_key, {})}
    today = date.fromisoformat(args.date) if args.date else date.today()

    warnings: list[str] = []

    try:
        require_numbers(desk, desk_name)
        notes = check_freezes(desk, rules, desk_name, today)

        asset = args.asset.upper()
        equity = float(desk["current_equity"])

        # Rule 1 - allowed universe.
        is_satellite = asset not in CORE_UNIVERSE
        if is_satellite:
            if not args.satellite:
                raise Veto(
                    f"{asset} is outside the core universe (BTC-USD, ETH-USD, SOL-USD). "
                    "If this is a deliberate satellite position, re-run with --satellite "
                    "and a written justification."
                )
            warnings.append(
                f"SATELLITE: {asset} is outside the core universe. Capped at "
                f"{rules['max_satellite_pct_of_equity']}% of equity."
            )

        # Rule 4 - a ticket without a stop and a target is not a ticket.
        if args.stop is None or args.entry is None:
            raise Veto("Every ticket needs an entry and a hard stop. No stop, no trade.")

        entry = float(args.entry)
        stop = float(args.stop)
        direction = args.direction.lower()

        if direction == "long" and stop >= entry:
            raise Veto(f"Long stop ({stop}) must sit below entry ({entry}).")
        if direction == "short" and stop <= entry:
            raise Veto(f"Short stop ({stop}) must sit above entry ({entry}).")

        stop_distance_pct = abs(entry - stop) / entry * 100
        if stop_distance_pct == 0:
            raise Veto("Stop distance is zero.")

        # Rule 3 - the position sizing formula, exactly as written.
        risk_pct, risk_note = allowed_risk_pct(desk, rules)
        risk_dollars = equity * (risk_pct / 100)
        position_notional = risk_dollars / (stop_distance_pct / 100)
        units = position_notional / entry
        leverage = position_notional / equity

        # The formula does not know about leverage. A tight stop produces a
        # position larger than the account. Flag it rather than sizing into it.
        if leverage > 1.0:
            warnings.append(
                f"LEVERAGE: the formula sizes this at {leverage:.2f}x your equity "
                f"(${position_notional:,.2f} on ${equity:,.2f}) because the stop is only "
                f"{stop_distance_pct:.2f}% away. Either widen the stop, or cap the position "
                f"at ${equity:,.2f} and accept the smaller risk of "
                f"{(equity * stop_distance_pct / 100) / equity * 100:.2f}%. "
                "Do not add leverage to make the formula fit."
            )

        if is_satellite:
            cap = equity * rules["max_satellite_pct_of_equity"] / 100
            if position_notional > cap:
                warnings.append(
                    f"SATELLITE CAP: position trimmed from ${position_notional:,.2f} "
                    f"to ${cap:,.2f} ({rules['max_satellite_pct_of_equity']}% of equity)."
                )
                position_notional = cap
                units = position_notional / entry

        # Rule - max total open risk 6%.
        open_risk = float(desk.get("open_risk_pct", 0.0))
        if open_risk + risk_pct > rules["max_total_open_risk_pct"]:
            raise Veto(
                f"Total open risk would reach {open_risk + risk_pct:.2f}% "
                f"(limit {rules['max_total_open_risk_pct']}%). "
                f"You already have {open_risk:.2f}% at risk in open positions. "
                "Close something or skip this."
            )

        # Rule 4 - max hold time.
        hold_days = args.hold_days
        if hold_days > rules["max_hold_days"]:
            raise Veto(
                f"Max hold time is {rules['max_hold_days']} days; you asked for {hold_days}."
            )

        if not args.target:
            warnings.append("No take-profit given. Rule 4 requires at least one target.")

    except Veto as veto:
        print("\n" + "=" * 62)
        print(f"RISK GATE: VETO - {desk_name}")
        print("=" * 62)
        print(f"\n{veto}\n")
        print("=== FINAL DESK OUTPUT ===")
        print("Decision: NO TRADE")
        print(f"Asset: {args.asset.upper()}")
        print(f"Risk notes: {veto}")
        print("=== END ===")
        print(f"\nLOG: {today.isoformat()} | {args.asset.upper()} | NO TRADE | "
              f"{str(veto)[:110]}")
        return 1

    reward_note = "n/a"
    if args.target:
        target = float(args.target)
        reward = abs(target - entry)
        risk_per_unit = abs(entry - stop)
        reward_note = f"{reward / risk_per_unit:.2f}R to {target}"

    decision = "PROBE" if args.probe else "TICKET"

    print("\n" + "=" * 62)
    print(f"RISK GATE: PASS - {desk_name}")
    print("=" * 62)
    for note in notes:
        print(f"  state    | {note}")
    print(f"  risk %   | {risk_pct}% ({risk_note})")
    for warning in warnings:
        print(f"  WARNING  | {warning}")

    print("\n=== FINAL DESK OUTPUT ===")
    print(f"Decision: {decision}")
    print(f"Asset: {asset}")
    print(f"Direction: {direction.upper()}")
    print(f"Entry zone: {entry}")
    print(f"Stop loss: {stop}  ({stop_distance_pct:.2f}% away)")
    print(f"Take profit: {args.target or 'NOT SET - required before entry'}  ({reward_note})")
    print(f"Max hold time: {hold_days} days (hard exit {rules['max_hold_days']} days)")
    print(f"Risk % of equity: {risk_pct}%  (${risk_dollars:,.2f})")
    print(
        f"Position size calculation: ${equity:,.2f} x {risk_pct}% / {stop_distance_pct:.2f}% "
        f"= ${position_notional:,.2f} notional = {units:.6f} units at {entry}"
    )
    print(f"Wind Report influence: {args.wind or 'not recorded'}")
    print(f"Key reasons (max 3): {args.reason or 'not recorded'}")
    print(f"Risk notes: {'; '.join(warnings) if warnings else 'all hard rules passed'}")
    print("=== END ===")
    print(
        f"\nLOG: {today.isoformat()} | {asset} | {decision} | "
        f"{direction} {units:.6f} units, stop {stop}, risk {risk_pct}%"
    )

    if args.log:
        log_file = HERE / (
            "Experimental_Sleeve_Log.md" if args.sleeve else "Main_Desk_Log.md"
        )
        with log_file.open("a") as fh:
            fh.write(
                f"\n| {today.isoformat()} | {asset} | {decision} | {direction.upper()} | "
                f"{entry} | {stop} | {args.target or '-'} | {risk_pct}% | "
                f"${position_notional:,.2f} | | |\n"
            )
        print(f"\nAppended to {log_file.name}. Fill in the result column when you close.")

    return 0


def show_status() -> int:
    state = load_state()
    today = date.today()
    print(f"\nBallast - state as of {today.isoformat()}")
    for desk_key, desk_name in (
        ("main_desk", "Main Desk"),
        ("experimental_sleeve", "Experimental Sleeve"),
    ):
        desk = state[desk_key]
        rules = {**RULES[desk_key], **state.get("rule_overrides", {}).get(desk_key, {})}
        print(f"\n{desk_name}")
        print("-" * len(desk_name))
        try:
            require_numbers(desk, desk_name)
        except Veto as veto:
            print(f"  {veto}")
            continue
        equity = float(desk["current_equity"])
        print(f"  Equity            ${equity:,.2f}")
        print(f"  Peak              ${float(desk['peak_equity']):,.2f}")
        print(f"  Open risk         {float(desk.get('open_risk_pct', 0)):.2f}% "
              f"of {rules['max_total_open_risk_pct']}% allowed")
        try:
            for note in check_freezes(desk, rules, desk_name, today):
                print(f"  {note}")
            risk_pct, risk_note = allowed_risk_pct(desk, rules)
            print(f"  Risk per trade    {risk_pct}% ({risk_note})")
            print("  Status            LIVE")
        except Veto as veto:
            print(f"  Status            BLOCKED - {veto}")
    print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ballast risk gate - independent verifier with veto power."
    )
    parser.add_argument("--status", action="store_true", help="Show desk state and exit.")
    parser.add_argument("--asset", help="e.g. SOL-USD")
    parser.add_argument("--direction", default="long", choices=["long", "short"])
    parser.add_argument("--entry", type=float, help="Entry price.")
    parser.add_argument("--stop", type=float, help="Hard stop-loss price.")
    parser.add_argument("--target", type=float, help="Take-profit price.")
    parser.add_argument("--hold-days", type=int, default=5, help="Planned max hold, in days.")
    parser.add_argument("--sleeve", action="store_true", help="Size against the sleeve, not the Main Desk.")
    parser.add_argument("--satellite", action="store_true", help="Acknowledge a non-core asset.")
    parser.add_argument("--probe", action="store_true", help="Mark the decision PROBE rather than TICKET.")
    parser.add_argument("--wind", help="One line on how the Wind Report fed this.")
    parser.add_argument("--reason", help="Up to three key reasons.")
    parser.add_argument("--date", help="Override today's date (YYYY-MM-DD).")
    parser.add_argument("--log", action="store_true", help="Append the decision to the log file.")
    args = parser.parse_args()

    if args.status:
        return show_status()
    if not args.asset:
        parser.error("--asset is required (or use --status)")
    return evaluate(args)


if __name__ == "__main__":
    sys.exit(main())

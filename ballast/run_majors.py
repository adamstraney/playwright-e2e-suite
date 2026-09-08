#!/usr/bin/env python3
"""
Ballast - Main Desk runner (v2.2)

Step 2 of the daily workflow. Runs TradingAgents over one allowed asset and
prints its research, then hands you over to the risk gate.

    python run_majors.py                  # today, SOL-USD
    python run_majors.py BTC-USD
    python run_majors.py ETH-USD 2026-09-07

What this script does and does not do
-------------------------------------
It runs the analyst debate and returns a rating: Buy / Overweight / Hold /
Underweight / Sell, or REVIEW when the model produced nothing parseable.

It does NOT produce a ticket. A rating is an opinion; a ticket is an opinion
plus a stop, a size and a limit check. The sizing and the hard rules live in
ballast_gate.py, which is arithmetic and cannot be argued with. Read this output,
pick your levels, then run the gate.
"""

from __future__ import annotations

import sys
from datetime import date

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

ALLOWED = ("BTC-USD", "ETH-USD", "SOL-USD")

# --- Local models via Ollama -------------------------------------------------
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "ollama"
config["deep_think_llm"] = "qwen2.5:32b"
config["quick_think_llm"] = "qwen2.5:14b"
config["max_debate_rounds"] = 1
# backend_url is left unset on purpose: the ollama provider already defaults to
# http://localhost:11434/v1. Set OLLAMA_BASE_URL if Ollama runs on another machine.

# A long local debate on a 32b model can run for many minutes. Checkpointing
# means a crash or a Ctrl-C resumes from the last completed step instead of
# starting the whole run again.
config["checkpoint_enabled"] = True


CONSTITUTION = """
YOUR RULES - read these before you look at the output below.

  Universe        BTC-USD, ETH-USD, SOL-USD. Satellite max 20% of equity,
                  and only with a written justification.
  Risk per trade  2.5% of current equity. 1.5% once you are 20% below peak.
  Sizing          Equity x risk% / stop distance%   (ballast_gate.py computes it)
  Every ticket    entry zone, hard stop, take-profit, max hold <= 5 days.
  Daily limit     -5% on the day  -> NO TRADE, freeze the rest of the day.
  Weekly limit    -12% on the week -> freeze the rest of the week.
  Drawdown        -20% from peak -> risk drops to 1.5%.
                  -30% from peak -> full pause, 14 days, then a written review.
  Open risk       6% across all open positions, total.
  Never           average down. Widen a stop. Touch Warped project tokens.
  Default         "NO TRADE" beats a forced setup.

  The Risk/Exit verifier has full veto. It is ballast_gate.py, not this model.
  The Wind Report is context. It is never a reason on its own.
"""


def main() -> int:
    ticker = (sys.argv[1] if len(sys.argv) > 1 else "SOL-USD").upper()
    run_date = sys.argv[2] if len(sys.argv) > 2 else date.today().isoformat()

    if ticker not in ALLOWED:
        print(f"'{ticker}' is not in the core universe {ALLOWED}.")
        print("Satellite positions are a deliberate exception - size them through")
        print("ballast_gate.py with --satellite and write down why.")
        return 1

    # These are crypto pairs, not companies. Passing asset_type="crypto" drops
    # the fundamentals analyst (there is no balance sheet for Solana) and tells
    # the remaining agents to treat the ticker as an asset. Without it the run
    # goes down the equity path and hunts for filings that do not exist.
    analysts = ("market", "social", "news")

    print("\n" + "=" * 62)
    print("MAJORS DESK - VERSION 2.2")
    print("=" * 62)
    print(CONSTITUTION)
    print(f"Asset: {ticker}    Analysis date: {run_date}")
    print(f"Models: {config['deep_think_llm']} (deep) / {config['quick_think_llm']} (quick)")
    print("A local 32b debate takes a while. Leave it running.\n")

    ta = TradingAgentsGraph(selected_analysts=analysts, debug=True, config=config)
    final_state, signal = ta.propagate(ticker, run_date, asset_type="crypto")

    print("\n" + "=" * 62)
    print("RESEARCH OUTPUT")
    print("=" * 62)
    print(final_state.get("final_trade_decision", "(no decision text returned)"))

    print("\n" + "=" * 62)
    print(f"RATING: {signal}")
    print("=" * 62)

    if str(signal).upper() == "REVIEW":
        print(
            "\nThe model produced no parseable rating. That is not a Hold - it means\n"
            "the run is unusable. Re-run it, or log NO TRADE and move on."
        )
        return 0

    if str(signal).lower() in ("hold", "underweight", "sell"):
        print(
            f"\n'{signal}' is not a long setup. Rule 7: NO TRADE beats a forced one.\n"
            "Log it as NO TRADE and stop here. Recording the no-trades is the point\n"
            "of week one."
        )
        return 0

    print(
        "\nNext step - this rating is not yet a trade. Pick your entry, your hard\n"
        "stop and your target from the research above, then let the gate size it:\n\n"
        f'  python ballast_gate.py --asset {ticker} --direction long \\\n'
        f'      --entry <price> --stop <price> --target <price> \\\n'
        f'      --hold-days 5 --wind "<one line>" --reason "<up to three>" --log\n\n'
        "If the gate vetoes it, the trade does not happen. That is the whole point."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

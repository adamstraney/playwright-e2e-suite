# WARPED TRADING DESK
## Complete Manual – Version 2.2

Owner: Adam (Warped Games)
Goal: Get the system running on your computer tonight
Rule: Follow only this document. Do not mix in other strategies.

> Kept as originally written. Where the setup steps differ from what is actually
> in this folder, `README.md` explains why - three things in Part 2.3 would not
> have behaved as intended. The rules in Parts 0, 4 and 5 are unchanged and are
> what `risk_gate.py` enforces.

---

## PART 0 – CRITICAL RULES (READ FIRST)

Main Desk and Experimental Sleeve use personal capital only.

Never sell or use Warped tokens (or other project-related Sui tokens) for trading.

Warped runway and game server costs stay completely separate from these desks.

Follow the risk rules exactly. No exceptions.

---

## PART 1 – YOUR NUMBERS (FILL IN NOW)

Main Desk starting capital: $ __________

Experimental Sleeve maximum capital: $ __________
(Recommended: 5–10% of total or a fixed small amount such as $150–$300)

Write these numbers down. Do not change them based on emotion later.

---

## PART 2 – ONE-TIME SETUP (Do these in order)

### 2.1 Install Ollama

Go to https://ollama.com/download and install Ollama for your system.

Open a terminal and run:

```bash
ollama pull qwen2.5:14b
ollama pull qwen2.5:32b
```

Leave Ollama running.

### 2.2 Install TradingAgents

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents

conda create -n tradingagents python=3.12 -y
conda activate tradingagents

pip install .
```

(If you do not have conda, install Miniconda first.)

### 2.3 Create the Main Desk Script

Inside the `TradingAgents` folder, create a file named `run_majors.py`.

> The corrected version lives in this folder. See "What changed from the manual"
> in `README.md`.

The Constitution as originally written:

```
You are a low-maintenance side-income trading desk.

ABSOLUTE RULES — THESE CANNOT BE OVERRIDDEN:

1. ONLY these assets are allowed: BTC-USD, ETH-USD, SOL-USD.
   Limited satellite (max 20% of equity) may be considered only if clearly justified.
2. Max risk per trade = 2.5% of current account equity.
3. Position sizing formula (mandatory):
   Position Size = Account Equity × 2.5% ÷ Stop Distance %
4. Every ticket MUST include:
   - Exact entry zone
   - Hard stop-loss
   - Take-profit target(s)
   - Maximum hold time (never more than 5 days)
5. Daily loss limit: if the desk is down 5% on the day → output "NO TRADE - DAILY LIMIT HIT"
6. Weekly loss limit: 12% → freeze for the rest of the week.
7. Prefer "NO TRADE" over forcing a setup.
8. The Risk/Exit function is an independent verifier with full veto power.
9. Real-time X sentiment and Wind Report are supporting context only.
10. Capital preservation comes first.

AGENT ROLES:
- Scout: Price action + Wind Report context on allowed universe.
- Analyst: Technical + basic context.
- Risk/Exit: Independent verifier. Applies all rules above with full veto.
- Desk Lead: Final synthesis only. Outputs strictly in the required format.
```

The required output format:

```
=== FINAL DESK OUTPUT ===
Decision: TICKET / PROBE / NO TRADE
Asset:
Direction:
Entry zone:
Stop loss:
Take profit:
Max hold time:
Risk % of equity:
Position size calculation:
Wind Report influence:
Key reasons (max 3):
Risk notes:
=== END ===

LOG: [date] | [asset] | [Decision] | [one-sentence summary]
```

### 2.4 Wallets / Accounts

Create or choose one wallet/exchange account for the Main Desk. Deposit only the
Main Desk capital.

Create a completely separate wallet/account for the Experimental Sleeve. Deposit
only the limited sleeve capital.

Never mix the two.

### 2.5 Logging Files

Create two simple text or markdown files:

- `Main_Desk_Log.md`
- `Experimental_Sleeve_Log.md`

---

## PART 3 – DAILY WORKFLOW (Start tonight)

**Step 1 – Wind Report.** Paste the Wind Report prompt into Grok. Save the
output. See `wind_report_prompt.md`.

**Step 2 – Run Main Desk.**

```bash
conda activate tradingagents
python run_majors.py
```

Read the full output. Only act on a TICKET or PROBE if it passes every hard rule.

**Step 3 – Log the decision.** Date, decision, asset and key levels. Later:
result plus one short note.

**Step 4 – Experimental Sleeve (optional).** Only if you have clear capacity and
want to test something small. Follow the sleeve's own tighter limits. Log
everything.

---

## PART 4 – HARD RULES (NEVER BREAK)

### Main Desk

- Max risk per trade: 2.5% of current equity
- Max total open risk: 6%
- Max hold time: 5 days
- Daily loss limit: 5% → freeze rest of day
- Weekly loss limit: 12% → freeze rest of week
- 20% drop from peak → reduce risk to 1.5% until new peak
- 30% drop from peak → full pause 14 days + review
- No averaging down
- Stops only tighten, never widen
- Independent Risk/Exit has full veto
- Evidence required for every ticket

### Experimental Sleeve

- Capital strictly limited to the amount you set
- Own tighter daily and weekly loss limits
- 25% drop from its own peak → frozen for 7 days
- Losses stay inside the sleeve
- Profits may be swept to Main Desk or used for tools

### Project Protection Rule

No Warped tokens or other project-related tokens are ever used in either desk.

---

## PART 5 – FIRST WEEK GOAL

Follow every rule exactly for 7 days.

Do not increase size. Do not loosen risk percentages. Record every NO TRADE.

Goal is process discipline, not maximum profit.

---

## PART 6 – QUICK START CHECKLIST (Tonight)

See the checklist at the end of `README.md`.

---

*End of Manual. Protect the Warped runway. Start with process, not aggression.*

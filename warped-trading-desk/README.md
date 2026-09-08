# Warped Trading Desk

Setup and daily tooling for the Warped Trading Desk, v2.2.

Personal capital only. No Warped tokens or other project-related Sui tokens in
either desk, ever. Warped runway and game server costs stay completely separate.

---

## Read this first: where things run

The manual says "get the system running on your computer tonight". That is
exactly right, and it is worth being clear about what that means.

Ollama and the language models have to run **on your own machine**. They are
several gigabytes of model weights doing the thinking locally, on your hardware,
with your data never leaving the house. That is the whole point of the local
setup, and it cannot be done for you on a server somewhere.

What lives in this folder is everything else: the scripts, the rules, the logs
and the prompts. You clone this folder onto your machine, install Ollama and
TradingAgents alongside it, and run it there.

So the honest split is:

| Piece | Where it runs | Who sets it up |
|---|---|---|
| Ollama + qwen2.5 models | Your computer | You, tonight, ~20 min |
| TradingAgents | Your computer | You, tonight, ~10 min |
| `run_majors.py`, `risk_gate.py`, logs | This folder | Done - ready to use |

---

## What changed from the manual, and why

Three things in the manual's `run_majors.py` would not have done what you
expected. All three are fixed in this folder. Worth understanding, because they
change what you can trust the output to be.

### 1. The Constitution was decorative

In the original script, `CONSTITUTION` and `OUTPUT_FORMAT` are Python strings
that get `print()`ed to your terminal. Printing text puts it on your screen. It
does not send it to the AI. The agents never saw a single one of those ten
rules - they ran their standard analysis, and you read a rulebook next to it.

This matters more than it sounds. Rules 2 through 7 are the ones protecting your
capital, and they were not connected to anything.

**The fix:** the rules moved out of the model and into arithmetic. `risk_gate.py`
computes your position size and checks every hard limit in Part 4 as plain maths.
Rule 8 says the Risk/Exit function is an independent verifier with full veto
power - a verifier that is a function cannot be talked out of a veto by a
persuasive argument, at 2am, on a day you want to be in a trade. That is a
stronger guarantee than asking a 32-billion-parameter model to remember ten
rules, and it is the version worth having.

The Constitution is still printed by `run_majors.py`, but now it is honestly
labelled: it is a checklist for **you**, before you read the output.

### 2. Crypto was being analysed as if it were a company

`ta.propagate(ticker, date)` defaults to the stock pipeline. TradingAgents has a
separate crypto pipeline, and the difference is real: on the stock path, agents
go looking for Solana's balance sheet, income statement and insider
transactions. Those do not exist, so that analyst returns noise and the debate
weighs the noise.

**The fix:** `propagate(ticker, run_date, asset_type="crypto")`, and the
fundamentals analyst is dropped from the run, which is what the tool's own CLI
does when it detects a `-USD` pair.

### 3. The output format was never going to appear

The script asks for a `=== FINAL DESK OUTPUT ===` block. But `propagate()`
returns a rating - one of Buy / Overweight / Hold / Underweight / Sell, or
`REVIEW` when nothing parseable came back. You would have waited out a long
local run and got back the word `Hold`.

**The fix:** `run_majors.py` prints the full research text and the rating.
`risk_gate.py` produces the `=== FINAL DESK OUTPUT ===` block, in your exact
format, with real numbers in it - because sizing is the part that has to be
correct, and it is arithmetic, not opinion.

One thing the original was right about that is worth keeping: `backend_url` does
not need setting. The Ollama provider already defaults to
`http://localhost:11434/v1`.

---

## One-time setup

### 1. Install Ollama and pull the models

Download from <https://ollama.com/download>, install it, then in a terminal:

```bash
ollama pull qwen2.5:14b
ollama pull qwen2.5:32b
```

That is roughly 28 GB of download. Leave Ollama running afterwards.

A note on hardware, so tonight is not a surprise: `qwen2.5:32b` wants about
20 GB of memory to run at a sensible speed. On a machine with less, it will
still work but each debate may take a long time. If it crawls, change
`deep_think_llm` to `qwen2.5:14b` in `run_majors.py` and see whether the output
is good enough before spending money on anything.

### 2. Install TradingAgents

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
conda create -n tradingagents python=3.12 -y
conda activate tradingagents
pip install .
```

If you do not have conda, install Miniconda first.

### 3. Put this folder where the scripts can find it

Copy `run_majors.py` from this folder into the `TradingAgents` folder you just
cloned, and keep the rest of this folder wherever you like:

```bash
cp warped-trading-desk/run_majors.py TradingAgents/
```

`risk_gate.py` has no dependencies at all - it runs on any Python 3.10+, in any
folder, with or without conda active. It works tonight even if Ollama gives you
trouble.

### 4. Fill in your numbers

```bash
cp desk_state.example.json desk_state.json
```

Open `desk_state.json` and fill in, for each desk:

- `starting_capital` - what you are funding it with
- `current_equity`, `peak_equity`, `day_start_equity`, `week_start_equity` -
  all four equal to the starting capital on day one

Part 1 of the manual says write these down and do not change them based on
emotion later. The gate enforces that from the other direction: until they are
filled in, it refuses to size anything.

Sleeve sizing, if you have not picked a number: 5-10% of total, or a fixed
small amount like $150-300.

`desk_state.json` is gitignored. Your capital numbers stay on your machine and
never reach GitHub.

### 5. Two wallets

One wallet or exchange account for the Main Desk, holding only Main Desk
capital. A completely separate one for the Experimental Sleeve, holding only the
sleeve capital. Never mix them. Record which is which in the `wallet` field of
each desk in `desk_state.json`.

### 6. Check it works

```bash
python3 risk_gate.py --status
```

It should print both desks and their current state.

---

## Daily workflow

### Step 1 - Wind Report

Paste the prompt from `wind_report_prompt.md` into Grok. Save the answer.
Supporting context only - it is never a reason to trade on its own.

### Step 2 - Run the Main Desk

```bash
conda activate tradingagents
cd TradingAgents
python run_majors.py SOL-USD
```

Defaults to SOL-USD and today's date. Pass a ticker, or a ticker and a date:
`python run_majors.py BTC-USD 2026-09-07`. Only BTC-USD, ETH-USD and SOL-USD
are accepted.

Read the research. If the rating comes back Hold, Underweight or Sell, the
script tells you to stop - that is rule 7 doing its job.

### Step 3 - Size it through the gate

Pick your entry, hard stop and target from the research, then:

```bash
python3 risk_gate.py --asset SOL-USD --direction long \
    --entry 200 --stop 188 --target 224 --hold-days 3 \
    --wind "SOL flow rotating in, Medium confidence" \
    --reason "trend intact; wind rotation; clean invalidation at 188" \
    --log
```

You get the `=== FINAL DESK OUTPUT ===` block with the size computed, or a
`NO TRADE` with the rule that stopped it. `--log` appends the row to
`Main_Desk_Log.md`.

If the gate vetoes, the trade does not happen. There is no override flag, on
purpose.

### Step 4 - Keep the state current

After any trade closes, update `current_equity` in `desk_state.json`, and
`peak_equity` if you made a new high. Set `open_risk_pct` to the total risk
across positions you currently hold. Reset `day_start_equity` each morning and
`week_start_equity` each Monday.

The gate is only as honest as those four numbers. This is the one manual step
in the loop, and it takes about thirty seconds.

### Step 5 - Sleeve, optional

`python3 risk_gate.py --sleeve ...` sizes against the sleeve's capital and its
tighter limits. Skipping it costs nothing.

---

## The hard rules, as implemented

Every one of these is enforced by `risk_gate.py`, not by a model's memory.

| Rule | Main Desk | Sleeve |
|---|---|---|
| Risk per trade | 2.5% | 2.0% |
| Risk after -20% from peak | 1.5% | 1.0% (at -15%) |
| Max total open risk | 6% | 4% |
| Max hold | 5 days | 5 days |
| Daily loss limit | -5%, freeze the day | -4% |
| Weekly loss limit | -12%, freeze the week | -10% |
| Full pause | -30% from peak, 14 days | -25% from peak, 7 days |
| Satellite cap | 20% of equity | 20% |

The manual specifies the sleeve's limits only as "tighter". The numbers above
are a starting point - change them in `rule_overrides` in `desk_state.json` if
you want different ones, but set them once, in advance, not mid-drawdown.

Also enforced: no stop, no trade. Long stops below entry, short stops above.
Non-core assets refused unless you explicitly flag them as satellite.

### One thing the sizing formula does not know about

`Position Size = Equity x 2.5% / Stop Distance %` is correct, and it has a sharp
edge. As the stop gets tighter, the position gets bigger. At a 2.5% stop
distance the position is 100% of your equity. At 1%, the formula asks for 2.5x
your account - which is leverage, which is not in your rules anywhere.

The gate flags this instead of quietly sizing into it. When you see the
LEVERAGE warning: widen the stop, or cap the position at your equity and take
the smaller risk. Do not add leverage to make the formula fit.

---

## Week one

Follow every rule exactly for seven days. Do not increase size. Do not loosen a
percentage. Record every NO TRADE.

The goal is process discipline, not maximum profit. A week of eight NO TRADE
rows in the log is a successful week one.

---

## Files

| File | What it is |
|---|---|
| `run_majors.py` | Step 2. Runs TradingAgents on one allowed asset. Copy into the TradingAgents folder. |
| `risk_gate.py` | Step 3. Sizing and the hard-rule veto. No dependencies. |
| `desk_state.example.json` | Template for your numbers. Copy to `desk_state.json`. |
| `wind_report_prompt.md` | Step 1. The Wind Report prompt. |
| `Main_Desk_Log.md` | Step 4. Decision log. |
| `Experimental_Sleeve_Log.md` | Sleeve log. |
| `MANUAL.md` | The original manual, kept as written. |

---

## Tonight's checklist

- [ ] Main Desk and sleeve capital numbers decided and written into `desk_state.json`
- [ ] Ollama installed, both models pulled, Ollama left running
- [ ] TradingAgents installed, `conda activate tradingagents` works
- [ ] `run_majors.py` copied into the TradingAgents folder
- [ ] `python3 risk_gate.py --status` prints both desks
- [ ] Main Desk wallet funded
- [ ] Sleeve wallet funded, separate account
- [ ] First Wind Report run and saved
- [ ] First `run_majors.py` cycle run end to end
- [ ] Result logged, even if it was NO TRADE

---

## A note on what this system is

This is a decision-support and discipline tool. It sizes positions correctly,
enforces your limits without negotiation, and makes you write down every
decision. Those are real and worth having.

It does not predict prices, and neither does the model behind it. A local
language model reading recent price data and news has no edge on direction, and
the research output should be read as a structured second opinion rather than a
signal. The part of this system most likely to make a difference over a year is
Part 4 and the logging - the parts that are just arithmetic and honesty.

Protect the Warped runway. Start with process, not aggression.

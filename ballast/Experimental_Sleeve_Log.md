# Experimental Sleeve Log

Capital is capped at the sleeve number and never topped up from the Main Desk.

Every cycle gets a line - including the days the answer is NO TRADE. The
no-trades are the record that the process is working. Week one is scored on
whether every day has a row, not on the P&L column.

`ballast_gate.py --log` appends the row for you; you fill in Result and Note when
the position closes.

| Date | Asset | Decision | Dir | Entry | Stop | Target | Risk % | Size | Result | Note |
|------|-------|----------|-----|-------|------|--------|--------|------|--------|------|

## Sleeve rules

- Losses stay inside the sleeve. A loss here is never funded from the Main Desk.
- Profits may be swept to the Main Desk or spent on tools.
- 25% below the sleeve's own peak -> frozen 7 days.
- Optional. A skipped sleeve day costs nothing.

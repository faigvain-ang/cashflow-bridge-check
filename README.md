# Cashflow Bridge Check

A local cash-flow reconciliation CLI using exact decimal-string inputs. Python **3.11+**, standard library only; no API key, installation step, model, or network request at runtime.

[Español](README.es.md) · [Cashflow Fieldnotes](https://filings.findfindata.com/)

## Run from source

```sh
git clone https://github.com/faigvain-ang/cashflow-bridge-check.git
cd cashflow-bridge-check
python cashflow_bridge.py examples/reconciled.json --json
python -m unittest discover -s tests -v
python site/build.py
```

On Windows, `python` must resolve to a Python 3.11+ installation. On systems using `python3`, replace `python` accordingly. There are **no third-party runtime or test dependencies**; no virtual environment is required.

## Input and result

The synthetic sample uses USD **millions**, one FY2025 period, and the same cash-and-cash-equivalents scope at both ends. Required metadata: `period`, `currency`, `unit`, `cash_basis`. All six amounts must be JSON **strings**, including an explicit `fx` (use `"0"` only after confirming no FX effect).

```json
{
  "period": "FY2025 — synthetic example",
  "currency": "USD",
  "unit": "million",
  "cash_basis": "Cash and cash equivalents; same scope at both period ends",
  "opening": "100", "operating": "35", "investing": "-20",
  "financing": "-10", "fx": "-2", "closing": "103",
  "adjustments": []
}
```

Formula: `opening + operating + investing + financing + fx + explicit adjustments = calculated closing`. **Net cash outflows are negative.** Do not negate a disclosed negative value again. Result: calculated `103`, reported `103`, difference `0`, `matches: true`. Difference always means **reported minus calculated**.

`--tolerance 0.01` is an absolute tolerance in the supplied unit: with millions, `0.01` means 10,000 currency units. Use `--tolerance 0` for exact equality. Exit codes: **0** match, **1** mismatch, **2** invalid input/CLI usage. Optional adjustments are objects such as `{"label":"Scope change","amount":"5"}`; only add independently supported items, never a balancing plug.

## Scope and limits

The tool checks arithmetic, not financial truth. It does not read PDFs, find omitted items, translate accounts, convert currency/units, or determine whether the cash definitions match. Manually verify period, scope, sign and units against the source. No investment advice, trading signal or promise of returns. Nonfinite values and JSON numeric amounts are rejected. Decimal context is sized to preserve the supplied integral/fractional places rather than silently using the default 28-digit precision.

## Site and maintenance

`site/content.json`, `site/config.json`, and the standard-library `site/build.py` build the independent bilingual static site into `docs/`. The final hostname is `filings.findfindata.com`; no document upload, analytics, backend or login. The site source and output are versioned together.

Maintained under **faigvain-ang** by the same team developing related Eqvero, KolmoPDF and KomoPDF ecosystem tools. This is not an independent product review or an official Eqvero API client. For source-linked public-filing research, see [Eqvero](https://eqvero.com/) and its [company research entry](https://eqvero.com/companies).

MIT license; no bundled third-party runtime code. All examples are synthetic, not company filings.

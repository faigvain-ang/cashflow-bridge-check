"""A deterministic cash-flow bridge. Python 3.11+, standard library only."""
import argparse
import json
import sys
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

AMOUNTS = ("opening", "operating", "investing", "financing", "fx", "closing")


def amount(value, name):
    if not isinstance(value, str):
        raise ValueError(f"{name}: use a decimal string, not a JSON number")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{name}: invalid decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{name}: amount must be finite")
    return result


def reconcile(data, tolerance="0.01"):
    for key in ("period", "currency", "unit", "cash_basis"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"{key}: a nonempty description is required")
    values = {key: amount(data.get(key), key) for key in AMOUNTS}
    limit = amount(tolerance, "tolerance")
    if limit < 0:
        raise ValueError("tolerance must be nonnegative")
    extra = []
    for item in data.get("adjustments", []):
        if not isinstance(item, dict) or not isinstance(item.get("label"), str) or not item["label"].strip():
            raise ValueError("each adjustment needs a nonempty label and decimal-string amount")
        extra.append(amount(item.get("amount"), item["label"]))
    terms = list(values.values()) + extra + [limit]
    # Size the context for all integral/fractional places, not Decimal's default 28 digits.
    precision = max(28, max(x.adjusted() for x in terms) - min(x.as_tuple().exponent for x in terms) + len(str(len(terms))) + 4)
    with localcontext() as context:
        context.prec = precision
        expected = sum((values[k] for k in AMOUNTS if k != "closing"), Decimal(0)) + sum(extra, Decimal(0))
        difference = values["closing"] - expected
        return {
            **{k: data[k] for k in ("period", "currency", "unit", "cash_basis")},
            "calculated_closing": format(expected, "f"),
            "reported_closing": format(values["closing"], "f"),
            "difference_reported_minus_calculated": format(difference, "f"),
            "tolerance": format(limit, "f"),
            "matches": abs(difference) <= limit,
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check opening + operating + investing + financing + FX + explicit adjustments = closing. Outflows must be negative.")
    parser.add_argument("input", type=Path, help="UTF-8 JSON; decimal-string amounts in one unit/currency/cash basis")
    parser.add_argument("--tolerance", default="0.01", help="absolute tolerance in the input unit (default 0.01)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        result = reconcile(json.loads(args.input.read_text(encoding="utf-8")), args.tolerance)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['period']} | {result['currency']} ({result['unit']})")
        print(f"Calculated closing: {result['calculated_closing']}")
        print(f"Reported closing:   {result['reported_closing']}")
        print(f"Difference:         {result['difference_reported_minus_calculated']}")
        print(f"Tolerance:          {result['tolerance']}")
        print("MATCH" if result["matches"] else "MISMATCH")
    return 0 if result["matches"] else 1


if __name__ == "__main__":
    sys.exit(main())

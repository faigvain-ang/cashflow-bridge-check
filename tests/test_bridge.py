import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cashflow_bridge import reconcile


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples/reconciled.json").read_text(encoding="utf-8"))

    def test_signed_flows_and_fx(self):
        self.assertEqual(reconcile(self.data)["calculated_closing"], "103")
        self.assertTrue(reconcile(self.data)["matches"])

    def test_missing_fx_is_not_zero(self):
        del self.data["fx"]
        with self.assertRaises(ValueError):
            reconcile(self.data)

    def test_mismatch_and_boundary(self):
        self.data["closing"] = "103.01"
        self.assertTrue(reconcile(self.data, "0.01")["matches"])
        self.assertFalse(reconcile(self.data, "0.009")["matches"])

    def test_exact_and_large_decimals(self):
        for key in ("opening", "operating", "investing", "financing", "fx", "closing"):
            self.data[key] = "0"
        self.data.update(opening="1000000000000000000000000000000.1", operating="0.2", closing="1000000000000000000000000000000.3")
        result = reconcile(self.data, "0")
        self.assertEqual(result["calculated_closing"], self.data["closing"])
        self.assertTrue(result["matches"])

    def test_explicit_adjustment(self):
        self.data.update(closing="108", adjustments=[{"label": "Scope change", "amount": "5"}])
        self.assertTrue(reconcile(self.data)["matches"])

    def test_invalid(self):
        for value in ("NaN", "Infinity", "1,20", 10, None):
            data = copy.deepcopy(self.data)
            data["opening"] = value
            with self.assertRaises(ValueError):
                reconcile(data)
        with self.assertRaises(ValueError):
            reconcile(self.data, "-1")


if __name__ == "__main__":
    unittest.main()

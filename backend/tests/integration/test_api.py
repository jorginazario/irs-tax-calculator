"""Integration tests for the FastAPI API layer."""

from decimal import Decimal

from starlette.testclient import TestClient

from src.api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# POST /api/calculate — full calculation
# ---------------------------------------------------------------------------


class TestFullCalculation:
    """POST /api/calculate — end-to-end tests."""

    def test_simple_w2_single(self):
        """Single filer, $75k W-2 wages."""
        payload = {
            "filing_status": "SINGLE",
            "w2s": [{"wages": "75000", "federal_withholding": "9000"}],
        }
        resp = client.post("/api/calculate", json=payload)
        assert resp.status_code == 200

        data = resp.json()
        summary = data["summary"]

        # Verify structure
        assert summary["filing_status"] == "SINGLE"
        assert Decimal(summary["total_income"]) == Decimal("75000")
        assert Decimal(summary["agi"]) == Decimal("75000")
        # Standard deduction for SINGLE = $14,600
        assert Decimal(summary["deduction_amount"]) == Decimal("14600")
        # Taxable income = 75000 - 14600 = 60400
        assert Decimal(summary["taxable_income"]) == Decimal("60400")
        # Total tax should be positive
        assert Decimal(summary["total_tax"]) > 0
        # Effective rate should be between 0 and 1
        assert Decimal("0") < Decimal(summary["effective_rate"]) < Decimal("1")

    def test_mixed_income_w2_div_cap_gains(self):
        """Mixed income: W-2 + 1099-DIV + 1099-B."""
        payload = {
            "filing_status": "MARRIED_FILING_JOINTLY",
            "w2s": [{"wages": "120000", "federal_withholding": "15000"}],
            "income_1099_div": [
                {"ordinary_dividends": "5000", "qualified_dividends": "3000"}
            ],
            "income_1099_b": [
                {"short_term_gains": "2000", "long_term_gains": "10000"}
            ],
        }
        resp = client.post("/api/calculate", json=payload)
        assert resp.status_code == 200

        data = resp.json()
        summary = data["summary"]

        # Total income = 120000 + 5000 + 2000 + 10000 = 137000
        assert Decimal(summary["total_income"]) == Decimal("137000")
        assert summary["filing_status"] == "MARRIED_FILING_JOINTLY"
        # Should have investment income components
        tax_comp = data["tax_computation"]
        assert "capital_gains_tax" in tax_comp
        assert "qualified_dividend_tax" in tax_comp

    def test_invalid_filing_status_returns_422(self):
        """Invalid filing status should return 422."""
        payload = {
            "filing_status": "INVALID_STATUS",
            "w2s": [{"wages": "50000"}],
        }
        resp = client.post("/api/calculate", json=payload)
        assert resp.status_code == 422

    def test_missing_filing_status_returns_422(self):
        """Missing filing_status field should return 422."""
        payload = {
            "w2s": [{"wages": "50000"}],
        }
        resp = client.post("/api/calculate", json=payload)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/calculate/estimate — quick estimate
# ---------------------------------------------------------------------------


class TestQuickEstimate:
    """POST /api/calculate/estimate — quick estimate tests."""

    def test_estimate_100k_single(self):
        """$100k single filer quick estimate."""
        payload = {
            "gross_income": "100000",
            "filing_status": "SINGLE",
        }
        resp = client.post("/api/calculate/estimate", json=payload)
        assert resp.status_code == 200

        data = resp.json()
        assert Decimal(data["gross_income"]) == Decimal("100000")
        assert data["filing_status"] == "SINGLE"
        # Standard deduction for SINGLE = $14,600
        assert Decimal(data["standard_deduction"]) == Decimal("14600")
        # Taxable = 100000 - 14600 = 85400
        assert Decimal(data["taxable_income"]) == Decimal("85400")
        # Tax should be positive and reasonable
        assert Decimal(data["estimated_tax"]) > 0
        # Effective rate between 0 and 1
        assert Decimal("0") < Decimal(data["effective_rate"]) < Decimal("1")
        # Marginal rate for 85400 single should be 22%
        assert Decimal(data["marginal_rate"]) == Decimal("0.22")


# ---------------------------------------------------------------------------
# GET /api/brackets/2024 — tax brackets
# ---------------------------------------------------------------------------


class TestBrackets:
    """GET /api/brackets/2024 — bracket data tests."""

    def test_returns_all_filing_statuses(self):
        """Should return brackets for all 5 filing statuses."""
        resp = client.get("/api/brackets/2024")
        assert resp.status_code == 200

        data = resp.json()
        assert data["tax_year"] == 2024

        expected_statuses = {
            "SINGLE",
            "MARRIED_FILING_JOINTLY",
            "MARRIED_FILING_SEPARATELY",
            "HEAD_OF_HOUSEHOLD",
            "QUALIFYING_SURVIVING_SPOUSE",
        }
        assert set(data["brackets"].keys()) == expected_statuses

    def test_seven_brackets_each(self):
        """Each filing status should have 7 brackets."""
        resp = client.get("/api/brackets/2024")
        data = resp.json()

        for status, brackets in data["brackets"].items():
            assert len(brackets) == 7, f"{status} has {len(brackets)} brackets, expected 7"

    def test_last_bracket_has_no_upper_bound(self):
        """The top bracket should have upper_bound = null."""
        resp = client.get("/api/brackets/2024")
        data = resp.json()

        for status, brackets in data["brackets"].items():
            assert brackets[-1]["upper_bound"] is None, (
                f"{status} top bracket should have no upper bound"
            )


# ---------------------------------------------------------------------------
# GET /api/deductions/2024 — standard deductions
# ---------------------------------------------------------------------------


class TestDeductions:
    """GET /api/deductions/2024 — standard deduction tests."""

    def test_returns_all_filing_statuses(self):
        """Should return deductions for all 5 filing statuses."""
        resp = client.get("/api/deductions/2024")
        assert resp.status_code == 200

        data = resp.json()
        assert data["tax_year"] == 2024

        expected_statuses = {
            "SINGLE",
            "MARRIED_FILING_JOINTLY",
            "MARRIED_FILING_SEPARATELY",
            "HEAD_OF_HOUSEHOLD",
            "QUALIFYING_SURVIVING_SPOUSE",
        }
        assert set(data["standard_deductions"].keys()) == expected_statuses

    def test_deduction_values_match_constants(self):
        """Deduction amounts should match the constants in tax_year_2024.py."""
        resp = client.get("/api/deductions/2024")
        data = resp.json()

        expected = {
            "SINGLE": "14600",
            "MARRIED_FILING_JOINTLY": "29200",
            "MARRIED_FILING_SEPARATELY": "14600",
            "HEAD_OF_HOUSEHOLD": "21900",
            "QUALIFYING_SURVIVING_SPOUSE": "29200",
        }
        for status, amount in expected.items():
            assert Decimal(data["standard_deductions"][status]) == Decimal(amount), (
                f"{status}: expected {amount}, got {data['standard_deductions'][status]}"
            )

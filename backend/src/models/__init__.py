"""Tax calculator models — re-exports for convenience."""

from src.models.exceptions import (
    InvalidFilingStatusError,
    MissingIncomeDataError,
    NegativeIncomeError,
    TaxCalculatorError,
    UnsupportedScenarioError,
)
from src.models.filing_status import FilingStatus
from src.models.tax_input import (
    AboveLineDeductions,
    AGIInput,
    BracketTaxInput,
    CapitalGainsTaxInput,
    CreditInput,
    FicaInput,
    GrossIncome,
    NiitInput,
    QualifiedDividendTaxInput,
    StandardDeductionInput,
)
from src.models.tax_output import (
    AGIResult,
    BracketDetail,
    BracketTaxResult,
    CapitalGainsTaxResult,
    CreditResult,
    FicaResult,
    NiitResult,
    PreferentialRateDetail,
    QualifiedDividendTaxResult,
    StandardDeductionResult,
)

__all__ = [
    "AGIInput",
    "AGIResult",
    "AboveLineDeductions",
    "BracketDetail",
    "BracketTaxInput",
    "BracketTaxResult",
    "CapitalGainsTaxInput",
    "CapitalGainsTaxResult",
    "CreditInput",
    "CreditResult",
    "FicaInput",
    "FicaResult",
    "FilingStatus",
    "GrossIncome",
    "InvalidFilingStatusError",
    "MissingIncomeDataError",
    "NegativeIncomeError",
    "NiitInput",
    "NiitResult",
    "PreferentialRateDetail",
    "QualifiedDividendTaxInput",
    "QualifiedDividendTaxResult",
    "StandardDeductionInput",
    "StandardDeductionResult",
    "TaxCalculatorError",
    "UnsupportedScenarioError",
]

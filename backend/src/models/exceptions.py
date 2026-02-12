"""Custom exceptions for the IRS Tax Calculator."""


class TaxCalculatorError(Exception):
    """Base exception for all tax calculator errors."""


class InvalidFilingStatusError(TaxCalculatorError):
    """Raised when an unrecognized filing status is provided."""


class MissingIncomeDataError(TaxCalculatorError):
    """Raised when required income data is absent."""


class NegativeIncomeError(TaxCalculatorError):
    """Raised when a non-negative income field receives a negative value."""


class UnsupportedScenarioError(TaxCalculatorError):
    """Raised when the calculator encounters a scenario it cannot handle."""

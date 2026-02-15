import type {
  W2Income,
  Income1099NEC,
  Income1099INT,
  Income1099DIV,
  Income1099B,
  ItemizedDeductions,
  TaxReturnInput,
} from '../types/index.ts';

export function createEmptyW2(): W2Income {
  return {
    wages: '',
    federal_withholding: '',
    social_security_wages: '',
    medicare_wages: '',
  };
}

export function createEmpty1099NEC(): Income1099NEC {
  return {
    compensation: '',
  };
}

export function createEmpty1099INT(): Income1099INT {
  return {
    interest: '',
  };
}

export function createEmpty1099DIV(): Income1099DIV {
  return {
    ordinary_dividends: '',
    qualified_dividends: '',
  };
}

export function createEmpty1099B(): Income1099B {
  return {
    short_term_gains: '',
    long_term_gains: '',
  };
}

export function createEmptyItemizedDeductions(): ItemizedDeductions {
  return {
    medical: '',
    state_and_local_taxes: '',
    mortgage_interest: '',
    charitable: '',
    casualty: '',
    other: '',
  };
}

export function createEmptyTaxReturn(): TaxReturnInput {
  return {
    filing_status: 'SINGLE',
    is_over_65: false,
    is_blind: false,
    w2s: [],
    income_1099_nec: [],
    income_1099_int: [],
    income_1099_div: [],
    income_1099_b: [],
    itemized_deductions: null,
    force_standard_deduction: false,
    hsa_deduction: '',
    student_loan_interest: '',
    educator_expenses: '',
    ira_deduction: '',
    self_employed_health_insurance: '',
    credits: { num_qualifying_children: 0 },
    estimated_payments: '',
  };
}

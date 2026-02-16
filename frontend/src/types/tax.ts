/**
 * TypeScript type definitions mirroring backend Pydantic models.
 * All Decimal fields serialize as strings in JSON.
 */

// --- Filing Status (mirrors backend/src/models/filing_status.py) ---

export type FilingStatus =
  | 'SINGLE'
  | 'MARRIED_FILING_JOINTLY'
  | 'MARRIED_FILING_SEPARATELY'
  | 'HEAD_OF_HOUSEHOLD'
  | 'QUALIFYING_SURVIVING_SPOUSE';

// --- Form-level INPUT models (mirrors backend/src/models/workflow_models.py) ---

export interface W2Income {
  wages: string;
  federal_withholding: string;
  social_security_wages: string;
  medicare_wages: string;
}

export interface Income1099NEC {
  compensation: string;
}

export interface Income1099INT {
  interest: string;
}

export interface Income1099DIV {
  ordinary_dividends: string;
  qualified_dividends: string;
}

export interface Income1099B {
  short_term_gains: string;
  long_term_gains: string;
}

export interface ItemizedDeductions {
  medical: string;
  state_and_local_taxes: string;
  mortgage_interest: string;
  charitable: string;
  casualty: string;
  other: string;
}

export interface TaxCredits {
  num_qualifying_children: number;
}

export interface TaxReturnInput {
  filing_status: FilingStatus;
  is_over_65: boolean;
  is_blind: boolean;
  w2s: W2Income[];
  income_1099_nec: Income1099NEC[];
  income_1099_int: Income1099INT[];
  income_1099_div: Income1099DIV[];
  income_1099_b: Income1099B[];
  itemized_deductions: ItemizedDeductions | null;
  force_standard_deduction: boolean;
  hsa_deduction: string;
  student_loan_interest: string;
  educator_expenses: string;
  ira_deduction: string;
  self_employed_health_insurance: string;
  credits: TaxCredits;
  estimated_payments: string;
}

// --- Workflow OUTPUT models (mirrors backend/src/models/workflow_models.py) ---

export interface IncomeResult {
  wages: string;
  self_employment_income: string;
  interest_income: string;
  ordinary_dividends: string;
  qualified_dividends: string;
  short_term_gains: string;
  long_term_gains: string;
  total_gross_income: string;
  net_investment_income: string;
}

export interface FicaResult {
  ss_tax: string;
  medicare_tax: string;
  additional_medicare_tax: string;
  se_tax: string;
  se_tax_deduction: string;
  total_fica: string;
}

export interface AGIResult {
  total_gross_income: string;
  total_above_line_deductions: string;
  agi: string;
}

export interface DeductionResult {
  standard_deduction_amount: string;
  itemized_total: string;
  used_standard: boolean;
  deduction_amount: string;
  taxable_income: string;
  ordinary_taxable_income: string;
  preferential_qualified_dividends: string;
  preferential_long_term_gains: string;
}

export interface TaxComputationResult {
  ordinary_tax: string;
  qualified_dividend_tax: string;
  capital_gains_tax: string;
  niit: string;
  total_income_tax: string;
}

export interface CreditsResult {
  child_tax_credit: string;
  nonrefundable_ctc_applied: string;
  refundable_ctc_applied: string;
  total_credits_applied: string;
  tax_after_credits: string;
}

export interface TaxSummary {
  filing_status: FilingStatus;
  total_income: string;
  agi: string;
  deduction_amount: string;
  taxable_income: string;
  ordinary_tax: string;
  qualified_dividend_tax: string;
  capital_gains_tax: string;
  niit: string;
  total_income_tax_before_credits: string;
  total_credits: string;
  income_tax_after_credits: string;
  total_fica: string;
  total_tax: string;
  effective_rate: string;
  marginal_rate: string;
  total_withholding: string;
  estimated_payments: string;
  total_payments: string;
  refund_or_owed: string;
}

export interface FullTaxCalculationResult {
  income: IncomeResult;
  fica: FicaResult;
  agi: AGIResult;
  deductions: DeductionResult;
  tax_computation: TaxComputationResult;
  credits: CreditsResult;
  summary: TaxSummary;
}

// --- Estimate models (POST /api/calculate/estimate) ---

export interface EstimateInput {
  gross_income: string;
  filing_status: FilingStatus;
}

export interface EstimateResult {
  gross_income: string;
  filing_status: FilingStatus;
  standard_deduction: string;
  taxable_income: string;
  estimated_tax: string;
  effective_rate: string;
  marginal_rate: string;
}

// --- Reference data (GET /api/brackets/2024, GET /api/deductions/2024) ---

export interface BracketEntry {
  upper_bound: string | null;
  rate: string;
}

export interface BracketsResponse {
  tax_year: number;
  brackets: Record<string, BracketEntry[]>;
}

export interface DeductionsResponse {
  tax_year: number;
  standard_deductions: Record<string, string>;
}

// --- History models (mirrors backend/src/api/models.py) ---

export interface CalculationSummary {
  id: number;
  created_at: string;
  filing_status: string;
  total_income: number;
  agi: number;
  taxable_income: number;
  federal_tax: number;
  total_credits: number;
  total_tax: number;
  effective_rate: number;
  marginal_rate: number;
  refund_or_owed: number;
}

export interface CalculationDetail extends CalculationSummary {
  input_data: TaxReturnInput;
  result_data: FullTaxCalculationResult;
}

export interface DeleteResponse {
  success: boolean;
  message: string;
}

// --- Analytics models ---

export type AnalysisTool = 'query' | 'chart' | 'table' | 'report';

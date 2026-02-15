import type { TaxReturnInput } from '../types/index.ts';

const NON_NEGATIVE_DECIMAL_RE = /^\d+(\.\d+)?$/;
const DECIMAL_RE = /^-?\d+(\.\d+)?$/;

/**
 * Check if a string represents a non-negative decimal number.
 */
export function isNonNegativeDecimal(value: string): boolean {
  return NON_NEGATIVE_DECIMAL_RE.test(value);
}

/**
 * Check if a string represents a decimal number (allows negative for capital gains/losses).
 */
export function isDecimal(value: string): boolean {
  return DECIMAL_RE.test(value);
}

/**
 * Validate a TaxReturnInput and return an array of error messages.
 * Returns an empty array if the input is valid.
 */
export function validateTaxReturn(input: TaxReturnInput): string[] {
  const errors: string[] = [];

  // Filing status is required (always present since it's typed, but check for empty)
  if (!input.filing_status) {
    errors.push('Filing status is required.');
  }

  // Validate W-2s
  for (let i = 0; i < input.w2s.length; i++) {
    const w2 = input.w2s[i];
    if (w2.wages && !isNonNegativeDecimal(w2.wages)) {
      errors.push(`W-2 #${i + 1}: wages must be a non-negative number.`);
    }
    if (w2.federal_withholding && !isNonNegativeDecimal(w2.federal_withholding)) {
      errors.push(`W-2 #${i + 1}: federal withholding must be a non-negative number.`);
    }
    if (w2.social_security_wages && !isNonNegativeDecimal(w2.social_security_wages)) {
      errors.push(`W-2 #${i + 1}: Social Security wages must be a non-negative number.`);
    }
    if (w2.medicare_wages && !isNonNegativeDecimal(w2.medicare_wages)) {
      errors.push(`W-2 #${i + 1}: Medicare wages must be a non-negative number.`);
    }
  }

  // Validate 1099-NEC
  for (let i = 0; i < input.income_1099_nec.length; i++) {
    const nec = input.income_1099_nec[i];
    if (nec.compensation && !isNonNegativeDecimal(nec.compensation)) {
      errors.push(`1099-NEC #${i + 1}: compensation must be a non-negative number.`);
    }
  }

  // Validate 1099-INT
  for (let i = 0; i < input.income_1099_int.length; i++) {
    const int = input.income_1099_int[i];
    if (int.interest && !isNonNegativeDecimal(int.interest)) {
      errors.push(`1099-INT #${i + 1}: interest must be a non-negative number.`);
    }
  }

  // Validate 1099-DIV
  for (let i = 0; i < input.income_1099_div.length; i++) {
    const div = input.income_1099_div[i];
    if (div.ordinary_dividends && !isNonNegativeDecimal(div.ordinary_dividends)) {
      errors.push(`1099-DIV #${i + 1}: ordinary dividends must be a non-negative number.`);
    }
    if (div.qualified_dividends && !isNonNegativeDecimal(div.qualified_dividends)) {
      errors.push(`1099-DIV #${i + 1}: qualified dividends must be a non-negative number.`);
    }
    const ordinaryNum = parseFloat(div.ordinary_dividends || '0');
    const qualifiedNum = parseFloat(div.qualified_dividends || '0');
    if (!Number.isNaN(ordinaryNum) && !Number.isNaN(qualifiedNum) && qualifiedNum > ordinaryNum) {
      errors.push(`1099-DIV #${i + 1}: qualified dividends cannot exceed ordinary dividends.`);
    }
  }

  // Validate 1099-B (allows negative for losses)
  for (let i = 0; i < input.income_1099_b.length; i++) {
    const b = input.income_1099_b[i];
    if (b.short_term_gains && !isDecimal(b.short_term_gains)) {
      errors.push(`1099-B #${i + 1}: short-term gains must be a valid number.`);
    }
    if (b.long_term_gains && !isDecimal(b.long_term_gains)) {
      errors.push(`1099-B #${i + 1}: long-term gains must be a valid number.`);
    }
  }

  // Validate above-the-line deductions
  if (input.hsa_deduction && !isNonNegativeDecimal(input.hsa_deduction)) {
    errors.push('HSA deduction must be a non-negative number.');
  }
  if (input.student_loan_interest && !isNonNegativeDecimal(input.student_loan_interest)) {
    errors.push('Student loan interest must be a non-negative number.');
  }
  if (input.educator_expenses && !isNonNegativeDecimal(input.educator_expenses)) {
    errors.push('Educator expenses must be a non-negative number.');
  }
  if (input.ira_deduction && !isNonNegativeDecimal(input.ira_deduction)) {
    errors.push('IRA deduction must be a non-negative number.');
  }
  if (input.self_employed_health_insurance && !isNonNegativeDecimal(input.self_employed_health_insurance)) {
    errors.push('Self-employed health insurance must be a non-negative number.');
  }

  // Validate itemized deductions (if provided)
  if (input.itemized_deductions) {
    const d = input.itemized_deductions;
    const fields = [
      ['medical', d.medical],
      ['state and local taxes', d.state_and_local_taxes],
      ['mortgage interest', d.mortgage_interest],
      ['charitable', d.charitable],
      ['casualty', d.casualty],
      ['other', d.other],
    ] as const;
    for (const [name, val] of fields) {
      if (val && !isNonNegativeDecimal(val)) {
        errors.push(`Itemized deduction "${name}" must be a non-negative number.`);
      }
    }
  }

  // Validate estimated payments
  if (input.estimated_payments && !isNonNegativeDecimal(input.estimated_payments)) {
    errors.push('Estimated payments must be a non-negative number.');
  }

  return errors;
}

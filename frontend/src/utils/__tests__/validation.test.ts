import { describe, it, expect } from 'vitest';

import { isNonNegativeDecimal, isDecimal, validateTaxReturn } from '../validation.ts';
import { createEmptyTaxReturn } from '../defaults.ts';
import type { TaxReturnInput } from '../../types/index.ts';

describe('isNonNegativeDecimal', () => {
  it('accepts "0"', () => {
    expect(isNonNegativeDecimal('0')).toBe(true);
  });

  it('accepts positive integers', () => {
    expect(isNonNegativeDecimal('12345')).toBe(true);
  });

  it('accepts positive decimals', () => {
    expect(isNonNegativeDecimal('123.45')).toBe(true);
  });

  it('rejects negative numbers', () => {
    expect(isNonNegativeDecimal('-100')).toBe(false);
  });

  it('rejects non-numeric strings', () => {
    expect(isNonNegativeDecimal('abc')).toBe(false);
  });

  it('rejects empty string', () => {
    expect(isNonNegativeDecimal('')).toBe(false);
  });
});

describe('isDecimal', () => {
  it('accepts positive numbers', () => {
    expect(isDecimal('123.45')).toBe(true);
  });

  it('accepts negative numbers', () => {
    expect(isDecimal('-500.00')).toBe(true);
  });

  it('accepts zero', () => {
    expect(isDecimal('0')).toBe(true);
  });

  it('rejects non-numeric strings', () => {
    expect(isDecimal('abc')).toBe(false);
  });

  it('rejects empty string', () => {
    expect(isDecimal('')).toBe(false);
  });
});

describe('validateTaxReturn', () => {
  it('returns no errors for a valid empty return', () => {
    const input = createEmptyTaxReturn();
    expect(validateTaxReturn(input)).toEqual([]);
  });

  it('returns no errors for valid W-2 data', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      w2s: [{ wages: '50000', federal_withholding: '5000', social_security_wages: '50000', medicare_wages: '50000' }],
    };
    expect(validateTaxReturn(input)).toEqual([]);
  });

  it('catches invalid W-2 wages', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      w2s: [{ wages: 'abc', federal_withholding: '0', social_security_wages: '0', medicare_wages: '0' }],
    };
    const errors = validateTaxReturn(input);
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain('W-2 #1');
    expect(errors[0]).toContain('wages');
  });

  it('catches negative W-2 withholding', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      w2s: [{ wages: '50000', federal_withholding: '-100', social_security_wages: '0', medicare_wages: '0' }],
    };
    const errors = validateTaxReturn(input);
    expect(errors.length).toBeGreaterThan(0);
  });

  it('catches qualified dividends exceeding ordinary dividends', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      income_1099_div: [{ ordinary_dividends: '100', qualified_dividends: '200' }],
    };
    const errors = validateTaxReturn(input);
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain('qualified dividends cannot exceed ordinary dividends');
  });

  it('allows negative capital gains (losses)', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      income_1099_b: [{ short_term_gains: '-500', long_term_gains: '-1000' }],
    };
    expect(validateTaxReturn(input)).toEqual([]);
  });

  it('catches invalid capital gains input', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      income_1099_b: [{ short_term_gains: 'xyz', long_term_gains: '100' }],
    };
    const errors = validateTaxReturn(input);
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain('1099-B #1');
  });

  it('catches invalid above-the-line deductions', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      hsa_deduction: '-100',
      student_loan_interest: 'abc',
    };
    const errors = validateTaxReturn(input);
    expect(errors).toHaveLength(2);
  });

  it('catches invalid itemized deductions', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      itemized_deductions: {
        medical: 'abc',
        state_and_local_taxes: '0',
        mortgage_interest: '0',
        charitable: '0',
        casualty: '0',
        other: '0',
      },
    };
    const errors = validateTaxReturn(input);
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain('medical');
  });

  it('catches invalid estimated payments', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      estimated_payments: '-500',
    };
    const errors = validateTaxReturn(input);
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain('Estimated payments');
  });

  it('validates multiple W-2s independently', () => {
    const input: TaxReturnInput = {
      ...createEmptyTaxReturn(),
      w2s: [
        { wages: '50000', federal_withholding: '5000', social_security_wages: '50000', medicare_wages: '50000' },
        { wages: 'bad', federal_withholding: '0', social_security_wages: '0', medicare_wages: '0' },
      ],
    };
    const errors = validateTaxReturn(input);
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain('W-2 #2');
  });
});

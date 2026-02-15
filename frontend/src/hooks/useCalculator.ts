import { useState, useCallback } from 'react';

import type { TaxReturnInput, FullTaxCalculationResult } from '../types/index.ts';
import { createEmptyTaxReturn } from '../utils/defaults.ts';
import { validateTaxReturn } from '../utils/validation.ts';
import { taxApi, ApiError } from '../services/api.ts';

export interface UseCalculatorReturn {
  formData: TaxReturnInput;
  setFormData: React.Dispatch<React.SetStateAction<TaxReturnInput>>;
  result: FullTaxCalculationResult | null;
  error: string | null;
  isLoading: boolean;
  calculate: () => Promise<void>;
  reset: () => void;
}

/**
 * Normalize empty string fields to "0" before sending to the API.
 * The backend expects Decimal-compatible strings, not empty strings.
 */
function normalizeEmptyToZero(input: TaxReturnInput): TaxReturnInput {
  const normalize = (v: string) => (v === '' ? '0' : v);

  return {
    ...input,
    w2s: input.w2s.map((w2) => ({
      wages: normalize(w2.wages),
      federal_withholding: normalize(w2.federal_withholding),
      social_security_wages: normalize(w2.social_security_wages),
      medicare_wages: normalize(w2.medicare_wages),
    })),
    income_1099_nec: input.income_1099_nec.map((nec) => ({
      compensation: normalize(nec.compensation),
    })),
    income_1099_int: input.income_1099_int.map((int) => ({
      interest: normalize(int.interest),
    })),
    income_1099_div: input.income_1099_div.map((div) => ({
      ordinary_dividends: normalize(div.ordinary_dividends),
      qualified_dividends: normalize(div.qualified_dividends),
    })),
    income_1099_b: input.income_1099_b.map((b) => ({
      short_term_gains: normalize(b.short_term_gains),
      long_term_gains: normalize(b.long_term_gains),
    })),
    itemized_deductions: input.itemized_deductions
      ? {
          medical: normalize(input.itemized_deductions.medical),
          state_and_local_taxes: normalize(input.itemized_deductions.state_and_local_taxes),
          mortgage_interest: normalize(input.itemized_deductions.mortgage_interest),
          charitable: normalize(input.itemized_deductions.charitable),
          casualty: normalize(input.itemized_deductions.casualty),
          other: normalize(input.itemized_deductions.other),
        }
      : null,
    hsa_deduction: normalize(input.hsa_deduction),
    student_loan_interest: normalize(input.student_loan_interest),
    educator_expenses: normalize(input.educator_expenses),
    ira_deduction: normalize(input.ira_deduction),
    self_employed_health_insurance: normalize(input.self_employed_health_insurance),
    estimated_payments: normalize(input.estimated_payments),
  };
}

export function useCalculator(): UseCalculatorReturn {
  const [formData, setFormData] = useState<TaxReturnInput>(createEmptyTaxReturn);
  const [result, setResult] = useState<FullTaxCalculationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const calculate = useCallback(async () => {
    setError(null);

    const validationErrors = validateTaxReturn(formData);
    if (validationErrors.length > 0) {
      setError(validationErrors.join(' '));
      return;
    }

    setIsLoading(true);
    try {
      const normalized = normalizeEmptyToZero(formData);
      const calcResult = await taxApi.calculate(normalized);
      setResult(calcResult);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [formData]);

  const reset = useCallback(() => {
    setFormData(createEmptyTaxReturn());
    setResult(null);
    setError(null);
  }, []);

  return { formData, setFormData, result, error, isLoading, calculate, reset };
}

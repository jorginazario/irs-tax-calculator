import { useState, useEffect } from 'react';
import { useCalculator } from '../hooks/useCalculator.ts';
import type { TaxReturnInput } from '../types/index.ts';
import FilingStatusSelector from '../components/FilingStatusSelector.tsx';
import IncomeSection from '../components/IncomeSection.tsx';
import DeductionSection from '../components/DeductionSection.tsx';
import CreditsSection from '../components/CreditsSection.tsx';
import PaymentsSection from '../components/PaymentsSection.tsx';
import ResultsDisplay from '../components/ResultsDisplay.tsx';
import ErrorDisplay from '../components/ErrorDisplay.tsx';

export default function CalculatorPage() {
  const { formData, setFormData, result, error, isLoading, calculate, reset } =
    useCalculator();
  const [dismissedError, setDismissedError] = useState<string | null>(null);

  // Reset dismissed state when a new error appears
  useEffect(() => {
    if (error !== dismissedError) {
      setDismissedError(null);
    }
  }, [error, dismissedError]);

  const showError = error && error !== dismissedError;

  const handleChange = (updates: Partial<TaxReturnInput>) => {
    setFormData((prev) => ({ ...prev, ...updates }));
  };

  // Compute total W-2 withholding for PaymentsSection display
  const totalWithholding = formData.w2s
    .reduce((sum, w2) => {
      const val = parseFloat(w2.federal_withholding);
      return sum + (Number.isNaN(val) ? 0 : val);
    }, 0)
    .toFixed(2);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void calculate();
  };

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      {showError && (
        <div className="mb-6">
          <ErrorDisplay
            message={error}
            onDismiss={() => setDismissedError(error)}
          />
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <FilingStatusSelector
          value={formData.filing_status}
          isOver65={formData.is_over_65}
          isBlind={formData.is_blind}
          onChange={handleChange}
        />

        <IncomeSection formData={formData} onChange={handleChange} />

        <DeductionSection formData={formData} onChange={handleChange} />

        <CreditsSection
          credits={formData.credits}
          onChange={(credits) => handleChange({ credits })}
        />

        <PaymentsSection
          estimatedPayments={formData.estimated_payments}
          totalWithholding={totalWithholding}
          onChange={(value) => handleChange({ estimated_payments: value })}
        />

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={isLoading}
            className="rounded-lg bg-blue-600 px-8 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg
                  className="h-4 w-4 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Calculating...
              </span>
            ) : (
              'Calculate Tax'
            )}
          </button>
          <button
            type="button"
            onClick={reset}
            className="rounded-lg border border-gray-300 bg-white px-8 py-3 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none"
          >
            Reset
          </button>
        </div>
      </form>

      {/* Results */}
      {result && (
        <div className="mt-8">
          <h2 className="mb-6 text-xl font-bold text-gray-900">
            Tax Calculation Results
          </h2>
          <ResultsDisplay result={result} />
        </div>
      )}

      <footer className="mt-12 border-t border-gray-200 pt-6 pb-8 text-center text-xs text-gray-400">
        <p>
          This calculator provides estimates only. Consult a qualified tax
          professional for official tax advice. Based on IRS tax tables and
          rates for Tax Year 2024.
        </p>
      </footer>
    </main>
  );
}

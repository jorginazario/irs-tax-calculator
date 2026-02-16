import { useState } from 'react';
import { useHistory } from '../hooks/useHistory.ts';
import { formatCurrency, formatPercent } from '../utils/format.ts';
import type { FilingStatus } from '../types/index.ts';
import { formatFilingStatus } from '../utils/format.ts';
import ResultsDisplay from '../components/ResultsDisplay.tsx';

export default function HistoryPage() {
  const {
    calculations,
    selectedDetail,
    error,
    isLoading,
    isDetailLoading,
    refresh,
    viewDetail,
    closeDetail,
    deleteCalculation,
  } = useHistory();

  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const handleDelete = async (id: number) => {
    await deleteCalculation(id);
    setConfirmDeleteId(null);
  };

  if (isLoading) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-8">
        <div className="text-center text-gray-500">Loading history...</div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Calculation History</h2>
        <button
          onClick={() => void refresh()}
          className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {calculations.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
          <p className="text-gray-500">No saved calculations yet.</p>
          <p className="mt-2 text-sm text-gray-400">
            Go to the Calculator page and run a tax calculation to see it here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {calculations.map((calc) => {
            const isRefund = calc.refund_or_owed > 0;
            const isOwed = calc.refund_or_owed < 0;

            return (
              <div
                key={calc.id}
                className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold text-gray-900">
                        {formatFilingStatus(calc.filing_status as FilingStatus)}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(calc.created_at + 'Z').toLocaleString()}
                      </span>
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-x-8 gap-y-2 text-sm sm:grid-cols-4">
                      <div>
                        <span className="text-gray-500">Income</span>
                        <p className="font-medium text-gray-900">
                          {formatCurrency(calc.total_income)}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">AGI</span>
                        <p className="font-medium text-gray-900">
                          {formatCurrency(calc.agi)}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Total Tax</span>
                        <p className="font-medium text-gray-900">
                          {formatCurrency(calc.total_tax)}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">
                          {isRefund ? 'Refund' : 'Owed'}
                        </span>
                        <p
                          className={`font-medium ${
                            isRefund
                              ? 'text-green-700'
                              : isOwed
                                ? 'text-red-700'
                                : 'text-gray-900'
                          }`}
                        >
                          {isRefund
                            ? formatCurrency(calc.refund_or_owed)
                            : isOwed
                              ? `(${formatCurrency(Math.abs(calc.refund_or_owed))})`
                              : formatCurrency(0)}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2 flex gap-6 text-xs text-gray-400">
                      <span>Effective: {formatPercent(calc.effective_rate)}</span>
                      <span>Marginal: {formatPercent(calc.marginal_rate)}</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => void viewDetail(calc.id)}
                      className="rounded-md border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 hover:bg-blue-100"
                    >
                      View
                    </button>
                    {confirmDeleteId === calc.id ? (
                      <div className="flex gap-1">
                        <button
                          onClick={() => void handleDelete(calc.id)}
                          className="rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => setConfirmDeleteId(null)}
                          className="rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setConfirmDeleteId(calc.id)}
                        className="rounded-md border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Detail Modal */}
      {(selectedDetail || isDetailLoading) && (
        <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 pt-8 pb-8">
          <div className="relative mx-4 w-full max-w-4xl rounded-xl bg-gray-50 p-6 shadow-2xl">
            <button
              onClick={closeDetail}
              className="absolute top-4 right-4 rounded-full bg-gray-200 p-2 text-gray-600 hover:bg-gray-300"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            {isDetailLoading ? (
              <div className="py-12 text-center text-gray-500">Loading details...</div>
            ) : selectedDetail ? (
              <div>
                <h3 className="mb-4 text-lg font-bold text-gray-900">
                  Calculation Detail — #{selectedDetail.id}
                </h3>
                <p className="mb-6 text-sm text-gray-500">
                  {formatFilingStatus(selectedDetail.filing_status as FilingStatus)} | {new Date(selectedDetail.created_at + 'Z').toLocaleString()}
                </p>
                <ResultsDisplay result={selectedDetail.result_data} />
              </div>
            ) : null}
          </div>
        </div>
      )}
    </main>
  );
}

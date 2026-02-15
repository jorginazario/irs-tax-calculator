interface PaymentsSectionProps {
  estimatedPayments: string;
  totalWithholding: string;
  onChange: (value: string) => void;
}

export default function PaymentsSection({
  estimatedPayments,
  totalWithholding,
  onChange,
}: PaymentsSectionProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Payments</h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Total W-2 Federal Withholding
          </label>
          <div className="relative">
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              $
            </span>
            <input
              type="text"
              value={totalWithholding}
              readOnly
              className="w-full rounded-md border border-gray-200 bg-gray-100 py-2 pl-7 pr-3 text-sm text-gray-500"
            />
          </div>
          <p className="mt-1 text-xs text-gray-400">
            Auto-calculated from your W-2 entries above.
          </p>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            Estimated Tax Payments
          </label>
          <div className="relative">
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              $
            </span>
            <input
              type="text"
              inputMode="decimal"
              value={estimatedPayments}
              onChange={(e) => onChange(e.target.value)}
              placeholder="0.00"
              className="w-full rounded-md border border-gray-300 py-2 pl-7 pr-3 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <p className="mt-1 text-xs text-gray-400">
            Quarterly estimated payments made during the tax year.
          </p>
        </div>
      </div>
    </div>
  );
}

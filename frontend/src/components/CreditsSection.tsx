import type { TaxCredits } from '../types/index.ts';

interface CreditsSectionProps {
  credits: TaxCredits;
  onChange: (credits: TaxCredits) => void;
}

export default function CreditsSection({ credits, onChange }: CreditsSectionProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Credits</h2>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-600">
          Number of Qualifying Children (for Child Tax Credit)
        </label>
        <input
          type="number"
          min={0}
          step={1}
          value={credits.num_qualifying_children}
          onChange={(e) => {
            const val = parseInt(e.target.value, 10);
            onChange({
              num_qualifying_children: Number.isNaN(val) ? 0 : Math.max(0, val),
            });
          }}
          className="w-32 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
        />
        <p className="mt-1 text-xs text-gray-400">
          Children under 17 who qualify for the Child Tax Credit ($2,000 per child for 2024).
        </p>
      </div>
    </div>
  );
}

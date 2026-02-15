import type { FilingStatus } from '../types/index.ts';

const FILING_STATUSES: { value: FilingStatus; label: string }[] = [
  { value: 'SINGLE', label: 'Single' },
  { value: 'MARRIED_FILING_JOINTLY', label: 'Married Filing Jointly' },
  { value: 'MARRIED_FILING_SEPARATELY', label: 'Married Filing Separately' },
  { value: 'HEAD_OF_HOUSEHOLD', label: 'Head of Household' },
  { value: 'QUALIFYING_SURVIVING_SPOUSE', label: 'Qualifying Surviving Spouse' },
];

interface FilingStatusSelectorProps {
  value: FilingStatus;
  isOver65: boolean;
  isBlind: boolean;
  onChange: (updates: {
    filing_status?: FilingStatus;
    is_over_65?: boolean;
    is_blind?: boolean;
  }) => void;
}

export default function FilingStatusSelector({
  value,
  isOver65,
  isBlind,
  onChange,
}: FilingStatusSelectorProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Filing Status</h2>

      <div className="space-y-2">
        {FILING_STATUSES.map((status) => (
          <label
            key={status.value}
            className="flex cursor-pointer items-center gap-3 rounded-md p-2 hover:bg-gray-50"
          >
            <input
              type="radio"
              name="filing_status"
              value={status.value}
              checked={value === status.value}
              onChange={() => onChange({ filing_status: status.value })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">{status.label}</span>
          </label>
        ))}
      </div>

      <div className="mt-4 border-t border-gray-100 pt-4">
        <p className="mb-2 text-sm font-medium text-gray-600">
          Additional deduction qualifiers
        </p>
        <div className="flex gap-6">
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="checkbox"
              checked={isOver65}
              onChange={(e) => onChange({ is_over_65: e.target.checked })}
              className="h-4 w-4 rounded text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Age 65 or older</span>
          </label>
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="checkbox"
              checked={isBlind}
              onChange={(e) => onChange({ is_blind: e.target.checked })}
              className="h-4 w-4 rounded text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Legally blind</span>
          </label>
        </div>
      </div>
    </div>
  );
}

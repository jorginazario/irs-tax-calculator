import type { TaxReturnInput, ItemizedDeductions } from '../types/index.ts';
import { createEmptyItemizedDeductions } from '../utils/defaults.ts';

interface DeductionSectionProps {
  formData: TaxReturnInput;
  onChange: (updates: Partial<TaxReturnInput>) => void;
}

function MoneyInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-gray-600">
        {label}
      </label>
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          $
        </span>
        <input
          type="text"
          inputMode="decimal"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="0.00"
          className="w-full rounded-md border border-gray-300 py-2 pl-7 pr-3 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
        />
      </div>
    </div>
  );
}

export default function DeductionSection({ formData, onChange }: DeductionSectionProps) {
  const useItemized = formData.itemized_deductions !== null;

  const toggleDeductionType = () => {
    if (useItemized) {
      onChange({ itemized_deductions: null, force_standard_deduction: false });
    } else {
      onChange({
        itemized_deductions: createEmptyItemizedDeductions(),
        force_standard_deduction: false,
      });
    }
  };

  const updateItemized = (field: keyof ItemizedDeductions, value: string) => {
    if (!formData.itemized_deductions) return;
    onChange({
      itemized_deductions: { ...formData.itemized_deductions, [field]: value },
    });
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Deductions</h2>

      {/* Standard vs Itemized toggle */}
      <div className="mb-6">
        <p className="mb-2 text-sm font-medium text-gray-600">Deduction Type</p>
        <div className="flex gap-4">
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="radio"
              name="deduction_type"
              checked={!useItemized}
              onChange={() => {
                if (useItemized) toggleDeductionType();
              }}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Standard Deduction</span>
          </label>
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="radio"
              name="deduction_type"
              checked={useItemized}
              onChange={() => {
                if (!useItemized) toggleDeductionType();
              }}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Itemized Deductions</span>
          </label>
        </div>
        {!useItemized && (
          <p className="mt-2 text-xs text-gray-400">
            The standard deduction amount will be calculated based on your filing status.
          </p>
        )}
      </div>

      {/* Itemized deduction fields */}
      {useItemized && formData.itemized_deductions && (
        <div className="mb-6 rounded-md border border-gray-100 bg-gray-50 p-4">
          <h3 className="mb-3 text-sm font-medium text-gray-700">Itemized Deductions</h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <MoneyInput
              label="Medical Expenses"
              value={formData.itemized_deductions.medical}
              onChange={(v) => updateItemized('medical', v)}
            />
            <MoneyInput
              label="State & Local Taxes (SALT)"
              value={formData.itemized_deductions.state_and_local_taxes}
              onChange={(v) => updateItemized('state_and_local_taxes', v)}
            />
            <MoneyInput
              label="Mortgage Interest"
              value={formData.itemized_deductions.mortgage_interest}
              onChange={(v) => updateItemized('mortgage_interest', v)}
            />
            <MoneyInput
              label="Charitable Contributions"
              value={formData.itemized_deductions.charitable}
              onChange={(v) => updateItemized('charitable', v)}
            />
            <MoneyInput
              label="Casualty & Theft Losses"
              value={formData.itemized_deductions.casualty}
              onChange={(v) => updateItemized('casualty', v)}
            />
            <MoneyInput
              label="Other Deductions"
              value={formData.itemized_deductions.other}
              onChange={(v) => updateItemized('other', v)}
            />
          </div>
        </div>
      )}

      {/* Above-the-line deductions */}
      <div>
        <h3 className="mb-3 text-sm font-medium text-gray-700">
          Above-the-Line Deductions (Adjustments to Income)
        </h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <MoneyInput
            label="HSA Deduction"
            value={formData.hsa_deduction}
            onChange={(v) => onChange({ hsa_deduction: v })}
          />
          <MoneyInput
            label="Student Loan Interest"
            value={formData.student_loan_interest}
            onChange={(v) => onChange({ student_loan_interest: v })}
          />
          <MoneyInput
            label="Educator Expenses"
            value={formData.educator_expenses}
            onChange={(v) => onChange({ educator_expenses: v })}
          />
          <MoneyInput
            label="IRA Deduction"
            value={formData.ira_deduction}
            onChange={(v) => onChange({ ira_deduction: v })}
          />
          <MoneyInput
            label="Self-Employed Health Insurance"
            value={formData.self_employed_health_insurance}
            onChange={(v) => onChange({ self_employed_health_insurance: v })}
          />
        </div>
      </div>
    </div>
  );
}

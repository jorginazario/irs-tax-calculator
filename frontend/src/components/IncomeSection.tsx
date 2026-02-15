import type { TaxReturnInput, W2Income, Income1099NEC, Income1099INT, Income1099DIV, Income1099B } from '../types/index.ts';
import {
  createEmptyW2,
  createEmpty1099NEC,
  createEmpty1099INT,
  createEmpty1099DIV,
  createEmpty1099B,
} from '../utils/defaults.ts';
import { useState } from 'react';

interface IncomeSectionProps {
  formData: TaxReturnInput;
  onChange: (updates: Partial<TaxReturnInput>) => void;
}

function MoneyInput({
  label,
  value,
  onChange,
  allowNegative = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  allowNegative?: boolean;
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
          placeholder={allowNegative ? '0.00' : '0.00'}
          className="w-full rounded-md border border-gray-300 py-2 pl-7 pr-3 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
        />
      </div>
    </div>
  );
}

function CollapsibleSection({
  title,
  count,
  children,
  defaultOpen = false,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="border-b border-gray-100 pb-4">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between py-2 text-left"
      >
        <span className="text-sm font-medium text-gray-700">
          {title}
          {count > 0 && (
            <span className="ml-2 inline-flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700">
              {count}
            </span>
          )}
        </span>
        <svg
          className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && <div className="mt-2">{children}</div>}
    </div>
  );
}

export default function IncomeSection({ formData, onChange }: IncomeSectionProps) {
  // W-2 handlers
  const addW2 = () => onChange({ w2s: [...formData.w2s, createEmptyW2()] });
  const removeW2 = (index: number) =>
    onChange({ w2s: formData.w2s.filter((_, i) => i !== index) });
  const updateW2 = (index: number, field: keyof W2Income, value: string) => {
    const updated = formData.w2s.map((w2, i) =>
      i === index ? { ...w2, [field]: value } : w2,
    );
    onChange({ w2s: updated });
  };

  // 1099-NEC handlers
  const addNEC = () =>
    onChange({ income_1099_nec: [...formData.income_1099_nec, createEmpty1099NEC()] });
  const removeNEC = (index: number) =>
    onChange({
      income_1099_nec: formData.income_1099_nec.filter((_, i) => i !== index),
    });
  const updateNEC = (index: number, field: keyof Income1099NEC, value: string) => {
    const updated = formData.income_1099_nec.map((nec, i) =>
      i === index ? { ...nec, [field]: value } : nec,
    );
    onChange({ income_1099_nec: updated });
  };

  // 1099-INT handlers
  const addINT = () =>
    onChange({ income_1099_int: [...formData.income_1099_int, createEmpty1099INT()] });
  const removeINT = (index: number) =>
    onChange({
      income_1099_int: formData.income_1099_int.filter((_, i) => i !== index),
    });
  const updateINT = (index: number, field: keyof Income1099INT, value: string) => {
    const updated = formData.income_1099_int.map((int, i) =>
      i === index ? { ...int, [field]: value } : int,
    );
    onChange({ income_1099_int: updated });
  };

  // 1099-DIV handlers
  const addDIV = () =>
    onChange({ income_1099_div: [...formData.income_1099_div, createEmpty1099DIV()] });
  const removeDIV = (index: number) =>
    onChange({
      income_1099_div: formData.income_1099_div.filter((_, i) => i !== index),
    });
  const updateDIV = (index: number, field: keyof Income1099DIV, value: string) => {
    const updated = formData.income_1099_div.map((div, i) =>
      i === index ? { ...div, [field]: value } : div,
    );
    onChange({ income_1099_div: updated });
  };

  // 1099-B handlers
  const addB = () =>
    onChange({ income_1099_b: [...formData.income_1099_b, createEmpty1099B()] });
  const removeB = (index: number) =>
    onChange({
      income_1099_b: formData.income_1099_b.filter((_, i) => i !== index),
    });
  const updateB = (index: number, field: keyof Income1099B, value: string) => {
    const updated = formData.income_1099_b.map((b, i) =>
      i === index ? { ...b, [field]: value } : b,
    );
    onChange({ income_1099_b: updated });
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">Income</h2>

      {/* W-2 Income */}
      <CollapsibleSection title="W-2 Wages & Salary" count={formData.w2s.length} defaultOpen>
        {formData.w2s.map((w2, index) => (
          <div key={index} className="mb-4 rounded-md border border-gray-100 bg-gray-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">W-2 #{index + 1}</span>
              <button
                type="button"
                onClick={() => removeW2(index)}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <MoneyInput
                label="Gross Wages"
                value={w2.wages}
                onChange={(v) => updateW2(index, 'wages', v)}
              />
              <MoneyInput
                label="Federal Withholding"
                value={w2.federal_withholding}
                onChange={(v) => updateW2(index, 'federal_withholding', v)}
              />
              <MoneyInput
                label="Social Security Wages"
                value={w2.social_security_wages}
                onChange={(v) => updateW2(index, 'social_security_wages', v)}
              />
              <MoneyInput
                label="Medicare Wages"
                value={w2.medicare_wages}
                onChange={(v) => updateW2(index, 'medicare_wages', v)}
              />
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={addW2}
          className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          + Add W-2
        </button>
      </CollapsibleSection>

      {/* 1099-NEC */}
      <CollapsibleSection title="1099-NEC Freelance/Contract" count={formData.income_1099_nec.length}>
        {formData.income_1099_nec.map((nec, index) => (
          <div key={index} className="mb-4 rounded-md border border-gray-100 bg-gray-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">1099-NEC #{index + 1}</span>
              <button
                type="button"
                onClick={() => removeNEC(index)}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
            <MoneyInput
              label="Non-Employee Compensation"
              value={nec.compensation}
              onChange={(v) => updateNEC(index, 'compensation', v)}
            />
          </div>
        ))}
        <button
          type="button"
          onClick={addNEC}
          className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          + Add 1099-NEC
        </button>
      </CollapsibleSection>

      {/* 1099-INT */}
      <CollapsibleSection title="1099-INT Interest Income" count={formData.income_1099_int.length}>
        {formData.income_1099_int.map((int, index) => (
          <div key={index} className="mb-4 rounded-md border border-gray-100 bg-gray-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">1099-INT #{index + 1}</span>
              <button
                type="button"
                onClick={() => removeINT(index)}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
            <MoneyInput
              label="Interest Income"
              value={int.interest}
              onChange={(v) => updateINT(index, 'interest', v)}
            />
          </div>
        ))}
        <button
          type="button"
          onClick={addINT}
          className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          + Add 1099-INT
        </button>
      </CollapsibleSection>

      {/* 1099-DIV */}
      <CollapsibleSection title="1099-DIV Dividends" count={formData.income_1099_div.length}>
        {formData.income_1099_div.map((div, index) => (
          <div key={index} className="mb-4 rounded-md border border-gray-100 bg-gray-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">1099-DIV #{index + 1}</span>
              <button
                type="button"
                onClick={() => removeDIV(index)}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <MoneyInput
                label="Ordinary Dividends"
                value={div.ordinary_dividends}
                onChange={(v) => updateDIV(index, 'ordinary_dividends', v)}
              />
              <MoneyInput
                label="Qualified Dividends"
                value={div.qualified_dividends}
                onChange={(v) => updateDIV(index, 'qualified_dividends', v)}
              />
            </div>
            <p className="mt-1 text-xs text-gray-400">
              Qualified dividends cannot exceed ordinary dividends.
            </p>
          </div>
        ))}
        <button
          type="button"
          onClick={addDIV}
          className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          + Add 1099-DIV
        </button>
      </CollapsibleSection>

      {/* 1099-B */}
      <CollapsibleSection title="1099-B Capital Gains/Losses" count={formData.income_1099_b.length}>
        {formData.income_1099_b.map((b, index) => (
          <div key={index} className="mb-4 rounded-md border border-gray-100 bg-gray-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">1099-B #{index + 1}</span>
              <button
                type="button"
                onClick={() => removeB(index)}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <MoneyInput
                label="Short-Term Gains/Losses"
                value={b.short_term_gains}
                onChange={(v) => updateB(index, 'short_term_gains', v)}
                allowNegative
              />
              <MoneyInput
                label="Long-Term Gains/Losses"
                value={b.long_term_gains}
                onChange={(v) => updateB(index, 'long_term_gains', v)}
                allowNegative
              />
            </div>
            <p className="mt-1 text-xs text-gray-400">
              Use negative values for losses.
            </p>
          </div>
        ))}
        <button
          type="button"
          onClick={addB}
          className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          + Add 1099-B
        </button>
      </CollapsibleSection>
    </div>
  );
}

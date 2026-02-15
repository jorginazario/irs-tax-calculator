import type { FullTaxCalculationResult } from '../types/index.ts';
import { formatCurrency, formatPercent, formatFilingStatus } from '../utils/format.ts';

interface ResultsDisplayProps {
  result: FullTaxCalculationResult;
}

function SummaryRow({
  label,
  value,
  bold = false,
  color,
}: {
  label: string;
  value: string;
  bold?: boolean;
  color?: string;
}) {
  return (
    <div className={`flex justify-between py-1 ${bold ? 'font-semibold' : ''}`}>
      <span className="text-gray-600">{label}</span>
      <span className={color ?? 'text-gray-900'}>{value}</span>
    </div>
  );
}

function SectionCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-base font-semibold text-gray-900">{title}</h3>
      <div className="space-y-1 text-sm">{children}</div>
    </div>
  );
}

export default function ResultsDisplay({ result }: ResultsDisplayProps) {
  const { summary, income, fica, deductions, tax_computation, credits } = result;

  const refundOrOwed = parseFloat(summary.refund_or_owed);
  const isRefund = refundOrOwed > 0;
  const isOwed = refundOrOwed < 0;

  return (
    <div className="space-y-6">
      {/* Top Summary Card */}
      <div
        className={`rounded-lg border-2 p-6 shadow-sm ${
          isRefund
            ? 'border-green-300 bg-green-50'
            : isOwed
              ? 'border-red-300 bg-red-50'
              : 'border-gray-200 bg-white'
        }`}
      >
        <div className="mb-4 text-center">
          <p className="text-sm font-medium text-gray-500">Tax Year 2024</p>
          <p className="text-sm text-gray-500">
            {formatFilingStatus(summary.filing_status)}
          </p>
        </div>
        <div className="grid grid-cols-1 gap-4 text-center sm:grid-cols-3">
          <div>
            <p className="text-sm text-gray-500">Total Income</p>
            <p className="text-lg font-semibold text-gray-900">
              {formatCurrency(summary.total_income)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Adjusted Gross Income</p>
            <p className="text-lg font-semibold text-gray-900">
              {formatCurrency(summary.agi)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">
              {isRefund ? 'Refund' : isOwed ? 'Amount Owed' : 'Balance'}
            </p>
            <p
              className={`text-2xl font-bold ${
                isRefund
                  ? 'text-green-700'
                  : isOwed
                    ? 'text-red-700'
                    : 'text-gray-900'
              }`}
            >
              {isRefund
                ? formatCurrency(refundOrOwed)
                : isOwed
                  ? `(${formatCurrency(Math.abs(refundOrOwed))})`
                  : formatCurrency(0)}
            </p>
          </div>
        </div>
      </div>

      {/* Income Breakdown */}
      <SectionCard title="Income Breakdown">
        <SummaryRow label="Wages (W-2)" value={formatCurrency(income.wages)} />
        <SummaryRow
          label="Self-Employment Income (1099-NEC)"
          value={formatCurrency(income.self_employment_income)}
        />
        <SummaryRow
          label="Interest Income (1099-INT)"
          value={formatCurrency(income.interest_income)}
        />
        <SummaryRow
          label="Ordinary Dividends (1099-DIV)"
          value={formatCurrency(income.ordinary_dividends)}
        />
        <SummaryRow
          label="Qualified Dividends"
          value={formatCurrency(income.qualified_dividends)}
        />
        <SummaryRow
          label="Short-Term Capital Gains"
          value={formatCurrency(income.short_term_gains)}
        />
        <SummaryRow
          label="Long-Term Capital Gains"
          value={formatCurrency(income.long_term_gains)}
        />
        <div className="mt-2 border-t border-gray-200 pt-2">
          <SummaryRow
            label="Total Gross Income"
            value={formatCurrency(income.total_gross_income)}
            bold
          />
        </div>
      </SectionCard>

      {/* Deductions */}
      <SectionCard title="Deductions">
        <SummaryRow
          label={deductions.used_standard ? 'Standard Deduction' : 'Itemized Deductions'}
          value={formatCurrency(deductions.deduction_amount)}
        />
        {!deductions.used_standard && (
          <SummaryRow
            label="(Standard deduction would have been)"
            value={formatCurrency(deductions.standard_deduction_amount)}
          />
        )}
        {deductions.used_standard && parseFloat(deductions.itemized_total) > 0 && (
          <SummaryRow
            label="(Itemized total would have been)"
            value={formatCurrency(deductions.itemized_total)}
          />
        )}
        <div className="mt-2 border-t border-gray-200 pt-2">
          <SummaryRow
            label="Taxable Income"
            value={formatCurrency(deductions.taxable_income)}
            bold
          />
        </div>
      </SectionCard>

      {/* Tax Computation */}
      <SectionCard title="Tax Computation">
        <SummaryRow
          label="Tax on Ordinary Income"
          value={formatCurrency(tax_computation.ordinary_tax)}
        />
        <SummaryRow
          label="Tax on Qualified Dividends"
          value={formatCurrency(tax_computation.qualified_dividend_tax)}
        />
        <SummaryRow
          label="Tax on Capital Gains"
          value={formatCurrency(tax_computation.capital_gains_tax)}
        />
        <SummaryRow
          label="Net Investment Income Tax (NIIT)"
          value={formatCurrency(tax_computation.niit)}
        />
        <div className="mt-2 border-t border-gray-200 pt-2">
          <SummaryRow
            label="Total Income Tax (before credits)"
            value={formatCurrency(tax_computation.total_income_tax)}
            bold
          />
        </div>
      </SectionCard>

      {/* Credits */}
      <SectionCard title="Credits">
        <SummaryRow
          label="Child Tax Credit"
          value={formatCurrency(credits.child_tax_credit)}
        />
        <SummaryRow
          label="Nonrefundable CTC Applied"
          value={formatCurrency(credits.nonrefundable_ctc_applied)}
        />
        <SummaryRow
          label="Refundable CTC Applied"
          value={formatCurrency(credits.refundable_ctc_applied)}
        />
        <div className="mt-2 border-t border-gray-200 pt-2">
          <SummaryRow
            label="Total Credits Applied"
            value={formatCurrency(credits.total_credits_applied)}
            bold
          />
          <SummaryRow
            label="Income Tax After Credits"
            value={formatCurrency(credits.tax_after_credits)}
            bold
          />
        </div>
      </SectionCard>

      {/* FICA */}
      <SectionCard title="FICA / Self-Employment Tax">
        <SummaryRow
          label="Social Security Tax"
          value={formatCurrency(fica.ss_tax)}
        />
        <SummaryRow
          label="Medicare Tax"
          value={formatCurrency(fica.medicare_tax)}
        />
        <SummaryRow
          label="Additional Medicare Tax"
          value={formatCurrency(fica.additional_medicare_tax)}
        />
        <SummaryRow
          label="Self-Employment Tax"
          value={formatCurrency(fica.se_tax)}
        />
        <div className="mt-2 border-t border-gray-200 pt-2">
          <SummaryRow
            label="Total FICA"
            value={formatCurrency(fica.total_fica)}
            bold
          />
        </div>
      </SectionCard>

      {/* Bottom Line */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-base font-semibold text-gray-900">
          Bottom Line
        </h3>
        <div className="space-y-1 text-sm">
          <SummaryRow
            label="Total Tax (Income + FICA)"
            value={formatCurrency(summary.total_tax)}
            bold
          />
          <div className="mt-2 border-t border-gray-200 pt-2">
            <SummaryRow
              label="Federal Withholding"
              value={formatCurrency(summary.total_withholding)}
            />
            <SummaryRow
              label="Estimated Payments"
              value={formatCurrency(summary.estimated_payments)}
            />
            <SummaryRow
              label="Total Payments"
              value={formatCurrency(summary.total_payments)}
              bold
            />
          </div>
          <div className="mt-2 border-t border-gray-200 pt-2">
            <SummaryRow
              label={isRefund ? 'Refund' : 'Amount Owed'}
              value={
                isRefund
                  ? formatCurrency(refundOrOwed)
                  : `(${formatCurrency(Math.abs(refundOrOwed))})`
              }
              bold
              color={isRefund ? 'text-green-700' : isOwed ? 'text-red-700' : undefined}
            />
          </div>
          <div className="mt-4 flex gap-8 border-t border-gray-100 pt-3">
            <div>
              <span className="text-xs text-gray-400">Effective Rate</span>
              <p className="font-semibold text-gray-900">
                {formatPercent(summary.effective_rate)}
              </p>
            </div>
            <div>
              <span className="text-xs text-gray-400">Marginal Rate</span>
              <p className="font-semibold text-gray-900">
                {formatPercent(summary.marginal_rate)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

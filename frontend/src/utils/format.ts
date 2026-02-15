import type { FilingStatus } from '../types/index.ts';

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
});

const percentFormatter = new Intl.NumberFormat('en-US', {
  style: 'percent',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/**
 * Format a monetary value as USD currency.
 * Accepts a string (Decimal from backend) or number.
 */
export function formatCurrency(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (Number.isNaN(num)) return '$0.00';
  return currencyFormatter.format(num);
}

/**
 * Format a decimal rate as a percentage (e.g., 0.22 -> "22.00%").
 * Accepts a string (Decimal from backend) or number.
 */
export function formatPercent(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (Number.isNaN(num)) return '0.00%';
  return percentFormatter.format(num);
}

const FILING_STATUS_LABELS: Record<FilingStatus, string> = {
  SINGLE: 'Single',
  MARRIED_FILING_JOINTLY: 'Married Filing Jointly',
  MARRIED_FILING_SEPARATELY: 'Married Filing Separately',
  HEAD_OF_HOUSEHOLD: 'Head of Household',
  QUALIFYING_SURVIVING_SPOUSE: 'Qualifying Surviving Spouse',
};

/**
 * Convert a filing status enum value to a human-readable label.
 */
export function formatFilingStatus(status: FilingStatus): string {
  return FILING_STATUS_LABELS[status];
}

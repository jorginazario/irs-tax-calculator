import { describe, it, expect } from 'vitest';

import { formatCurrency, formatPercent, formatFilingStatus } from '../format.ts';

describe('formatCurrency', () => {
  it('formats a positive number', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });

  it('formats a string decimal', () => {
    expect(formatCurrency('50000')).toBe('$50,000.00');
  });

  it('formats zero', () => {
    expect(formatCurrency('0')).toBe('$0.00');
  });

  it('formats a negative number', () => {
    expect(formatCurrency(-500)).toBe('-$500.00');
  });

  it('handles NaN gracefully', () => {
    expect(formatCurrency('abc')).toBe('$0.00');
  });

  it('formats large numbers with commas', () => {
    expect(formatCurrency('1000000.50')).toBe('$1,000,000.50');
  });
});

describe('formatPercent', () => {
  it('formats 0.22 as 22.00%', () => {
    expect(formatPercent(0.22)).toBe('22.00%');
  });

  it('formats string decimal rate', () => {
    expect(formatPercent('0.1234')).toBe('12.34%');
  });

  it('formats zero', () => {
    expect(formatPercent(0)).toBe('0.00%');
  });

  it('handles NaN gracefully', () => {
    expect(formatPercent('abc')).toBe('0.00%');
  });

  it('formats 1.0 as 100.00%', () => {
    expect(formatPercent(1)).toBe('100.00%');
  });
});

describe('formatFilingStatus', () => {
  it('formats SINGLE', () => {
    expect(formatFilingStatus('SINGLE')).toBe('Single');
  });

  it('formats MARRIED_FILING_JOINTLY', () => {
    expect(formatFilingStatus('MARRIED_FILING_JOINTLY')).toBe('Married Filing Jointly');
  });

  it('formats MARRIED_FILING_SEPARATELY', () => {
    expect(formatFilingStatus('MARRIED_FILING_SEPARATELY')).toBe('Married Filing Separately');
  });

  it('formats HEAD_OF_HOUSEHOLD', () => {
    expect(formatFilingStatus('HEAD_OF_HOUSEHOLD')).toBe('Head of Household');
  });

  it('formats QUALIFYING_SURVIVING_SPOUSE', () => {
    expect(formatFilingStatus('QUALIFYING_SURVIVING_SPOUSE')).toBe('Qualifying Surviving Spouse');
  });
});

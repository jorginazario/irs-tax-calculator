import type {
  TaxReturnInput,
  FullTaxCalculationResult,
  EstimateInput,
  EstimateResult,
  BracketsResponse,
  DeductionsResponse,
} from '../types/index.ts';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    let detail: string;
    try {
      const body = await response.json() as { detail?: string };
      detail = body.detail ?? response.statusText;
    } catch {
      detail = response.statusText;
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<T>;
}

export const taxApi = {
  /** Full tax calculation — POST /api/calculate */
  calculate(input: TaxReturnInput): Promise<FullTaxCalculationResult> {
    return request<FullTaxCalculationResult>('/calculate', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  },

  /** Quick estimate — POST /api/calculate/estimate */
  estimate(input: EstimateInput): Promise<EstimateResult> {
    return request<EstimateResult>('/calculate/estimate', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  },

  /** Get 2024 tax brackets — GET /api/brackets/2024 */
  getBrackets(): Promise<BracketsResponse> {
    return request<BracketsResponse>('/brackets/2024');
  },

  /** Get 2024 standard deductions — GET /api/deductions/2024 */
  getDeductions(): Promise<DeductionsResponse> {
    return request<DeductionsResponse>('/deductions/2024');
  },
};

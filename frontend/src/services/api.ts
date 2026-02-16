import type {
  TaxReturnInput,
  FullTaxCalculationResult,
  EstimateInput,
  EstimateResult,
  BracketsResponse,
  DeductionsResponse,
  CalculationSummary,
  CalculationDetail,
  DeleteResponse,
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

  // --- History endpoints ---

  /** List all saved calculations — GET /api/history */
  getHistory(): Promise<CalculationSummary[]> {
    return request<CalculationSummary[]>('/history');
  },

  /** Get a single saved calculation with full detail — GET /api/history/:id */
  getHistoryDetail(id: number): Promise<CalculationDetail> {
    return request<CalculationDetail>(`/history/${id}`);
  },

  /** Delete a saved calculation — DELETE /api/history/:id */
  deleteCalculation(id: number): Promise<DeleteResponse> {
    return request<DeleteResponse>(`/history/${id}`, { method: 'DELETE' });
  },

  // --- Analysis endpoints ---

  /** Query tax data with natural language — POST /api/analysis/query */
  analysisQuery(question: string): Promise<{ result: string }> {
    return request<{ result: string }>('/analysis/query', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  },

  /** Generate a Plotly chart — POST /api/analysis/chart */
  analysisChart(prompt: string): Promise<{ result: string }> {
    return request<{ result: string }>('/analysis/chart', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  },

  /** Generate a markdown table — POST /api/analysis/table */
  analysisTable(prompt: string): Promise<{ result: string }> {
    return request<{ result: string }>('/analysis/table', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  },

  /** Generate an analytical report — POST /api/analysis/report */
  analysisReport(prompt: string): Promise<{ result: string }> {
    return request<{ result: string }>('/analysis/report', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  },
};

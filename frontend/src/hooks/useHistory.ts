import { useState, useEffect, useCallback } from 'react';
import type { CalculationSummary, CalculationDetail } from '../types/index.ts';
import { taxApi, ApiError } from '../services/api.ts';

export function useHistory() {
  const [calculations, setCalculations] = useState<CalculationSummary[]>([]);
  const [selectedDetail, setSelectedDetail] = useState<CalculationDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDetailLoading, setIsDetailLoading] = useState(false);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await taxApi.getHistory();
      setCalculations(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Failed to load history');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const viewDetail = useCallback(async (id: number) => {
    setIsDetailLoading(true);
    setError(null);
    try {
      const detail = await taxApi.getHistoryDetail(id);
      setSelectedDetail(detail);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Failed to load calculation detail');
    } finally {
      setIsDetailLoading(false);
    }
  }, []);

  const closeDetail = useCallback(() => {
    setSelectedDetail(null);
  }, []);

  const deleteCalculation = useCallback(async (id: number) => {
    setError(null);
    try {
      await taxApi.deleteCalculation(id);
      setCalculations((prev) => prev.filter((c) => c.id !== id));
      if (selectedDetail?.id === id) {
        setSelectedDetail(null);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Failed to delete calculation');
    }
  }, [selectedDetail]);

  return {
    calculations,
    selectedDetail,
    error,
    isLoading,
    isDetailLoading,
    refresh,
    viewDetail,
    closeDetail,
    deleteCalculation,
  };
}

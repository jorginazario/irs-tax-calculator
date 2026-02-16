import { useState, useCallback } from 'react';
import type { AnalysisTool } from '../types/index.ts';
import { taxApi, ApiError } from '../services/api.ts';

export function useAnalysis() {
  const [selectedTool, setSelectedTool] = useState<AnalysisTool>('query');
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const execute = useCallback(async () => {
    if (!prompt.trim()) return;
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      let response: { result: string };
      switch (selectedTool) {
        case 'query':
          response = await taxApi.analysisQuery(prompt);
          break;
        case 'chart':
          response = await taxApi.analysisChart(prompt);
          break;
        case 'table':
          response = await taxApi.analysisTable(prompt);
          break;
        case 'report':
          response = await taxApi.analysisReport(prompt);
          break;
      }
      if (response.result.startsWith('Error:')) {
        setError(response.result);
      } else {
        setResult(response.result);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Analysis request failed');
    } finally {
      setIsLoading(false);
    }
  }, [selectedTool, prompt]);

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
    setPrompt('');
  }, []);

  return {
    selectedTool,
    setSelectedTool,
    prompt,
    setPrompt,
    result,
    error,
    isLoading,
    execute,
    clear,
  };
}

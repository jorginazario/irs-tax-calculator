import { useAnalysis } from '../hooks/useAnalysis.ts';
import type { AnalysisTool } from '../types/index.ts';

const TOOLS: { key: AnalysisTool; label: string; placeholder: string }[] = [
  {
    key: 'query',
    label: 'Query',
    placeholder: 'e.g., How many calculations are there? What is the average effective rate?',
  },
  {
    key: 'chart',
    label: 'Chart',
    placeholder: 'e.g., Bar chart of total tax by filing status',
  },
  {
    key: 'table',
    label: 'Table',
    placeholder: 'e.g., Table of all calculations showing income, tax, and effective rate',
  },
  {
    key: 'report',
    label: 'Report',
    placeholder: 'e.g., Comprehensive analysis of all saved tax calculations',
  },
];

function simpleMarkdownToHtml(md: string): string {
  return md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Headers
    .replace(/^### (.+)$/gm, '<h4 class="text-base font-semibold mt-4 mb-2">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="text-lg font-semibold mt-6 mb-3">$1</h3>')
    .replace(/^# (.+)$/gm, '<h2 class="text-xl font-bold mt-6 mb-3">$1</h2>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Table rows
    .replace(/^\| (.+) \|$/gm, (_, content: string) => {
      const cells = content.split(' | ').map((c: string) => c.trim());
      // Separator row
      if (cells.every((c: string) => /^[-:]+$/.test(c))) return '';
      const tag = 'td';
      const row = cells.map((c: string) => `<${tag} class="border border-gray-300 px-3 py-1">${c}</${tag}>`).join('');
      return `<tr>${row}</tr>`;
    })
    // Wrap consecutive <tr> in <table>
    .replace(/((?:<tr>.+<\/tr>\n?)+)/g, '<table class="w-full border-collapse border border-gray-300 text-sm my-4">$1</table>')
    // Line breaks
    .replace(/\n/g, '<br/>');
}

export default function AnalyticsPage() {
  const {
    selectedTool,
    setSelectedTool,
    prompt,
    setPrompt,
    result,
    error,
    isLoading,
    execute,
    clear,
  } = useAnalysis();

  const currentTool = TOOLS.find((t) => t.key === selectedTool)!;

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <h2 className="mb-6 text-xl font-bold text-gray-900">Analytics</h2>

      <p className="mb-6 text-sm text-gray-500">
        Use AI-powered tools to analyze your saved tax calculations. Requires the
        backend to have <code className="rounded bg-gray-100 px-1">ANTHROPIC_API_KEY</code> set.
      </p>

      {/* Tool Selector */}
      <div className="mb-6 flex gap-2">
        {TOOLS.map((tool) => (
          <button
            key={tool.key}
            onClick={() => setSelectedTool(tool.key)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              selectedTool === tool.key
                ? 'bg-blue-600 text-white shadow-sm'
                : 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            {tool.label}
          </button>
        ))}
      </div>

      {/* Prompt Input */}
      <div className="mb-6">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={currentTool.placeholder}
          rows={3}
          className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
      </div>

      {/* Action Buttons */}
      <div className="mb-8 flex gap-3">
        <button
          onClick={() => void execute()}
          disabled={isLoading || !prompt.trim()}
          className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg
                className="h-4 w-4 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Analyzing...
            </span>
          ) : (
            'Run Analysis'
          )}
        </button>
        {(result || error) && (
          <button
            onClick={clear}
            className="rounded-lg border border-gray-300 bg-white px-6 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
          >
            Clear
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 whitespace-pre-wrap">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
          {selectedTool === 'query' ? (
            <pre className="overflow-x-auto rounded-lg bg-gray-900 p-6 text-sm text-green-300 whitespace-pre-wrap">
              {result}
            </pre>
          ) : selectedTool === 'chart' ? (
            <iframe
              srcDoc={result}
              sandbox="allow-scripts"
              className="h-[500px] w-full rounded-lg border-0"
              title="Tax Data Chart"
            />
          ) : (
            <div
              className="prose prose-sm max-w-none p-6"
              dangerouslySetInnerHTML={{ __html: simpleMarkdownToHtml(result) }}
            />
          )}
        </div>
      )}
    </main>
  );
}

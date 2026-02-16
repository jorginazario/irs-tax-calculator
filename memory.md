# Project Decision Log — IRS Tax Calculator

## Architecture Decisions
- **Decimal everywhere**: All monetary values use `Decimal` with `ROUND_HALF_UP` — no floats
- **Pydantic v2**: Typed input/output at every boundary with `model_validator`
- **WAT Framework**: Tools (pure functions) → Workflows (orchestration) → Agents (LLM decisions)
- **Single tax year**: 2024 only — constants in `backend/src/data/tax_year_2024.py`
- **5 filing statuses**: SINGLE, MFJ, MFS, HOH, QSS
- **Income sources**: W-2, 1099-NEC, 1099-INT, 1099-DIV, 1099-B

## Completed Phases

### Phase 1: Foundation ✅
- Monorepo structure: `backend/` (Python/FastAPI) + `frontend/` (React/Vite/TS)
- Tax year 2024 constants with IRS citations (Rev. Proc. 2023-34)
- Pydantic models: `tax_input.py`, `tax_output.py`, `workflow_models.py`, `filing_status.py`, `exceptions.py`
- All 10 core tools built and unit tested:
  - `calculate_bracket_tax`, `calculate_agi`, `lookup_standard_deduction`
  - `calculate_capital_gains_tax`, `calculate_qualified_dividend_tax`
  - `calculate_niit`, `calculate_fica`, `apply_credit`
  - `format_currency`, `preferential_rate`

### Phase 2: Workflows ✅
- All 8 workflows built and tested:
  - `income_workflow` — aggregate all income sources, compute NII
  - `agi_workflow` — gross income minus above-the-line deductions
  - `fica_workflow` — W-2 FICA + self-employment tax + SE deduction
  - `deduction_workflow` — standard vs. itemized; partition ordinary/preferential income
  - `tax_computation_workflow` — bracket tax + preferential-rate tax + NIIT stacking (IRC §1(h))
  - `credits_workflow` — CTC, EITC, refundable/non-refundable
  - `summary_workflow` — effective rate, marginal rate, refund/owed
  - `orchestrator` — single entry: `calculate_full_tax(TaxReturnInput) -> FullTaxCalculationResult`

### Phase 3: API + Frontend ✅
- **Backend API** (158 backend tests pass):
  - `backend/src/api/main.py` — FastAPI app with CORS (localhost:5173, 4173)
  - `backend/src/api/routes.py` — 4 endpoints: POST /api/calculate, POST /api/calculate/estimate, GET /api/brackets/2024, GET /api/deductions/2024
  - `backend/src/api/models.py` — EstimateInput, EstimateResult, BracketsResponse, DeductionsResponse
  - `backend/src/api/exception_handlers.py` — custom exception → HTTP status mapping
  - `backend/tests/integration/test_api.py` — 10 integration tests
- **Frontend Foundation** (38 frontend tests pass):
  - `frontend/src/types/tax.ts` — TypeScript interfaces mirroring all backend models
  - `frontend/src/services/api.ts` — typed fetch wrapper (taxApi object)
  - `frontend/src/utils/format.ts` — formatCurrency, formatPercent, formatFilingStatus
  - `frontend/src/utils/validation.ts` — client-side validation matching backend rules
  - `frontend/src/utils/defaults.ts` — factory functions for empty form objects
  - `frontend/src/hooks/useCalculator.ts` — form state + API integration hook
- **Frontend UI**:
  - 7 components: FilingStatusSelector, IncomeSection, DeductionSection, CreditsSection, PaymentsSection, ResultsDisplay, ErrorDisplay
  - `frontend/src/pages/CalculatorPage.tsx` — main page composing all components
  - TailwindCSS styling, responsive layout, green/red color-coding for refund/owed

### Phase 4: SQLite Database + MCP Data Analyst Server ✅
- **SQLite Database** (175 backend tests pass):
  - `backend/src/database/db.py` — Connection manager (raw sqlite3, no ORM)
  - `backend/src/database/schema.sql` — tax_calculations table
  - `backend/src/database/repository.py` — CRUD: save, list, get, delete calculations
  - Auto-persist: orchestrator.py auto-saves after calculate_full_tax() (try/except, won't break calc)
  - History API routes: GET /api/history, GET /api/history/{id}, DELETE /api/history/{id}
  - DB file: `backend/tax_data.db` (gitignored via *.db)
  - Lifespan handler in main.py for DB init/close
  - 10 new repository tests + 7 new history API integration tests
- **MCP Data Analyst Server**:
  - `mcp_server/server.py` — FastMCP server with 4 tools
  - `mcp_server/context.py` — Tax domain knowledge for LLM system prompts
  - `mcp_server/tools/query_data.py` — Natural language → SQL → results (read-only)
  - `mcp_server/tools/create_chart.py` — LLM-driven Plotly chart generation (HTML output)
  - `mcp_server/tools/create_table.py` — LLM-driven markdown table generation
  - `mcp_server/tools/generate_report.py` — LLM-driven analytical report generation
  - All tools use Claude API (anthropic SDK) with read-only SQL validation
  - Run with: `python -m mcp_server.server`

### Phase 5: History Page + Analytics Page ✅
- **Frontend Routing** (react-router-dom):
  - `frontend/src/main.tsx` — wrapped `<App>` in `<BrowserRouter>`
  - `frontend/src/App.tsx` — shared header + `<NavBar>` + `<Routes>` (3 routes: `/`, `/history`, `/analytics`)
  - `frontend/src/components/NavBar.tsx` — tab navigation with active state styling
  - `frontend/src/pages/CalculatorPage.tsx` — refactored (header moved to App.tsx)
- **History Page**:
  - `frontend/src/hooks/useHistory.ts` — fetch, view detail, delete calculations
  - `frontend/src/pages/HistoryPage.tsx` — card list, detail modal (reuses ResultsDisplay), delete with confirmation
- **Analytics Page**:
  - `frontend/src/hooks/useAnalysis.ts` — tool selector, prompt/result state, execute
  - `frontend/src/pages/AnalyticsPage.tsx` — 4 tools (Query/Chart/Table/Report), prompt textarea, results rendering (pre/iframe/markdown)
- **Backend Analysis API** (183 backend tests pass):
  - `backend/src/api/analysis_routes.py` — 4 async endpoints wrapping MCP tool functions (query, chart, table, report)
  - Imports MCP tools directly (not subprocess); uses sys.path hack for mcp_server package
  - All endpoints check ANTHROPIC_API_KEY, return 503 if missing
  - `backend/tests/integration/test_analysis_api.py` — 8 tests (4 API key guard + 4 mocked tool calls)
- **Types**: Added CalculationSummary, CalculationDetail, DeleteResponse, AnalysisTool to `frontend/src/types/tax.ts`
- **API Service**: Extended `taxApi` with 7 new methods (3 history + 4 analysis)

## Remaining Polish
- Agent layer (InputClassifierAgent, DeductionStrategyAgent)
- Responsive design pass
- End-to-end tests

## Key File Paths
- Constants: `backend/src/data/tax_year_2024.py`
- Models: `backend/src/models/`
- Tools: `backend/src/tools/`
- Workflows: `backend/src/workflows/`
- Orchestrator: `backend/src/workflows/orchestrator.py`
- Database: `backend/src/database/` (db.py, repository.py, schema.sql)
- API: `backend/src/api/main.py` (entrypoint: `src.api.main:app`)
- Analysis API: `backend/src/api/analysis_routes.py` (4 endpoints under /api/analysis/)
- MCP Server: `mcp_server/server.py` (entrypoint: `python -m mcp_server.server`)
- Frontend app: `frontend/src/App.tsx` → Routes (Calculator, History, Analytics)
- Frontend types: `frontend/src/types/tax.ts`
- Frontend components: `frontend/src/components/`
- Frontend pages: `frontend/src/pages/` (CalculatorPage, HistoryPage, AnalyticsPage)
- Tests: `backend/tests/` (183 tests), `frontend/src/utils/__tests__/` (38 tests)

## Git
- Remote: https://github.com/jorginazario/irs-tax-calculator
- Branch: `main`

## Dev Commands
- Backend: `cd backend && uvicorn src.api.main:app --reload`
- Frontend: `cd frontend && npm run dev`
- Backend tests: `cd backend && python -m pytest tests/ -v`
- Frontend tests: `cd frontend && npx vitest run`

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

## Current Phase: Phase 4 — Polish

### What's needed:
- Agent layer (InputClassifierAgent, DeductionStrategyAgent)
- Responsive design pass
- End-to-end tests

## Key File Paths
- Constants: `backend/src/data/tax_year_2024.py`
- Models: `backend/src/models/`
- Tools: `backend/src/tools/`
- Workflows: `backend/src/workflows/`
- Orchestrator: `backend/src/workflows/orchestrator.py`
- API: `backend/src/api/main.py` (entrypoint: `src.api.main:app`)
- Frontend app: `frontend/src/App.tsx` → `CalculatorPage`
- Frontend types: `frontend/src/types/tax.ts`
- Frontend components: `frontend/src/components/`
- Tests: `backend/tests/` (158 tests), `frontend/src/utils/__tests__/` (38 tests)

## Git
- Remote: https://github.com/jorginazario/irs-tax-calculator
- Branch: `main`

## Dev Commands
- Backend: `cd backend && uvicorn src.api.main:app --reload`
- Frontend: `cd frontend && npm run dev`
- Backend tests: `cd backend && python -m pytest tests/ -v`
- Frontend tests: `cd frontend && npx vitest run`

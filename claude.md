# CLAUDE.md — IRS Tax Calculator Project

## Project Overview
Build an IRS tax calculator with a **React frontend** and **Python (FastAPI) backend**, covering **tax year 2024** only. Supported scenarios: W-2 income, 1099 income, and investment income (capital gains/dividends).

---

## Tech Stack
- **Frontend:** React 18+ with TypeScript, Vite, TailwindCSS
- **Backend:** Python 3.12+, FastAPI, Pydantic v2
- **Math:** Python `Decimal` for all currency — never use `float`
- **Testing:** pytest (backend), Vitest (frontend)
- **Linting:** Ruff (Python), ESLint + Prettier (React)

---

## WAT Framework Guidelines

### Workflows
Workflows are deterministic, ordered sequences of steps. Use workflows when the task has a predictable, fixed path.

**Rules:**
- Break complex tax logic into discrete, composable workflow steps
- Each workflow step should have a single responsibility
- Workflows must be idempotent — same input always produces same output
- Use orchestrator functions to chain steps; never nest workflows deeply
- Document each workflow with input/output contracts using Pydantic models

**Tax Calculator Workflows:**
1. **Income Workflow:** Collect and categorize income sources (W-2 wages, 1099-NEC/MISC, 1099-B capital gains, 1099-DIV dividends/qualified dividends)
2. **AGI Workflow:** Sum gross income → apply above-the-line deductions → compute AGI
3. **Deduction Workflow:** Determine standard vs. itemized; compute taxable income
4. **Tax Computation Workflow:** Apply 2024 brackets → add capital gains tax (0%/15%/20%) → add NIIT if applicable
5. **Credits Workflow:** Apply eligible credits (earned income, child tax, etc.)
6. **Summary Workflow:** Compute final liability, effective rate, marginal rate, refund/owed

### Agents
Agents are LLM-driven decision-makers that handle ambiguity. Use agents when the path depends on dynamic input or user context.

**Rules:**
- Agents decide *which* workflow or tool to invoke — they do NOT contain business logic
- Keep agent scope narrow: one agent per domain
- Agents must explain reasoning via structured output before acting
- Agents fail gracefully with clear error messages, never silently guess
- Limit agent autonomy — require confirmation before irreversible actions

**Tax Calculator Agents:**
- **InputClassifierAgent:** Determines income type from ambiguous user input
- **DeductionStrategyAgent:** Recommends standard vs. itemized based on user data

### Tools
Tools are atomic, reusable Python functions called by workflows or agents.

**Rules:**
- Tools must be pure functions (no side effects, deterministic)
- Every tool uses Pydantic models for typed inputs/outputs
- Tools validate their own inputs and raise descriptive errors
- Name tools as `verb_noun` (e.g., `calculate_bracket_tax`)
- Keep tools under ~50 lines; split if larger

**Tax Calculator Tools:**
```
calculate_bracket_tax(taxable_income, filing_status) → Decimal
lookup_standard_deduction(filing_status, is_blind, is_over_65) → Decimal
calculate_agi(gross_income, above_line_deductions) → Decimal
calculate_capital_gains_tax(short_term, long_term, ordinary_income, filing_status) → Decimal
calculate_niit(magi, net_investment_income, filing_status) → Decimal
calculate_fica(w2_wages, self_employment_income) → FicaResult
apply_credit(tax_owed, credit_amount, is_refundable) → Decimal
calculate_qualified_dividend_tax(qualified_divs, ordinary_income, filing_status) → Decimal
format_currency(amount) → str
```

---

## 2024 Tax Data (constants)

All rates, brackets, and thresholds live in `backend/src/data/tax_year_2024.py`:
- Federal income tax brackets (7 brackets per filing status)
- Standard deduction amounts by filing status
- Capital gains rate thresholds (0% / 15% / 20%)
- NIIT threshold ($200k single, $250k MFJ)
- Social Security wage base ($168,600)
- Medicare rates (1.45% + 0.9% additional over $200k/$250k)
- Common credits: Child Tax Credit, Earned Income Credit thresholds

**Cite IRS sources in comments** (e.g., `# Rev. Proc. 2023-34, Form 1040 Line 16`)

---

## Code Standards

### Architecture
```
irs-tax-calculator/
├── CLAUDE.md
├── backend/
│   ├── src/
│   │   ├── tools/            # Pure functions (atomic tax operations)
│   │   ├── workflows/        # Deterministic step sequences
│   │   ├── agents/           # LLM-driven decision points
│   │   ├── data/             # 2024 brackets, rates, thresholds
│   │   ├── models/           # Pydantic input/output schemas
│   │   └── api/              # FastAPI routes
│   ├── tests/
│   │   ├── tools/
│   │   ├── workflows/
│   │   └── integration/
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/       # React UI components
│   │   ├── pages/            # Page-level views
│   │   ├── hooks/            # Custom hooks (useCalculator, etc.)
│   │   ├── services/         # API client (fetch wrappers)
│   │   ├── types/            # TypeScript interfaces
│   │   └── utils/            # Formatting helpers
│   ├── package.json
│   └── vite.config.ts
└── docs/
```

### Backend Rules
- All monetary values use `Decimal` with `ROUND_HALF_UP`
- Pydantic models for every API request/response
- FastAPI dependency injection for shared config
- Custom exceptions: `InvalidFilingStatus`, `MissingIncomeData`, `UnsupportedScenario`
- Never return a tax result if inputs are incomplete — return 422 with missing fields

### Frontend Rules
- TypeScript strict mode enabled
- All API responses typed with matching interfaces from `types/`
- Form validation mirrors backend validation (fail fast on the client)
- Use controlled components for all tax input forms
- Display currency with `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })`
- Responsive layout — works on mobile

### Testing
- **Every tool must have unit tests** with known IRS examples
- Use IRS Publication 17 / tax tables as ground truth for test data
- Test edge cases: $0 income, max bracket boundary, NIIT threshold crossover, mixed income types
- Integration tests run full workflows with sample W-2 and 1099 returns
- Frontend: test form validation and API integration with mocked responses

---

## Supported Income Types

| Source | Form | Fields |
|--------|------|--------|
| Wages/Salary | W-2 | Gross wages, federal withholding, state withholding, Social Security wages, Medicare wages |
| Freelance/Contract | 1099-NEC | Non-employee compensation |
| Interest | 1099-INT | Interest income |
| Dividends | 1099-DIV | Ordinary dividends, qualified dividends |
| Capital Gains | 1099-B | Short-term gains/losses, long-term gains/losses |

---

## API Endpoints (FastAPI)

```
POST /api/calculate          — Full tax calculation (accepts all income + deductions)
POST /api/calculate/estimate — Quick estimate from gross income + filing status
GET  /api/brackets/2024      — Return 2024 tax brackets
GET  /api/deductions/2024    — Return standard deduction amounts
```

---

## Build Order (Recommended)

### Phase 1: Foundation
1. Set up monorepo structure (backend + frontend)
2. Create `data/tax_year_2024.py` with all constants
3. Define Pydantic models for inputs/outputs
4. Build core tools: `calculate_bracket_tax`, `lookup_standard_deduction`, `calculate_agi`
5. Unit test all tools against IRS tables

### Phase 2: Workflows
6. Build Income Workflow (aggregate all sources)
7. Build AGI → Deduction → Tax Computation pipeline
8. Build Capital Gains tax tool + integration
9. Build Summary Workflow
10. Integration tests with sample returns

### Phase 3: API + Frontend
11. FastAPI routes with Pydantic validation
12. React form: filing status, income inputs (W-2, 1099, investments)
13. Results display: breakdown, effective rate, marginal rate
14. Error handling and edge case UX

### Phase 4: Polish
15. Agent layer for ambiguous inputs (optional)
16. Responsive design pass
17. End-to-end tests

---

## Session Commands
```bash
# Backend
cd backend && pip install -r requirements.txt
pytest                          # run all tests
pytest tests/tools/ -v          # test tools only
ruff check src/                 # lint
uvicorn src.api.main:app --reload  # dev server

# Frontend
cd frontend && npm install
npm run dev                     # Vite dev server
npm run test                    # Vitest
npm run lint                    # ESLint
npm run build                   # production build
```

---Yes 

## Key Reminders
- **Correctness over speed** — tax errors have real consequences
- Always cite IRS form/line references in code comments
- Use `Decimal` everywhere — never `float` for money
- Validate inputs at every boundary (frontend, API, tool)
- Commit after each completed tool or workflow with descriptive messages
- When in doubt, reference IRS Publication 17 and Rev. Proc. 2023-34

## Memory
- MANDATORY: Log all architectural decisions and completed steps to memory.md."

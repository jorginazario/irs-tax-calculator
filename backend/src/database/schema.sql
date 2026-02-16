CREATE TABLE IF NOT EXISTS tax_calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    filing_status TEXT NOT NULL,
    input_data TEXT NOT NULL,
    total_income REAL NOT NULL,
    agi REAL NOT NULL,
    taxable_income REAL NOT NULL,
    federal_tax REAL NOT NULL,
    total_credits REAL NOT NULL,
    total_tax REAL NOT NULL,
    effective_rate REAL NOT NULL,
    marginal_rate REAL NOT NULL,
    refund_or_owed REAL NOT NULL,
    result_data TEXT NOT NULL
);

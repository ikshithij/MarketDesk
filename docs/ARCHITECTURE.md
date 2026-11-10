# Architecture

## One local application

The production frontend is compiled with Vite and served by the FastAPI process on loopback. SQLite owns personal records, JSON provider caches, FTS5 research search, job status and AI usage records. Two worker threads run bounded refresh jobs; provider traffic is globally serialised at no more than approximately 1.7 requests per second. Interactive pages stay usable while refreshes run. An optional in-process scheduler refreshes watched SEC data every six hours while the application is open.

React + TypeScript is retained from the preferred stack. Vite replaces Next.js because this application needs neither server rendering nor a second Node server for normal use. CSS uses a small set of design tokens rather than a component framework. Python handles all financial calculations; the browser never generates executable research code.

DuckDB/Parquet should be added when cross-sectional histories outgrow SQLite JSON caches. Introducing both databases for 20 starter issuers would add operational complexity without a demonstrated need. Likewise, no Redis, Elasticsearch, vector database or redundant backtest engine is installed.

## Ownership

- `server/store.py`: transactions, schema, caches and settings. Connections use WAL and a busy timeout. The default data directory can be replaced with `MARKETDESK_DATA_DIR`.
- `server/providers.py`: SEC, Alpha Vantage and FRED boundaries. Fixed HTTPS endpoints, timeouts, explicit credentials and provenance. Failed refreshes retain the last successful cache.
- `server/finance.py`: deterministic XBRL normalisation, ratios, weighted average portfolio accounting and a small fixed-rule backtester. No I/O or model dependency.
- `server/main.py`: validated API, deterministic search intents, background orchestration, notebook/search and optional AI research.
- `src/api.ts`: API transport and number formatting.
- `src/Chart.tsx`: lifecycle-managed TradingView Lightweight Charts.
- `src/main.tsx`: coherent product workflows. Navigation state is local UI state; persistent personal records are server-owned.
- `src/style.css`: responsive visual system, focus visibility and reduced-motion handling.

## Financial invariants

1. Financial observations are never seeded. Starter symbols are identities only.
2. Reported annual durations are 300–380 days; standalone quarters are 65–110 days. YTD cash flows are never relabelled as standalone quarters.
3. Each duration retains its exact start/end and source accession/tag/filing date. Latest available restatements replace prior observations for that exact period. These are current research views, not point-in-time datasets for backtesting.
4. Balance-sheet observations must match a verified duration's end date. Unsupported/custom XBRL tags remain missing. Debt is available only when both current and noncurrent long-term debt tags exist; it is not a complete debt taxonomy.
5. FCF = operating cash flow − payments for property, plant and equipment. Net margin = net income / revenue. Growth compares consecutive annual ends only. Zero denominators remain missing.
6. Portfolio accounting uses weighted average cost, includes fees, and rejects sales beyond dated available shares. Quotes must match transaction currency. A supplied spot GBP/USD rate converts aggregates; it is not historical FX P&L or UK tax lot accounting.
7. Backtest signals use only prior closes and execute at next adjusted open. Explicit costs and slippage reduce cash on both sides. Adjustment factors approximate total-return exposure; no dividend cash ledger exists. Current-security survivorship bias and in-sample limitations stay visible.

## Boundaries and constraints

Local host/origin checks, server-only secrets, no arbitrary provider URL, no dynamic SQL identifiers from requests, parameterised SQL, no arbitrary code execution, and no brokerage execution. Provider error messages do not expose credential-bearing URLs. Notebook FTS queries are quoted as phrases to avoid malformed operators. Inputs reject NaN/infinity and negative sizes.

Data refresh is explicit by default; SEC watchlist scheduling is opt-in. Job status survives process restarts, and interrupted jobs are marked failed on startup. Current jobs are serialised at the application level; new refresh requests join the current job instead of launching unlimited work. This is designed for one local process, not multi-worker deployment.

The OpenAI call has a bounded output token budget, uses cached public company context and logs token counts. Provider/model selection is currently environment-based and OpenAI-only. Actual provider billing remains authoritative; a dollar estimate is intentionally not hard-coded.

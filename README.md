# MarketDesk

**The personal financial intelligence terminal.** A local-first research workspace for macOS, built with React, TypeScript, FastAPI and SQLite.

This is the first working release of the [product brief](docs/PRODUCT_BRIEF.md), not a claim that every capability in that brief is finished. Financial data is never fabricated to fill the interface. Company prices and charts load automatically from Yahoo Finance without keys. Official financial statements require SEC contact configuration; other optional providers require their own credentials.

## Run on your Mac

Requirements: macOS, Python 3.12+, Node.js 22+ and npm. Install once:

```sh
./setup.command
```

Then double-click **start.command** in Finder, or run:

```sh
./start.command
```

MarketDesk opens at **http://127.0.0.1:8000**. The startup window keeps the local server running; Control-C stops it. No cloud account, Docker, Redis or brokerage connection is needed. For development, start the API with `.venv/bin/python -m uvicorn server.main:app --host 127.0.0.1 --port 8000` and run `npm run dev` in another terminal.

## Make it useful

1. Search a company or select one from the briefing. The latest available quote and charts load automatically without keys.
2. Optional: open **Settings & data**, add your contact email for SEC fair access, and save. **Financials → Load official financials** retrieves official financials and filing metadata in the background.
3. Star companies for your watchlist. Filter reported financials in **Discover**, compare companies and save useful screens.
4. Add transactions to **Portfolio** and record your investment thesis in **Research**.
5. Optional: copy `.env.example` to `.env`, add provider keys and restart. Prices, macro data and AI use separate provider entitlements. A ChatGPT subscription is not API access.

**No credentials?** Latest quotes, one-year daily charts, latest-session five-minute charts, notes, manual transactions, watchlists, saved screens, local search and exports work. Official statement observations remain unavailable until SEC access is configured.

## What works

- Responsive dark research workspace with universal search and keyboard focus shortcut (⌘/Ctrl K).
- Search by ticker/name, deterministic natural-language intent routing and visible editable filter translations. Supported screening conditions: sector, minimum annual revenue growth, minimum net margin and positive free cash flow. Unsupported conditions are explicitly not applied.
- 20 identity-only starter companies; SEC directory lookup can add other US-listed issuers on demand when SEC access is configured. Sector classification for new companies remains unclassified.
- SEC annual and standalone quarterly XBRL financials, provenance, latest restatements, growth, margins and FCF. Filing links go to SEC originals.
- Research briefing, watchlists, growth radar, saved screens and company comparison.
- Automatic Yahoo Finance public quotes with original timestamps and delay labels, one-year daily history, latest-session five-minute bars, line/candlestick charts and 60-second polling while a company is viewed. This is an unofficial public feed for personal research, not a guaranteed real-time exchange service. The Alpha Vantage adapter remains available in source for future provider selection.
- Optional FRED observations for Treasury yields, policy rates, inflation and unemployment.
- Manual USD/GBP transactions with fees, weighted average cost, realised/unrealised P&L and explicitly dated user-supplied spot FX. Missing prices/FX prevent misleading partial totals.
- Reproducible long/cash SMA backtest with prior-close signals, next adjusted-open execution, costs, slippage, equity curve, buy-and-hold comparison and trade history.
- Optional OpenAI research using only cached structured financial evidence. Usage tokens are recorded. Model configurable through `.env`. Full filing contents and live news are not sent or claimed to have been read.
- SQLite FTS research notebook, workspace JSON export, cached observations and persistent background job status.
- Optional six-hour watchlist SEC refresh while the app is running. Market-price refreshes are explicit to conserve provider quotas.

## Data and privacy

Personal data and provider caches live in `.marketdesk/marketdesk.db` (gitignored). Copy that file while the app is stopped for a complete backup, or use **Settings → Export personal workspace** for notes, transactions, watchlists, screens and preferences. JSON export does not include provider caches. There is no import UI yet.

Secrets stay in `.env` or the server environment and are never returned to the browser. SEC receives your configured contact identity; Yahoo Finance receives the viewed ticker and refresh requests; FRED receives its relevant requests; OpenAI receives a company question and cached public financial context only when you press the AI research button. Personal notes and portfolio data are not included in the AI payload. Fonts use the system stack: no external font request or analytics is required.

Bind only to loopback. Host/origin checks reject unrelated websites and DNS rebinding attempts. This is a single-user local app with no remote authentication; do not expose it through a public tunnel. No brokerage execution or generated-code execution exists.

## Verification

```sh
npm run build
.venv/bin/python -m unittest discover -s tests -v
```

Tests cover reporting durations, restatements, missing values, growth calculations, cost basis/fees, missing FX, overselling, causality of backtest execution, cost impact, API validation, notebook FTS, watchlists, provider failures and local access boundaries. Tests use isolated temporary databases and test-only synthetic fixtures; fixtures are never served by the application.

Yahoo QCOM market-data retrieval has been verified live without credentials. SEC, FRED and AI still require configuration and have not been end-to-end verified with the user's credentials. See [verification](docs/VERIFICATION.md).

## Engineering decisions and remaining work

Read [architecture](docs/ARCHITECTURE.md), [research and dependency decisions](docs/RESEARCH.md), [provider matrix](docs/DATA_PROVIDERS.md), and [delivery status](docs/DELIVERY_STATUS.md).

The current Quant Lab is a single-security educational simulation. It is not a survivorship-corrected market-wide strategy engine or evidence of out-of-sample performance. Portfolio P&L is not tax accounting; no corporate-action ledger or historical FX accounting is implemented. Advanced features from the brief are tracked explicitly rather than represented with invented results.

# MarketDesk

A simple, local company research workspace: write a company's name and receive a detailed online AI analysis with linked evidence. It uses your existing Codex sign-in. Financial data needs no new accounts, API key or SEC contact setup.

## Run on your Mac

Requirements: macOS, Python 3.12+, Node.js 22+, npm, and the [Codex CLI](https://developers.openai.com/codex/cli/) signed in with your existing account.

```sh
./setup.command
codex login status
./start.command
```

Or double-click `start.command`. Open <http://127.0.0.1:8000>. If Codex needs sign-in, run `codex login` yourself and retry. The app checks existing sign-in; it never copies credentials. Research uses your account's AI usage allowance and may encounter its limits.

For development, run `.venv/bin/python -m uvicorn server.main:app --host 127.0.0.1 --port 8000` and `npm run dev` in separate terminals.

## Use it

- **Today:** type “Qualcomm”, another company name or a ticker, then press **Analyse company**. Choose a listing if there are multiple matches. An optional question can focus the research.
- **Companies:** compare every workspace company in a sortable ratings table, then reopen saved analyses. The new AI opinion ratings are out of five, with cited reasoning for every component, a server-calculated long-term total, coverage counts, price snapshots and CSV export. Today highlights the top researched candidates. [Read the fixed rating rubric](docs/COMPANY_RATINGS.md). “All” covers the current workspace, initially 20 US equities, not every listed stock.
- **Detailed company reports:** reopen saved analyses. Each report contains business, financials, growth, valuation, long-term view, short-term timing, leadership/news, risks and monitoring questions. Findings distinguish reported information, calculations and AI interpretation, with links and evidence gaps. Separate tabs show price context and source details.
- **Refresh research** creates a new report, preserving the original. Asking a follow-up also creates a separate sourced report. A matching completed report is reused for 24 hours unless explicitly refreshed. Runs remain available if you leave the page.
- **Quant Lab:** retain the educational long/cash moving-average experiment with explicit costs and assumptions. This is separate from registered strategy TR-001 and does not establish predictive performance.

The interface is research, not broker execution. Trading 212 listing eligibility is not verified. UK regular-hours, long-only and no-leverage constraints are included in the AI research prompt. The comparison ranks exploratory AI opinions, not validated buy/sell signals. There is no automated morning report.

## Data and AI

Company-name discovery and latest available price history use public Yahoo Finance endpoints. This is an unofficial feed with provider timestamps and delay labels, not guaranteed real-time exchange data. Research uses Codex live web tools to find original company disclosures and dated news. Structured SEC facts are optional context, never a prerequisite. Blocked documents and search-only sources should be identified in the report; source-access labels are AI-reported, not independent document verification.

Codex runs non-interactively in a temporary directory with read-only sandboxing, live web enabled, and shell tools, apps, plugins, computer use and multi-agent execution disabled. It receives company identity, public market context, the canonical research policy and the question you enter. No portfolio or notebook data is included. Do not put private information into research questions. Your AI allowance is used only when starting a new research run. One worker and a maximum of three pending runs bound concurrent usage; runs time out after ten minutes.

Reports require nine sections, at least three source references, safe HTTPS source URLs and resolvable citations for reported/derived findings. A run with no recorded web-tool calls is rejected. These checks validate structure and attribution, not factual truth. AI can misread evidence or calculate incorrectly. Numerical forecast confidence remains unvalidated and must not be invented.

Personal data, provider caches and saved reports live in `.marketdesk/marketdesk.db` (gitignored). Copy the database while the app is stopped for a full backup. Each report can be exported as JSON. New research runs save the exact prompt and policy/context hashes for audit; full source-document snapshots are not archived, so reports remain exploratory rather than point-in-time backtest evidence. Interrupted research is marked failed at restart; previous reports stay available.

Bind only to loopback. Host/origin checks reject unrelated websites. This is a single-user local app; there is no remote authentication. Existing notebook, portfolio, watchlist and optional provider endpoints remain in the backend, but are outside the simplified interface.

Optional environment settings are documented in `.env.example`. No new key is needed for the main workflow. The older API-key research endpoint is retained for compatibility, separate from the new online company researcher.

## Verification and continuity

```sh
npm run build
.venv/bin/python -m unittest discover -s tests -q
python3 scripts/check_research_standard.py
python3 scripts/check_company_ratings.py
```

Read the [research standard](docs/RESEARCH_STANDARD.md), [methods paper](docs/papers/MarketDesk_Research_Methods_v1.0.docx), and [company researcher implementation](docs/COMPANY_RESEARCH.md). The versioned standard and six strategy definitions remain unchanged. Registered strategies, calibrated forecast probabilities and automatic trading are not implemented by this update.

See [product brief](docs/PRODUCT_BRIEF.md) and [architecture](docs/ARCHITECTURE.md) for earlier system scope. Earlier delivery documents describe the previous multi-panel interface; the company researcher document records this release's actual behavior.

## US and UK market-wide expansion

The [tested full-market data solution](docs/research/US_UK_FULL_MARKET_SOLUTION_2026-11-10.md) records official exchange-directory probes, a 24-ticker financial-field sample, current share/valuation routes and the proposed numerical-screen → top-100 AI workflow. This is a researched implementation specification, not a claim that the app already covers every issuer. Live raw responses and sample summaries are retained locally in `.marketdesk/research-probes/`. The existing methods and rating rubric remain unchanged.

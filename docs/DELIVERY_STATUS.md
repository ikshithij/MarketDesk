# Delivery status

This release establishes a usable local research application and its deterministic calculation/data boundaries. The master brief describes a much larger product; the items below distinguish working paths from remaining work.

| Brief area | Working now | Remaining |
|---|---|---|
| Universal search | Ticker/name lookup, SEC directory additions, company/compare/screen/portfolio/filing intents, visible supported filters | General semantic questions, complete screening grammar, unsupported-condition parser, research history |
| Daily briefing | Local coverage, watchlist, latest cached filings, growth ranking, research entry points | Live indices, breadth, sectors, earnings/catalysts, news personalisation |
| Discovery | Local-universe numeric screener, saved screens, reasons, missing-data exclusion, transparent annual-growth ranking | Market-wide ingestion; valuation/momentum/event filters; historical change alerts |
| Company research | Annual/standalone-quarterly standard XBRL, health/growth/cash metrics, source metadata, filing links, notes, comparison | Segments, estimates, earnings calendar/history, full statements/custom taxonomy coverage, ownership/insider tables, verified relationships |
| Markets | Optional FRED rates/inflation/unemployment | Global indices, ETF/FX/commodity/crypto providers and breadth |
| Charts | Automatic keyless Yahoo quotes, daily/latest-session line/candlestick charts, zoom/crosshair, sourced quote timestamps, 60-second updates | Volume, indicators, earnings/trade overlays, chart comparisons and saved layouts |
| News | Direct SEC disclosures as a distinct filings workspace | Licensed news feeds, deduplication, company event attribution and grounded “why moved” answers |
| Portfolio | Dated buys/sells, fees, weighted average cost, realised/unrealised P&L, USD/GBP spot conversion, missing-price protection | Corporate-action/FX ledger, portfolio time series, allocation analytics, benchmark/risk attribution/correlations; tax-specific lots |
| Quant Lab | Explicit SMA rules, costs/slippage, next-open simulation, standard result metrics, trades, equity and benchmark curves | Natural-language strategy compiler, multi-asset portfolio engine, point-in-time universes, walk-forward/out-of-sample splits and robust corporate-action ledger |
| AI | Optional model-configurable OpenAI structured-financial Q&A with source context/token log and save-to-notebook | Other model providers, full filing retrieval/cited passages, spend estimates/limits, committee, OpenBB MCP, TradingAgents, Kronos and RD-Agent execution |
| Local operation | Single process serving frontend, SQLite/FTS/caches, optional watchlist scheduler, background refresh, JSON export, macOS launch scripts | Native app packaging, migrations/import UI, DuckDB/Parquet analytics at scale |

## Next engineering gates

1. Validate SEC taxonomy coverage against real company fixtures and exercise live provider flows with user-owned keys and entitlements.
2. Add corporate-action/security-master and point-in-time data before presenting historical portfolio risk or market-wide backtests.
3. Add full filing ingestion with passage-level provenance before offering annual-report risk extraction or investment-committee reports.
4. Add broader licensed market/news coverage before personal daily briefings claim market completeness.
5. Isolate autonomous research environments with no access to local secrets before enabling any code-generating agent framework.

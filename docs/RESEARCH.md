# Product and dependency research

Primary sources reviewed on 10 November 2026. These are design and integration decisions, not claims that a framework has been fully benchmarked or audited. Repository availability and README/licence review are not a reproducible release-maintenance audit; pin and recheck any candidate before adoption.

## Product lessons

| Product / primary reference | Useful pattern | MarketDesk decision |
|---|---|---|
| [Bloomberg Terminal](https://www.bloomberg.com/professional/products/bloomberg-terminal/) | Connected market/company research is the relevant reference; the product page returned 403 in this environment, so current feature/price details were not verified | One connected research workspace; do not replicate legacy density or claim equivalent data coverage |
| [Koyfin](https://www.koyfin.com/features/) | Financial charts, fundamentals and screening in one workspace | Keep company context consistent across screen, comparison and research |
| [Finviz](https://finviz.com/) | Fast scan of securities, screening and breadth | Visible numeric filters and readable results; avoid copying a page full of simultaneous signals |
| [TradingView Lightweight Charts](https://www.tradingview.com/lightweight-charts/) | Responsive financial charting with a small focused library | Use the open-source chart library; preserve its attribution |
| [TIKR](https://www.tikr.com/) | Connected screening, financial history and research workflow | Reduce the distance between discovery and evaluating a business; do not imply Capital IQ coverage from free SEC access |
| [Fiscal.ai](https://fiscal.ai/) | Auditable financial data and a separate data API | Keep source and reporting dates visible; evaluate commercial normalisation before expanding custom XBRL coverage |
| [Quartr](https://www.quartr.ai/features) | Company material and evidence-oriented research | Prefer original dated disclosures; transcripts require their own rights and integration |
| [Perplexity Finance](https://www.perplexity.ai/finance) | Question-led entry point; page content was not accessible for detailed inspection | Universal question box with deterministic routes first. Do not pretend to have live sourced answers without retrieval |
| [OpenBB](https://docs.openbb.co/odp/python/extensions/providers) | Provider-specific data adapters and credentials | Separate provider boundaries; avoid assuming a platform installation supplies data entitlements |

## Dependency decisions

Only React, TypeScript, Vite, Lucide, Lightweight Charts, FastAPI, Uvicorn and HTTPX are installed as direct application dependencies. Python's SQLite and statistics support the initial workload. Node and Python lock files record the tested environment. No AI framework executes autonomous code.

| Candidate / primary source | Licence / fit assessment | Decision / revisit trigger |
|---|---|---|
| [OpenBB](https://docs.openbb.co/odp/python/extensions/providers) | Broad provider ecosystem; provider auth/data dependencies remain. Current provider APIs must be checked before adoption | Defer platform dependency; direct SEC/FRED/Alpha Vantage adapters are sufficient for the first path. Revisit for broad coverage or MCP tooling |
| [EdgarTools](https://github.com/dgunning/edgartools) | MIT; structured filing/ownership extraction; requires SEC identity and underlying disclosures | Strong next candidate for full filing ingestion and custom taxonomy coverage. Not necessary for the limited company-facts adapter |
| [DuckDB](https://github.com/duckdb/duckdb) | MIT analytical engine; suited to columnar histories | Defer until historical cross-sectional analytics justify a second storage engine; then use Parquet and DuckDB together |
| pandas / NumPy | Widely used numerical ecosystem; BSD-licensed projects. No version-specific compatibility benchmark performed | Defer for the small fixed calculations. Adopt with one tested Python environment when bulk analytics arrive |
| [Lightweight Charts](https://github.com/tradingview/lightweight-charts) | Apache-2.0 with TradingView attribution requirements; standalone financial charts | Installed v5 through the npm lock; instance cleanup and chart lifecycle are isolated |
| [vectorbt](https://github.com/polakowo/vectorbt) | Current README states Apache 2.0 **with Commons Clause**, not unrestricted Apache-2.0. NumPy/Numba/pandas workload and optional dependencies add compatibility obligations | Not installed. Revisit only after licence and data requirements fit the intended distribution |
| [Zipline Reloaded](https://github.com/stefan-jansen/zipline-reloaded) | Apache-2.0; event-driven engine with ingestion/calendar/bundle work | Defer until multi-asset historical research and point-in-time universes exist |
| ML4T Backtest | The brief does not uniquely identify a repository/version. A guessed repository could not be verified | Do not install an ambiguous package. Resolve exact project and licence before evaluation |
| [Microsoft Qlib](https://github.com/microsoft/qlib) | MIT; much broader model/data/research pipeline than the first local product needs | Separate future research environment, not a dependency of basic company research |
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | Apache-2.0; multi-agent LLM workflow entails provider credentials, data dependencies and multiple model calls | Evaluated as optional future committee runner. Start with one bounded evidence-based request and explicit missing evidence |
| [Kronos](https://github.com/shiyu-coder/Kronos) | MIT code; neural market model adds checkpoints, model execution resources and independent validation | Experimental future process only. Do not expose forecasts as facts or install model weights without an evaluation need |
| [Microsoft RD-Agent](https://github.com/microsoft/RD-Agent) | MIT; autonomous research/code generation adds isolation and execution requirements | Defer until a restricted environment without local secrets is available |
| [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | MIT; investor-style agents overlap with committee workflows | Do not combine redundant agent orchestration stacks; no brokerage/execution integration |
| [daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) | MIT; independent analysis/dashboard/notification application | Learn from concise briefing flow; do not embed a second application or enable third-party messaging |
| [QuantStats](https://github.com/ranaroussi/quantstats) | Apache-2.0; return-series reporting and risk metrics | Good future reporting candidate once trustworthy historical portfolio return series exist |
| [PyPortfolioOpt](https://github.com/PyPortfolio/PyPortfolioOpt) | MIT; optimisation requires meaningful return/covariance inputs and solver dependencies | Defer until portfolio history, FX and corporate actions are handled; no suggested weights from insufficient inputs |

## Compatibility, resource and cost reasoning

The normal app runs one Python server and a browser. No GPU, model checkpoint, vector store or distributed service is needed. The 20 starter identities are not a historical universe; additional issuers can be added from SEC directory search. Market-wide ingestion, ownership extraction, earnings estimates and transcripts are separate data-engineering projects.

Provider costs are independent of software licences. SEC is official public reported information; FRED needs the user's key; Alpha Vantage adjusted history depends on plan and quota; AI incurs API charges separately from a ChatGPT subscription. Unknown pricing is labelled contract/plan-dependent rather than guessed.

The initial Quant Lab intentionally has one fixed transparent strategy rather than several overlapping engines. It cannot correct survivorship bias without a delisted-security universe, and it cannot provide point-in-time fundamentals from restated current company facts. Those constraints are visible in the application and delivery status.

The optional OpenAI adapter follows the [official chat completion API schema](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) with server-side credentials, an output cap and usage logging. Live model access/quality remains unverified without user credentials. Other model providers need a separate implementation before they can be selected.

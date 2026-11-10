# MARKETDESK
## The Personal Financial Intelligence Terminal

### Master Product and Engineering Brief

You are acting as the founding engineering team, product architect, quantitative researcher, financial data engineer and design director for **MarketDesk**.

Your responsibility is to design and build an exceptional personal financial intelligence application.

You have substantial independence to research, challenge, improve and implement the proposed solution.

I am providing the product vision and the outcomes I care about. You are responsible for determining the best architecture, libraries, interaction patterns and implementation details.

Do not blindly implement every suggestion. If you discover a better approach, use it and document your reasoning.

**The objective is to make institutional-quality financial research accessible, exceptionally intuitive and useful for an individual investor.**

Think about what Bloomberg Terminal, FactSet, TradingView, Koyfin, Finviz, Perplexity and modern AI research platforms do well.

Then reconsider how their combined capabilities could work in a much simpler, more intelligent product.

Do not imitate their complexity.

---

# PART 1 — THE PRODUCT VISION

## 1. What are we building?

MarketDesk is a local-first financial research and investment intelligence terminal.

It should let me:

- Understand what is happening across financial markets.
- Discover companies and investment opportunities.
- Research any publicly traded company in depth.
- Understand why a stock is rising or falling.
- Compare companies using financial and market data.
- Identify promising stocks before they become obvious.
- Analyse earnings, financial statements and company filings.
- Discover news, catalysts, risks and market trends.
- Analyse and monitor my investment portfolio.
- Test trading strategies against historical data.
- Use AI to research complicated financial questions.
- Keep a searchable record of research and investment decisions.

The application should provide access to professional research capabilities without requiring professional trading software knowledge.

### The most important design principle

**Make complex financial analysis feel simple.**

I want to open MarketDesk and immediately understand:

1. What is happening?
2. What matters?
3. What should I investigate?
4. Why does it matter?
5. What information supports that conclusion?

Everything else should support these five questions.

An excellent experience means I can move from discovering an interesting company to understanding its financial position, valuation, risks and possible opportunities with very little effort.

This must not become a complicated application full of disconnected dashboards.

---

# PART 2 — PRODUCT INTELLIGENCE

## 2. Think independently

You are not simply implementing a specification.

Before coding, research the current open-source financial software ecosystem and relevant financial research products.

Investigate:
- Bloomberg Terminal
- Koyfin
- Finviz
- TradingView
- OpenBB
- Fiscal.ai
- TIKR
- Quartr
- Perplexity Finance
- Other relevant modern financial research products

Understand which features users find useful and which create unnecessary complexity.

Look for better approaches than those suggested in this document.

Your job is to identify the smallest number of thoughtfully designed features that can deliver the greatest practical value.

Do not build features merely because competitors have them.

### You have permission to:

- Choose better-maintained libraries.
- Replace unsuitable dependencies.
- Propose more efficient architectures.
- Combine several features into simpler workflows.
- Remove redundant interfaces.
- Introduce useful features not explicitly requested.
- Improve the information architecture.
- Design intelligent default behaviours.
- Implement additional relevant open-source technologies.
- Challenge assumptions when technical evidence supports doing so.

Explain important decisions in project documentation, but do not repeatedly interrupt development for minor decisions.

Build a coherent product, not a collection of GitHub repositories.

---

# PART 3 — THE USER EXPERIENCE

## 3. One search box should unlock the entire application

Universal search is the centre of MarketDesk.

It should be accessible from every page.

Users should be able to type a company name, ticker, financial question, investment idea or natural-language screening request.

Examples:

"What is happening with Qualcomm?"

"Find semiconductor stocks with revenue growth above 20%."

"Which AI companies are generating positive free cash flow?"

"Why did Micron fall after earnings?"

"Find undervalued companies with strong earnings growth."

"Compare Nvidia, Broadcom, Micron and AMD."

"Show companies benefiting from increased data-centre spending."

"Which of my holdings have earnings next week?"

"Find stocks with strong fundamentals that have fallen more than 15%."

"Which companies have recently increased their guidance?"

### Search behaviour

The system should understand the intent and select the appropriate workflow automatically.

Possible intents:
- Ticker lookup
- Company research
- Market-wide screening
- Financial comparison
- News research
- Portfolio analysis
- Quantitative analysis
- Filing search
- General financial questions

Do not require the user to select a search mode before entering a question.

Use structured numerical queries for financial screening.

Use retrieval-based AI reasoning for complex research questions.

Use deterministic calculations for financial metrics.

Never fabricate data, citations, stock prices or search results.

When possible, provide answers directly instead of forcing the user to open another page.

Provide useful follow-up actions based on the current research context.

## 4. Progressive disclosure

Simplicity does not mean removing advanced functionality.

It means showing the correct amount of information at the correct time.

For example, a company page should initially show:
- Current or most recent available price
- Price performance
- A concise description
- Fundamental financial health
- Growth
- Valuation
- Important recent developments
- Upcoming catalysts
- Major risks

Detailed financial statements, technical indicators, ownership tables and historical datasets should remain available through clear secondary views.

The user should never need to navigate a complex menu to answer a common question.

Design the application around progressive disclosure, thoughtful defaults and contextual actions.

## 5. Minimise manual work

I do not want to configure dozens of things before the application becomes useful.

Use sensible defaults for:
- Market coverage
- Company screening
- Financial ratios
- Charts
- Performance comparisons
- Risk metrics
- Data refresh intervals
- Investment research reports

Allow advanced customisation without making it mandatory.

Remember my watchlists, saved screens, research history and preferences.

Make routine updates automatic when the application is running.

Avoid requiring me to manually download financial data, import CSV files or execute terminal commands during everyday use.

The terminal is for installation and development, not normal operation.

---

# PART 4 — CORE EXPERIENCE

## 6. Home — My market briefing

The homepage should answer:

**What do I need to know today?**

Design an intelligent daily market briefing.

Potential information:
- Major market indices
- Market breadth and sentiment
- Important macroeconomic developments
- Sector performance
- Significant market movers
- Unusual volume or price activity
- Major earnings announcements
- Important news
- Watchlist developments
- Portfolio changes
- New companies matching saved screens

Avoid clutter.

Prioritise relevance over the amount of information displayed.

The homepage should feel like a concise daily briefing prepared by a capable research analyst.

Let users investigate individual developments directly.

## 7. Discover — Find opportunities

This is one of the most important modules.

Create an exceptionally capable stock discovery engine.

It should identify potential opportunities using combinations of:

### Fundamentals
- Revenue growth
- Earnings growth
- Margin expansion
- Free cash flow
- Return on invested capital
- Debt
- Cash reserves
- Capital expenditure
- Financial efficiency

### Valuation
- P/E
- Forward P/E
- EV/EBITDA
- EV/FCF
- Price-to-sales
- Historical valuation ranges
- Sector-relative valuation

### Market behaviour
- Momentum
- Relative strength
- Volume
- Volatility
- Moving averages
- Drawdowns
- Breakouts
- Price recovery patterns

### Events
- Earnings surprises
- Guidance revisions
- Insider transactions
- Institutional ownership disclosures
- Regulatory filings
- Corporate announcements
- Significant business developments

Allow searches combining several categories.

For example:

"Find profitable mid-cap technology companies with accelerating revenue, manageable debt and improving relative strength."

Translate this into a visible, editable filter query.

Show:
- Matching companies
- Relevant financial metrics
- Why each company qualifies
- Data freshness
- Missing information
- Comparable companies
- Potential risks

### Opportunity Radar

Develop an intelligent opportunity discovery feature.

It should regularly analyse available company data and identify potentially interesting changes.

Examples:
- Earnings acceleration
- Margin improvements
- Valuation compression
- Financial strength improvements
- Unusual price behaviour
- Relative strength changes
- New sector leaders
- Significant fundamental developments

Use transparent, reproducible ranking methods.

Avoid claiming that the system can predict profitable investments.

It should help me find things worth investigating, not pretend to know the future.

## 8. Company Research — Understand a business

Every company should have a comprehensive research page.

The default view should summarise the company clearly.

Include:
- Company overview
- Business segments
- Revenue sources
- Industry and competitors
- Stock performance
- Financial strength
- Growth trends
- Valuation
- Financial statements
- Earnings history
- SEC filings
- Institutional ownership
- Insider activity
- News and events
- Risk factors
- Peer comparison

### Financial statements

Provide historical:
- Income statements
- Balance sheets
- Cash flow statements

Support annual and quarterly periods.

Calculate useful financial ratios automatically.

Provide visual trends and growth comparisons.

Clearly distinguish:
- Reported financial results
- Analyst estimates
- Derived calculations
- AI interpretations

Never confuse reporting periods.

### Company relationships

Explore whether company relationships can improve investment research.

For example:
- Suppliers
- Customers
- Competitors
- Industry exposure
- Revenue concentration
- Shared economic drivers

Only display relationships supported by reliable information.

Do not invent supply-chain connections.

## 9. Markets — Understand the bigger picture

Support research across:
- US equities
- ETFs
- Major global indices
- Government bonds
- Interest rates
- Foreign exchange
- Commodities
- Cryptocurrency
- Macroeconomic indicators

Prioritise useful information rather than comprehensive but poorly maintained coverage.

Include sector comparisons, performance tables, economic trends and market breadth.

Use consistent timestamps and distinguish real-time, delayed and end-of-day data.

## 10. Charts — Professional, but easy

Create excellent interactive charts.

Use TradingView Lightweight Charts or a superior compatible open-source solution.

Support:
- Candlesticks
- Volume
- Multiple timeframes
- Price comparisons
- Moving averages
- RSI
- MACD
- Volatility indicators
- Earnings events
- Trade markers
- Saved chart layouts

Technical indicators should be optional rather than displayed everywhere.

Performance must remain smooth.

Avoid unnecessary animation, large charting dependencies and slow rendering.

## 11. News — Understand why something happened

Create a research-oriented financial news interface.

Support:
- Company-specific news
- Market developments
- Earnings announcements
- SEC filings
- Economic events
- Significant corporate changes

Group duplicate coverage.

Link stories to relevant securities.

Let users ask questions such as:

"Why did this company fall today?"

"What's changed in its business over the last quarter?"

"What are the main risks discussed in its latest annual report?"

Ground answers in dated, attributable sources.

Do not substitute generic AI narratives for verified events.

## 12. Portfolio — Understand my investments

Create a personal portfolio workspace.

Support:
- Manual holdings
- Transaction history
- Cost basis
- Realised P&L
- Unrealised P&L
- GBP and USD
- FX conversion
- Portfolio allocation
- Sector concentration
- Correlations
- Volatility
- Drawdowns
- Benchmark comparison
- Investment notes

Let users ask:

"Am I too concentrated in semiconductors?"

"Which holdings contribute most to my portfolio risk?"

"How has my portfolio performed against the S&P 500?"

"Which holdings have deteriorating fundamentals?"

Support reliable calculation with clear assumptions.

Do not connect a real brokerage account initially.

## 13. Quant Lab — Test investment ideas

Include an accessible strategy research environment.

Possible frameworks:
- pandas
- NumPy
- vectorbt
- Zipline Reloaded
- ML4T Backtest
- Microsoft Qlib

Research the most appropriate combination.

Do not install redundant engines without a clear purpose.

Users should be able to describe a strategy in plain English.

For example:

"Buy profitable semiconductor stocks after a 10% correction when their long-term trend remains positive. Sell after a 20% gain or a specified downside limit."

Translate this into explicit rules.

Show the resulting strategy definition before testing.

Backtests must account for:
- Historical data availability
- Corporate actions
- Look-ahead bias
- Survivorship bias
- Transaction costs
- Slippage
- Position sizing
- Benchmark selection
- Chronological train/test splits
- Out-of-sample performance

Results should include:
- Total return
- CAGR
- Maximum drawdown
- Sharpe ratio
- Win rate
- Profit factor
- Trade history
- Equity curve
- Benchmark comparison

Make backtest results easy to understand.

Explain the assumptions and limitations.

## 14. AI Research — An analyst inside the terminal

Evaluate and integrate:
- TradingAgents
- OpenBB MCP
- Appropriate document retrieval frameworks
- Kronos as an experimental forecasting module
- Microsoft RD-Agent for advanced quantitative research

These should be independent modules.

Use AI for tasks where it adds clear value.

Examples:
- Summarising earnings reports
- Comparing companies
- Building bull and bear theses
- Analysing financial risks
- Searching lengthy filings
- Explaining market developments
- Generating investment research reports
- Translating plain-English questions into structured queries

Do not use expensive AI calls for simple mathematical calculations.

Allow model-provider configuration.

Prefer inexpensive and efficient implementations.

Keep API costs visible.

Do not assume a ChatGPT subscription automatically provides API access.

### AI investment committee

Explore an optional multi-agent workflow.

Possible perspectives:
- Fundamental analyst
- Technical analyst
- Bull researcher
- Bear researcher
- Risk analyst
- Portfolio manager

Produce a single readable research report rather than exposing endless agent conversations.

Display evidence, conclusions, disagreements and uncertainties.

AI-generated investment opinions must never be represented as guaranteed forecasts.

---

# PART 5 — TECHNICAL ARCHITECTURE

## 15. Research and select the best tools

The following projects are starting points, not mandatory dependencies.

Financial data:
- OpenBB
- SEC EDGAR
- EdgarTools
- FRED

Data processing:
- pandas
- NumPy
- DuckDB
- Parquet

Visualisation:
- TradingView Lightweight Charts

Backtesting:
- vectorbt
- Zipline Reloaded
- ML4T Backtest

AI and quantitative research:
- TradingAgents
- Kronos
- Microsoft Qlib
- RD-Agent

Other projects worth evaluating:
- ai-hedge-fund
- daily_stock_analysis
- QuantStats
- PyPortfolioOpt
- Relevant open-source financial screening frameworks

Investigate each project's:
- Maintenance activity
- Technical suitability
- API compatibility
- Licence
- Resource requirements
- Documentation
- Data dependencies
- Ongoing costs

Choose the smallest sensible set that covers the desired capabilities.

Do not install libraries simply because they appeared in the original social media article.

## 16. Preferred application stack

I favour:
- Next.js
- React
- TypeScript
- Tailwind CSS
- Python
- FastAPI
- SQLite
- DuckDB

However, you may change these choices if a clearly superior architecture exists.

The application must run well on macOS.

Prefer local operation.

Avoid cloud infrastructure unless it provides a meaningful capability that cannot be delivered locally.

Do not introduce unnecessary microservices.

Separate incompatible Python environments where required.

Long-running research tasks must not freeze the interface.

Use caching, asynchronous jobs and appropriate background processing.

## 17. Financial data strategy

This is a critical engineering problem.

Research what data is genuinely available without a large recurring cost.

Create a provider matrix documenting:
- Available datasets
- Price
- Rate limits
- Historical coverage
- Data delay
- Licensing restrictions
- Reliability
- Authentication requirements

Prefer official sources for reported financial information.

Use commercial APIs only where their additional value justifies the cost.

Implement provider adapters so data sources can be changed without rewriting the application.

Maintain provenance and freshness metadata.

Handle:
- Missing data
- Incorrect or inconsistent symbols
- Stock splits
- Dividends
- Currency conversion
- Delisted securities
- Restated financial statements
- Reporting-period differences
- Rate limits
- Network failures

Never silently populate missing values with invented information.

## 18. Local storage and search

Use a practical storage design.

Suggested approach:
- SQLite for user settings, watchlists, notes and application data.
- DuckDB and Parquet for analytical financial datasets.
- Full-text indexing for filings and research documents.
- Semantic search only where useful.

Avoid unnecessary infrastructure such as Redis, Elasticsearch or distributed databases unless a clear performance requirement justifies them.

Implement caching and incremental updates.

The goal is a reliable application with minimal maintenance.

## 19. Security

- Store credentials outside source control.
- Use local environment configuration.
- Do not expose API keys in the browser.
- Validate external data.
- Avoid arbitrary code execution from user queries.
- Run autonomous research code in a restricted environment.
- Apply conservative network and file permissions.
- Do not add live trading or brokerage execution without a separate security review.

---

# PART 6 — DESIGN DIRECTION

## 20. Visual identity

Product name: **MarketDesk**

Build a distinctive, modern financial research interface.

It should feel sophisticated, calm, precise and genuinely enjoyable to use.

Avoid copying Bloomberg's dense legacy interface.

Take inspiration from:
- Contemporary financial dashboards
- High-quality professional software
- Modern editorial design
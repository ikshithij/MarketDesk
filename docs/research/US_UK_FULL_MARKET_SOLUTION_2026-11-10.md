# US and UK market screening, then AI research on the top 100

Research and feasibility decision, 10 November 2026. This document specifies the next implementation. Its source probes are implemented and were run live; the full-market ingestion, numerical ranking and 100-company research queue are not yet implemented in MarketDesk. The existing 20-company AI table is not a market-wide shortlist.

## Decision

Use official exchange directories for discovery, keyless structured public financial/price endpoints for an exploratory numerical screen, primary issuer/regulatory disclosures for reconciliation, and the existing authorised online AI researcher for up to 100 shortlisted issuers. Cache the inputs locally and refresh changes. No new financial-data account is required for the routes that succeeded in the probes.

This is a feasible current-market research system. Complete coverage, a licensed real-time exchange feed and an unbiased historical backtest are separate claims that these probes do not establish. Yahoo access is unofficial and can change or be rate-limited. A public URL or library licence does not grant redistribution rights to underlying market data.

## What was actually tested

The reproducible probes and raw downloaded payloads are in `.marketdesk/research-probes/`. Public URLs, status codes, UTC retrieval times, byte counts and SHA-256 hashes are retained. These files are outside the application database and are gitignored. Nothing was inserted into the live ranking table.

| Test | Observed result | What it proves and does not prove |
|---|---|---|
| Nasdaq listed directory | HTTP 200; 5,607 security rows | Public directory access, not 5,607 unique companies |
| Other US exchange directory | HTTP 200; 7,674 security rows | Public coverage beyond Nasdaq; classification still required |
| ETF/test flags removed from both files | 7,460 candidate security rows | Still includes securities needing common/preferred/warrant/unit/ADR/fund classification and issuer deduplication |
| LSE issuer and instrument download metadata | HTTP 200 | Public download discovery works; metadata dates were 1 October and 2 November 2026 |
| LSE downloadable files | HTTP 200; valid ZIP signatures for both XLSX files | Actual files downloaded without sign-in; no claim of parsed issuer completeness yet |
| Aquis static security CSV | HTTP 200; 909 rows, 297 ordinary rows, 292 tradable non-test ordinary rows | Includes securities needing venue/issuer deduplication; not a count of unique UK companies |
| 24 named US/UK ticker requests | 22 returned all 11 requested annual financial fields; JPM and HSBA.L returned 7 and 8 | A deliberately varied small sample, not a random sample or whole-market coverage estimate; availability is not correctness |
| QCOM, SHEL.L, SGE.L, JET2.L history | HTTP 200; 501–506 daily bars each, including adjusted-close arrays and volume | Approximately two years available for these four; no claim of verified corporate-action accounting |
| Recent shares for those four | HTTP 200; latest observations dated 10 November 2026 | More recent than annual share counts; provider observation date is not necessarily issuer disclosure date |
| Valuation measures for those four | Recent vendor market cap, EV and P/E returned | Useful cross-checks; dates and EV definitions must not be silently mixed |
| ECB XML | HTTP 200; reference date 10 November 2026 | Keyless reference FX conversion; not an executable broker exchange rate |
| SEC directory and four company-facts requests | HTTP 403 from this host | SEC is documented as public/keyless, but direct access is presently blocked here; do not promise that adding an email alone resolves it |
| Aquis website page | HTTP 429 | Website scraping is unnecessary when the official static CSV works |

The 24-ticker sample was QCOM, MSFT, NVDA, JPM, XOM, KO, JNJ, CAT, RGR, IRDM, HRL, HD, SHEL.L, SGE.L, JET2.L, AZN.L, RR.L, GAW.L, NXT.L, FEVR.L, W7L.L, CAPD.L, HSBA.L and BNZL.L. These are ticker requests, not a verified current-listing sample. Stored periods and freshness must be assessed before eligibility.

## Sources and their roles

### Listing identities

[Nasdaq's directory definitions](https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs) explain the listed/other-listed formats and flags. Snapshot the files daily, including their creation timestamp. Keep exchange symbols separate from provider symbols and retain raw names and listing history. Directory flags alone do not identify every operating company or resolve multiple share classes.

Use [LSE issuer/instrument reports](https://www.londonstockexchange.com/en/reports/issuers-and-instruments) for London Main Market and AIM discovery, with [Aquis's security list](https://www.aquis.eu/stock-exchange/rules-and-regulations/document-library) for the additional UK venue. Do not substitute FTSE 100 constituents for all UK listings. UK-listed and UK-incorporated are different attributes. US OTC, private companies and non-admitted overseas trading lines must have explicit scope labels rather than being quietly counted as exchange-listed operating companies.

One stable issuer record should map to its securities through CIK, LEI, ISIN, exchange/MIC and verified identifiers. An ADR and its underlying ordinary shares cannot become two independent company candidates. ADR ratios and share classes must be reconciled before price × shares is used.

### Financials, prices and shares

The tested Yahoo financial time-series endpoint returned revenue, gross profit, operating income, net income, operating cash flow, capex, assets, debt, cash plus short-term investments, ordinary share count and equity. This is the route used by [yfinance's financial-statement implementation](https://github.com/ranaroussi/yfinance/blob/main/yfinance/scrapers/fundamentals.py). The library notes that financial history can be limited to four annual years or five quarters. It is not a paid-data entitlement or a service guarantee.

The [shares implementation](https://github.com/ranaroussi/yfinance/blob/main/yfinance/base.py) and [valuation implementation](https://github.com/ranaroussi/yfinance/blob/main/yfinance/scrapers/quote.py) describe additional time-series routes. Raw chart metadata in our tests did not contain market cap or shares, so neither should be assumed available from the price response alone.

Use [SEC company facts and submissions](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) for authoritative US evidence where accessible. SEC supplies nightly bulk archives, avoiding one request per fact. [Fair-access guidance](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data) requires declared identification and moderated requests. An identifying User-Agent is not a data account. Our host's 403 remains an unresolved operational issue; no credential or identity was invented to bypass it.

For UK reconciliation, use issuer annual/interim reports, regulatory announcements and [FCA structured annual reports](https://www.fca.org.uk/markets/filing-structured-annual-financial-reports). Coverage and tagging differ across issuers and markets. The [FCA's October 2026 NSM announcement](https://www.fca.org.uk/markets/primary-markets/regulatory-disclosures/national-storage-mechanism) describes a bulk API as a future MIRA feature, so the design must not assume that API is already available. [Companies House bulk accounts](https://www.gov.uk/guidance/companies-house-data-products) are supplemental; the register also contains private companies and is not a ready-made listed-company fundamentals feed. Parent-only accounts must not replace consolidated issuer accounts.

[ECB reference FX](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) permits consistently labelled research conversion. Store the reference date and derive USD/GBP from the two EUR-base rates. Keep this distinct from Trading 212 conversion fees and execution rates.

### Sources rejected or optional

[StockAnalysis prohibits automated collection](https://stockanalysis.com/terms-of-use/) and says it has [no programmatic data interface](https://stockanalysis.com/help/faq/api-access/). Do not make its visible financial tables the bulk backend.

The public [Defeat Beta dataset](https://huggingface.co/datasets/defeatbeta/yahoo-finance-data) is an optional bulk US research cache. Its metadata downloaded successfully and lists dated files and hashes; its documented layout currently covers US data, not UK. Underlying provenance, definitions, licence scope and currency/action conventions need review before adoption. A community copy is not independent corroboration of the same Yahoo figures. No full financial Parquet download or completeness audit was performed in this research.

[Trading 212 instrument metadata](https://docs.trading212.com/api/instruments/instruments) can verify brokerage availability using the user's existing account and read-only access, if connected later. No new brokerage/data account is necessary, but credentials are still required for that API. The current solution must label availability unverified until it is checked; it must not create orders or request trading permissions.

## Metrics to compute locally

Store original facts once, including provider field, units, currency, fiscal period, publication time if known, first-seen time, ingestion time and source hash. Compute derived metrics in Python rather than asking an LLM to invent them.

| Area | Inputs and calculations | Main limitations |
|---|---|---|
| Business scale | Revenue and current market cap | Share class, ADR ratio, current shares and FX |
| Growth | Revenue/profit year-on-year; multi-year CAGR when sufficient comparable periods exist | Exceptional items, acquisitions and short history |
| Profitability | Gross, operating and net margins | Financial-sector gross profit is not comparable |
| Cash generation | Operating cash flow, capex, FCF, cash conversion | Normalize capex sign and distinguish PPE from intangibles/acquisitions |
| Financial strength | Debt, cash, net debt, equity; leverage ratios with supported definitions | Debt must be interest-bearing with explicit lease treatment; cash plus investments is not identical to cash equivalents |
| Valuation | FCF/equity value, operating income/EV, earnings multiple, price/book where meaningful | Negative/near-zero denominators and provider EV conventions |
| Registered quality inputs | Gross profit / average assets; OCF / average assets; negative accruals `(OCF − NI)/average assets` | Both asset observations and exact comparable annual periods required |
| Trend/context | 252-to-21-session total-return momentum, 200-session average, volatility and drawdown | Confirm adjusted-series dividend/split semantics before calling it documented total return |
| Tradeability | 60-session median daily traded value in GBP | Raw price × raw volume, GBP conversion, completed sessions and venue aggregation |
| Evidence quality | Field completeness, fact ages, contradictions and source traceability | Keep separate from return probabilities |

Observed traps include Shell's GBp quote versus USD accounts; Sage's annual share count versus a much newer provider share series; negative capex amounts in the sampled Yahoo field; nominal currency metadata attached to share-count fields; and provider month-end labels that need not equal an issuer's exact fiscal closing day. Do not fix these by blindly applying absolute values, changing dates or treating missing balance-sheet items as zero.

## The numerical screen and top-100 queue

1. Discover all securities in the declared US/UK venues. Retain excluded/unmapped rows with reasons. Coverage counts must distinguish discovered securities, unique issuers, mapped quotes, complete fundamentals, numerically screened issuers and AI-reviewed candidates.
2. Resolve operating ordinary shares and one eligible listing per issuer. Preserve separate country-of-listing, incorporation, sector and currency attributes. Flag banks, insurers and property investment companies outside the initial accounting model.
3. Apply the existing £1bn market-cap and £5m median daily traded-value gates, 60-session liquidity window, 450-day annual fiscal-end age and 150-day shares age. Require current price/FX context. The age of a provider observation is not proof of original disclosure freshness.
4. For a **qualified LT-QV-001 run**, use the exact registered formula and all its prerequisites: three country/sector quality percentiles and two value percentiles, equally weighted within each group, then 50% quality plus 50% value. Require at least 20 eligible peers per group. EV includes the registered debt/preferred/noncontrolling/cash components. No missing metric becomes zero and no unknown preferred/noncontrolling balance is assumed absent.
5. A provider EV or unverified adjusted series can support a labelled exploratory discovery view, but cannot silently satisfy those registered definitions. Any broader preliminary formula must receive its own sandbox ID and frozen specification before use. Do not relabel our existing AI 0–5 ratings as this numerical screen.
6. Freeze a dated candidate manifest. Select up to the top 100 eligible issuers for long-term AI due diligence, within this one ranking family and with the existing entry-percentile condition. Do not combine earnings, reversal, momentum and quality-value units into a new unspecified score. Do not force a 50/50 country allocation or pad the list to 100 if only fewer qualify.
7. Reconcile shortlisted numerical inputs against primary reports first. If a company fails or its rank changes, retain the original screen and create a new verified manifest; refill from the next candidate with an audit trail. A provisional discovery candidate and a fully eligible candidate are distinct states.
8. Run the existing online AI dossier and separate versioned opinion rubric on the confirmed queue. Publish completed reports progressively. Use a durable queue with idempotent `(issuer, cohort, prompt, evidence hash)` keys, retries/backoff, interruption recovery and account-usage limits. The current three-request dossier cap needs a queue coordinator; the existing code cannot yet orchestrate 100 full dossiers simply by accepting a list.

The 100-company queue is a research workload limit, not a 100-position portfolio or a new return target. Monthly registered rebalancing remains unchanged; daily data refresh and monitoring do not redefine it. Enlarging coverage creates a new dated cohort under the user's explicit request, not an inherited backtest track record.

## What AI does for those 100

Read actual annual/interim results and dated news. Check exceptional profit items, cash conversion, debt maturity, dilution, customer concentration, management execution and thesis-breaking risks. Reconcile the source periods, valuation inputs and conflicting documents. Produce the detailed nine-section report plus the separate cited ratings already implemented. Keep quantitative rank, subjective AI view, evidence coverage and unvalidated forecast confidence in distinct columns.

Reuse the user's existing authorised AI access. Refresh a dossier for new filings, material news, expired evidence or an explicit user request, rather than rewriting all 100 reports every morning. A full initial pass will be a background workload; no duration or token-cost guarantee is inferred from the small probes. One failed company must not invalidate the rest of the queue.

## Refresh, storage and acceptance

Keep raw downloads immutable and indexed in SQLite, matching the current app. Use explicit typed observations and feature snapshots; add partitioned Parquet/DuckDB only if bulk-data scale warrants it. Start with conservative provider pacing, honour 429/Retry-After, checkpoint work and never rotate identities to evade restrictions. Refresh directories daily, prices after the relevant regular session, financials on new releases plus periodic staleness checks, and primary-document evidence on shortlist entry or changes. Cache parsed documents and calculations.

Before publishing a full-market top 100, require a coverage report for each venue, a classified/deduplicated universe, whole-universe metric completeness by country/sector, checked unit/period/share/FX handling, per-candidate eligibility reasons, exact reproducible scores, verified source links, a frozen 100-or-fewer manifest and a restart-safe AI queue. Sample-test large, small, overseas, dual-listed, loss-making and excluded financial firms. Source-probe success alone does not meet these acceptance conditions.

The next implementation should therefore produce a searchable all-market coverage table first, a reproducible numerical shortlist second, and the AI review queue third. Current limitations are visible data gaps and source access, not the Mac's ability to calculate thousands of rows. No calibrated probability, profitable alpha or completed deployment is asserted by this research.

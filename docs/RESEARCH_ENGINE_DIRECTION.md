# MarketDesk: evidence, experiments and a simple morning decision

Direction captured 10 November 2026 from the user's revised brief. This supersedes dashboard breadth as the product priority; it does not claim the proposed engine is already implemented.

## User constraints

- No new financial-data accounts. Existing AI access is acceptable.
- Online research and AI reasoning; a disconnected offline calculator is insufficient.
- Local Mac compute initially; an always-running home server later.
- UK user, Trading 212, regular trading hours only. Assume long-only Invest/ISA securities, no leverage or shorting unless the user changes that scope.
- Preserve and substantially improve Quant Lab. The rest of the interface should be much simpler.
- Daily concise ranked research, separating long-term ownership from short-term opportunities, with evidence and measured confidence.
- No premise that a stock is destined to rise, including strong companies through crises.

## Research findings and implications

### What comparable projects do

[Qlib](https://github.com/microsoft/qlib) provides model/data/backtest research workflows. [TradingAgents](https://github.com/TauricResearch/TradingAgents) uses specialist LLM roles and debate. [RD-Agent](https://github.com/microsoft/RD-Agent) automates research and development experiments. These are useful engineering patterns, not proof that their outputs will beat a benchmark net of this user's execution costs. Do not install multiple overlapping stacks merely to imitate their feature lists.

### Failure mechanisms worth designing around

1. **Selection among many experiments.** A search that tries enough equations can produce an impressive winner by luck. Record every model, parameter choice, universe and failed experiment. Use multiple-testing-aware evaluation, including Deflated Sharpe where its assumptions apply; do not treat it as a probability that a particular stock will rise. Source: [Bailey and López de Prado, Deflated Sharpe Ratio](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf).
2. **Publication and regime decay.** McLean and Pontiff examined 97 published predictors and reported average portfolio returns declining out of sample and further after publication. That is evidence against copying a paper's original headline performance, not evidence that no strategy can work. Source: [Journal of Finance](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12365).
3. **Temporal leakage.** Later financial restatements, today's surviving constituents and news first seen after the decision cannot be used in a historical decision. Modern LLMs may also remember later events even when prompted to act as of an old date. Source: [Scaling Point-in-Time Language Models, NBER working paper](https://www.nber.org/papers/w35247). Historical LLM-generated narratives are exploratory unless model/data timing can be defended; prospective evaluation is essential.
4. **Untradeable profits.** A headline may arrive after close and the stock may gap before the user can buy. Backtests must enter at the next eligible regular-session price after data retrieval, processing and an explicit reaction delay. Historical close, last trade and executable ask are different observations.
5. **Turnover and costs.** Small gross advantages can disappear after spreads, slippage, FX conversion and applicable purchase taxes. Source: [Novy-Marx and Velikov](https://www.nber.org/papers/w20721). Test costs and sensitivity, including no-fill conditions for limit orders.
6. **Confusing quality with cheapness.** Research supports studying profitability, growth, safety and valuation together. The AQR quality study is a portfolio/long-short finding; it is not a guarantee for an individual long-only investment. Source: [Quality Minus Junk](https://www.aqr.com/Insights/Research/Working-paper/Quality-minus-Junk).
7. **Narrative certainty.** Agent agreement, a compelling CEO story and a numerical company score are not calibrated probabilities. Extract claims with evidence, retain contradictions and require observed predictive results before numerical forecast confidence.
8. **Incomplete public histories.** Searchable public pages do not automatically provide reproducible point-in-time datasets, delisted securities, historical estimates, clean corporate actions or executable quotes. Mark affected experiments ineligible for strong performance claims rather than silently assuming those gaps away.

## Product: three primary views

**Today**: a short report with distinct long-term and short-term lists, material changes, reasons to wait, and the next eligible UK-local execution time. No requirement to generate a buy every day. Each item has a short explanation, main contrary evidence, forecast horizon, evidence links, model validation state and a price/expiry condition. Show only a handful of candidates.

**Companies**: one search box and a business dossier. Start with how the company makes money, cash-flow quality, competitive position, valuation assumptions, risks and what changed. Put the price chart, statements and filings behind secondary detail. A saved company is a research object, not a new dashboard.

**Quant Lab**: describe an idea, inspect its explicit rules, test it and see the complete experiment history. Separate exploration, locked historical validation and prospective paper results. It is the place where AI earns or loses trust. Research notebooks and model health live here as supporting views.

Hide provider mechanics and storage administration from the normal workflow. Public data access should be automatic where permitted. Sources and freshness remain easy to inspect. Portfolio context may be added without recreating a full brokerage interface.

## Separate horizons and questions

Initial proposed horizons (defaults, not user-confirmed investment mandates): long term 3–5 years; short term 5–20 trading sessions. Avoid subsecond/minute trading with public feeds and manual execution.

### Long-term company ownership

Study cash generation per diluted share, cash conversion, accruals, reinvestment returns, capital requirements, debt maturity/liquidity, dilution, customer concentration, competition and sector-specific demand. Treat ROIC/owner-earnings estimates as accounting-sensitive derived measures with definitions and missingness, not universally comparable facts.

Use explicit bear/base/bull cash-flow and valuation assumptions and reverse valuation: what business performance does today's price already require? A plausible business thesis is separate from an investable price. Test quality/value composites across sectors and multiple regimes, including crisis drawdown and recovery; do not optimise for hindsight-selected crisis survivors.

### Short-term opportunities

Begin with a small registered set of momentum, reversal and event-drift hypotheses. Study event novelty, volume/liquidity, volatility, earnings timing and regime. Analyst-surprise features require timestamped consensus data; omit them if unavailable. A reported increase is not automatically an earnings surprise.

Separate news verification from sentiment. Founder/CEO claims need dated original evidence, entity resolution, event deduplication and a plausible economic mechanism. Several articles repeating one release are one event, not independent corroboration.

## Storage: preserve what was knowable

SQLite owns configuration, tasks, experiments and reports. Append-only raw files plus Parquet/DuckDB support larger analytical histories as needed. The database must preserve availability time, not simply store more columns.

Proposed records:

- security: stable identifier, ticker/exchange/currency history, listing/delisting, Trading 212 availability and last verification;
- observation: metric/value/unit, period start/end, source document, publication timestamp, first-seen timestamp, ingestion timestamp, revision and quality flags;
- document: URL/publisher, source hash, publication and first-seen times, retrieved text, passage offsets, permitted retention metadata;
- event: company/entity, event category, effective/publication/first-seen time, original evidence and duplicate cluster;
- feature snapshot: as-of cutoff, availability rules, expression/version and source observation IDs;
- experiment: economic hypothesis, typed formula/rules, universe snapshot, cost/session policy, parameters, data hash, code/model/prompt version, search-family ID and status;
- prediction: immutable issued-at time, horizon, eligible entry window, benchmark, distribution/probability if validated, conditions and abstention reason;
- outcome: executable-entry assumptions, gross/net GBP returns, benchmark result, drawdown, completion and missing-data state;
- report: immutable decision cutoff, ranked candidates, evidence, changes since prior report and delivery state.

Store public reporting publication time separately from first-seen time. For a live system, data was not usable before it was actually received. Historical datasets need a documented availability approximation and cannot inherit a fabricated first-seen timestamp.

## AI's role and execution boundary

AI searches online sources, extracts cited facts, proposes economically motivated hypotheses and typed equations, reviews contradictions, and writes a short report. Deterministic services perform calculations and validation. A generated score is not the model's confidence.

Start with a restricted typed expression language: rolling operations, lags, arithmetic, comparisons and named indicators. Check units, horizon, availability and missingness. Let genuinely new methods graduate into isolated versioned Python workers, with resource limits, read-only data and no access to broker credentials or model secrets. Do not run arbitrary model-written Python in the main API process.

Existing authorised AI access may be sufficient through a supported integration. Current [official OpenAI guidance](https://developers.openai.com/siwc/token-sharing-open-source) documents eligible plan usage for open-source/local apps and self-hosted environments; eligibility, limits and any server migration must be verified. This is not implemented and must not be replaced by copying session cookies or assuming the app can reuse the current chat's tools.

## Public data and account policy

[SEC's read APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) require no account or API key. Automated access still needs a compliant application identity and conservative fair-access behaviour; do not invent a contact email. Public issuer investor-relations releases/filings provide primary evidence. Yahoo's public feed is useful for a first personal price history but is unofficial and cannot guarantee clean long-range/intraday coverage. [GDELT](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) can support news discovery; retrieve and attribute original reports where access permits. [Kenneth French's library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) supplies research factor/portfolio benchmarks, not a historical tradable security master.

Google is a discovery aid, not an observation database or a substitute for original sources. Do not scrape search snippets into purportedly complete financial data. A no-new-data-accounts first version is feasible; an institution-complete global point-in-time dataset is not established by these sources. Exclude unsupported experiments rather than adding a paid-data registration requirement silently.

## UK and Trading 212 execution

- Enforce the user's regular-hours-only policy even though [Trading 212 offers extended hours for eligible instruments](https://helpcentre.trading212.com/hc/en-us/articles/13574400364445-24-5-Trading-Invest-Stocks-ISA).
- US regular equity hours are 09:30–16:00 America/New_York, normally 14:30–21:00 UK time, with temporary 13:30–20:00 UK sessions when daylight-saving changes differ. LSE normal continuous hours are 08:00–16:30 Europe/London. Use actual exchange calendars/holidays/early closes, never hard-coded UTC offsets. Sources: [NYSE](https://www.nyse.com/trade/hours-calendars), [LSE](https://www.londonstockexchange.com/en/resources/faqs/personal-investing).
- Proposed delivery is 07:30 Europe/London, before LSE opens, plus a short refresh shortly before the next US open. These are product defaults, not an automation scheduled in this chat. A morning US candidate expires or is re-evaluated if new information or a price gap invalidates its thesis before entry.
- Match each instrument/listing/currency against public broker availability; do not assume every Yahoo ticker or US ETF is buyable in the user's account. Availability can differ by account/entity. Do not connect the broker or submit orders.
- [Trading 212 FX conversion](https://helpcentre.trading212.com/hc/en-us/articles/360018909758-What-is-the-FX-fee-Invest-Stocks-ISA) is currently 0.15% when conversion occurs. Model actual conversion events; do not double-charge if currency is retained in an eligible account.
- Include applicable [issuer/exchange taxes and charges](https://helpcentre.trading212.com/hc/en-us/articles/11471996799517-What-are-the-fees-in-the-Invest-ISAs-and-SIPP), notably UK SDRT on eligible purchases (generally 0.5%, with exemptions). Account type, instrument and order review determine actual charges; do not treat every LSE security identically.
- Express realised/prospective outcomes in GBP as well as security currency. Separate FX market exposure from conversion fees. Tax-wrapper capital-gains treatment depends on account type and is not assumed.

## Confidence: what can honestly be promised

Current prototype: no validated predictive edge. Existing tests prove implementation invariants, not investment success. Its one-security SMA backtest is exploratory, not historical validation of this proposed engine.

High engineering confidence: an auditable research/data pipeline, deterministic calculations, source-linked summaries and a reproducible experiment history can be built. Evidence extraction still needs cross-checks and coverage reporting. Moderate research confidence: useful business-quality/valuation comparisons can be produced from sufficiently complete sources. Unknown investment performance: profitable after-cost short-term selection or persistent benchmark outperformance cannot be promised before validation. No defensible win-rate percentage is available today.

Separate these report fields:

1. Evidence quality: source reliability, recency, coverage and contradictions; a documented rubric, not a price probability.
2. Model validation: exploratory / historically validated / prospective paper results / suspended.
3. Business thesis: scenario assumptions, supporting and contrary evidence, invalidation conditions.
4. Forecast, only if earned: an explicit target event, eligible entry, horizon, benchmark, net costs and base rate. Show calibration and an uncertainty interval where supportable. Otherwise display insufficient evidence.

An example of a measurable short-term target is outperformance of the nominated benchmark over the next 20 trading sessions, net of the user's costs, measured from the first permitted entry after the decision. This differs from merely ending above today's price. A score of 80/100 must never be displayed as an 80% probability of success.

A future 60% probability label is justified only if similar out-of-sample probability buckets actually realise around that frequency, with adequate effective sample size and stable calibration. Evaluate Brier/log loss and reliability against a relevant base-rate forecast. Return magnitude, tail loss and net expected utility also matter; hit rate alone can conceal a losing strategy. Overlapping horizons, sector-correlated stocks and shared events reduce independence. Time-block/event-aware resampling and uncertainty are required; hundreds of correlated signals are not hundreds of independent trials.

## Validation gates before ranked investment signals

1. Verify price/corporate-action histories and point-in-time statement availability. Treat periods with unavailable delisted/history data as limited-universe studies, not survivorship-free tests.
2. Register benchmark, target horizon, cost assumptions, candidate families and data cutoffs before testing. Begin with simple published factor baselines and transparent equations; permit complex models only when they improve locked tests.
3. Use nested chronological train/selection/calibration/test blocks; purge/embargo overlapping labels where appropriate. Do not repeatedly tune on the final holdout.
4. Record all search trials; evaluate selection-adjusted results, parameter sensitivity, sector/regime concentration and higher-cost scenarios. Compare to buy-and-hold, cash and simple quality/value/momentum baselines in the same currency and universe. Separate broad market/factor exposure from incremental selection value.
5. Shadow-run immutable predictions prospectively before introducing confidence labels. A short paper period tests operations but cannot establish multi-year robustness; the required evidence depends on horizon, effect size and independent observations, not a fixed promotional number of days.
6. Calibrate probabilities on data separate from model selection; evaluate the frozen policy on unseen/prospective outcomes. Abstain on data gaps, weak validation, changed regimes and infeasible entry prices.
7. Preserve old predictions/reports and score every result, including delisted/unavailable outcomes. Suspend a model when calibration/cost/data gates fail. Do not silently replace it while keeping the old track record.

## Implementation order

1. Simplify the workspace to Today / Companies / Quant Lab and display current validation state honestly.
2. Build dated evidence storage and original-document retrieval for a constrained liquid US/UK universe accessible through Trading 212; no new data accounts.
3. Make Quant Lab a registered experiment system with executable sessions/costs, point-in-time features and frozen validation.
4. Connect existing authorised online AI to research/extraction/typed hypotheses, with limits and failure recovery.
5. Generate a short morning research report and a permanent prediction/outcome ledger; do not enable automated trading.
6. Move the same worker/queue/storage lifecycle to the home server once its environment is specified. Add model monitoring and only then introduce empirically calibrated forecast probabilities.

Acceptance for the first engine release is reproducible, dated, source-backed research with clear abstention and a verifiable experiment ledger. Consistent profitable prediction is an empirical question for that engine to test, not an acceptance result that can be asserted during implementation.

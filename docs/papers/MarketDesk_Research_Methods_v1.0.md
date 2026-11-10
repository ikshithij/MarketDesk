# MarketDesk Research Methods and Strategy Standard

Evidence review and reproducible operating protocol for a UK investor using Trading 212

Version 1.0 | 10 November 2026 | Prepared for the MarketDesk project owner

## Abstract

MarketDesk should prioritise a small set of reproducible investment experiments over a large collection of dashboards or freely generated AI recommendations. This paper reviews established strategy families, recent public evidence of institutional use, and the practical constraints of a UK investor trading ordinary shares during regular market hours. Quality combined with valuation, cross sectional momentum, and a long only trend overlay form the initial baseline. Earnings drift and short term reversal remain conditional research candidates. Machine learning and language models support research and later challenger models; their outputs do not establish investment skill without independent evaluation.

The proposed system preserves the information available at each decision, registers all experiments, models realistic execution and costs, and records predictions before outcomes are known. It separates evidence quality, business analysis and empirically calibrated forecast confidence. No MarketDesk strategy has yet demonstrated a validated predictive edge. The thresholds and equations in this paper are frozen initial research rules, not optimised parameters or demonstrated trading recommendations. The accompanying operating standard and machine readable registry make this methodology persistent across future conversations.

## 1 Purpose and interpretation

This paper answers three questions: which strategy families deserve implementation, how MarketDesk should investigate them, and what prevents its methodology drifting between conversations. The intended result is a useful morning research service with a simple Today, Companies and Quant Lab interface. The computation can run on the user's Mac and later a home server. Financial sources should not require new accounts; existing authorised AI access is acceptable. Broker execution remains manual.

Successful has several meanings. A published historical result demonstrates behaviour in a particular sample under particular assumptions. An implemented institutional strategy demonstrates adoption. An audited live track record demonstrates results for a particular manager, mandate and period. None automatically establishes that a new long only retail implementation will beat its own benchmark after costs. This review therefore avoids ranking strategies by incomparable advertised annual returns. It does not audit proprietary fund positions or reproduce the cited studies.

The evidence cut off is 10 November 2026. Current practice is documented using public manager and index provider material available by that date. Such material is useful for establishing what firms say they use, but is commercially interested evidence. Academic findings are distinguished from our proposed adaptations. No user account type, capital amount or personal risk tolerance has been supplied; the standard assumes long only Invest or Stocks ISA securities and tests hypothetical portfolios, rather than prescribing allocation of the user's money.

The prior master brief remains historical context. For future development, docs/RESEARCH_STANDARD.md and research/standard_v1.json are the normative baseline. This paper explains that baseline. Conflicts must be recorded and resolved explicitly rather than allowing whichever chat is newest to silently redefine the project.

## 2 What is used in systematic investing today

AQR's current systematic equities description includes measurable profitability, momentum, risk and sentiment characteristics, together with machine learning and natural language processing. This supports building a combined quantitative and document research workflow; it does not reveal proprietary formulas or establish a net return target for MarketDesk. [1]

Invesco's October 2026 factor review identifies value, size, momentum, volatility and quality as recurring equity strategy families. These are useful comparison categories rather than five independent opportunities: exposures can overlap, and their behaviour depends on construction and market conditions. [2]

FTSE Russell's November 2026 quality research warns that unconstrained quality portfolios have become more exposed to profitable technology businesses and that quality is not automatically defensive. For MarketDesk, sector concentration must be inspected before interpreting a quality ranking as business resilience. [3]

Public platforms also show the engineering direction. Qlib supplies data and model research workflows; RD Agent automates experiments; TradingAgents organises specialist language model roles. We can adopt reproducibility and evidence review without installing three overlapping orchestration stacks. An AI debate is a method of generating and criticising hypotheses, not an observed probability of a profitable trade. [4–6]

### Strategy selection matrix

| Strategy family | Evidence relevant to selection | Decision for MarketDesk |
|---|---|---|
| Quality and valuation | Established profitability and quality literature; continuing systematic use | Initial long term baseline LT QV 001 |
| Cross sectional momentum | Published intermediate horizon return persistence | Initial comparison baseline EQ MOM 001 |
| Time series trend | Long historical research, often diversified and long short | Restricted long only overlay TR 001 |
| Earnings drift | Historic underreaction evidence with recent execution and efficiency concerns | Conditional experiment ST EARN 001 |
| Short term reversal | Plausible liquidity provision mechanism with high implementation sensitivity | Exploratory experiment ST REV 001 |
| Machine learning ranking | Published nonlinear prediction results in particular datasets | Stage two challenger ML 001 |
| Pairs and statistical arbitrage | Relative value research often requiring both long and short positions | Excluded from initial long only mandate |
| High frequency and options carry | Different data, execution, leverage and tail risk requirements | Excluded from initial scope |

## 3 Evidence and failure modes

### Quality valuation and business ownership

The Quality Minus Junk research studies profitability, growth, safety and payout characteristics across diversified portfolios. Its long short evidence motivates studying business quality, but cannot be imported as a promised return for a concentrated long only shortlist. MarketDesk will evaluate valuation separately and compare the combined policy with quality alone and value alone. [7]

Buffett's Alpha associates Berkshire's historical results with inexpensive, safer, high quality shares and persistent leverage. That decomposition is relevant to the user's emphasis on companies, but Berkshire's financing, private businesses, scale and mandate differ from a retail account. MarketDesk will investigate quality and price without attempting to reproduce its leverage. [8]

A sound business need not have a rising share price through every crisis. Valuation compression, financing needs, sector exposure and changes in expected growth can overwhelm current profitability. The long term engine must ask what performance the current price already assumes, what could undermine cash generation and how the investment behaves under adverse scenarios.

### Momentum and trend

Jegadeesh and Titman's foundational study reports return persistence over intermediate holding periods using winner and loser portfolios. This supports an independently specified momentum baseline, not the assumption that a recent intraday rise predicts tomorrow. Our 12 month signal excluding the latest month is a conventional research adaptation whose exact implementation will be tested separately. [9]

A Century of Evidence on Trend Following studies diversified time series momentum across markets and long histories. Its construction includes opportunities unavailable in a long only share account. A single ETF switching between long and cash is a deliberately narrower experiment and must be judged against that ETF's own buy and hold outcome. [10]

Momentum can reverse sharply; trend filters can repeatedly buy and sell in sideways markets. A model that improves one drawdown may miss a rapid recovery. We will report turnover, time in cash and benchmark opportunity cost instead of describing an overlay as crisis protection by definition.

### Earnings and news

Historical earnings research supports investigating delayed responses, while attention and liquidity research offers possible explanations. This establishes a hypothesis rather than a universal current effect. [11] A 2026 study of earnings price jumps reports evidence consistent with efficient post announcement price formation after 2016 in its setting. This directly argues against assuming an old earnings drift result remains capturable after the next market opening. [12]

MarketDesk will distinguish seasonal earnings improvement from a surprise relative to analyst consensus. Public filings usually supply reported results, not a timestamped historical consensus series. If the consensus dataset is unavailable, the model must use a separately named seasonal expectation rule and disclose the difference. CEO or founder stories require entity checks, original dated evidence and a mechanism affecting the business; repeated coverage of one release is not several independent events.

### Why promising results often disappoint

McLean and Pontiff study 97 published predictors and report lower returns outside original samples and after publication. Their results support scepticism about transporting historical headline performance into a new implementation. They do not establish that all predictability disappears. [13]

The Deflated Sharpe Ratio corrects for selection effects and non normal returns under its assumptions. It addresses strategy evaluation after a search, not the likelihood that an individual stock will rise. We will preserve trial counts and correlated model families so that a selected result can be interpreted honestly. [14]

Trading costs matter especially when a strategy turns over quickly. Novy Marx and Velikov study anomalies and cost mitigation, including distinctions between entering and continuing to hold a position. This motivates the entry and retention buffers in our proposed monthly strategies. [15]

Financial backtests can leak later restatements, future constituents and subsequently revised macroeconomic values into earlier decisions. Language models add memory of later company events. Research on point in time language models demonstrates why a historical date in a prompt is not a sufficient chronological boundary. Historical language model forecasts will remain exploratory unless temporal validity can be defended; prospective predictions are the primary test of the online researcher. [16]

## 4 Fixed scope and common definitions

### Universe and liquidity

The first universe contains verified ordinary US and UK equities available to the user through Trading 212. Instruments are identified by issuer, listing, exchange, currency and a stable identifier where available. Ticker history and delistings must be preserved. A public broker list can indicate availability, but account specific eligibility remains to be checked. Different listings and ADRs of the same issuer must not be counted as independent company exposures.

The initial research eligibility rules are a market capitalisation of at least GBP 1 billion equivalent and a median daily traded value of at least GBP 5 million equivalent over the preceding 60 sessions. These are conservative project defaults, not empirical discoveries. FX and GBp versus GBP units must be normalised before either test. Historical eligibility uses information available then, never today's market capitalisation. Missing eligibility data makes an instrument ineligible for that experiment.

Banks, insurers and property investment companies are excluded from the first accounting factor cohort because their balance sheets and cash flows require different definitions. Their exclusion is a scope limitation, not a judgement of investment quality. A separate sector methodology would require a new registered cohort.

### Time horizons and prices

Long term company scenarios cover three to five years. The initial measurable equity factor outcome is 12 month benchmark relative total return; that outcome is not a calibrated three year company forecast. Short term primary outcomes use 20 trading sessions for earnings events and five sessions for reversal. Momentum and trend have their own rebalance and holding rules. Results across these horizons must not be pooled into one win rate.

Feature returns use documented total return series where available. Execution uses tradable raw prices plus a separate split and dividend ledger. Never execute a position at an adjusted historical price and also credit the same dividend again. A price history without verified actions may support exploratory charts, but cannot establish validated strategy performance.

### Financial observations and ranking

Version 1 uses exact annual reported periods for the accounting baseline, with a maximum fiscal end age of 450 days. This avoids silently mixing annual, quarterly and cumulative year to date flows. Quarterly changes are retained for the company dossier. A future trailing four quarter model must prove its period reconstruction and receive its own strategy version.

Ratios use the reporting currency consistently. Market capitalisation uses the latest publicly available outstanding share count, adjusted for known subsequent splits, with an observation age limit of 150 days. Annual diluted average shares are not an interchangeable substitute for shares outstanding at a valuation date. Missing denominators, negative denominators that invalidate a ratio, and currency inconsistencies are not replaced with zero.

Accounting signals are converted to percentile ranks within a country and sector comparison group containing at least 20 eligible issuers. Higher percentile means more attractive under the named rule. Tied values receive the average rank. Groups with fewer observations remain unranked; no broad market fallback is silently substituted. This requirement may substantially reduce a small public data universe and is part of the feasibility gate.

## 5 Registered baseline strategies

The following rules are MarketDesk proposals. Their thresholds, weights and horizons are chosen before evaluation to create a reproducible starting point. They are not quoted optimal settings from the cited papers. All are initially registered but not implemented or validated.

### LT QV 001 Quality at a reasonable valuation

For each eligible operating company, compute annual gross profit divided by average assets, operating cash flow divided by average assets, and the negative of accruals defined as net income less operating cash flow divided by average assets. Average assets means the average of opening and closing annual assets. All three observations are required. Quality Q is the arithmetic mean of their country sector percentile ranks.

Value V is the mean of free cash flow yield and operating earnings yield ranks. Free cash flow is operating cash flow less cash purchases of property plant and equipment. The first yield divides this by current market capitalisation; the second divides operating income by enterprise value. Enterprise value is market capitalisation plus interest bearing debt and preferred capital plus non controlling interests minus cash and cash equivalents. Every component must be available and definitions comparable; missing components are not assumed zero. Nonpositive enterprise value makes that yield ineligible.

The score gives equal weight to quality and value. All required submetrics must exist. Positive annual net income and positive operating cash flow are absolute eligibility requirements. The portfolio enters the top quintile, retains holdings while they remain in the top two quintiles and rebalances monthly. Buffers reduce avoidable trading; they do not prove an improvement in advance.

$$S_{QV}=0.5Q+0.5V$$

Use 20 equal target slots with a maximum starting position of five percent and sector exposure of 25 percent. Unfilled slots remain cash; existing holdings are not automatically enlarged to consume them. Caps apply at rebalancing, not as a claim that daily price movement cannot breach them. Candidate ties are broken by stable instrument ID. The primary comparison is against the same country's predeclared broad equity benchmark and a simple equal weight eligible universe portfolio, with matched currency and cost treatment.

Separately, the AI dossier examines cash flow durability, reinvestment, competitive threats, dilution, governance and customer concentration. A reverse valuation and bear base bull scenarios state what growth and cash conversion would justify the current price. These scenarios are sensitivity analyses, not assigned likelihoods. For an operating business, the enterprise valuation engine uses free cash flow to the firm, defined as operating earnings after an explicit tax assumption plus depreciation and amortisation less capital expenditure and the change in noncash working capital. It discounts these flows at the cost of capital, then subtracts net financing claims to obtain equity value; it must not discount equity cash flow at an enterprise discount rate.

$$EV=\sum_{s=1}^{T}\frac{FCFF_s}{(1+w)^s}+\frac{FCFF_T(1+g)}{(w-g)(1+w)^T}$$

For a five year reverse valuation, solve for the near term cash flow growth needed to match the observed enterprise value under each cost of capital of 8, 10 and 12 percent and terminal growth of 0 and 2 percent. These six cases are fixed sensitivity assumptions, not estimated probabilities or universal fair discount rates. Require w greater than g, and report unavailable if the starting cash flow or financing bridge cannot be defended. Record taxes, working capital, reinvestment and terminal assumptions. A separate business scenario can explain why an implied growth rate appears demanding; it cannot relabel that judgement as a calibrated return forecast. Unsupported estimates of maintenance capital expenditure or a durable moat must be labelled judgement. AI narrative cannot secretly change the tested ranking.

### EQ MOM 001 Intermediate momentum

Rank eligible equities within each country by total return from 252 sessions before the decision to 21 sessions before it. The latest month is excluded from the signal. Daily total return observations and action histories must be sufficient; the rule does not infer historical winners from current constituents.

$$M_t=\frac{TR_{t-21}}{TR_{t-252}}-1$$

Enter the top quintile, retain holdings while they remain in the top two quintiles, and rebalance monthly with the same 20 slots and concentration limits as LT QV 001. Record this as a distinct strategy, rather than adding it to the quality value score whenever it makes a chart look better. A combined model needs its own registered ID and evaluation. Primary outcomes are net portfolio returns, benchmark relative returns, turnover and drawdown over complete evaluation periods; 20 day labels may be reported only as secondary diagnostics.

### TR 001 Long only trend overlay

For one predeclared, eligible unleveraged broad equity UCITS ETF, hold the ETF when its latest completed close is above its 200 session simple moving average; otherwise hold cash. The nominated instrument and listing are frozen before testing. A different index, ETF or averaging window is a different trial. The signal is computed after the session and executed at the next permitted regular session opening after the decision is ready.

$$a_t=\mathbf{1}\left(P_t>\frac{1}{200}\sum_{j=0}^{199}P_{t-j}\right)$$

Use a verified cash return series if available and a disclosed zero cash return sensitivity otherwise. Compare against buy and hold of the same ETF; also report average equity exposure so lower risk caused by holding less equity is not misdescribed as stock selection skill. Fund expenses already embedded in ETF prices must not be deducted twice. No short futures, leverage or claim of reproducing a diversified managed futures strategy is permitted.

### ST EARN 001 Seasonal earnings drift

This conditional experiment uses public earnings releases and filings. Define a seasonal earnings change as reported comparable EPS this quarter less reported comparable EPS four quarters earlier. Divide that change by the sample standard deviation of the preceding eight seasonal changes, excluding the current one. At least 13 comparable quarters are required. Split adjustments, share classes and GAAP versus adjusted EPS must be consistent; a zero or unavailable standard deviation makes the signal unavailable.

$$U_q=\frac{EPS_q-EPS_{q-4}}{s\left(\Delta EPS_{q-1},\ldots,\Delta EPS_{q-8}\right)}$$

A candidate requires U of at least one and positive year on year quarterly revenue growth. This is a seasonal expectation signal, not analyst consensus surprise. Buy at the next full regular session opening after the event becomes usable under section 7, then hold for 20 sessions. Multiple earnings events from one issuer do not create overlapping duplicate positions. The first test uses no tuned stop loss or profit target. Corporate events and early forced exits are handled through the action ledger.

The publication timestamp and actual first seen timestamp are compulsory. If only a filing date is available, the event study is exploratory and cannot claim a captured intraday or overnight opportunity. Contemporary original evidence and next open execution are essential; a historical earnings drift citation alone does not qualify this strategy for the morning shortlist.

### ST REV 001 Short term reversal within a trend

This experiment tests whether a five session company decline relative to its country benchmark is followed by a partial recovery while the stock remains above its 200 session average. The residual is the stock's five session total return minus the benchmark's five session total return. It is a simple benchmark difference, not a regression estimated abnormal return.

$$D_t=R_{i,t-5:t}-R_{b,t-5:t}$$

Eligible candidates are in the bottom five percent of the country comparison universe by D. Enter at the next full regular session opening after the decision is usable and hold five sessions, without averaging down or overlapping positions in the same issuer. This is an exploratory liquidity and reversal hypothesis. A negative company development can make a price decline rational and persistent.

News review produces dated risk flags and a separately recorded human research decision. It cannot be retrospectively used to exclude losing trades from the numeric baseline. A future news filtered strategy requires an explicit rule and its own prospective cohort. Missing news coverage is not evidence that no bad news exists.

## 6 Challenger models and excluded approaches

Gu Kelly and Xiu compare machine learning methods for return prediction and show the potential value of nonlinear interactions in their research setting. That is a reason to test controlled challengers after transparent baselines, not a performance forecast for this project. [17] ML 001 will start with a regularised linear model and one tree based challenger using the same eligible features, targets, chronological splits and costs. The benchmark is the best predeclared simple policy, not a deliberately weak comparator.

Keep the initial feature set below 30 named numerical features, the parameter search below 20 configurations per challenger family and the daily new experiment budget at ten. These limits are governance choices to contain selection bias and compute cost. Every failed configuration still counts. Expanding the search requires a recorded version change; a budget is not a statistical correction by itself.

Pairs trading commonly combines long and short positions in related securities. Gatev Goetzmann and Rouwenhorst provide an important historical research reference, but the implementation and borrow requirements do not fit the initial mandate. [18] Market making, latency arbitrage, options volatility selling and leveraged futures carry similarly introduce execution or payoff structures outside the stated scope. They are excluded rather than approximated with misleading long only substitutes.

Foundation price models, reinforcement learning and unconstrained autonomous equation searches are not initial production methods. They may be registered later when a concrete economic hypothesis, data access and evaluation advantage justify their complexity. The permanent standard permits discovery while keeping each experiment comparable and traceable.

## 7 Execution and transaction cost protocol

The user trades during regular sessions only. NYSE regular equity hours are 09:30 to 16:00 New York time; London normally operates 08:00 to 16:30 local time. UK equivalents for US hours vary around daylight saving changes. Exchange calendars determine holidays and early closes; broker instrument specific restrictions can be narrower. Extended hours availability must not override the user's policy. [19–20]

A source observation is usable only after it is both public and actually retrieved. The standard adds a 30 minute processing and human response allowance to the later timestamp. The baseline execution model uses the next full regular session opening strictly after that readiness time. It never buys at a closing price that preceded the research report. For a report prepared during a session, this intentionally waits until the following session; a later intraday model must be registered separately.

$$t_{ready}=\max(t_{published},t_{firstseen})+30\;\text{minutes}$$

A simulated open is an execution assumption, not proof that Trading 212 filled that price. Buys add spread and slippage; sells subtract them. The initial illustrative baseline uses ten basis points per side for half spread plus slippage combined, with 25 and 50 basis point stress cases. These are declared assumptions until actual execution observations are available. The five percent daily traded value participation cap is a further eligibility check, not a market impact estimate.

Trading 212 currently lists a 0.15 percent fee for an FX conversion. The model charges it on conversion events, not every trade regardless of currency balance. Invest account multicurrency treatment can differ from Stocks ISA, so the account policy is an explicit field and unresolved settings produce alternative scenarios rather than an invented answer. [21–22] Applicable UK share purchase duty is generally 0.5 percent, subject to instrument specific exemptions. Other exchange and regulatory charges are maintained in a dated schedule, and order review remains authoritative for an actual order. [23–24]

All outcomes are reported in GBP and the security's currency. FX market movement and conversion charges are different effects. Tax wrapper treatment is not inferred. Historical cost tests distinguish a current cost schedule sensitivity from a historically accurate schedule; present day fees must not silently be backdated to 2008.

For short term experiments use at most 20 simultaneous five percent hypothetical positions, at most one per issuer, and a 25 percent sector cap at entry. Rank simultaneous candidates by the registered signal with stable ID tie breaks. No leverage, borrowing, automatic trading, tactical enlargement of losing positions or assumption of a stop fill through a gap is allowed. These research constraints are not personalised position size advice.

## 8 Data architecture and online research

The system will retain immutable public source snapshots and a reproducible analytical view. SQLite stores tasks, settings, experiments, reports and prediction records. Parquet with DuckDB supports larger observation and price histories. Data scale is justified by measured coverage and query needs, not by the belief that a larger database automatically creates skill.

Every financial observation records security ID, metric definition, unit, currency, period start and end, public release time, first seen time, ingestion time, source hash and revision. Every document records its URL, publisher, retained text where permitted and passage offsets. A feature stores the cutoff and source observation IDs used to derive it. A prediction stores strategy and standard versions, instrument, horizon, benchmark, earliest entry, expiry, model output and abstention reasons before its outcome is known.

SEC's public research APIs require no account or key, while automated access must comply with its application identity and fair access rules. [25] Investor relations sites supply original releases and presentations. Yahoo's public data can support initial personal research, but its unofficial endpoint does not guarantee a clean historical security master or complete action coverage. GDELT can discover news; original publishers remain the evidence and their access or retention conditions still apply. [26] Kenneth French's library supplies factor and research portfolio comparisons rather than historical broker eligibility or individual delisted security data. [27]

The first ingestion release should assess 150 to 300 liquid US and UK issuers. This is a target for a feasibility study, not an assertion that free sources already provide complete point in time coverage. If there are too few eligible observations for a strategy, report that failure. Restrict the study or retain an exploratory label; do not silently fill gaps or require an unapproved paid account.

No strategy can claim survivorship corrected crisis performance without failed and delisted companies and their outcomes. In particular, a list of today's successful companies cannot establish what an investor could have discovered before 2008. Older unstructured filings and incomplete price histories may make that test infeasible under the account constraint. Document the coverage boundary and start a prospective record where historical reconstruction cannot be defended.

AI works online to discover original material, extract cited facts, propose typed formulas, investigate contrary evidence and write the short report. Numerical services own calculations. Prompts and responses are versioned. Retrieved documents are untrusted inputs, never instructions to disclose secrets or change methodology. Generated Python, if eventually necessary, runs in a restricted worker with read only snapshots and resource limits rather than inside the API process.

Existing authorised AI access is an integration constraint, not permission to copy browser sessions or assume a home server inherits this chat's tools. Choose and test a supported authentication path once during implementation. A daily task must survive expired authorisation, provider downtime and rate limits by recording a failed run instead of presenting an old report as new.

## 9 Validation and the meaning of confidence

### Chronological design

First freeze the eligible universe construction, data availability rules, strategy family, target, benchmark and search budget. Target observations include missing and failed outcomes; they cannot be deleted because a provider no longer recognises a ticker. Where a complete long history exists, use expanding time blocks with an initial five year training or development window and subsequent nonoverlapping one year outer test blocks. Three year thesis outcomes will require longer evidence and cannot be validated by one year folds.

Within each development block, reserve chronological periods for parameter selection and probability calibration. Purge observations whose outcome intervals cross a fold boundary and apply an embargo at least as long as the relevant label horizon. Numerical preprocessing is fit on development data only; contemporaneous percentile ranks may use only the eligible cross section available at that date. The final holdout is opened once for a frozen family. A revision after seeing it becomes a new family version and needs new independent evidence.

These lengths are initial policy choices, not a universal statistical theorem. When history is inadequate, the model stays exploratory. A public historical price backtest may demonstrate behaviour of a rule, but cannot retroactively validate the full modern AI research process. That process must issue predictions prospectively.

### Required comparisons and uncertainty

Report annualised return, volatility, drawdown, turnover, exposure, tail losses, profit factor and net GBP benchmark relative outcomes. Compare with buy and hold, equal weight eligible equities and the predeclared quality value, momentum and trend baselines where relevant. Include cash and a matched risk comparison so a market exposure change is not confused with security selection. The exact benchmark instrument, currency series and expense treatment are frozen in the run manifest before testing.

Use 10000 bootstrap resamples with seed 212. Register block length per family before testing; blocks for overlapping forward labels must be at least as long as the outcome horizon, and longer dependence must be assessed rather than assumed absent. Use time block and event aware resampling; overlapping 20 day outcomes and companies responding to the same event are not independent samples. Report effective sample limitations, confidence intervals and results by market, sector and regime. Include two and five times baseline execution friction. Search adjusted statistics such as Deflated Sharpe are supplementary diagnostics, not guarantees, and depend on defensible trial accounting. A single headline Sharpe or a handful of crisis anecdotes cannot qualify a model.

A numerical promotion requires a positive net benchmark relative mean with a predeclared one sided 95 percent block bootstrap lower bound above zero on untouched aggregate outer test outcomes, adequate coverage, no single outer test year supplying more than half the sum of positive annual excess contributions, and survival of the two times friction scenario. The concentration rule is a project governance choice, not proof of generalisation. When several strategy families are submitted to the same final holdout, use a familywise false positive budget of five percent with a Bonferroni adjustment across those submissions; the corresponding one sided bound replaces the unadjusted 95 percent threshold. Count rejected submissions as well as accepted ones. This deliberately conservative correction is separate from inner model selection and Deflated Sharpe diagnostics. Families that fail remain research records. More testing cannot be used to erase a failed result.

### Calibration and reporting

Forecast confidence refers to a defined event, such as net GBP outperformance of a specified benchmark over the next 20 sessions from the eligible entry. It is separate from the probability of any positive return and from an analyst's belief in business quality. Calibration asks whether forecast groups realise their stated frequency; it does not follow from an AI declaring its confidence.

$$BS=\frac{1}{N}\sum_{k=1}^{N}(p_k-y_k)^2$$

The Brier score measures squared probability error for a binary outcome. Also report log loss, reliability plots and a same horizon base rate comparator. A probabilistic model may be published numerically only after frozen prospective predictions, a completed calibration protocol and at least 200 nonoverlapping time or event clusters are available; its Brier improvement over the base rate must have a 95 percent block bootstrap lower bound above zero. Two hundred is a minimum governance threshold, not a guarantee of useful precision. If independence cannot be justified or evidence is too sparse, keep the number suppressed.

A 60 percent win rate can still lose money when losses outweigh wins. Expected net return, downside distribution, tail exposure and benchmark return therefore accompany probabilities. An 80 out of 100 research score must never be displayed as an 80 percent probability of making money. Until empirical calibration qualifies a model, the report says that forecast confidence is unvalidated.

### Model lifecycle

Every model begins as registered, then moves through implemented, exploratory, historically evaluated and prospective paper evaluation states. Operational release of a daily report can occur while its research labels are unvalidated. Publication of numeric probability labels and evidence of historical alpha are separate permissions. No status can imply profitable live investing merely because a backtest or unit test passed.

A 90 session paper period checks operations and collects outcomes; it is not enough to establish a multi year investment edge. Data integrity failures suspend the affected model immediately. A material definition or execution change creates a new cohort with a new track record. Scheduled quarterly reviews can suspend or retire a model, but cannot rewrite old predictions. Monitor at each report for stale inputs and infeasible entry; assess calibration on predeclared completed blocks rather than changing models every losing day.

## 10 The daily report and human decision

Proposed report delivery is 07:30 Europe London before the UK session, followed by a short update 30 minutes before the next US regular opening. The schedule is a specification, not an automation created by this paper. Each report has a data cutoff and a visible completion state. A US candidate can change before entry because of a price gap or new original evidence; its entry conditions must be rechecked and the original report retained.

The report contains up to three long term company research priorities and up to three eligible short term setups, followed by material changes and a clear wait decision when nothing qualifies. Rank long term research using LT QV 001; rank earnings and reversal candidates only within their own family. Do not combine different signal units into a single worth score. A later cross strategy allocation needs its own objective and validation.

Each item states the business or event thesis in two sentences, strongest contrary evidence, source dates, horizon, eligible session, entry assumptions, model state and a change or expiry condition. It distinguishes a research priority from an empirically qualified trade signal. AI cannot invent current catalysts to fill the template. Human overrides are stored separately with their reasons and are scored as a distinct decision stream, not mixed into the model's historical record.

For a company such as Qualcomm, the dossier would investigate the revenue and cash contribution of its actual business lines, demand cyclicality, customer dependence, licensing exposure, competition and capital allocation using original disclosures. Those are research questions, not conclusions about the company's current valuation or future return. No numerical Qualcomm recommendation is made in this paper.

## 11 Implementation plan and acceptance criteria

Milestone one creates the permanent research contracts, strategy registry and change history. Milestone two simplifies the interface to Today, Companies and Quant Lab without implying that unbuilt forecasting capabilities exist. Milestone three creates the dated observation and original document store, validates corporate actions and publishes a coverage report. Milestone four implements the three baseline rules and executable cost/session tests. Milestone five adds online AI evidence extraction and typed hypotheses using existing authorised access. Milestone six issues immutable prospective morning reports and measures outcomes before enabling confidence labels.

Each milestone requires a reproducible run manifest and an explicit implemented versus planned statement. Data tests must cover revisions, financial period alignment, unit and currency conversion, delisted outcomes, split/dividend accounting and availability cutoffs. Strategy tests must verify that perturbing future observations cannot change earlier signals, costs reduce returns as expected, and no overnight event receives an impossible earlier fill. Report tests must verify sources, timestamps, labels and abstention behaviour.

The first home server release uses a persistent task queue, idempotent ingestion, restart recovery, bounded workers, backup and provider retry policies. It runs the same versioned strategy package as the Mac. The architecture remains a local Python service and browser interface; the server hardware, storage and supported AI authorisation path are resolved before deployment. This paper does not claim that the present in process scheduler is already a durable server deployment.

## 12 Standardisation and controlled change

Standard 1.0 is the baseline for subsequent work. Each future conversation starts by reading AGENTS.md, docs/RESEARCH_STANDARD.md, research/standard_v1.json and research/CHANGELOG.md. If the user supplies a conflicting new requirement, record the conflict and its effect; do not treat old defaults as overriding the user's explicit instruction. Routine bug fixes can preserve the standard, while a changed strategy definition, target, universe, cost assumption or confidence gate must be versioned and logged.

New ideas are welcome as separately registered sandbox experiments. They cannot silently replace the baseline or inherit its test record. A new source can update observations under existing definitions, but a revised metric, model, prompt that changes predictions, or dataset reconstruction requires a new run/cohort identity. Patches fix implementation defects; minor versions add compatible research candidates; major versions change the baseline contract. Actual trades remain outside this project's execution authority.

The operating standard is machine readable and names every initial rule, parameter, policy and status. The paper is the reasoning record; the standard is the day to day development contract; the registry identifies experiments; the change log explains movement between versions. A conflict is resolved explicitly and all affected artefacts are updated together.

## 13 Conclusions and unresolved evidence

The strongest first implementation is a controlled quality value research process with momentum and trend comparisons. Short term earnings and reversal rules should be studied, with no presumption that an accessible after cost edge survives. Contemporary institutional use supports relevance, not a promised success rate. An AI researcher becomes useful by collecting evidence and testing hypotheses honestly, rather than continuously generating more confident language.

The current MarketDesk prototype supplies a limited source adapter, charts and a simple educational backtest. It has not implemented this paper's complete data store, accounting universe, validation or probability calibration. Historical coverage of delisted equities, point in time shares and statements, complete action histories, instrument eligibility and reliable document timestamps remain feasibility gates. The no new data accounts constraint may prevent some historical claims. Where it does, the correct result is a narrower study or insufficient evidence.

This methodology standardises how conclusions are reached, not what the market must do. Future implementation can change through recorded evidence and explicit user direction while preserving comparable experiments and an honest record of errors.

## References

All web sources reviewed 10 November 2026. Descriptions of contemporary practice are provider statements. Research references support the named findings, not the untested MarketDesk parameter choices.

[1] AQR. Systematic Equity. Current public description of systematic signals and use of machine learning and text. https://www.aqr.com/Learning-Center/Systematic-Equities

[2] Invesco. Factor investing foundations Five equity factors. 19 October 2026. https://www.invesco.com/apac/en/institutional/insights/factor-investing/factor-investing-foundations-five-equity-factors.html

[3] Chan T Monach M and Lesyk S. Quality still works Its character has changed. FTSE Russell 9 November 2026. Public research overview consulted. https://www.lseg.com/en/ftse-russell/research/quality-still-works

[4] Microsoft. Qlib. Repository and project description. https://github.com/microsoft/qlib

[5] Microsoft. RD Agent. Repository and project description. https://github.com/microsoft/RD-Agent

[6] TauricResearch. TradingAgents. Repository and project description. https://github.com/TauricResearch/TradingAgents

[7] Asness C Frazzini A and Pedersen L H. Quality Minus Junk. AQR research overview 2018. https://www.aqr.com/Insights/Research/Working-paper/Quality-minus-Junk

[8] Frazzini A Kabiller D and Pedersen L H. Buffett's Alpha. Financial Analysts Journal 2018 AQR overview. https://www.aqr.com/insights/research/journal-article/buffetts-alpha

[9] Jegadeesh N and Titman S. Returns to Buying Winners and Selling Losers Implications for Stock Market Efficiency. Journal of Finance 1993 volume 48 pages 65 to 91. Publisher abstract consulted. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x

[10] Hurst B Ooi Y H and Pedersen L H. A Century of Evidence on Trend Following Investing. AQR journal article overview 2017. https://www.aqr.com/insights/research/journal-article/a-century-of-evidence-on-trend-following-investing

[11] DellaVigna S and Pollet J. Investor Inattention Firm Reaction and Friday Earnings Announcements. NBER Working Paper 11683 2005. Abstract consulted. https://www.nber.org/papers/w11683

[12] Christensen K Timmermann A and Veliyev B. Warp speed price moves Jumps after earnings announcements. Author abstract arXiv version 2 January 2026 with related journal DOI listed. https://arxiv.org/abs/2601.08962

[13] McLean R D and Pontiff J. Does Academic Research Destroy Stock Return Predictability. Journal of Finance 2016 volume 71 pages 5 to 32. Publisher abstract consulted. https://doi.org/10.1111/jofi.12365

[14] Bailey D H and López de Prado M. The Deflated Sharpe Ratio Correcting for Selection Bias Backtest Overfitting and Non Normality. 2014 author paper. https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf

[15] Novy Marx R and Velikov M. A Taxonomy of Anomalies and their Trading Costs. NBER Working Paper 20721 2014. Public abstract consulted. https://www.nber.org/papers/w20721

[16] Kelly B T Malamud S Schwab J and Xu T A. Scaling Point in Time Language Models. NBER Working Paper 35247 May 2026. Public abstract consulted. https://www.nber.org/papers/w35247

[17] Gu S Kelly B and Xiu D. Empirical Asset Pricing via Machine Learning. Review of Financial Studies 2020 with author manuscript September 2019. Author abstract consulted through indexed manuscript; full PDF retrieval timed out. https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf

[18] Gatev E Goetzmann W N and Rouwenhorst K G. Pairs Trading Performance of a Relative Value Arbitrage Rule. NBER Working Paper 7032 1999. Public abstract consulted. https://www.nber.org/papers/w7032

[19] NYSE. Holidays and Trading Hours. https://www.nyse.com/trade/hours-calendars

[20] London Stock Exchange. Personal Investing FAQs. https://www.londonstockexchange.com/en/resources/faqs/personal-investing

[21] Trading 212. What is the FX fee Invest and Stocks ISA. https://helpcentre.trading212.com/hc/en-us/articles/360018909758-What-is-the-FX-fee-Invest-Stocks-ISA

[22] Trading 212. Can I choose the currency in which to buy or sell assets for Invest accounts. https://helpcentre.trading212.com/hc/en-us/articles/34159237080861-Can-I-choose-the-currency-in-which-to-buy-sell-assets-for-Invest-accounts

[23] Trading 212. What are the fees in the Invest ISAs and SIPP. https://helpcentre.trading212.com/hc/en-us/articles/11471996799517-What-are-the-fees-in-the-Invest-ISAs-and-SIPP

[24] HMRC. Tax when you buy shares Overview. https://www.gov.uk/tax-buy-shares

[25] US Securities and Exchange Commission. EDGAR Application Programming Interfaces. https://www.sec.gov/search-filings/edgar-application-programming-interfaces

[26] GDELT Project. GDELT DOC 2 API Debuts. https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

[27] Kenneth R French. Data Library. https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

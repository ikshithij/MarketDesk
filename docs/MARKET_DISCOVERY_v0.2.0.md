# MarketDesk 0.2.0: market discovery

Released 10 November 2026. This release implements the data solution researched in [the source assessment](research/US_UK_FULL_MARKET_SOLUTION_2026-11-10.md).

## What runs

Companies imports current Nasdaq and other US exchange symbol directories, the LSE equity instrument workbook (Main Market and AIM), and Aquis securities. Every discovered security remains inspectable, including funds, excluded instruments, missing data and unresolved mappings. Securities are not unique companies; OTC and private companies are outside scope. Directory publication dates are shown separately from retrieval dates.

US annual financials, profiles, shares and daily prices come from the public [Defeat Beta Yahoo Finance dataset](https://huggingface.co/datasets/defeatbeta/yahoo-finance-data), whose upstream data is Yahoo Finance/Nasdaq and whose dataset licence is ODC-BY. Preserve that attribution when exporting or redistributing its data. This is an unofficial research cache, not an exchange real-time feed. UK daily prices and annual statements use public Yahoo endpoints. ECB reference rates normalize currencies, including pence. Aquis securities without verified price mappings stay unranked. Initial bulk input is approximately 600 MB; DuckDB processes it locally with a 512 MB memory limit. Data-source access can fail or be throttled.

The initial live run discovered 19,457 securities (13,281 US, 6,176 UK). This is a snapshot count, not a promise of complete fundamentals or a count of investable companies. No financial-data account is required.

## Fixed numerical method

[SCREEN-PUBLIC-001 v1.0.0](../research/public_screen_v1.json) is an exploratory discovery model, separate from the unchanged research standard, six registered strategies and AI company rating rubric. It requires £1 billion capitalization, £5 million median daily traded-value proxy over 60 completed observations, positive net income and operating cash flow, recent shares/FX/prices and annual statements no older than 450 days. Missing fields are never zero-filled.

Quality equally averages country/sector percentiles of gross profit, operating cash flow and negative accruals, each divided by average annual assets. Value equally averages free cash flow yield and operating income divided by an EV proxy. The final score is 50% quality and 50% value. Groups require at least 20 unique inferred issuers; tied ranks are averaged. The EV proxy omits preferred capital and noncontrolling claims; vendor adjustments and share-class capitalization are unverified. Scores are relative screening opinions, not return probabilities or qualified LT-QV-001 signals.

Only after collection finishes does the app freeze up to 100 unique issuers from their peer groups' top quintile, ordered by discovery score. A manifest hash records the original inputs and configuration. The provisional table is labelled while scanning. Duplicate identities, small groups and invalid/stale inputs remain visible with reasons.

## AI research

With automatic research enabled, the frozen shortlist enters a durable sequential queue using existing Codex sign-in and live web tools. Each company gets a sourced nine-section dossier and a reconciliation of screen inputs with primary disclosures. A supported reconciliation requires at least three distinct numerical primary-source checks. These checks are AI-reported, not independently verified. Contradicted or insufficient evidence is flagged for review; it does not overwrite the numerical cohort or silently replace the candidate. Supported reports proceed to the existing out-of-five company rating rubric.

A queue can contain 100 candidates without producing 100 supported ratings. Missing sources, contradictions, authentication limits and research failures remain visible. Research uses your existing AI allowance. Pause/resume and failed-job retry controls are available; a report already running may finish before the next queue step pauses. Jobs resume after an app restart. No orders are placed and Trading 212 availability is not verified. UK regular-hours, long-only and no-leverage constraints remain in research prompts.

## Storage and reproducibility

New SQLite tables are additive. Existing company reports, ratings, notes and transactions are retained. Source files are stored by SHA-256 under `.marketdesk/market-snapshots/`; provenance records include source URL, retrieval time and publisher date where supplied. Run configuration is snapshotted. Each row exposes its metrics, exclusions and source hashes; the full scan exports to CSV. The data and snapshots are gitignored. A pre-release SQLite backup was taken before the live migration.

The numerical policy has a separate hash lock checked by `python3 scripts/check_public_screen.py`. Changes require a new version and entry in `research/PUBLIC_SCREEN_CHANGELOG.md`; do not silently edit the registered strategy baseline. Corporate-action-corrected historical tests, calibrated probabilities, broker integration, scheduled morning delivery and a home-server deployment are not delivered by this release.

## Validation

Production frontend build, 78 unit/integration tests, existing research/rating locks and the new screen policy lock. Live source ingestion and the browser table were checked against the actual local run. The first full scan and 100-company AI batch are long-running background work; their completion is shown in the interface rather than assumed.

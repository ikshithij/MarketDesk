# Company researcher implementation — 10 November 2026

This release implements on-demand company dossiers and simplifies the workspace to Today, Companies and Quant Lab. It does not change Research Standard 1.0.0 or its strategy registry. Research analysis is exploratory; it is not a validated stock-selection system.

## Workflow

A user enters a company name or ticker. Local identities resolve directly; public Yahoo Finance search provides additional equity listings and lets the user disambiguate. Selected identities are added to the local database. SEC contact configuration is not required.

The server captures the latest public quote and reproducible historical observations where available. It supplies those observations, optional already-cached SEC facts, the user's question, and the canonical policy to the existing signed-in Codex CLI. Live web tools retrieve company disclosures and news. Shell, apps, plugins, browser/computer automation and multi-agent tools are disabled for the research subprocess. No arbitrary model-generated code runs.

The model returns schema-constrained JSON. Server checks require all nine sections, at least three unique source IDs, safe public HTTPS source URLs and valid source references on reported/calculated findings. No web-tool calls means no published report. Obvious numerical probability claims are rejected, but semantic compliance is not fully mechanically enforceable. The UI distinguishes reported facts, calculations and interpretation. Source access is self-reported by the AI and can be wrong; URL checks do not verify page contents. Original source bytes and independently verified source-access traces are not archived.

One queued worker handles up to three pending jobs. Same-company/same-question active runs deduplicate, including repeated refresh clicks. Completed matching reports are reused for 24 hours unless refreshed. A new refresh or follow-up writes a new report and keeps earlier reports. A failed run publishes no partial report. Restart marks interrupted runs failed. The ten-minute process timeout stops a stuck run. Reports and original context survive in SQLite; an individual JSON download includes report data and engine metadata.

## Continuity

Every new run uses the canonical policy in `research/standard_v1.json`, including constraints and unvalidated status. Engine `company-dossier-1.0.0` records report version, exact prompt, prompt hash, policy hash and context hash. Codex's selected default model is reported as such when its CLI does not identify the actual model; this limits exact reproducibility. A model override can be set explicitly through `MARKETDESK_CODEX_MODEL`. Saved policy and prompt support audit, not deterministic regeneration.

The first live QCOM acceptance run was produced before prompt/hash recording was added. It retains its original context, report, engine version and usage, and is deliberately not rewritten to imply metadata it did not capture. Future runs include the additional records. It completed via the existing ChatGPT-authorized Codex CLI, with eight linked sources and five completed web-tool calls. This confirms online integration, not the factual correctness of every claim or investment performance.

## Verification

The production TypeScript/Vite build and 51 Python tests passed. Added tests cover missing citations/sections, unsafe sources, invented probability claims, adjusted-data gaps, constrained CLI configuration, rejection of runs without web use, exclusion of API keys from the child environment, company-name resolution without SEC, active-run deduplication, restart recovery, cached-report access without AI, preservation of older reports and failure handling when market data or AI is unavailable.

The existing educational SMA backtest remains separate from TR-001. Broad universe ingestion, verified Trading 212 listing availability, point-in-time source snapshots, qualified strategy scoring, calibrated return probabilities, automated daily scheduling and brokerage execution are still unimplemented.

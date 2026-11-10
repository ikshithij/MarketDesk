# AI company ratings and comparison — version 1.0.0

User authority, 10 November 2026: “I want a clear number or rating for each thing … a large table … all stocks … what's most worth it and best.” This release adds a separate, explicitly exploratory company-opinion rubric, AI-COMPANY-001. It does not promote or alter Research Standard 1.0.0, LT-QV-001, the other five registered strategies, their execution rules, or probability calibration gates.

## What the numbers mean

Nine integer ratings use a common 0–5 scale: 0 severe concerns; 1 weak; 2 below average; 3 mixed/reasonable; 4 attractive; 5 exceptional. Higher is always favourable, including risk resilience. Null is insufficient evidence, never zero. The exact dimensions, anchors and formula are frozen in `research/company_ratings_v1.json`; changes require a new rubric version and an entry in the ratings change log.

The long-term total describes the AI's subjective assessment of 3–5 year company attractiveness at the captured price. Python computes:

`overall = (20*business + 25*financials + 15*growth + 20*valuation + 20*long_term) / 100`

It is displayed out of five to one decimal. Financials receive the largest weight to reflect the owner's cash-flow focus. These weights are product defaults, not estimated or validated predictors. Near-term setup, leadership, risk resilience and evidence coverage remain visible but do not enter the total, separating horizons and avoiding further double counting. This does not eliminate overlap between the five weighted judgments. Sector-specific economics and cross-sector comparability remain limitations.

Labels are assigned to the unrounded total: Strong candidate >=4; Worth a closer look >=3.5; Mixed >=2.5; Less attractive below 2.5. These are research opinions, not action thresholds or probabilities. Rankings use descending unrounded totals, ticker as deterministic tie order, and shared ranks for exact ties. Rounded totals can appear tied while their raw totals differ.

An overall rank requires every weighted rating, at least three distinct source documents including one primary source marked read, evidence coverage >=3, a recent positive non-stale quote, and an assessment no older than seven days. Source access and evidence coverage are AI-reported, not independently audited. Source URL/citation checks validate attribution structure, not correctness. Banks, insurers and property investment companies stay outside this initial rubric; known workspace exclusions JPM and UNH are enforced by the server, with explicit banking/insurance/property sectors also excluded. Unknown sector classification remains a limitation and the researcher is instructed to abstain on excluded accounting types.

## Coverage and live research

“All companies” means all identities currently in the workspace, initially 20 US equities. It does not mean every listed stock or a complete US/UK universe. The table shows total, researched and rankable counts and preserves unresearched companies as blank rows. Searching and analysing additional names adds them to the workspace; they can then be rated individually or through Research missing ratings. There is no full-market discovery claim.

Online comparison research runs in batches of five using the existing signed-in Codex CLI and its web tools. Captured prices come from the public market provider; the model retrieves financial reports and news, supplies reasons/citations for each rating, a thesis, contrary evidence, valuation calculation, catalyst and change-of-mind condition. A missing catalyst can leave near-term setup blank even when long-term ratings are supported. The tool must record web use before anything is published. No new data accounts are required.

Each completed batch publishes independent immutable assessments. Later refreshes append rows and retain older assessments. Completed current-day assessments are reused unless explicitly refreshed. One active comparison job deduplicates repeated clicks; it shares the bounded AI worker with full dossiers. Progress counts processed companies, not necessarily successful assessments; batch failures are shown with their symbols. Restart marks interrupted jobs failed without deleting completed batches. Each AI subprocess has the existing ten-minute timeout. The exact prompt, its hash, rubric hash and provider token usage are saved with each batch's assessments. Full original document snapshots and an independently verified tool-access ledger are not archived.

The company dossier shows the latest rating overlay and its separate timestamp. This does not rewrite the older dossier or pretend the two runs share an evidence cutoff. On the What to watch next section, the supplemental score is explicitly labelled evidence coverage. The table exposes captured price/date, all dimensions, sorting/filtering, expandable reasoning, citations and CSV export. Today highlights up to three top eligible researched companies. No portfolio allocation, order execution, proven alpha or calibrated return probability is created.

## Research context

[Investor.gov's research guidance](https://www.investor.gov/research-you-invest) explains the role of public company disclosures in investor due diligence. Its [stock overview](https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks) distinguishes stock types, including growth and value, and discusses risks. These sources support inspecting disclosures, price and risk separately; they do not endorse this rubric, its weights, the generated ratings or any MarketDesk stock conclusion. Reviewed 10 November 2026.

## Verification

The production build and 61 Python tests passed. Public London prices quoted in pence are now preserved as GBX and displayed in pence, preventing a pounds-versus-pence label error in price snapshots. Existing US quote behavior is unchanged.

The added tests cover fixed weights, server-owned aggregates, missing-score abstention, stale dates/quotes, excluded accounting types, evidence gates, invalid numbers/citations/URLs, requested company coverage, immutable assessments, stable table coverage, duplicate jobs, restart recovery, cached reuse, CSV blanks and retention of older assessments after AI failure. Test fixtures live only in temporary databases; application ratings require actual live research.

Live acceptance on 10 November 2026 completed all 20 workspace companies in four batches, with no failed batch. Eighteen met ranking gates; JPM and UNH remained unranked under the accounting exclusions. The dated CSV snapshot contains all 20 companies and 25 columns. The browser checks exercised the populated table, valuation sorting, company/sector filtering, Qualcomm's cited rating detail and the rating overlay on its original dossier. This is operational evidence, not a validation of rating accuracy or stock performance.

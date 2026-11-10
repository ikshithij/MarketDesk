# Company opinion rubric change log

## AI-COMPANY-001 1.0.0 — 10 November 2026

Authority: explicit user request for clear numeric ratings for each area, a large stock comparison table and an expert view of the most worthwhile companies.

Added a new exploratory rubric rather than changing a baseline strategy. Previous state: qualitative dossiers with no numeric company scores or comparison ranking. New state: nine cited 0–5 AI opinion ratings, with a deterministic five-dimension weighted long-term total (business 20 / financials 25 / growth 15 / valuation 20 / long-term outlook 20). Near-term, stewardship, resilience and evidence coverage are excluded from the aggregate; no cross-strategy signal units are mixed.

The initial cohort is the 20 current workspace identities, not all listed securities. No inherited performance record, profitability evidence or numeric probability is claimed. Seven-day assessment/quote limits, minimum sources, missing-data abstention and accounting exclusions gate ranking. Future rubric or prompt changes affecting judgments create separately versioned cohorts; old assessments remain intact. The original 1.0.0 standard, methods paper, registry, lock and baseline change log remain unchanged.

Validation required for predictive claims remains the baseline's historical and prospective research process, which has not been completed. Current software tests and live tool integration demonstrate implementation only. See docs/COMPANY_RATINGS.md for anchors, formula, coverage, data limitations and operational behavior.

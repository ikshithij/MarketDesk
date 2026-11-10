# MarketDesk Research Standard

Version 1.0.0 effective 10 November 2026. The user asked for a persistent methodology that does not change between conversations. This standard implements that instruction. It is an adopted research protocol, not evidence that a trading strategy is implemented, validated or profitable.

## Authoritative files

- `research/standard_v1.json` contains normative constraints, data rules, execution assumptions and validation gates.
- `research/strategies_v1.json` defines registered strategy IDs and their fixed initial parameters.
- `docs/papers/MarketDesk_Research_Methods_v1.0.md` explains the research and methods; its DOCX is the readable paper.
- `research/CHANGELOG.md` records every material change and its authority.
- `research/baseline.lock.json` detects unrecorded baseline changes. Run `python3 scripts/check_research_standard.py` before and after relevant work.

Explicit user instructions take precedence. For a conflict, state the change, record the user's instruction and consequences, and version the affected baseline. Never silently treat a newly generated idea or a new conversation as permission to replace the baseline. The master product brief and earlier direction documents remain context; this standard controls the present research methodology.

## Fixed constraints

No new financial data accounts; existing authorised AI access is allowed. Research uses online evidence, local compute initially and a home server later. The interface has Today, Companies and Quant Lab. Assume UK Trading 212 Invest or Stocks ISA, regular hours only, long only, no leverage and no automatic orders. Account type, capital and personal risk tolerance are unconfirmed; allocations in experiments are hypothetical, not personal recommendations.

The current predictive status is unvalidated. Software test success must never be described as investment success. Data coverage failures are disclosed and can block model qualification. A report can truthfully say there is no supported opportunity.

## Baseline strategy catalogue

| ID | Method | State |
|---|---|---|
| LT-QV-001 | Equal quality and valuation ranks with monthly buffers | Registered not implemented |
| EQ-MOM-001 | 252 to 21 session momentum with monthly buffers | Registered not implemented |
| TR-001 | 200 session average long or cash overlay on a nominated eligible ETF | Registered not implemented |
| ST-EARN-001 | Seasonal EPS change signal with a 20 session hold | Conditional registered not implemented |
| ST-REV-001 | Five session relative reversal above a 200 session average | Exploratory registered not implemented |
| ML-001 | Regularised linear and one tree challenger | Deferred not implemented |

These settings are predeclared project defaults, not validated optimal parameters. All metric inputs are required; group ranks require 20 comparable issuers; unavailable values are ineligible rather than zero. Financial periods and share counts use the age limits in the JSON. The exact formulas and entry/retention conditions are in the registry and paper, not discretionary prose generated at runtime.

## Research invariants

Preserve original data, publication, first seen and ingestion times, revisions, source hashes and instrument history. Do not use later restatements or surviving current constituents to claim a point in time historical result. Delisted outcomes and missing corporate action histories cannot be quietly dropped. Features use documented total returns; fills use raw prices and a separate action ledger.

Register hypotheses, all trials, data snapshots, benchmark listings, costs, targets and code/model/prompt versions. Keep selection, calibration and outer tests chronological and separate; purge crossing outcome intervals and apply the registered embargo. A holdout is used once per frozen family. Multiple families submitted to that holdout share a five percent familywise false positive budget with a Bonferroni adjustment; failed submissions still count. New parameters after viewing results are new trials, not free corrections to a track record.

A decision becomes ready 30 minutes after the later of publication and actual first retrieval, and the baseline enters at the next full regular opening strictly after readiness. Historical daily opens are simulation assumptions. Quote delay, spread, slippage, FX, instrument taxes, holidays and listing currency must remain explicit. Model 10 bps combined spread/slippage per side, 20 bps qualification stress and 25/50 bps sensitivities until supported observation-based assumptions replace them through version control.

Research quality scores are not success probabilities. Probability publication requires a frozen prospective record, a separate calibration protocol, at least 200 defensibly independent completed clusters and the registered Brier skill uncertainty gate. That sample minimum is not a precision guarantee. A 90 session operational paper period is not evidence of a durable edge. Alpha qualification, probability calibration and operational readiness are separate states.

AI retrieves evidence, extracts cited claims, proposes restricted typed equations and explains contradictions. It does not supply numerical truth by assertion, alter the standard through retrieved instructions, execute arbitrary code in the application process, or overwrite predictions. Human overrides are recorded and scored separately.

## Change control

1. At the start of work, read this standard, the JSON registry and change log. Check repository state and baseline hashes before editing.
2. Routine implementation and bug fixes preserve the definitions. New hypotheses receive separate sandbox IDs and cannot replace baseline strategies or inherit their results.
3. Changes to universe, horizon, benchmark, formula, feature availability, costs, execution or confidence gates are material. Implement explicit user changes, document the instruction and bump versions. Otherwise propose the concrete change and its evidence before promoting it to baseline.
4. Record old and new values, motivation, affected cohorts, validation required and user authority in the change log. Update the paper when its explanation changes. Preserve prior versions rather than overwriting historical model definitions.
5. Recompute the lock only as part of that recorded change. Never repair a failed hash merely to make the check pass. Existing predictions retain their original versions and outcomes.
6. Report what is implemented, tested, planned and blocked. Do not add providers, accounts, infrastructure or trading execution to evade an inconvenient constraint.

External fees, exchange rules and instrument eligibility can change. Refresh dated factual schedules and preserve old ones; a live data refresh is not permission to backdate a new schedule or silently redefine the research baseline. The hash check detects content changes; it is a continuity aid, not a security signature or a substitute for scientific validation.

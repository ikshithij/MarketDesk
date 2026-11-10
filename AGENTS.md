# MarketDesk agent instructions

## Persistent research methodology

The user explicitly requested consistent methods across conversations. Before research or implementation that affects MarketDesk's investment methodology, read:

1. `docs/RESEARCH_STANDARD.md`
2. `research/standard_v1.json`
3. `research/strategies_v1.json`
4. `research/CHANGELOG.md`

Run `python3 scripts/check_research_standard.py` before and after relevant changes. Read the detailed paper `docs/papers/MarketDesk_Research_Methods_v1.0.md` for the affected strategy or method.

Preserve the baseline across chats. Do not silently replace equations, horizons, datasets, execution assumptions, benchmarks or confidence gates. New ideas use separate sandbox strategy IDs. Material baseline changes require explicit user direction or a concrete evidence-backed proposal before promotion, plus versioned files and a change log entry. Explicit user instructions take precedence; record the effect rather than obstructing them.

No new financial data accounts. Existing authorised AI access is acceptable. Preserve UK regular-hours-only, long-only, no-leverage and manual-order constraints. Never claim calibrated probabilities, profitable alpha, implemented methods or completed deployment without the corresponding evidence. Source facts, AI interpretations, experimental results and plans must remain distinguishable.

## Codebase exploration

<!-- codebase-memory-mcp:start -->
For structural codebase exploration, use the installed `codebase-memory` skill.
<!-- codebase-memory-mcp:end -->

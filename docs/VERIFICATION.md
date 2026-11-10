# Verification

## Executed locally

- Production TypeScript/Vite build: passed.
- Python unittest suite: 41 tests passed (isolated temporary databases; synthetic finance fixtures exist only in tests).
- FastAPI startup on loopback: passed.
- Browser preview: initial briefing, desktop and narrow responsive layouts rendered; default discovery listed company identities without invented financials; universal search resolved “Compare Nvidia and AMD” to the comparison view with missing financial values clearly shown.
- Dependency installation: npm audit reported zero vulnerabilities at installation time. This is a package audit, not a complete security review.

## Not claimed

No user-owned SEC contact, Alpha Vantage, FRED or OpenAI key was supplied during implementation. Live SEC/FRED retrieval, paid entitlements, AI answer quality and real-world XBRL taxonomy completeness have not been verified end-to-end. The UI exposes this state rather than serving fake financial observations. Mocked tests verify error handling and local invariants; they do not substitute for live data validation.

Backtest fixtures verify execution timing and costs, not predictive merit. Current simulation limitations are displayed with results. Portfolio values are suppressed if required prices/FX are missing; weighted average accounting is not UK share matching or tax reporting.

## Automatic quotes follow-up

Live Yahoo Finance QCOM retrieval returned a quote, original exchange timestamp and 251 daily bars without credentials. Added regression tests for prior-session change calculation (never using start-of-year close), null bars, missing adjusted prices, symbol validation, nonfinite quotes, cache reuse and stale fallback. SEC and prices now refresh independently.

Browser follow-up: QCOM page showed the real quote ($171.47, 9 Nov 2026 21:00 GMT), one-year daily and latest-session five-minute charts, exchange status, day range, 52-week range and volume. Prices loaded with no SEC contact or API key. The market was outside its regular session; no real-time tick claim was made.

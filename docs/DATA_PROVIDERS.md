# Provider matrix

Reviewed 10 November 2026 against primary documentation. Plans, entitlements and terms can change. The application does not buy subscriptions or grant redistribution rights.

| Source | Available data / coverage | Cost / authentication | Rate / delay | Historical coverage | Reliability / rights / implementation |
|---|---|---|---|---|---|
| [SEC EDGAR](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Company facts, US-GAAP XBRL, submissions, issuer directory | Public access; identifying User-Agent/contact required | SEC ceiling 10 requests/sec; app is deliberately slower; filing publication times apply | Depends on issuer and structured filing availability; older filings need further ingestion | Official reported facts; custom tags/inconsistent taxonomy remain gaps. Implemented company facts, directory and recent filing links; not full filing text |
| [Alpha Vantage](https://www.alphavantage.co/documentation/) | Adjusted daily OHLCV and corporate-action factors for supported equities | API key. Adjusted daily entitlement may require paid plan; no claim of universal free access | [Support](https://www.alphavantage.co/support/) advertises 25 requests/day for most free datasets. App treats daily bars as EOD, never real-time | Provider documents 25+ years for daily endpoint; this release requests compact (~100 bars), not full history | Provider quotas/terms apply; no redistribution permission inferred. Implemented optional adapter, explicit errors and cached prior success |
| [FRED](https://fred.stlouisfed.org/docs/api/fred/) | Rates, inflation, unemployment and macro series | User's own API key; see [key requirements](https://fred.stlouisfed.org/docs/api/api_key.html) | Series release frequency varies; no real-time market quote claim. No fixed undocumented rate limit assumed | Series-dependent, often decades; current UI requests latest 10 observations | Official series aggregator; underlying series may have separate copyright/usage restrictions. Latest observations implemented; vintage/ALFRED point-in-time history not implemented |
| [OpenBB providers](https://docs.openbb.co/odp/python/extensions/providers) | Broad provider abstraction, not a licence to underlying datasets | Per-provider keys and fees | Underlying provider limits/delays remain | Underlying source-dependent | Evaluated; not installed. Installing OpenBB does not remove paid-data dependencies |
| [Fiscal.ai](https://fiscal.ai/) | Auditable standardised fundamentals and data API | Commercial; obtain a quote/entitlement | Contract-dependent | Contract-dependent | Candidate to improve custom-tag, global and segment coverage; not integrated |

## Failure and freshness policy

Every cached provider payload has a retrieval timestamp. Quotes include observation date, currency and delay. Financial statements retain fiscal dates and filing provenance. Missing fields remain `null`/unavailable. A provider failure does not replace usable caches with zeros or random example values. Existing observations can become stale; the UI shows their dates rather than relabelling a cache hit as live data. A fuller stale-threshold policy is still required for alerts and portfolio risk analytics.

SEC ticker directory metadata is cached after first use; it is not yet refreshed automatically for symbol changes/delistings. The starter sector labels are manually curated identities; added directory companies remain unclassified until supported classification is available. Screen results cover the locally added company universe only.

## Deliberate gaps

Analyst estimates, consolidated real-time exchange feeds, historical delisted universes, security master corporate actions, earnings calendars, segment/customer/supplier relationships, global fundamentals, broad news licensing and complete ownership/insider extraction are not free side effects of the installed stack. They require specific datasets and validation. No fabricated approximations are displayed.

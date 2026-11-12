"""Prospective, equal-slot paper tracking for a frozen discovery shortlist."""

from math import isfinite
from datetime import datetime, time, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

from . import providers, store
from .company_analysis import AnalysisError

MARKETS = {
    'US': (ZoneInfo('America/New_York'), time(9, 30), 'SPY'),
    'UK': (ZoneInfo('Europe/London'), time(8), 'ISF.L'),
}


def start(run_id):
    with store.db() as connection:
        run = connection.execute(
            "SELECT cohort_hash FROM market_runs WHERE id=? AND status='complete'", (run_id,)
        ).fetchone()
        if not run or not run['cohort_hash']:
            raise AnalysisError('Finish the market scan before starting a paper basket.')
        members = connection.execute(
            """SELECT symbol,name,country,rank FROM market_observations
            WHERE run_id=? AND shortlisted=1 ORDER BY rank,listing_id LIMIT 20""", (run_id,)
        ).fetchall()
        if not members:
            raise AnalysisError('This scan has no shortlisted companies.')
        connection.execute(
            'INSERT OR IGNORE INTO paper_baskets VALUES (?,?,?)',
            (run_id, store.now(), run['cohort_hash']),
        )


def bars(symbol, country, started, now):
    zone, opening, _ = MARKETS[country]
    endpoint = f'https://query2.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe="")}'
    payload = providers.fetch(endpoint, {
        'period1': int(started.timestamp()), 'period2': int(now.timestamp()), 'interval': '1d',
    })
    result = payload['chart']['result'][0]
    prices = result['indicators']['quote'][0]
    sessions = {}
    for timestamp, first, last in zip(result['timestamp'], prices['open'], prices['close']):
        day = datetime.fromtimestamp(timestamp, zone).date()
        if day >= now.astimezone(zone).date() or datetime.combine(day, opening, zone) <= started:
            continue
        if all(isinstance(value, (int, float)) and isfinite(value) and value > 0
               for value in (first, last)):
            sessions[day.isoformat()] = (first, last)
    return sessions


def read(run_id, refresh=False):
    with store.db() as connection:
        basket = connection.execute('SELECT * FROM paper_baskets WHERE run_id=?', (run_id,)).fetchone()
        if not basket:
            return None
        members = [dict(row) for row in connection.execute(
            """SELECT symbol,name,country,rank FROM market_observations
            WHERE run_id=? AND shortlisted=1 ORDER BY rank,listing_id LIMIT 20""", (run_id,)
        )]
    result = {**dict(basket), 'members': members, 'history': []}
    key = f'paper-basket:{run_id}'
    previous = store.cached(key)
    if previous and not refresh:
        return previous['data']
    if not refresh:
        return result
    now = datetime.now(timezone.utc)
    started = datetime.fromisoformat(basket['started_at'])
    result['checked_at'] = now.isoformat()
    if all(now.astimezone(zone).date() <= started.astimezone(zone).date()
           for zone, _, _ in MARKETS.values()):
        return result
    try:
        benchmarks = {
            country: bars(MARKETS[country][2], country, started, now)
            for country in {member['country'] for member in members}
        }
        prices = [bars(m['symbol'], m['country'], started, now) for m in members]
    except (providers.ProviderError, KeyError, IndexError, TypeError, ValueError):
        return {**(previous['data'] if previous else result),
                'warning': 'A price feed was unavailable. Previous results are retained.'}
    common = set.intersection(*(set(series) for series in [*prices, *benchmarks.values()]))
    if not common:
        return {**(previous['data'] if previous else result),
                'warning': 'Waiting for a completed session with prices for every holding and benchmark.'}
    entry = previous['data']['entry_date'] if previous else min(common)
    if entry not in common or (previous and max(common) < previous['data']['history'][-1]['date']):
        return {**previous['data'], 'warning': 'Some saved session prices are missing from the latest response.'}
    result['entry_date'] = entry
    for day in sorted(common):
        moves = [series[day][1] / series[entry][0] - 1 for series in prices]
        comparisons = [
            benchmarks[m['country']][day][1] / benchmarks[m['country']][entry][0] - 1
            for m in members
        ]
        result['history'].append({
            'date': day,
            'basket_pct': 100 * sum(moves) / 20,
            'benchmark_pct': 100 * sum(comparisons) / 20,
        })
    result['members'] = [{**member, 'return_pct': 100 * move}
                         for member, move in zip(members, moves)]
    store.cache(key, result)
    return result

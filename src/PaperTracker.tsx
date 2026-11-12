import {useEffect, useState} from 'react';
import {api} from './api';

type Basket = {
  started_at: string;
  entry_date?: string;
  warning?: string;
  history: {date: string; basket_pct: number; benchmark_pct: number}[];
  members: {symbol: string; rank: number; return_pct?: number}[];
};

const pct = (value: number) => (value > 0 ? '+' : '') + value.toFixed(2) + '%';

export default function PaperTracker({runId}: {runId: string}) {
  const [basket, setBasket] = useState<Basket | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState('');
  const path = '/market-runs/' + runId + '/paper';

  useEffect(() => {
    let active = true;
    api<Basket | null>(path).then(value => {
      if (active) setBasket(value);
    }).catch(reason => {
      if (active) setError(reason.message);
    }).finally(() => {
      if (active) setBusy(false);
    });
    return () => { active = false; };
  }, [path]);

  async function update() {
    setBusy(true);
    setError('');
    try {
      setBasket(await api<Basket>(basket ? path + '/refresh' : path, 'POST', {}));
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const latest = basket?.history.at(-1);
  return <section className="market-method">
    <h3>Top 20 paper tracker</h3>
    <p>Simulate £100 per pick, with unused slots held in cash. Entry uses the first shared session open after tracking starts. Price updates use completed sessions through the previous local date.</p>
    <button className="button secondary" disabled={busy} onClick={update}>
      {busy ? 'Loading…' : basket ? 'Refresh closing prices' : 'Start paper tracking'}
    </button>
    {error && <p role="alert">{error}</p>}
    {basket?.warning && <p role="status">{basket.warning}</p>}
    {basket && !latest && <p>Tracking started. Refresh after the next shared trading session has ended and its local date has rolled over.</p>}
    {latest && basket && <>
      <p><strong>{pct(latest.basket_pct)}</strong> · £{(latest.basket_pct * 20).toFixed(2)} simulated P/L · {pct(latest.basket_pct - latest.benchmark_pct)} percentage-point spread vs benchmark.</p>
      <p>Entry {basket.entry_date}. Price returns use local currency and constant FX, before dividends and trading costs. The benchmark uses SPY for US slots and ISF.L for UK slots.</p>
      <div className="market-table-scroll"><table>
        <thead><tr><th>Session</th><th>Basket since entry</th><th>Benchmark since entry</th></tr></thead>
        <tbody>{[...basket.history].reverse().map(row => <tr key={row.date}>
          <td>{row.date}</td><td>{pct(row.basket_pct)}</td><td>{pct(row.benchmark_pct)}</td>
        </tr>)}</tbody>
      </table></div>
      <details><summary>Returns by holding</summary><ul>{basket.members.map(member =>
        <li key={member.rank}>{member.symbol} · {pct(member.return_pct ?? 0)}</li>
      )}</ul></details>
    </>}
  </section>;
}

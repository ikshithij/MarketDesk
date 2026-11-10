"""Check continuity of the recorded research baseline without changing it."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / 'research/baseline.lock.json').read_text())
errors = []
for relative, expected in lock['sha256'].items():
    target = ROOT / relative
    if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        errors.append(relative)
policy = json.loads((ROOT / 'research/standard_v1.json').read_text())
registry = json.loads((ROOT / 'research/strategies_v1.json').read_text())
if policy['standard_version'] != registry['standard_version']:
    errors.append('Policy and strategy registry versions disagree')
ids = [s['id'] for s in registry['strategies']]
if len(ids) != len(set(ids)):
    errors.append('Duplicate strategy identifiers')
if errors:
    raise SystemExit('Research baseline differs from its recorded release. Review and record changes before updating the lock:\n' + '\n'.join(errors))
print('MarketDesk research standard ' + policy['standard_version'] + ' matches its recorded baseline; ' + str(len(ids)) + ' strategy definitions.')

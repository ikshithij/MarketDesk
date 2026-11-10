"""Verify the separate opinion rubric without changing the research baseline."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'research/company_ratings_v1.lock.json').read_text())
path=root/lock['path'];rubric=json.loads(path.read_text())
assert hashlib.sha256(path.read_bytes()).hexdigest()==lock['sha256'],'Rating rubric changed without a recorded version.'
assert rubric['version']==lock['version'] and rubric['id']==lock['id']
assert sum(d['weight'] for d in rubric['dimensions'])==100
assert len({d['id'] for d in rubric['dimensions']})==9
print('AI-COMPANY-001 ratings rubric '+rubric['version']+' matches its recorded baseline; opinion ratings, not validated forecasts.')

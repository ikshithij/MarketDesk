"""Reject silent edits to the separate public discovery policy."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
policy_path = root / 'research/public_screen_v1.json'
policy = json.loads(policy_path.read_text())
lock = json.loads((root / 'research/public_screen_v1.lock.json').read_text())
assert policy['id'] == lock['id'], 'Discovery model identity changed'
assert policy['version'] == lock['version'], 'Discovery model version changed'
assert hashlib.sha256(policy_path.read_bytes()).hexdigest() == lock['sha256'], 'Discovery policy changed: version and document the change explicitly'
print(f"Public discovery policy {policy['id']} v{policy['version']} unchanged")

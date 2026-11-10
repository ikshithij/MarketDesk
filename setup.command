#!/bin/zsh
set -e
cd "${0:A:h}"
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.lock.txt
npm ci
npm run build
echo 'MarketDesk is installed. Open start.command for everyday use.'

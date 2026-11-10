#!/bin/zsh
set -e
cd "${0:A:h}"
if [[ ! -x .venv/bin/python || ! -f dist/index.html ]]; then
  echo 'Run ./setup.command once to install MarketDesk.'
  read 'reply?Press Enter to close.'
  exit 1
fi
(sleep 2; open http://127.0.0.1:8000) &
echo 'MarketDesk is running locally. Keep this window open; Control-C stops it.'
.venv/bin/python -m uvicorn server.main:app --host 127.0.0.1 --port 8000

#!/usr/bin/env bash
# Runs the RAG example. Usage: ./run.sh [path/to/file.pdf]
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install -r requirements.txt
fi

exec ./.venv/bin/python main.py "$@"

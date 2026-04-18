#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "${SCRIPT_DIR}/requirements.txt" ]]; then
  APP_ROOT="${SCRIPT_DIR}"
elif [[ -f "${SCRIPT_DIR}/../../requirements.txt" ]]; then
  APP_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
else
  echo "Error: Could not locate project root from ${SCRIPT_DIR}." >&2
  exit 1
fi

cd "${APP_ROOT}"

if [[ ! -d .venv ]]; then
  echo "Error: .venv is missing. Run ./install.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"
WORKERS="${WORKERS:-1}"

exec python -m uvicorn backend.app.main:app \
  --host "${HOST}" \
  --port "${PORT}" \
  --log-level "${LOG_LEVEL}" \
  --workers "${WORKERS}"

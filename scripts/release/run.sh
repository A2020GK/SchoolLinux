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

LOCAL_IP="${LOCAL_IP:-}"

if [[ -z "${LOCAL_IP}" ]] && command -v hostname >/dev/null 2>&1; then
  LOCAL_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
fi

if [[ -z "${LOCAL_IP}" ]] && command -v ip >/dev/null 2>&1; then
  LOCAL_IP="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "src") {print $(i + 1); exit}}')"
fi

echo "Starting backend server..."
echo "Local URL:   http://localhost:${PORT}"
if [[ -n "${LOCAL_IP}" ]]; then
  echo "Network URL: http://${LOCAL_IP}:${PORT}"
else
  echo "Network URL: http://<local network ip>:${PORT}"
fi
echo
echo "Starting SL3..."
echo 
sleep 1

exec python -m uvicorn backend.app.main:app \
  --host "${HOST}" \
  --port "${PORT}" \
  --log-level "${LOG_LEVEL}" \
  --workers "${WORKERS}"

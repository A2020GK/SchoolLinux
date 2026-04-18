#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ -f "${SCRIPT_DIR}/requirements.txt" ]]; then
  APP_ROOT="${SCRIPT_DIR}"
elif [[ -f "${SCRIPT_DIR}/../../requirements.txt" ]]; then
  APP_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
else
  echo "Error: Could not locate project root from ${SCRIPT_DIR}." >&2
  exit 1
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: ${PYTHON_BIN} is not available. Install Python 3 first." >&2
  exit 1
fi

cd "${APP_ROOT}"

if [[ ! -f requirements.txt ]]; then
  echo "Error: requirements.txt was not found in ${APP_ROOT}." >&2
  exit 1
fi

if [[ ! -d .venv ]]; then
  "${PYTHON_BIN}" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

if [[ ! -f frontend/dist/index.html ]]; then
  echo "Warning: frontend/dist/index.html was not found."
  echo "The backend will still run API-only mode until frontend build is present."
fi

echo "Install completed."
echo "Run the app with: ./run.sh"

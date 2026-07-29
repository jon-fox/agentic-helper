#!/usr/bin/env bash
# Run the harness using Hermes' own uv venv, so `import run_agent` and all of
# Hermes' dependencies resolve. Our package is added via PYTHONPATH.
#
#   ./run.sh info
#   ./run.sh once "What's in ~/Downloads?"
#   ./run.sh repl
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

# Resolve the Hermes checkout: explicit env wins, else the official-installer
# location (~/.hermes/hermes-agent), else a manual clone at ~/hermes-agent.
HERMES_REPO="${HERMES_REPO:-}"
if [ -z "$HERMES_REPO" ]; then
  for d in "$HERMES_HOME/hermes-agent" "$HOME/hermes-agent"; do
    if [ -f "$d/run_agent.py" ]; then HERMES_REPO="$d"; break; fi
  done
fi
HERMES_REPO="${HERMES_REPO:-$HERMES_HOME/hermes-agent}"

if [ ! -f "$HERMES_REPO/run_agent.py" ]; then
  echo "Hermes not found at: $HERMES_REPO" >&2
  echo "Run ./scripts/install_hermes.sh, or set HERMES_REPO=/path/to/hermes-agent." >&2
  exit 2
fi

export HERMES_REPO
export PYTHONPATH="$REPO_DIR/src:${PYTHONPATH:-}"
exec uv run --project "$HERMES_REPO" python -m agentic_helper.cli "$@"

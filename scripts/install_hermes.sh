#!/usr/bin/env bash
# Set up Hermes for in-process use, then wire up this harness.
#
# Uses the OFFICIAL installer (curl install.sh | bash), which is the supported,
# current install path. It lays down a repo checkout + venv at
# ~/.hermes/hermes-agent and a `hermes` launcher on PATH. We then add our two
# extras: link the helper_tools plugin and register the Moonshot provider.
#
# Note: the pip package (`pip install hermes-agent`) is deprecated + stale and
# is intentionally NOT used here.
#
#   ./scripts/install_hermes.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
HERMES_REPO="${HERMES_REPO:-$HERMES_HOME/hermes-agent}"

if [ -f "$HERMES_REPO/run_agent.py" ]; then
  echo "==> Hermes checkout already present: $HERMES_REPO"
else
  echo "==> Installing Hermes via the official installer"
  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
fi

if [ ! -f "$HERMES_REPO/run_agent.py" ]; then
  echo "!! Expected a Hermes checkout at $HERMES_REPO but didn't find run_agent.py." >&2
  echo "   If the installer used a different location, set HERMES_REPO and re-run." >&2
  exit 1
fi

echo "==> Linking helper_tools plugin into $HERMES_HOME/plugins"
mkdir -p "$HERMES_HOME/plugins"
ln -sfn "$REPO_DIR/plugins/helper_tools" "$HERMES_HOME/plugins/helper_tools"

echo "==> Configuring Moonshot (Kimi) provider — key is pulled from \$MOONSHOT_API_KEY"
( cd "$HERMES_REPO" && uv run python "$REPO_DIR/scripts/configure_moonshot.py" )

KEY_ENV="${MOONSHOT_KEY_ENV:-MOONSHOT_API_KEY}"
cat <<EOF

Done. Hermes checkout: $HERMES_REPO
Next steps:
  1. Provide the Moonshot key (Hermes reads it from \$$KEY_ENV):
       echo '$KEY_ENV=sk-...' >> $HERMES_HOME/.env
  2. Smoke-test the harness:
       ./run.sh info
       ./run.sh once "List the files in this folder"
EOF

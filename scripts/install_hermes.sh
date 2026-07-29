#!/usr/bin/env bash
# Install the Hermes Agent (for in-process library use) and wire up this harness.
#
#   ./scripts/install_hermes.sh
#
# Override the checkout location with HERMES_REPO=/path ./scripts/install_hermes.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_REPO="${HERMES_REPO:-$HOME/hermes-agent}"

echo "==> Hermes checkout: $HERMES_REPO"
if [ ! -d "$HERMES_REPO/.git" ]; then
  git clone https://github.com/NousResearch/hermes-agent.git "$HERMES_REPO"
else
  echo "    already cloned; pulling latest (ff-only)"
  git -C "$HERMES_REPO" pull --ff-only || true
fi

echo "==> uv sync (installs Hermes' dependencies into its venv)"
( cd "$HERMES_REPO" && uv sync )

echo "==> Creating ~/.hermes layout"
mkdir -p "$HOME/.hermes"/{cron,sessions,logs,memories,skills,plugins}
if [ ! -f "$HOME/.hermes/config.yaml" ]; then
  cp "$HERMES_REPO/cli-config.yaml.example" "$HOME/.hermes/config.yaml"
  echo "    wrote ~/.hermes/config.yaml (edit model/provider as needed)"
fi
touch "$HOME/.hermes/.env"

echo "==> Linking helper_tools plugin into ~/.hermes/plugins"
ln -sfn "$REPO_DIR/plugins/helper_tools" "$HOME/.hermes/plugins/helper_tools"

echo "==> Configuring Moonshot (Kimi) provider — key is pulled from \$MOONSHOT_API_KEY"
( cd "$HERMES_REPO" && uv run python "$REPO_DIR/scripts/configure_moonshot.py" )

KEY_ENV="${MOONSHOT_KEY_ENV:-MOONSHOT_API_KEY}"
cat <<EOF

Done. Next steps:
  1. Provide the Moonshot key (Hermes reads it from \$$KEY_ENV):
       echo '$KEY_ENV=sk-...' >> ~/.hermes/.env
  2. Smoke-test the harness:
       HERMES_REPO="$HERMES_REPO" ./run.sh info
       HERMES_REPO="$HERMES_REPO" ./run.sh once "List the files in this folder"
EOF

#!/usr/bin/env python3
"""Idempotently register Moonshot (Kimi) as a custom provider in Hermes.

Writes a `moonshot` entry under `custom_providers` in ~/.hermes/config.yaml and
makes it the default model. The API key is NOT stored in config — Hermes reads
it at runtime from an environment variable (`key_env`), so the secret stays out
of the config file. Set that env var in ~/.hermes/.env or your shell.

Override defaults via env when running:
    MOONSHOT_MODEL=kimi-k2-0905-preview \
    MOONSHOT_BASE_URL=https://api.moonshot.ai/v1 \
    MOONSHOT_KEY_ENV=MOONSHOT_API_KEY \
    uv run python scripts/configure_moonshot.py
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml  # provided by Hermes' venv

CONFIG = Path.home() / ".hermes" / "config.yaml"
BASE_URL = os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
MODEL = os.environ.get("MOONSHOT_MODEL", "kimi-k2-0905-preview")
KEY_ENV = os.environ.get("MOONSHOT_KEY_ENV", "MOONSHOT_API_KEY")


def main() -> int:
    data = {}
    if CONFIG.exists():
        data = yaml.safe_load(CONFIG.read_text()) or {}

    # Replace any existing 'moonshot' entry (idempotent), keep the rest.
    providers = [
        p for p in (data.get("custom_providers") or []) if p.get("name") != "moonshot"
    ]
    providers.append(
        {
            "name": "moonshot",
            "base_url": BASE_URL,
            "key_env": KEY_ENV,  # <- key is pulled from this env var, not stored here
            "api_mode": "chat_completions",
        }
    )
    data["custom_providers"] = providers

    model = data.get("model") or {}
    model["provider"] = "moonshot"
    model["default"] = MODEL
    data["model"] = model

    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(yaml.safe_dump(data, sort_keys=False))

    print(
        f"✓ moonshot provider set: base_url={BASE_URL}, model={MODEL}, key_env={KEY_ENV}"
    )
    if not os.environ.get(KEY_ENV):
        print(
            f"  ⚠  ${KEY_ENV} is not set yet — add it to ~/.hermes/.env before running the agent."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import os
from pathlib import Path

import yaml

CONFIG = Path.home() / ".hermes" / "config.yaml"


def main() -> int:
    data = {}
    if CONFIG.exists():
        data = yaml.safe_load(CONFIG.read_text()) or {}

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

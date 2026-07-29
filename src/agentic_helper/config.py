"""Harness settings, sourced from environment variables (and an optional .env).

Note: these configure the *harness*. LLM provider secrets (API keys) live in
~/.hermes/.env and are read by Hermes itself — you generally don't set them here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:  # optional: load a local .env if python-dotenv is available
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a convenience, not a requirement
    pass


def _split(csv: str | None) -> list[str] | None:
    if not csv:
        return None
    items = [x.strip() for x in csv.split(",") if x.strip()]
    return items or None


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    """Everything the Harness needs to construct an AIAgent."""

    model: str = ""  # empty -> Hermes resolves from ~/.hermes/config.yaml
    provider: str | None = None
    api_mode: str | None = None
    base_url: str | None = None
    api_key: str | None = None  # optional; Hermes also reads ~/.hermes/.env
    enabled_toolsets: list[str] | None = None  # allowlist; None = Hermes default
    disabled_toolsets: list[str] | None = None  # denylist
    max_iterations: int = 40
    system_prompt: str | None = None
    save_trajectories: bool = False
    quiet: bool = True  # suppress Hermes' own console chatter for clean output
    skip_memory: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model=os.environ.get("HELPER_MODEL", ""),
            provider=os.environ.get("HELPER_PROVIDER") or None,
            api_mode=os.environ.get("HELPER_API_MODE") or None,
            base_url=os.environ.get("HELPER_BASE_URL") or None,
            api_key=os.environ.get("HELPER_API_KEY") or None,
            enabled_toolsets=_split(os.environ.get("HELPER_TOOLSETS")),
            disabled_toolsets=_split(os.environ.get("HELPER_DISABLED_TOOLSETS")),
            max_iterations=int(os.environ.get("HELPER_MAX_ITERATIONS", "40")),
            system_prompt=os.environ.get("HELPER_SYSTEM_PROMPT") or None,
            save_trajectories=_bool(os.environ.get("HELPER_SAVE_TRAJECTORIES")),
            quiet=_bool(os.environ.get("HELPER_QUIET"), default=True),
            skip_memory=_bool(os.environ.get("HELPER_SKIP_MEMORY")),
        )

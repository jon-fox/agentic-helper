"""Locate a Hermes Agent checkout and make `import run_agent` work.

Hermes is used as a library by importing its top-level `run_agent` module
(`from run_agent import AIAgent`). That module lives at the repo root, so we
add the repo root to sys.path. Dependencies are expected to already be present
in the active interpreter (see run.sh, which runs us inside Hermes' uv venv).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _candidate_locations() -> list[str]:
    hermes_home = os.environ.get("HERMES_HOME") or str(Path.home() / ".hermes")
    return [
        loc
        for loc in (
            os.environ.get("HERMES_REPO"),
            str(Path(hermes_home) / "hermes-agent"),  # official installer lands here
            str(Path.home() / "hermes-agent"),  # manual `git clone` default
            str(Path(__file__).resolve().parents[2] / "vendor" / "hermes-agent"),
        )
        if loc
    ]


def find_hermes_repo() -> Path | None:
    """Return the first checkout that contains run_agent.py, or None."""
    for loc in _candidate_locations():
        p = Path(loc).expanduser()
        if (p / "run_agent.py").is_file():
            return p
    return None


def ensure_hermes_importable() -> Path:
    """Ensure `run_agent` is importable; return the Hermes repo root.

    Raises RuntimeError with actionable guidance if no checkout is found.
    """
    try:
        import run_agent  # noqa: F401  (already on the path / installed)

        return Path(run_agent.__file__).resolve().parent
    except ModuleNotFoundError:
        pass

    repo = find_hermes_repo()
    if repo is None:
        raise RuntimeError(
            "Could not locate a Hermes Agent checkout (no run_agent.py found).\n"
            "Fix one of:\n"
            "  • export HERMES_REPO=/path/to/hermes-agent\n"
            "  • run ./scripts/install_hermes.sh (clones + uv sync)\n"
            "Then run the harness via ./run.sh so it uses Hermes' venv."
        )

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    return repo

"""Tool handlers — what actually runs when the LLM calls a tool.

Hermes contract: a handler receives the parsed `args` dict (plus **kwargs such
as task_id) and MUST return a JSON string. Keep them defensive — return a
structured {"success": false, "error": ...} rather than raising.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

NOTES_FILE = Path.home() / ".hermes" / "helper_notes.md"


def save_note(args: dict, **kwargs) -> str:
    text = (args.get("text") or "").strip()
    if not text:
        return json.dumps({"success": False, "error": "text is required"})

    tag = (args.get("tag") or "").strip()
    prefix = f"[{tag}] " if tag else ""
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with NOTES_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"- {prefix}{text}\n")

    return json.dumps({"success": True, "file": str(NOTES_FILE)})


def list_dir(args: dict, **kwargs) -> str:
    path = Path(args.get("path") or os.getcwd()).expanduser()
    if not path.exists():
        return json.dumps({"success": False, "error": f"no such path: {path}"})
    if not path.is_dir():
        return json.dumps({"success": False, "error": f"not a directory: {path}"})

    try:
        entries = sorted(
            ("dir" if child.is_dir() else "file", child.name)
            for child in path.iterdir()
        )
    except PermissionError:
        return json.dumps({"success": False, "error": f"permission denied: {path}"})

    return json.dumps(
        {
            "success": True,
            "path": str(path),
            "entries": [{"type": kind, "name": name} for kind, name in entries],
        }
    )


def on_post_tool_call(tool_name, args, result, task_id=None, **kwargs) -> None:
    """Lifecycle hook — fires after every tool call across the whole agent."""
    logger.debug("post_tool_call: %s (task=%s)", tool_name, task_id)

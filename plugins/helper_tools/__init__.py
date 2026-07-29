"""helper_tools — a custom Hermes plugin for the agentic-helper harness.

Hermes discovers plugins from ~/.hermes/plugins/<name>/. Each plugin needs a
plugin.yaml manifest and this register(ctx) function, which wires tool schemas
(what the LLM sees) to handlers (what runs).
"""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)


def register(ctx) -> None:
    ctx.register_tool(
        name="save_note",
        toolset="helper",
        schema=schemas.SAVE_NOTE,
        handler=tools.save_note,
    )
    ctx.register_tool(
        name="list_dir",
        toolset="helper",
        schema=schemas.LIST_DIR,
        handler=tools.list_dir,
    )
    # Fires after every tool call (all tools, not just ours) — handy for audit.
    ctx.register_hook("post_tool_call", tools.on_post_tool_call)
    logger.info("helper_tools registered: save_note, list_dir (toolset 'helper')")

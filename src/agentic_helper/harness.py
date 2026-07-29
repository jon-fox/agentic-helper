"""Harness: a thin, stateful wrapper around Hermes' AIAgent.

Design goals:
  • Keep a stable, small surface (ask / chat_once / reset / info).
  • Thread multi-turn context automatically via run_conversation's message list.
  • Fail loudly with actionable errors if Hermes isn't installed.

AIAgent contract used here (from Hermes' public Python API):
  chat(message: str) -> str
  run_conversation(user_message, system_message=None,
                   conversation_history=None, task_id=None)
      -> {"final_response": str, "messages": list}
"""

from __future__ import annotations

from typing import Any

from .bootstrap import ensure_hermes_importable
from .config import Settings


class Harness:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        # Put Hermes on the path *before* importing run_agent.
        self.repo = ensure_hermes_importable()
        from run_agent import AIAgent  # noqa: E402 - deferred until path is set

        self._AIAgent = AIAgent
        self._agent = self._build_agent()
        self.history: list[dict[str, Any]] = []

    def _build_agent(self):
        s = self.settings
        return self._AIAgent(
            model=s.model,
            provider=s.provider,
            api_mode=s.api_mode,
            base_url=s.base_url,
            api_key=s.api_key,
            enabled_toolsets=s.enabled_toolsets,
            disabled_toolsets=s.disabled_toolsets,
            max_iterations=s.max_iterations,
            save_trajectories=s.save_trajectories,
            quiet_mode=s.quiet,
            skip_memory=s.skip_memory,
            platform="agentic-helper",
        )

    # --- interaction -------------------------------------------------------

    def ask(self, message: str) -> str:
        """Run one multi-turn-aware step; preserves history across calls."""
        result = self._agent.run_conversation(
            user_message=message,
            system_message=self.settings.system_prompt,
            conversation_history=self.history or None,
        )
        # Persist the full message list so the next turn has context.
        self.history = result.get("messages", self.history)
        return result.get("final_response", "")

    def chat_once(self, message: str) -> str:
        """Stateless single-shot using the simple chat() interface."""
        return self._agent.chat(message)

    def reset(self) -> None:
        """Start a fresh conversation thread."""
        self.history = []

    # --- introspection -----------------------------------------------------

    def info(self) -> dict[str, Any]:
        s = self.settings
        return {
            "hermes_repo": str(self.repo),
            "model": s.model or "(from ~/.hermes/config.yaml)",
            "provider": s.provider or "(from ~/.hermes/config.yaml)",
            "enabled_toolsets": s.enabled_toolsets or "(Hermes default)",
            "disabled_toolsets": s.disabled_toolsets or [],
            "max_iterations": s.max_iterations,
            "history_len": len(self.history),
        }

"""Command-line entry point for the agentic-helper harness.

Subcommands:
  once "<message>"   Send one message, print the reply. --stateless for chat().
  repl               Interactive multi-turn session.
  info               Show resolved config + Hermes repo location.
"""

from __future__ import annotations

import argparse
import sys

from .config import Settings
from .harness import Harness

try:  # pretty output if rich is available, plain otherwise
    from rich.console import Console
    from rich.markdown import Markdown

    _console = Console()

    def _out(text: str) -> None:
        _console.print(Markdown(text))

    def _err(text: str) -> None:
        _console.print(f"[red]{text}[/red]")

except Exception:  # pragma: no cover

    def _out(text: str) -> None:
        print(text)

    def _err(text: str) -> None:
        print(text, file=sys.stderr)


def _build_harness() -> Harness:
    try:
        return Harness(Settings.from_env())
    except RuntimeError as exc:
        _err(str(exc))
        raise SystemExit(2)


def cmd_once(args: argparse.Namespace) -> int:
    helper = _build_harness()
    print(helper.chat_once(args.message) if args.stateless else helper.ask(args.message))
    return 0


def cmd_repl(args: argparse.Namespace) -> int:
    helper = _build_harness()
    _out("**agentic-helper** — commands: `/reset` `/info` `/quit` (or Ctrl-D)")
    while True:
        try:
            line = input("\nyou › ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if line in ("/quit", "/exit"):
            return 0
        if line == "/reset":
            helper.reset()
            _out("_history cleared_")
            continue
        if line == "/info":
            for key, value in helper.info().items():
                print(f"  {key}: {value}")
            continue
        try:
            reply = helper.ask(line)
        except Exception as exc:  # keep the REPL alive through model/tool errors
            _err(f"error: {exc}")
            continue
        _out(reply)


def cmd_info(args: argparse.Namespace) -> int:
    helper = _build_harness()
    for key, value in helper.info().items():
        print(f"{key}: {value}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentic-helper",
        description="In-process harness around the Hermes Agent.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_once = sub.add_parser("once", help="Send a single message and print the reply.")
    p_once.add_argument("message")
    p_once.add_argument(
        "--stateless",
        action="store_true",
        help="Use chat() instead of the threaded run_conversation().",
    )
    p_once.set_defaults(func=cmd_once)

    p_repl = sub.add_parser("repl", help="Interactive multi-turn session.")
    p_repl.set_defaults(func=cmd_repl)

    p_info = sub.add_parser("info", help="Show resolved config + Hermes repo location.")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

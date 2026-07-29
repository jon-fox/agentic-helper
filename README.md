# agentic-helper

A thin, in-process **harness** that wraps the [Nous Research Hermes Agent](https://github.com/NousResearch/hermes-agent) for daily tasks.

It embeds Hermes' stable `AIAgent` Python class directly (no server), threads
multi-turn conversation context for you, lets you control which toolsets the
agent may use, and ships a custom tool plugin as an example of extending it.

## How it fits together

```
your code / CLI
      │  Harness.ask(...)
      ▼
agentic_helper.Harness ──imports──► run_agent.AIAgent   (Hermes, in-process)
                                        │
                                        ├─ built-in toolsets: web, file, terminal, memory, …
                                        └─ ~/.hermes/plugins/helper_tools  (custom: save_note, list_dir)
```

- **Harness** (`src/agentic_helper/harness.py`) — wraps `AIAgent`; `ask()` uses
  `run_conversation()` and keeps the returned message list so context persists.
- **bootstrap** — finds your Hermes checkout and puts `run_agent` on `sys.path`.
- **config** — `Settings.from_env()` reads `HELPER_*` vars (and a local `.env`).
- **helper_tools plugin** — a real Hermes plugin (`plugin.yaml` + `register(ctx)`).

## Setup

Hermes runs from source (it discovers tools by importing repo modules), so it
needs a checkout. Rather than clone by hand, `install_hermes.sh` uses Hermes'
**official installer** — the supported, current path — which lays down a checkout
+ venv at `~/.hermes/hermes-agent`. (The `pip install hermes-agent` package is
deprecated and stale, so we don't use it.)

```bash
./scripts/install_hermes.sh          # official installer + link plugin + configure Moonshot
echo 'MOONSHOT_API_KEY=sk-...' >> ~/.hermes/.env      # Hermes pulls the key from this env var
cp .env.example .env                 # optional: override model/provider/toolsets per-run
```

The installer registers **Moonshot (Kimi)** as a custom provider whose API key is
read from `$MOONSHOT_API_KEY` — the key is never written into config. Change the
model with `MOONSHOT_MODEL=...` before running it, or edit `~/.hermes/config.yaml`
afterward. If you already have a checkout elsewhere, set `HERMES_REPO=/path`.

## Usage

Always run via `./run.sh` — it executes the harness inside Hermes' uv venv so
all of Hermes' dependencies resolve:

```bash
./run.sh info                          # show resolved config + Hermes location
./run.sh once "List the files here"    # single message, threaded
./run.sh once --stateless "hello"      # single-shot AIAgent.chat()
./run.sh repl                          # interactive: /reset  /info  /quit
```

Or embed it in your own Python (run inside Hermes' venv):

```python
from agentic_helper import Harness, Settings

helper = Harness(Settings(enabled_toolsets=["file", "helper"]))
print(helper.ask("Save a note tagged 'todo': buy milk"))
print(helper.ask("Now list the notes file's folder"))   # remembers context
```

## Configuration (`HELPER_*` env / `.env`)

| Variable | Purpose | Default |
|---|---|---|
| `HERMES_REPO` | Path to the Hermes checkout | `~/hermes-agent` |
| `HELPER_MODEL` | Model id (blank = Hermes config) | — |
| `HELPER_PROVIDER` | Provider id (blank = Hermes config) | — |
| `HELPER_TOOLSETS` | Allowlist, comma-separated | Hermes default |
| `HELPER_DISABLED_TOOLSETS` | Denylist, comma-separated | — |
| `HELPER_MAX_ITERATIONS` | Tool-calling loop cap | `40` |
| `HELPER_SYSTEM_PROMPT` | System message | — |
| `HELPER_QUIET` | Suppress Hermes console chatter | `true` |

LLM API keys are **not** set here — they live in `~/.hermes/.env`.

## The custom plugin

`plugins/helper_tools/` is symlinked into `~/.hermes/plugins/` by the installer:

- `save_note(text, tag?)` — appends to `~/.hermes/helper_notes.md`
- `list_dir(path?)` — read-only directory listing

Enable it by including `helper` in `HELPER_TOOLSETS`. Add your own tools by
editing `schemas.py` (what the model sees) and `tools.py` (what runs), then
wiring them in `__init__.py`'s `register(ctx)`.

"""agentic-helper: a thin, in-process harness around the Hermes Agent.

The public surface is intentionally tiny:

    from agentic_helper import Harness, Settings

    helper = Harness(Settings.from_env())
    print(helper.ask("What files are in this folder?"))
"""

from .config import Settings
from .harness import Harness

__all__ = ["Settings", "Harness"]
__version__ = "0.1.0"

import os
from pathlib import Path

MOONSHOT_BASE_URL = os.environ.get("MOONSHOT_BASE_URL") 
MOONSHOT_API_KEY = os.environ.get("MOONSHOT_API_KEY")

# using relative path here from hermes
HERMES_CONFIG = Path.home() / ".hermes" / "config.yaml"

KIMI_K_2_6 = "kimi-k2.6"

BASE_MODEL =  KIMI_K_2_6
ROUTING_MODEL = KIMI_K_2_6
INTENT_MODEL = KIMI_K_2_6
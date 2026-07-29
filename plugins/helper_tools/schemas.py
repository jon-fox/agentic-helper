"""Tool schemas — the JSON descriptions the LLM reads to decide when/how to call.

Keep descriptions crisp and action-oriented: the model only knows what you write
here, so state exactly when to use the tool and what each parameter means.
"""

SAVE_NOTE = {
    "name": "save_note",
    "description": (
        "Append a short note to the user's persistent notes file "
        "(~/.hermes/helper_notes.md). Use when the user asks you to remember, "
        "jot down, or save something for later."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "The note content to save."},
            "tag": {
                "type": "string",
                "description": "Optional short category tag, e.g. 'idea' or 'todo'.",
            },
        },
        "required": ["text"],
    },
}

LIST_DIR = {
    "name": "list_dir",
    "description": (
        "List files and folders in a directory on the local machine (read-only). "
        "Use to inspect the workspace before acting on files."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory to list. Defaults to the current working directory.",
            },
        },
        "required": [],
    },
}

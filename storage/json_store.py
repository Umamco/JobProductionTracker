# handles all reading/writing to your JSON data files (jobs, staff, logs).

import json
import os
from typing import Any


def ensure_directory(path: str) -> None:
    """Ensure the parent folder of a file path exists."""
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def load_json(file_path: str, default: Any) -> Any:
    """Load JSON data from file_path, or return default if not found/invalid."""
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(file_path: str, data: Any) -> None:
    """Save Python data as JSON with indentation."""
    ensure_directory(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

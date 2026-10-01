"""
ResolveAI Environment Loader
Safely loads .env and .env.local configuration files from project root into os.environ.
Zero third-party dependencies required.
"""

import os
from pathlib import Path

def load_env_files():
    """
    Search for .env and .env.local in project root or current working directory
    and load non-existing keys into os.environ.
    """
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    possible_paths = [
        root_dir / ".env.local",
        root_dir / ".env",
        Path.cwd() / ".env.local",
        Path.cwd() / ".env",
    ]

    for env_path in possible_paths:
        if env_path.exists() and env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        # Do not overwrite already set environment variables
                        if key and key not in os.environ:
                            os.environ[key] = val
            except Exception:
                pass

# Automatically load when imported
load_env_files()

from pathlib import Path
from typing import Any
import yaml

def load_config(path: str | Path = "config/config.yaml") -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    if cfg.get("project", {}).get("seed") is None:
        raise ValueError("project.seed is required")
    return cfg

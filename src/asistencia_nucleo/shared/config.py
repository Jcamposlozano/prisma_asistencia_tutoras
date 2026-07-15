"""Carga de configuración (configs/base.yaml + override por ENV)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_ROOT = Path(__file__).resolve().parents[3]


def deep_merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(config_dir: str | None = None) -> dict[str, Any]:
    base_dir = Path(config_dir) if config_dir else _ROOT / "configs"
    env = os.getenv("ENV", "dev").lower()
    with (base_dir / "base.yaml").open(encoding="utf-8") as f:
        cfg: dict[str, Any] = yaml.safe_load(f) or {}
    env_path = base_dir / f"{env}.yaml"
    if env_path.exists():
        with env_path.open(encoding="utf-8") as f:
            cfg = deep_merge(cfg, yaml.safe_load(f) or {})

    cfg.setdefault("umbrales", {}).setdefault("presente_min", 60)
    cfg["umbrales"].setdefault("parcial_min", 29)
    cfg.setdefault("matching", {}).setdefault("umbral_auto", 90)
    cfg["matching"].setdefault("umbral_revisar", 70)
    return cfg

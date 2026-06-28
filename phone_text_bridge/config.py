"""Configuration for phone-text-bridge."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"


@dataclass(frozen=True)
class BridgeConfig:
    host: str
    port: int
    ssl_certfile: str
    ssl_keyfile: str


def load_config() -> BridgeConfig:
    load_dotenv(ENV_PATH)
    return BridgeConfig(
        host=os.getenv("BRIDGE_HOST", "0.0.0.0").strip(),
        port=int(os.getenv("BRIDGE_PORT", "8766")),
        ssl_certfile=os.getenv("BRIDGE_SSL_CERTFILE", "").strip(),
        ssl_keyfile=os.getenv("BRIDGE_SSL_KEYFILE", "").strip(),
    )


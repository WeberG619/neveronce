"""Imprint — Persistent, correctable memory for AI.

The memory layer that learns from mistakes.
"""

__version__ = "0.1.0"

from .memory import Memory
from .db import ImprintDB

__all__ = ["Memory", "ImprintDB"]

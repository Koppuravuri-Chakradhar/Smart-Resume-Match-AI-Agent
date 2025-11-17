"""
Lightweight session state manager for passing data between agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SessionState:
    """In-memory store shared across agents for a single orchestration run."""

    data: Dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        """Persist a value under a key."""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve value from the state store."""
        return self.data.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        """Return a shallow copy of the state."""
        return dict(self.data)


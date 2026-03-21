"""Session management with undo/redo.

Tracks command history for undo/redo operations.
Since FFmpeg is stateless (no project file), session tracks
the commands executed for replay capability.
"""

import copy
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CommandEntry:
    """A single command entry in session history."""

    action: str
    args: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "args": self.args,
            "result": self.result,
            "timestamp": self.timestamp,
        }


class Session:
    """Session state tracker for undo/redo."""

    def __init__(self):
        self._history: List[CommandEntry] = []
        self._undo_stack: List[CommandEntry] = []
        self._current_index: int = -1

    def record(self, action: str, args: Dict[str, Any], result: Optional[Dict[str, Any]] = None):
        """Record a command execution.

        Args:
            action: Command action name.
            args: Command arguments.
            result: Execution result.
        """
        import time
        entry = CommandEntry(
            action=action,
            args=copy.deepcopy(args),
            result=copy.deepcopy(result) if result else None,
            timestamp=time.time(),
        )
        # Clear redo stack when new command is recorded
        self._undo_stack.clear()
        self._history.append(entry)
        self._current_index = len(self._history) - 1

    def undo(self) -> Optional[CommandEntry]:
        """Undo the last command.

        Returns:
            The undone command entry, or None if nothing to undo.
        """
        if not self._history:
            return None

        entry = self._history.pop()
        self._undo_stack.append(entry)
        self._current_index = len(self._history) - 1
        return entry

    def redo(self) -> Optional[CommandEntry]:
        """Redo the last undone command.

        Returns:
            The redone command entry, or None if nothing to redo.
        """
        if not self._undo_stack:
            return None

        entry = self._undo_stack.pop()
        self._history.append(entry)
        self._current_index = len(self._history) - 1
        return entry

    def history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get command history.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            List of command entry dicts.
        """
        entries = self._history
        if limit:
            entries = entries[-limit:]
        return [e.to_dict() for e in entries]

    def status(self) -> Dict[str, Any]:
        """Get session status.

        Returns:
            Dict with session state info.
        """
        return {
            "total_commands": len(self._history),
            "undo_available": len(self._history) > 0,
            "redo_available": len(self._undo_stack) > 0,
            "current_index": self._current_index,
        }

    def clear(self):
        """Clear all history."""
        self._history.clear()
        self._undo_stack.clear()
        self._current_index = -1

    def save(self, path: str):
        """Save session to file.

        Args:
            path: File path to save to.
        """
        data = {
            "history": [e.to_dict() for e in self._history],
            "undo_stack": [e.to_dict() for e in self._undo_stack],
        }
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str):
        """Load session from file.

        Args:
            path: File path to load from.
        """
        with open(path, "r") as f:
            data = json.load(f)

        self._history = [
            CommandEntry(
                action=e["action"],
                args=e["args"],
                result=e.get("result"),
                timestamp=e.get("timestamp", 0.0),
            )
            for e in data.get("history", [])
        ]
        self._undo_stack = [
            CommandEntry(
                action=e["action"],
                args=e["args"],
                result=e.get("result"),
                timestamp=e.get("timestamp", 0.0),
            )
            for e in data.get("undo_stack", [])
        ]
        self._current_index = len(self._history) - 1


# Global session instance
_session: Optional[Session] = None


def get_session() -> Session:
    """Get or create the global session instance."""
    global _session
    if _session is None:
        _session = Session()
    return _session

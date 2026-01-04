from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ShareInfo:
    """Represents share information for a security in the portfolio"""

    target: float = 0.0
    actual: float = 0.0
    final: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Serialize ShareInfo to a plain dict."""
        return {
            "target": float(self.target),
            "actual": float(self.actual),
            "final": float(self.final),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ShareInfo":
        """Create ShareInfo from a dict, tolerates missing keys."""
        si = ShareInfo()
        if not isinstance(d, dict):
            return si
        try:
            si.target = float(d.get("target", si.target))
            si.actual = float(d.get("actual", si.actual))
            si.final = float(d.get("final", si.final))
        except Exception:
            pass
        return si

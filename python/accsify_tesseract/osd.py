"""
Orientation and Script Detection (OSD).
=======================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OrientationScriptResult:
    """Result of an Orientation and Script Detection (OSD) analysis."""
    orientation_deg: int
    orientation_confidence: float
    script_name: str
    script_confidence: float

    @property
    def is_upright(self) -> bool:
        """True if the text is right-side up (0 degrees orientation)."""
        return self.orientation_deg == 0

    def __repr__(self) -> str:
        return (
            f"<OrientationScriptResult orient={self.orientation_deg}° (conf={self.orientation_confidence:.2f}), "
            f"script='{self.script_name}' (conf={self.script_confidence:.2f})>"
        )

"""
DEPRECATED: This module is deprecated and will be removed in future versions.
Use src.domain.entities instead.

This file now re-exports from the new domain layer for backward compatibility.
"""

# Re-export from new domain layer
from src.domain.entities.video_analysis import (
    AudioContext,
    VisualBeat,
    Voiceover,
    Beat,
    Overall,
    VideoAnalysis
)

# Maintain backward compatibility
__all__ = [
    "AudioContext",
    "VisualBeat",
    "Voiceover",
    "Beat",
    "Overall",
    "VideoAnalysis"
]

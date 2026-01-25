"""
Domain entities - Pure business models with no framework dependencies
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class AudioContext(BaseModel):
    dialogue_brief: Optional[str] = None
    sound_cues: List[str] = Field(default_factory=list)


class VisualBeat(BaseModel):
    """Stage 1 Output - Visual timeline"""
    id: int
    start_s: float
    end_s: float
    visual_description: str
    camera_movement: Optional[str] = None


class Voiceover(BaseModel):
    """Voiceover configuration for a beat"""
    script: Optional[str] = None
    subtitle: Optional[str] = None
    pause_after_s: Optional[float] = 0.0  # Dramatic pause after this voiceover


class Beat(BaseModel):
    """Narrative beat with timing and content"""
    id: Optional[int] = None
    start_s: Optional[float] = None
    end_s: Optional[float] = None
    visual_summary: Optional[str] = None
    key_visuals: List[str] = Field(default_factory=list)
    on_screen_text: Optional[str] = None
    audio_context: Optional[AudioContext] = None
    voiceover: Optional[Voiceover] = None


class Overall(BaseModel):
    """Overall video metadata and narrative"""
    hook: Optional[str] = None
    one_sentence_summary: Optional[str] = None
    tone: Optional[str] = None
    content_warnings: List[str] = Field(default_factory=list)
    full_narrative_script: Optional[str] = None  # Complete narrative for entire video


class VideoAnalysis(BaseModel):
    """Complete video analysis with narrative beats"""
    language: Optional[str] = "es"
    duration_s: Optional[float] = 0.0
    overall: Optional[Overall] = None
    visual_timeline: List[VisualBeat] = Field(default_factory=list)  # Raw visual analysis
    beats: List[Beat] = Field(default_factory=list)  # Final narrated beats
    final_cta: Optional[str] = None

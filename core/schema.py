from typing import List, Optional
from pydantic import BaseModel, Field

class AudioContext(BaseModel):
    dialogue_brief: Optional[str] = None
    sound_cues: List[str] = Field(default_factory=list)

# Stage 1 Output
class VisualBeat(BaseModel):
    id: int
    start_s: float
    end_s: float
    visual_description: str
    camera_movement: Optional[str] = None
    
# Stage 2 Output (and final)
class Voiceover(BaseModel):
    script: Optional[str] = None
    subtitle: Optional[str] = None

class Beat(BaseModel):
    id: Optional[int] = None
    start_s: Optional[float] = None
    end_s: Optional[float] = None
    visual_summary: Optional[str] = None
    key_visuals: List[str] = Field(default_factory=list)
    on_screen_text: Optional[str] = None
    audio_context: Optional[AudioContext] = None
    voiceover: Optional[Voiceover] = None

class Overall(BaseModel):
    hook: Optional[str] = None
    one_sentence_summary: Optional[str] = None
    tone: Optional[str] = None
    content_warnings: List[str] = Field(default_factory=list)

class VideoAnalysis(BaseModel):
    language: Optional[str] = "es"
    duration_s: Optional[float] = 0.0
    overall: Optional[Overall] = None
    visual_timeline: List[VisualBeat] = Field(default_factory=list) # Raw visual analysis
    beats: List[Beat] = Field(default_factory=list) # Final narrated beats
    final_cta: Optional[str] = None

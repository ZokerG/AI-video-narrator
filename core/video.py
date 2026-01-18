from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from typing import List
import os
import tempfile
import numpy as np
from scipy.io import wavfile

def check_video_duration(video_path: str) -> float:
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.close()
    return duration

def mix_audio_with_video(
    video_path: str, 
    audio_map: List[dict], 
    output_path: str, 
    keep_original_audio: bool = True,
    original_volume_factor: float = 1.0
):
    """
    Combina el video con los archivos de narración TTS.
    
    Args:
        video_path: Path to original video
        audio_map: List of dicts { 'path': str, 'start_s': float }
        output_path: Where to save final video
        keep_original_audio: Whether to include the original video sound
        original_volume_factor: Volume factor for original audio (0.0 to 1.0)
    """
    video = VideoFileClip(video_path)
    original_audio = video.audio
    
    audio_clips = []
    
    # ALWAYS add TTS narration clips first
    for item in audio_map:
        if os.path.exists(item['path']):
            # Create AudioFileClip
            audioclip = AudioFileClip(item['path'])
            # Set start time (MoviePy v2.0 uses with_start)
            audioclip = audioclip.with_start(item['start_s'])
            audio_clips.append(audioclip)
        else:
            print(f"Warning: Audio file {item['path']} not found.")
    
    # THEN conditionally add original audio with volume control
    if keep_original_audio and original_audio:
        # Apply volume factor if different from 1.0
        if original_volume_factor != 1.0:
            # Export to temporary WAV, modify volume, and reload
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = temp_audio.name
            temp_audio.close()
            
            try:
                # Export original audio to WAV
                original_audio.write_audiofile(temp_path, fps=44100, nbytes=2, codec='pcm_s16le', logger=None)
                
                # Read WAV file
                sample_rate, audio_data = wavfile.read(temp_path)
                
                # Multiply by volume factor
                audio_data = (audio_data * original_volume_factor).astype(audio_data.dtype)
                
                # Write modified audio
                wavfile.write(temp_path, sample_rate, audio_data)
                
                # Load modified audio
                original_audio = AudioFileClip(temp_path)
                print(f"   🔊 Original audio volume adjusted to {original_volume_factor*100:.0f}%")
            except Exception as e:
                print(f"   ⚠️ Warning: Could not adjust volume, using original: {e}")
                # If volume adjustment fails, use original audio as-is
            finally:
                # Clean up temp file if it still exists
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass
        
        audio_clips.append(original_audio)

    if audio_clips:
        final_audio = CompositeAudioClip(audio_clips)
        # MoviePy v2.0 uses with_audio
        final_video = video.with_audio(final_audio)
    else:
        # No audio (no TTS generated at all)
        final_video = video.without_audio()
    
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    video.close()

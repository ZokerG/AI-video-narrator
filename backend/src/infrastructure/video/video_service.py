from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
from typing import List, Optional
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
    original_volume_factor: float = 1.0,
    background_track_path: Optional[str] = None,
    background_volume_factor: float = 0.1
):
    """
    Combina el video con los archivos de narración TTS y música de fondo opcional.
    
    Args:
        video_path: Path to original video
        audio_map: List of dicts { 'path': str, 'start_s': float }
        output_path: Where to save final video
        keep_original_audio: Whether to include the original video sound
        original_volume_factor: Volume factor for original audio (0.0 to 1.0)
        background_track_path: Path to background music file
        background_volume_factor: Volume for background music (0.0 to 1.0, default 0.1)
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
    
    # ADD Background Music if provided
    if background_track_path and os.path.exists(background_track_path):
        try:
            bg_music = AudioFileClip(background_track_path)
            
            # Loop if shorter than video
            if bg_music.duration < video.duration:
                # Calculate number of loops needed
                repeats = int(np.ceil(video.duration / bg_music.duration))
                bg_music = concatenate_audioclips([bg_music] * repeats)
            
            # Trim to video duration
            bg_music = bg_music.subclipped(0, video.duration)
            
            # Adjust volume (Available in MoviePy v1 as volumex, v2 might differ but audio_fadein usually works)
            # We will use the same manual numpy approach as original audio to be safe and consistent
            # Export to temp wav to adjust volume reliably
            temp_bg = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            bg_temp_path = temp_bg.name
            temp_bg.close()
            
            bg_music.write_audiofile(bg_temp_path, fps=44100, nbytes=2, codec='pcm_s16le', logger=None)
            
            # Read and adjust volume
            sr, bg_data = wavfile.read(bg_temp_path)
            bg_data = (bg_data * background_volume_factor).astype(bg_data.dtype)
            wavfile.write(bg_temp_path, sr, bg_data)
            
            # Load back
            bg_music_final = AudioFileClip(bg_temp_path)
            audio_clips.append(bg_music_final)
            print(f"   🎵 Added background track: {os.path.basename(background_track_path)} (Vol: {background_volume_factor*100:.0f}%)")
            
            # Clean up later handled by OS or maybe we should track it
        except Exception as e:
            print(f"   ⚠️ Error processing background music: {e}")
    
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

def create_reel_video(
    scenes: List[dict],
    audio_map: List[dict],
    output_path: str,
    background_track: Optional[str] = None
):
    """
    Creates a vertical Reel/Short from images and audio.
    OPTIMIZED for speed - reduced resolution, no dynamic effects.
    """
    from moviepy import ImageClip, CompositeVideoClip, ColorClip
    
    clips = []
    current_time = 0.0
    
    # 9:16 Aspect Ratio - REDUCED for speed (720x1280 instead of 1080x1920)
    W, H = 720, 1280
    
    for i, scene in enumerate(scenes):
        img_path = scene.get('image_path')
        duration = scene.get('duration_estimate', 3.0)
        
        # Audio for this scene
        if i < len(audio_map):
            audio_info = audio_map[i]
            if 'duration' in audio_info:
                duration = audio_info['duration']
        
        if not img_path or not os.path.exists(img_path):
            print(f"⚠️ Image not found for scene {i}: {img_path}")
            clip = ColorClip(size=(W, H), color=(0,0,0), duration=duration)
        else:
            # Create Image Clip - SIMPLIFIED (no dynamic zoom)
            clip = ImageClip(img_path).with_duration(duration)
            
            # Resize to cover screen
            img_w, img_h = clip.size
            ratio = img_w / img_h
            target_ratio = W / H
            
            if ratio > target_ratio:
                new_h = H
                new_w = int(img_w * (H / img_h))
                clip = clip.resized(height=H)
            else:
                new_w = W
                new_h = int(img_h * (W / img_w))
                clip = clip.resized(width=W)
                
            # Center Crop
            clip = clip.cropped(width=W, height=H, x_center=new_w/2, y_center=new_h/2)
            
            # ❌ REMOVED dynamic zoom effect - was very slow
            # clip = clip.with_effects([vfx.Resize(lambda t: 1.0 + 0.05 * t)])
            
        clip = clip.with_start(current_time)
        clips.append(clip)
        current_time += duration
        
    # Combine Clips
    final_video = CompositeVideoClip(clips, size=(W, H))
    
    # Add Audio
    audio_clips = []
    for item in audio_map:
        if os.path.exists(item['path']):
            ac = AudioFileClip(item['path']).with_start(item['start_s'])
            audio_clips.append(ac)
            
    # Background Music
    if background_track and os.path.exists(background_track):
        bg = AudioFileClip(background_track)
        if bg.duration < final_video.duration:
             repeats = int(np.ceil(final_video.duration / bg.duration))
             bg = concatenate_audioclips([bg] * repeats)
        bg = bg.subclipped(0, final_video.duration)
        audio_clips.append(bg)

    if audio_clips:
        final_audio = CompositeAudioClip(audio_clips)
        final_video = final_video.with_audio(final_audio)

    # Export - OPTIMIZED settings
    print(f"🎬 Exporting Reel ({W}x{H}) to {output_path}...")
    final_video.write_videofile(
        output_path, 
        fps=24,  # Reduced from 30
        codec="libx264", 
        audio_codec="aac",
        threads=8,  # Increased from 4
        preset="ultrafast"  # Fastest encoding
    )

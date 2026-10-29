"""Stage 4: combine the animated 480p clip with the narration audio (MoviePy 2.x)."""

import os


def assemble(video_path, audio_path, out_path):
    """Write an H.264/AAC MP4 with the audio aligned to t=0.

    The audio is trimmed to the video duration when it runs longer.
    Returns ``out_path``.
    """
    # Imported here so that importing this module does not require MoviePy.
    from moviepy import AudioFileClip, VideoFileClip

    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)

    with VideoFileClip(video_path) as video, AudioFileClip(audio_path) as audio:
        audio = audio.with_start(0)
        if audio.duration > video.duration:
            audio = audio.subclipped(0, video.duration)
        clip = video.with_audio(audio)
        clip.write_videofile(
            out_path,
            codec="libx264",
            audio_codec="aac",
        )
    return out_path

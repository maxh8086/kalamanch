"""MCP stdio server exposing the four KalaManch stages as tools."""

from mcp.server.fastmcp import FastMCP

from kalamanch.assemble import assemble
from kalamanch.upscale import upscale
from kalamanch.video import animate
from kalamanch.voice import synthesize

mcp = FastMCP("kalamanch")


def _run(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:  # return the error text to the MCP client
        return f"error: {exc}"


@mcp.tool()
def run_voice(text: str, profile: str, out_path: str) -> str:
    """Stage 2: synthesize narration via the local Voicebox server. Returns the output path or the error text."""
    return _run(synthesize, text, profile, out_path)


@mcp.tool()
def run_animate(portrait: str, seconds: float, out_path: str) -> str:
    """Stage 3: image-to-video via the Wan 2.1 command (WAN_CMD). Returns the output path or the error text."""
    return _run(animate, portrait, seconds, out_path)


@mcp.tool()
def run_assemble(video_path: str, audio_path: str, out_path: str) -> str:
    """Stage 4: assemble the 480p clip and audio into an H.264 MP4. Returns the output path or the error text."""
    return _run(assemble, video_path, audio_path, out_path)


@mcp.tool()
def run_upscale(in_path: str, out_path: str, scale: int = 2) -> str:
    """Stage 5: upscale with Video2X and Real-ESRGAN. Returns the output path or the error text."""
    return _run(upscale, in_path, out_path, scale=scale)


if __name__ == "__main__":
    mcp.run()

"""Stage 5: upscale the assembled MP4 with the Video2X CLI and Real-ESRGAN."""

import subprocess


def upscale(in_path, out_path, scale=2):
    """Run Video2X with the Real-ESRGAN backend and return ``out_path``.

    The flag set (-i, -o, -p, -s) must be verified against the installed
    Video2X version. Run ``video2x --help`` inside the container before use.
    """
    subprocess.run(
        ["video2x", "-i", in_path, "-o", out_path, "-p", "realesrgan", "-s", str(scale)],
        check=True,
    )
    return out_path

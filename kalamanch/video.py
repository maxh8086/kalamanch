"""Stage 3: image-to-video through a Wan 2.1 I2V command.

WAN_CMD is a shell command template with {portrait}, {seconds} and {out}
placeholders. Each value is shell-quoted before substitution, so do not add
quotes around the placeholders in the template.
WAN_WEIGHTS points at the Q4_K_M GGUF weights. The command flags are unverified
until tested on the target machine.
"""

import os
import shlex
import subprocess

from kalamanch.voice import unload_models


def animate(portrait, seconds, out_path):
    """Run the WAN_CMD template for one portrait and return ``out_path``."""
    template = os.environ.get("WAN_CMD")
    if not template:
        message = "WAN_CMD is not set. Set it to a Wan 2.1 I2V command template."
        if not os.environ.get("WAN_WEIGHTS"):
            message += " WAN_WEIGHTS is also unset; point it at the Q4_K_M GGUF weights."
        raise RuntimeError(message)

    # Free GPU memory held by Voicebox before Wan loads its weights.
    unload_models()

    command = template.format(
        portrait=shlex.quote(str(portrait)),
        seconds=shlex.quote(str(seconds)),
        out=shlex.quote(str(out_path)),
    )
    subprocess.run(command, shell=True, check=True)
    return out_path

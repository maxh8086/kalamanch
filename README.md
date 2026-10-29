# KalaManch

A containerised five-stage local video pipeline, exposed as an MCP stdio server.

## Stages

1. Narration script: text only, approved upstream.
2. Voice synthesis: `run_voice` calls the local Voicebox REST server.
3. Image-to-video: `run_animate` runs the Wan 2.1 I2V command on a portrait.
4. Assembly: `run_assemble` combines the 480p clip and narration into an MP4 with MoviePy.
5. Upscale: `run_upscale` runs Video2X with Real-ESRGAN to 1080p.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `VOICEBOX_URL` | `http://127.0.0.1:17493` | Base URL of the Voicebox server |
| `VOICEBOX_MODEL` | none (required) | Model id for `POST /v1/audio/speech`; list ids at `GET /v1/models` |
| `WAN_CMD` | none (required) | Shell template with `{portrait}`, `{seconds}`, `{out}`; values are shell-quoted |
| `WAN_WEIGHTS` | none | Path to the Q4_K_M GGUF Wan 2.1 weights |

## Build and run

```sh
docker build -t kalamanch:dev .
docker run -i kalamanch:dev
```

## Tests

```sh
python -m unittest discover -s tests -t . -q
```

## Status

Voicebox endpoint and Wan command flags are unverified until tested on the target machine.

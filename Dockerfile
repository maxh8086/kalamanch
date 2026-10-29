# Base pinned to the digest pulled on 2026-10-29. Re-pin deliberately when upgrading Video2X.
FROM ghcr.io/k4yt3x/video2x@sha256:e21b6893269b4cb6f5603802726fd7537be241f6b39217b73530478861acbca1

# The base is Arch Linux: python3, ffmpeg and video2x are present, pip is not.
# pacman is not used because the base's keyring is not initialised.
# System Python 3.13 is externally managed (PEP 668), so pip lives in a venv.
RUN set -eux; \
    command -v ffmpeg; \
    command -v video2x; \
    python3 -m venv /opt/venv; \
    /opt/venv/bin/pip --version
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY kalamanch/ /app/kalamanch/

# stdio MCP server: no port is exposed.
ENTRYPOINT ["python", "-m", "kalamanch.mcp_server"]

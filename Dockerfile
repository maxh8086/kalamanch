# TODO before publishing: pin the base image to a digest, for example
#   FROM ghcr.io/k4yt3x/video2x:latest@sha256:<digest>
FROM ghcr.io/k4yt3x/video2x:latest

# Install Python, pip and ffmpeg only when the base image lacks them.
RUN set -eux; \
    if ! command -v python3 >/dev/null 2>&1 \
       || ! python3 -m pip --version >/dev/null 2>&1 \
       || ! command -v ffmpeg >/dev/null 2>&1; then \
        apt-get update; \
        apt-get install -y --no-install-recommends python3 python3-pip python3-venv ffmpeg; \
        rm -rf /var/lib/apt/lists/*; \
    fi

# Isolated virtualenv avoids the system-wide pip restriction on Debian/Ubuntu.
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY kalamanch/ /app/kalamanch/

# stdio MCP server: no port is exposed.
ENTRYPOINT ["python", "-m", "kalamanch.mcp_server"]

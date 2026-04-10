FROM debian:trixie-slim
RUN <<EOF
apt -y update
DEBIAN_FRONTEND=noninteractive apt -y install fontconfig git libgl1 libxrender1 python3.13 python3.13-venv
python3.13 -m venv /python
. /python/bin/activate
EOF
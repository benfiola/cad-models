#!/bin/sh -ex
arch="$(arch)"
apt -y update
DEBIAN_FRONTEND=noninteractive apt -y install libgl1 python3.12 python3.12-venv
python3.12 -m venv /python
. /python/bin/activate
pip install "https://github.com/CadQuery/ocp-build-system/releases/download/7.7.2.1/cadquery_ocp-7.7.2.1-cp312-cp312-manylinux_2_35_${arch}.whl"
pip install -e .
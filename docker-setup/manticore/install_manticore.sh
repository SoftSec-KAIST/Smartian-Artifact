#!/bin/bash

set -e

python3 -m venv /home/test/tools/manticore/venv
source /home/test/tools/manticore/venv/bin/activate
python3 -m pip install wheel

cd /home/test/tools/manticore

git clone https://github.com/trailofbits/manticore.git
cd /home/test/tools/manticore/manticore
git checkout 7144c73e44638c767f6a1e5ed896781aaa2bba8b
patch -p1 < ../manticore.patch
python3 -m pip install .[native]

deactivate

#!/bin/bash

set -e

python3 -m venv /home/test/tools/mythril/venv
source /home/test/tools/mythril/venv/bin/activate
python3 -m pip install wheel

cd /home/test/tools/mythril

git clone https://github.com/ConsenSys/mythril.git
cd /home/test/tools/mythril/mythril
git checkout c90bf04d39e3246d40f1ea5a52e7419178bb5f23
patch -p1 < ../mythril.patch
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
mkdir -p /home/test/.mythril
cp /home/test/tools/mythril/mythril/mythril/support/assets/signatures.db /home/test/.mythril/signatures.db

deactivate

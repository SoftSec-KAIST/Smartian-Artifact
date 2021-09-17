#!/bin/bash

set -e

python3 -m venv /home/test/tools/ilf/venv
source /home/test/tools/ilf/venv/bin/activate
python3 -m pip install wheel
python3 -m pip install z3-solver

cd /home/test/tools/ilf/go/src

# copy ilf
git clone https://github.com/eth-sri/ilf.git
cd /home/test/tools/ilf/go/src/ilf
git checkout 9e8e3015a48783634658c8e748f113d2da2628c7
patch -p1 < ../ilf.patch
cd /home/test/tools/ilf/go/src

# install go-ethereum
mkdir -p /home/test/tools/ilf/go/src/github.com/ethereum/
cd /home/test/tools/ilf/go/src/github.com/ethereum/
git clone https://github.com/ethereum/go-ethereum.git
cd /home/test/tools/ilf/go/src/github.com/ethereum/go-ethereum
git checkout 86be91b3e2dff5df28ee53c59df1ecfe9f97e007
git apply /home/test/tools/ilf/go/src/ilf/script/patch.geth
cd /home/test/tools/ilf/go/src/ilf

# install python dependencies
python3 -m pip install -r requirements.txt --no-cache-dir
go build -o execution.so -buildmode=c-shared export/execution.go

# for postprocessing
python3 -m pip install eth_abi web3

deactivate

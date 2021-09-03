#!/bin/bash

# arg1: command (build or clean)
# arg2: benchmark
# arg3: compiler version

set -e

function download_solc() {
    wget https://github.com/ethereum/solidity/releases/download/v$1/solc-static-linux
    mv ./solc-static-linux ./solc
    chmod +x ./solc
}

function build() {
    mkdir -p $1/abi/
    mkdir -p $1/bin/
    mkdir -p tmp/
    download_solc $2
    while IFS=, read -r file name
    do
        # Compile ABI
        ./solc --abi -o tmp/ $1/sol/$file.sol
        cp tmp/$name.abi $1/abi/$file.abi
        rm -rf tmp/*
        # Compile bytecode
        ./solc --bin -o tmp/ $1/sol/$file.sol
        cp tmp/$name.bin $1/bin/$file.bin
        rm -rf tmp/*
    done < ./assets/$1.list
    rm -rf tmp/
}

if [ "$#" -ne 2 ]; then
    echo "Usage:"
    echo "  ./build.sh <benchmark> <solc version>"
else
    build $1 $2
fi

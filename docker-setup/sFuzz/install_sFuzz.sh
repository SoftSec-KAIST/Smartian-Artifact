#!/bin/bash

set -e

cd /home/test/tools/sFuzz

# Download and patch sFuzz
git clone --recursive https://github.com/duytai/sFuzz
cd /home/test/tools/sFuzz/sFuzz
git checkout eb690d4287af4c7dc0ecfce7447e4b4462775d55
patch -p1 < ../sFuzz.patch

# Install dependencies
sudo ./scripts/install_cmake.sh --prefix /usr/local
sudo ./scripts/install_deps.sh

# Build sFuzz
mkdir build
cd /home/test/tools/sFuzz/sFuzz/build
cmake ..
cd /home/test/tools/sFuzz/sFuzz/build/fuzzer
make

# Add environments
cp /home/test/tools/sFuzz/sFuzz/build/fuzzer/fuzzer /home/test/tools/sFuzz/fuzzer

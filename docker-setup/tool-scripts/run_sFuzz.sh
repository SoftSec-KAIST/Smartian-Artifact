#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file
# Arg3 : Bytecode file
# Arg4 : ABI file
# Arg5 : Main contract name
# Arg6 : Optional argument to pass

TOOLDIR=/home/test/tools/sFuzz
WORKDIR=/home/test/sFuzz-workspace

# Set up workdir
mkdir -p $WORKDIR
# Set up fuzzer
cp $TOOLDIR/fuzzer $WORKDIR/fuzzer
# Set up environment
cp -r $TOOLDIR/assets $WORKDIR/assets
mkdir -p $WORKDIR/output
mkdir -p $WORKDIR/contracts
touch $WORKDIR/output/log.txt
# Set up source file
cp $2 $WORKDIR/contracts/$5.sol
# Run sFuzz
cd $WORKDIR
./fuzzer -g -r 1 -d $1 --attacker ReentrancyAttacker $6 > $WORKDIR/output/stdout.txt 2>&1
chmod +x ./fuzzMe
./fuzzMe >> $WORKDIR/output/stdout.txt 2>&1

#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file
# Arg3 : Bytecode file
# Arg4 : ABI file
# Arg5 : Main contract name
# Arg6 : Optional argument to pass

TOOLDIR=/home/test/tools/sFuzz
WORKDIR=/home/test/sFuzz-workspace
OUTDIR=/home/test/output

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

# Postprocess
cd /home/test/scripts
kill -9 run_sFuzz.sh

WORKDIR=/home/test/sFuzz-workspace

mkdir -p $OUTDIR
# Move raw tc
mkdir -p $OUTDIR/raw_tc
mkdir -p $OUTDIR/raw_misc
cp $WORKDIR/output/tc_* $OUTDIR/raw_tc/
cp $WORKDIR/contracts/*.json $OUTDIR/raw_misc/
# Move logs
mv $WORKDIR/output/log.txt $OUTDIR/log.txt
mv $WORKDIR/output/stdout.txt $OUTDIR/stdout.txt

# Move output
mv $WORKDIR/output $OUTDIR/testcase

exit 1
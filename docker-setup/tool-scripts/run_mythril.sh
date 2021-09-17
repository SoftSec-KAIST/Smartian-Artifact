#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file
# Arg3 : Bytecode file
# Arg4 : ABI file
# Arg5 : Main contract name
# Arg6 : Optional argument to pass

TOOLDIR=/home/test/tools/mythril
WORKDIR=/home/test/mythril-workspace

source /home/test/tools/mythril/venv/bin/activate

# Set up workdir
mkdir -p $WORKDIR
# Set up environment
mkdir -p $WORKDIR/output
mkdir -p $WORKDIR/output/bugs
touch $WORKDIR/output/log.txt
# Run mythril
$TOOLDIR/mythril/myth analyze -f $3 --execution-timeout $1 $6 > \
  $WORKDIR/output/stdout.txt 2>&1

deactivate

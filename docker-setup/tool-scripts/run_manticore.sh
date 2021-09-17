#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file
# Arg3 : Bytecode file
# Arg4 : ABI file
# Arg5 : Main contract name
# Arg6 : Optional argument to pass

TOOLDIR=/home/test/tools/manticore
WORKDIR=/home/test/manticore-workspace

source /home/test/tools/manticore/venv/bin/activate

# Set up workdir
mkdir -p $WORKDIR
mkdir -p $WORKDIR/output
touch $WORKDIR/output/log.txt
# Run manticore
timeout $1s python /home/test/scripts/run_manticore.py $1 $2 $5 $6 > \
  $WORKDIR/output/stdout.txt 2>&1

deactivate

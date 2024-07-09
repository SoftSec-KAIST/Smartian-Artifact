#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file
# Arg3 : Bytecode file
# Arg4 : ABI file
# Arg5 : Main contract name
# Arg6, Arg7, Arg8 : Optional argument to pass

OUTDIR=/home/test/output
TOOLDIR=/home/test/tools/SmarTest
WORKDIR=/home/test/SmarTest-workspace

# Set up workdir
mkdir -p $WORKDIR
# Set up environment
mkdir -p $WORKDIR/output
mkdir -p $WORKDIR/output/bugs
touch $WORKDIR/output/log.txt

cd $TOOLDIR
eval $(opam env)
./build
# Run SmarTest
$TOOLDIR/main.native -input $2 -main $5 -mode exploit -exploit_timeout $1 io $6 \
  > $WORKDIR/output/stdout.txt 2>&1

python3 /home/test/scripts/SmarTest_postprocess.py

mv $WORKDIR/output $OUTDIR

#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file
# Arg3 : Bytecode file
# Arg4 : ABI file
# Arg5 : Main contract name
# Arg6 : Optional argument to pass

TOOLDIR=/home/test/tools/ilf/go/src/ilf
WORKDIR=/home/test/ilf-workspace

source /home/test/tools/ilf/venv/bin/activate

# Set up workdir
mkdir -p $WORKDIR
mkdir -p $WORKDIR/output
touch $WORKDIR/output/log.txt
# Preprocess
python3 $TOOLDIR/preprocess/ilf_preprocess.py --source $2 --name $5 --proj $WORKDIR/proj --ilf $TOOLDIR
# Run ilf
cd $TOOLDIR
timeout $1s python3 -m ilf --log_to_file $WORKDIR/log --proj $WORKDIR/proj \
  --contract $5 --fuzzer imitation --model ./model --limit 1 $6 > \
  $WORKDIR/output/stdout.txt 2>&1

deactivate

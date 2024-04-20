#!/bin/bash


# Arg1 : Tool name
# Arg2 : Bytecode file
# Arg3 : ABI file
# Arg4 : Main contract name
# Arg5 : Time interval for coverage logging

OUTDIR=/home/test/output
SCRIPTDIR=/home/test/scripts
REPLAYER=/home/test/tools/Smartian/build/Smartian

function postprocess_sFuzz() {
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

    # Postprocess
    python3 $SCRIPTDIR/sFuzz_postprocess.py $1 $WORKDIR/output
    # Move output
    mv $WORKDIR/output $OUTDIR/testcase
}

function postprocess_mythril() {
    kill -9 run_mythril.sh

    WORKDIR=/home/test/mythril-workspace

    source /home/test/tools/mythril/venv/bin/activate

    mkdir -p $OUTDIR
    # Move logs
    mv $WORKDIR/output/log.txt $OUTDIR/log.txt
    mv $WORKDIR/output/stdout.txt $OUTDIR/stdout.txt
    # Move bug tc
    mv $WORKDIR/output/bugs $OUTDIR/bugs
    # Move raw tc
    mkdir -p $OUTDIR/raw_tc
    cp $WORKDIR/output/tc_* $OUTDIR/raw_tc/

    # Postprocess
    python3 $SCRIPTDIR/mythril_postprocess.py $1 $WORKDIR/output
    python3 $SCRIPTDIR/mythril_postprocess.py $1 $OUTDIR/bugs

    # Move output
    mv $WORKDIR/output $OUTDIR/testcase

    deactivate
}


function postprocess() {
    case $1 in
        sFuzz) postprocess_sFuzz $4;;
        mythril) postprocess_mythril $4 $2;;
    esac
}

postprocess $1 $2 $3 $4
$REPLAYER replay -p $2 -i $OUTDIR/testcase -t $5 > $OUTDIR/cov.txt 2>&1
if [ $1 = smartian ]; then
    $REPLAYER replay -p $2 -i $OUTDIR/testcase > $OUTDIR/with_dfeed.txt 2>&1
    $REPLAYER replay -p $2 -i $OUTDIR/testcase --noddfa > $OUTDIR/without_dfeed.txt 2>&1
fi

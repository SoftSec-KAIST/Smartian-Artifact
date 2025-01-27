#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/B1-* 1> /dev/null 2>&1; then
    echo "$OUTDIR/B1-* exists, please remove it."
    exit 1
fi

if ls $OUTDIR/result-B1-compare 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-B1-compare exists, please remove it."
    exit 1
fi

mkdir -p $OUTDIR/result-B1-compare

# Run smartian, sFuzz, mythril, and SmarTest.
python $SCRIPTDIR/run_experiment.py B1 smartian 3600 $1
python $SCRIPTDIR/run_experiment.py B1 sFuzz 3600 $1
python $SCRIPTDIR/run_experiment.py B1 mythril 3600 $1
python $SCRIPTDIR/run_experiment.py B1 SmarTest 3600 $1

mkdir -p $OUTDIR/result-B1-compare/smartian
mv $OUTDIR/B1-smartian-* $OUTDIR/result-B1-compare/smartian/
mkdir -p $OUTDIR/result-B1-compare/sFuzz
mv $OUTDIR/B1-sFuzz-* $OUTDIR/result-B1-compare/sFuzz/
mkdir -p $OUTDIR/result-B1-compare/mythril
mv $OUTDIR/B1-mythril-* $OUTDIR/result-B1-compare/mythril/

mkdir -p $OUTDIR/result-B1-compare/SmarTest
mv $OUTDIR/B1-SmarTest-* $OUTDIR/result-B1-compare/SmarTest/

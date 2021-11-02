#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/B1-noarg-* 1> /dev/null 2>&1; then
    echo "$OUTDIR/B1-noarg-* exists, please remove it."
    exit 1
fi

if ls $OUTDIR/result-B1-compare 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-B1-compare exists, please remove it."
    exit 1
fi

mkdir -p $OUTDIR/result-B1-compare

# Run smartian, sFuzz, manticore, and mythril.
for i in $(seq $1); do
    python $SCRIPTDIR/run_experiment.py B1-noarg smartian 3600
    python $SCRIPTDIR/run_experiment.py B1-noarg sFuzz 3600
    python $SCRIPTDIR/run_experiment.py B1-noarg manticore 3600 B1
    python $SCRIPTDIR/run_experiment.py B1-noarg mythril 3600
done
mkdir -p $OUTDIR/result-B1-compare/smartian
mv $OUTDIR/B1-noarg-smartian-* $OUTDIR/result-B1-compare/smartian/
mkdir -p $OUTDIR/result-B1-compare/sFuzz
mv $OUTDIR/B1-noarg-sFuzz-* $OUTDIR/result-B1-compare/sFuzz/
mkdir -p $OUTDIR/result-B1-compare/manticore
mv $OUTDIR/B1-noarg-manticore-* $OUTDIR/result-B1-compare/manticore/
mkdir -p $OUTDIR/result-B1-compare/mythril
mv $OUTDIR/B1-noarg-mythril-* $OUTDIR/result-B1-compare/mythril/

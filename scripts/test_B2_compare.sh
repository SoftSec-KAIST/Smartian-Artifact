#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/B2-* 1> /dev/null 2>&1; then
    echo "$OUTDIR/B2-* exists, please remove it."
    exit 1
fi

if ls $OUTDIR/result-B2-compare 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-B2-compare exists, please remove it."
    exit 1
fi

mkdir -p $OUTDIR/result-B2-compare

# Run smartian, ilf, sFuzz, manticore, and mythril.
for i in $(seq $1); do
    python $SCRIPTDIR/run_experiment.py B2 smartian 3600
    python $SCRIPTDIR/run_experiment.py B2 ilf 3600
    python $SCRIPTDIR/run_experiment.py B2 sFuzz 3600
    python $SCRIPTDIR/run_experiment.py B2 manticore 3600 B2
    python $SCRIPTDIR/run_experiment.py B2 mythril 3600
done
mkdir -p $OUTDIR/result-B2-compare/smartian
mv $OUTDIR/B2-smartian-* $OUTDIR/result-B2-compare/smartian/
mkdir -p $OUTDIR/result-B2-compare/ilf
mv $OUTDIR/B2-ilf-* $OUTDIR/result-B2-compare/ilf/
mkdir -p $OUTDIR/result-B2-compare/sFuzz
mv $OUTDIR/B2-sFuzz-* $OUTDIR/result-B2-compare/sFuzz/
mkdir -p $OUTDIR/result-B2-compare/manticore
mv $OUTDIR/B2-manticore-* $OUTDIR/result-B2-compare/manticore/
mkdir -p $OUTDIR/result-B2-compare/mythril
mv $OUTDIR/B2-mythril-* $OUTDIR/result-B2-compare/mythril/

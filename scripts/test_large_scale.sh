#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/B3-smartian-* 1> /dev/null 2>&1; then
    echo "$OUTDIR/B3-smartian-* exists, please remove it."
    exit 1
fi

if ls $OUTDIR/result-large-scale 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-large-scale exists, please remove it."
    exit 1
fi

mkdir -p $OUTDIR/result-large-scale/

for i in $(seq $1); do
    python $SCRIPTDIR/run_experiment.py B3 smartian 3600
done
mv $OUTDIR/B3-smartian-* $OUTDIR/result-large-scale/

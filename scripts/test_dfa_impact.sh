#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/B1-smartian-* 1> /dev/null 2>&1; then
    echo "$OUTDIR/B1-smartian-* exists, please remove it."
    exit 1
fi

if ls $OUTDIR/result-dfa-impact 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-dfa-impact exists, please remove it."
    exit 1
fi

mkdir -p $OUTDIR/result-dfa-impact

# With both data-flow analyses enabled.
python $SCRIPTDIR/run_experiment.py B1 smartian 3600 $1
mkdir -p $OUTDIR/result-dfa-impact/dfa
mv $OUTDIR/B1-smartian-* $OUTDIR/result-dfa-impact/dfa/

# With only static data-flow analysis enabled.
python $SCRIPTDIR/run_experiment.py B1 smartian 3600 $1 --noddfa
mkdir -p $OUTDIR/result-dfa-impact/static
mv $OUTDIR/B1-smartian-* $OUTDIR/result-dfa-impact/static/

# With only dynamic data-flow analysis enabled.
python $SCRIPTDIR/run_experiment.py B1 smartian 3600 $1 --nosdfa
mkdir -p $OUTDIR/result-dfa-impact/dynamic
mv $OUTDIR/B1-smartian-* $OUTDIR/result-dfa-impact/dynamic/

# Without any data-flow analysis.
python $SCRIPTDIR/run_experiment.py B1 smartian 3600 $1 "--noddfa --nosdfa"
mkdir -p $OUTDIR/result-dfa-impact/nodfa
mv $OUTDIR/B1-smartian-* $OUTDIR/result-dfa-impact/nodfa/

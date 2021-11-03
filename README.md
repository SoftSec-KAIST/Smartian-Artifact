Smartian Artifact
========

[Smartian](https://github.com/SoftSec-KAIST/Smartian) is a grey-box fuzzer for
Ethereum smart contracts. This repository contains artifacts for the
experiments in our paper in ASE 2021, "Smartian: Enhancing Smart Contract
Fuzzing with Static and Dynamic Data-Flow Analyses".

# Structure

We run all our experiments in a dockerized environment. In
[docker-setup](./docker-setup), we provide various files required to build the
docker image. The [benchmarks](./benchmarks) directory contains benchmarks we
used for the experiments. In [scripts](./scripts), you can find scripts to run
the experiments and analyze their results.

# Setup

We assume that your system has Docker installed. Also, you should be able to run
the `docker` command without `sudo`. The following command will build the
docker image name 'smartian-artifact', using our [Dockerfile](./Dockerfile).

```
$ ./build.sh
```

Next, check the `MAX_INSTANCE_NUM` configurations parameter in
[scripts/run\_experiment.py](./scripts/run_experiment.py) script.
We ran the experiments in a server machine with 88 cores, so this parameter is
currently set to 72. Make sure that this parameter value is lower than the
number of cores in your machine.

# Evaluation of the impact of data-flow-analyses

To reproduce the experiment in Section V.B of our paper, you can run the
following script.  This script internally executes `run_experiment.py` to run
Smartian with four different modes explained in the paper. Here, the script
argument specifies the number of repetition for the experiment.

```
$ ./scripts/test_dfa_impact.sh 5
```

After the above command finishes, you will obtain the `output/result-dfa-impact`
directory that contains the raw data. For instance, `dfa` subdirectory contains
the result of running Smartian with both static and dynamic analyses enabled
(which is the default mode).

```
$ ls output/result-dfa-impact/
dfa  dynamic  nodfa  static
$ ls output/result-dfa-impact/dfa/
B1-smartian-1  B1-smartian-2  B1-smartian-3  B1-smartian-4  B1-smartian-5
```

Now, you can parse the experiment results as below. You may also take a look at
`plot_cov.py`, `count_b1_alarm.py`, and `measure_overhead.py` scripts to get
more statistics.
```
$ python scripts/plot_b1_cve.py output/result-dfa-impact/dfa/*
```

# Comparison between Smartian and other tools

Similarly, you can use the following scripts to reproduce the experiment in
Section V.C of our paper, which compares Smartian against other testing tools.

```
$ ./scripts/test_B1_compare.sh 5
$ ./scripts/test_B2_compare.sh 5
```

Then, you will get the raw data under `output/result-B1-compare` and
`output/result-B2-compare`. Note that ILF does not support integer overflow
detection, so it is not tested on B1.

```
$ ls output/result-B1-compare/
manticore  mythril  sFuzz  smartian
$ ls output/result-B2-compare/
ilf  manticore  mythril  sFuzz  smartian
```

To obtain the results in our paper, you may refer to the following commands.
```
$ python scripts/plot_b1_cve.py output/result-B1-compare/smartian/*
$ python scripts/plot_b2_bug.py output/result-B2-compare/smartian/*
$ python scripts/count_b2_alarm.py output/result-B2-compare/smartian/*
```

# Large-scale experiment with Smartian

Lastly, we also provide the script for the large-scale experiment in Section
V.D of the paper.

```
$ ./scripts/test_large_scale.sh 1
$ python scripts/count_b3_alarm.py output/result-large-scale/B3-smartian-1/
```

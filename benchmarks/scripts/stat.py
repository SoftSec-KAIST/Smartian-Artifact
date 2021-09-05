import sys
import os
import subprocess
import numpy

def get_sloc(bench_dir, target):
    sol = "./%s/sol/%s.sol" % (bench_dir, target)
    p = subprocess.Popen(["cloc", sol], stdout=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode("ascii")
    out = out.strip().split("\n")
    for line in out:
        if "Solidity" in line:
            line = line.split()
            return int(line[-1])

def get_stat(bench_dir):
    list_file = os.path.join("assets", "%s.list" % bench_dir)
    slocs = []
    f = open(list_file)
    for line in f.readlines():
        target = line.split(",")[0]
        print("Checking %s" % target)
        sloc = get_sloc(bench_dir, target)
        slocs.append(sloc)
    f.close()
    print("Mean SLoC: %f" % numpy.mean(slocs))
    print("StdDev SLoC: %f" % numpy.std(slocs))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s <benchmark name>" % sys.argv[0])
        exit(1)
    bench_dir = sys.argv[1]
    get_stat(bench_dir)

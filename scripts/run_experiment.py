import sys, os, subprocess, time, queue, threading
from subprocess import PIPE
from common import BASE_DIR, BENCHMARK_DIR


IMAGE_NAME = "smartian-artifact"
MAX_INSTANCE_NUM = 60
AVAILABLE_BENCHMARKS = ["B1", "B2", "B3"]
SUPPORTED_TOOLS = ["smartian", "sFuzz", "mythril", "SmarTest"]
WorkQueue = queue.Queue()
OUTDIR = "output"
lock = threading.Lock()


def run_cmd(cmd_str, check=True):
    print("[*] Executing command '%s'" % cmd_str)
    args = cmd_str.split()
    try:
        p = subprocess.run(args, check=check, stdout=PIPE, stderr=PIPE)
        return p.stdout
    except Exception as e:
        print(e)
        exit(1)


def run_cmd_in_docker(container, cmd_str, check=True):
    print("[*] Executing '%s' in container %s" % (cmd_str, container))
    docker_prefix = "docker exec %s /bin/bash -c" % container
    args = docker_prefix.split() + [cmd_str]
    try:
        p = subprocess.run(args, stdout=PIPE, stderr=PIPE)
        return p.stdout
    except Exception as e:
        print(e)
        exit(1)


def check_cpu_count():
    n_str = run_cmd("nproc")
    try:
        if int(n_str) < MAX_INSTANCE_NUM:
            print("Not enough CPU cores, please decrease MAX_INSTANCE_NUM")
            exit(1)
    except Exception as e:
        print(e)
        print("Failed to count the number of CPU cores, abort")
        exit(1)

def decide_outpath(benchmark, tool, target):
    prefix = benchmark + "-" + tool
    i = 0
    while True:
        i += 1
        outpath = os.path.join(BASE_DIR, OUTDIR, "%s-%d" % (prefix, i), target[0])
        if not os.path.exists(outpath):
            outdir = os.path.join(BASE_DIR, OUTDIR, "%s-%d" % (prefix, i))
            return outdir

def make_outdir(benchmark, tool):
    prefix = benchmark + "-" + tool
    i = 0
    while True:
        i += 1
        outdir = os.path.join(BASE_DIR, OUTDIR, "%s-%d" % (prefix, i))
        if not os.path.exists(outdir):
            return outdir


def get_B1_target_bug(target, tool):
    csv_path = os.path.join(BENCHMARK_DIR, "assets", "B1-cve.csv")
    f = open(csv_path, "r")
    for line in f:
        line = line.strip()
        if line != "":
            if target == line.split(',')[0]:
                f.close()
                if tool == "smartian":
                    return "-b IB:" + line.split(',')[2]
                elif tool == "SmarTest":
                    return "-target_bug IO:" + line.split(',')[1]

def get_targets(benchmark):
    list_name = benchmark + ".list"
    list_path = os.path.join(BENCHMARK_DIR, "assets", list_name)
    f = open(list_path, "r")
    targets = []
    for line in f:
        line = line.strip()
        if line != "":
            line = line.split(',')
            targets.append(line)
    f.close()
    return targets

def fetch_works(targets):
    works = []
    for i in range(MAX_INSTANCE_NUM):
        if len(targets) <= 0:
            break
        works.append(targets.pop(0))
    return works

def spawn_container(target, cpu_idx):
    container = target[0] + "-" + str(cpu_idx)
    cmd = "docker run --rm -m=6g --cpuset-cpus=%d -it -d --name %s %s" % \
            (cpu_idx, container, IMAGE_NAME)
    run_cmd(cmd)

def run_fuzzing(benchmark, target, tool, timelimit, opt, cpu_idx):
    bench_dirname = benchmark.split("-")[0]
    targ, name = target
    src = "/home/test/benchmarks/%s/sol/%s.sol" % (bench_dirname, targ)
    bin = "/home/test/benchmarks/%s/bin/%s.bin" % (bench_dirname, targ)
    abi = "/home/test/benchmarks/%s/abi/%s.abi" % (bench_dirname, targ)
    if "B1" in benchmark and tool in ["smartian", "SmarTest"]:
        opt = opt + " " + str(get_B1_target_bug(targ, tool))
    args = "%d %s %s %s %s '%s'" % (timelimit, src, bin, abi, name, opt)
    script = "/home/test/scripts/run_%s.sh" % tool
    cmd = "%s %s" % (script, args)
    container = targ + "-" + str(cpu_idx)
    run_cmd_in_docker(container, cmd)

def store_outputs(target, outdir, cpu_idx):
    targ, _ = target
    cmd = "docker cp %s:/home/test/output %s/%s" % (targ + "-" + str(cpu_idx), outdir, targ)
    run_cmd(cmd)

def cleanup_container(target, cpu_idx):
    targ = target[0]+"-"+str(cpu_idx)
    cmd = "docker kill %s" % targ
    run_cmd(cmd)

def worker(cpu_idx, benchmark, tool, timelimit, opt):
    global WorkQueue
    while not WorkQueue.empty():
        with lock:
            try:
                target = WorkQueue.get(block=False)
            except queue.Empty:
                break
        spawn_container(target, cpu_idx)
        run_fuzzing(benchmark, target, tool, timelimit, opt, cpu_idx)
        with lock:
            store_outputs(target, decide_outpath(benchmark, tool, target), cpu_idx)
            cleanup_container(target, cpu_idx)
        time.sleep(2)

def main():
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        print("Usage: %s <benchmark> <tool> <timelimit> <iterate>" % \
              sys.argv[0])
        exit(1)

    benchmark = sys.argv[1]
    tool = sys.argv[2]
    timelimit = int(sys.argv[3])
    iterate = int(sys.argv[4])
    opt = sys.argv[5] if len(sys.argv) == 6 else ""

    check_cpu_count()
    if benchmark not in AVAILABLE_BENCHMARKS:
        print("Unavailable benchmark: %s" % benchmark)
        exit(1)
    if tool not in SUPPORTED_TOOLS:
        print("Unsupported tool: %s" % tool)
        exit(1)

    for i in range(iterate):
        outdir = make_outdir(benchmark, tool)
        os.makedirs(outdir)

    global WorkQueue
    targets = []
    for i in range(iterate): targets += get_targets(benchmark)
    for target in targets: WorkQueue.put(target)

    active_threads = []
    for i in range(MAX_INSTANCE_NUM):
        thread = threading.Thread(target=worker, args=(i, benchmark, tool, timelimit, opt))
        thread.start()
        active_threads.append(thread)

    for thread in active_threads:
        thread.join()

if __name__ == "__main__":
    main()

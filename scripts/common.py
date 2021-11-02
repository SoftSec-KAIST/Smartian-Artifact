import os

### Constants and configurations.

TOTAL_TIME = 60 # Total fuzzing time in minute.
PLOT_INTERVAL = 5 # Interval to plot the number of found bugs over time.

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
BENCHMARK_DIR = os.path.join(BASE_DIR, "benchmarks")
B1_CVE_INFO_FILE = os.path.join(BENCHMARK_DIR, "assets", "B1-cve.csv")
B2_BUG_INFO_FILE = os.path.join(BENCHMARK_DIR, "assets", "B2-bug.csv")

FUZZ_LOG_NAME = "log.txt"
COV_FILE_NAME = "cov.txt"

AF = "AssertionFailure"
AW = "ArbitraryWrite"
BD = "BlockstateDependency"
CH = "ControlHijack"
EL = "EtherLeak"
IB = "IntegerBug"
ME = "MishandledException"
MS = "MultipleSend"
RE = "Reentrancy"
SC = "SuicidalContract"
TO = "TransactionOriginUse"

### Functions to retrieve tool configuration.

def append_sig_suffix(sig_list, suffix):
    return list(map(lambda sig: sig + suffix, sig_list))

def get_tool_sigs(tool, bug_sigs):
    tool = tool.lower()
    if tool == "default":
        return bug_sigs
    elif tool == "smartian-ilf":
        return append_sig_suffix(bug_sigs, "ILF")
    elif tool == "smartian-sfuzz":
        return append_sig_suffix(bug_sigs, "SFuzz")
    elif tool == "smartian-mythril":
        return append_sig_suffix(bug_sigs, "Mythril")
    elif tool == "smartian-manticore":
        return append_sig_suffix(bug_sigs, "Manticore")
    else:
        print('Invalid tool string: %s' % tool)
        exit(1)

### Functions to retrieve benchmark information.

def init_b1_cve_info(IB_sig):
    cve_info = { }
    cve_csv_file = open(B1_CVE_INFO_FILE, "r")
    for buf in cve_csv_file:
        tokens = buf.strip().split(",")
        if len(tokens) != 3:
            print("Invalid entry in CSV file: %s" % buf)
            exit(1)
        targ = tokens[0]
        # The third column contains the PC address of add/sub/mul.
        cve_pcs = tokens[2].split("/")
        cve_info[targ] = []
        for cve_pc in cve_pcs:
            cve_info[targ].append((IB_sig, cve_pc))
    cve_csv_file.close()
    return cve_info

def has_bug(s):
    if s == "-":
        return False
    elif "/" in s:
        return True
    elif int(s) >= 0:
        return True
    else:
        print("Invalid bug str: %s" % s)
        assert(False)

def init_b2_bug_info(BD_sig, ME_sig, RE_sig):
    bug_info = { }
    bug_csv_file = open(B2_BUG_INFO_FILE, "r")
    for buf in bug_csv_file:
        tokens = buf.strip().split(",")
        if len(tokens) != 4:
            print("Invalid entry in CSV file: %s" % buf)
            exit(1)
        targ = tokens[0]
        bug_list = []
        bug_list.append((BD_sig, has_bug(tokens[1])))
        bug_list.append((ME_sig, has_bug(tokens[2])))
        bug_list.append((RE_sig, has_bug(tokens[3])))
        bug_info[targ] = bug_list
    bug_csv_file.close()
    return bug_info

### Functions for parsing log files.

def read_log_file(result_dir, targ):
    targ_dir = os.path.join(result_dir, targ)
    log_path = os.path.join(targ_dir, FUZZ_LOG_NAME)
    f = open(log_path, "r")
    buf = f.read()
    f.close()
    return buf

def parse_fuzz_log(buf, sig):
    idx_sig = buf.find(sig)
    if idx_sig == -1:
        return None
    buf = buf[:idx_sig]
    idx_start = buf.rfind("[")
    idx_end = buf.rfind("]")
    assert(idx_start != -1 and idx_end != -1)
    # Python only supports datetime parsing, and not timedelta parsing.
    buf = buf[idx_start + 1 : idx_end]
    tokens = list(map(int, buf.strip().split(":")))
    sec = tokens[0] * 86400 + tokens[1] * 3600 + tokens[2] * 60 + tokens[3]
    return sec

def count_from_log(buf, sig, per_contract):
    if per_contract:
        return (1 if sig in buf else 0)
    else:
        pc_list = []
        for line in buf.split("\n"):
            if sig not in line:
                continue
            else:
                pc = line.split(sig)[1].strip().split()[0]
                if pc not in pc_list:
                    pc_list.append(pc)
        return len(pc_list)

### Functions to print the parsed result.

def collect_found_times(bug_sig, time_map_list, targ):
    found_times = []
    for time_map in time_map_list:
        if (targ, bug_sig) in time_map:
            found_time = time_map[(targ, bug_sig)]
            found_times.append(found_time)
    return found_times

def print_found_time(bug_sig, targ_list, time_map_list):
    iter_cnt = len(time_map_list)
    for targ in targ_list:
        found_times = collect_found_times(bug_sig, time_map_list, targ)
        if len(found_times) == 0:
            print("Never found %s from %s" % (bug_sig, targ))
        elif len(found_times) == iter_cnt:
            sec = ", ".join(map(str, found_times))
            print("Fully found %s from %s: [%s] sec" % (bug_sig, targ, sec))
        else:
            sec = ", ".join(map(str, found_times))
            print("Partly found %s from %s: [%s] sec" % (bug_sig, targ, sec))

def count_found_before(bug_sigs, time_map, sec):
    n = 0
    for (targ, found_bug) in time_map:
        found_time = time_map[(targ, found_bug)]
        if found_bug in bug_sigs and found_time < sec:
            n += 1
    return n

def plot_count_over_time(bug_sigs, time_map_list):
    for minute in range(0, TOTAL_TIME + PLOT_INTERVAL, PLOT_INTERVAL):
        sec = 60 * minute
        count_list = []
        for time_map in time_map_list:
            count_list.append(count_found_before(bug_sigs, time_map, sec))
        count_avg = float(sum(count_list)) / len(count_list)
        print("%02dm: %.1f" % (minute, count_avg))


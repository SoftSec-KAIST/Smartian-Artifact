import sys, os
from common import get_tool_sigs, init_b1_cve_info
from common import read_log_file, parse_fuzz_log
from common import print_found_time, plot_count_over_time
from common import IB

def analyze_targ(cve_points, result_dir, targ, time_map):
    buf = read_log_file(result_dir, targ)
    found_times = []
    for (bug_sig, cve_pc) in cve_points:
        alarm_sig = "%s at %x" % (bug_sig, int(cve_pc, 16))
        found_time = parse_fuzz_log(buf, alarm_sig)
        if found_time is not None:
            found_times.append(found_time)

    if len(found_times) != 0:
        time_map[(targ, bug_sig)] = min(found_times)

def analyze_dir(cve_info, result_dir, targ_list):
    time_map = {}
    for targ in targ_list:
        cve_points = cve_info[targ]
        analyze_targ(cve_points, result_dir, targ, time_map)
    return time_map

def print_found_count(time_map_list):
    found_sets = map(lambda m: set(m.keys()), time_map_list)
    found_always_n = len(set.intersection(*found_sets))
    found_at_least_once_n = len(set.union(*found_sets))
    found_min_n = min(map(len, found_sets))
    found_max_n = max(map(len, found_sets))
    print("%d bugs were found all the time" % found_always_n)
    print("%d bugs were found at least once" % found_at_least_once_n)
    print("At least %d bugs were found in each run" % found_min_n)
    print("At most %d bugs were found in each run" % found_max_n)

def main():
    if len(sys.argv) < 2:
        print("Usage: %s [result dirs ...]" % sys.argv[0])
        exit(1)

    if sys.argv[1] in ["--sfuzz", "--manticore", "--mythril"]:
        sig_set = "smartian-" + sys.argv[1][2:] # e.g., "smartian-sfuzz"
        result_dirs = sys.argv[2:]
    else:
        sig_set = "default"
        result_dirs = sys.argv[1:]

    bug_sigs = get_tool_sigs(sig_set, [IB])
    IB_sig = bug_sigs[0]
    cve_info = init_b1_cve_info(IB_sig)
    targ_list = os.listdir(result_dirs[0])
    targ_list.sort()

    time_map_list = []
    for result_dir in result_dirs:
        time_map = analyze_dir(cve_info, result_dir, targ_list)
        time_map_list.append(time_map)

    print_found_time(IB_sig, targ_list, time_map_list)
    print("===================================")
    plot_count_over_time([IB_sig], time_map_list)
    print("===================================")
    print_found_count(time_map_list)

if __name__ == "__main__":
    main()

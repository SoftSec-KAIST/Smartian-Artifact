import sys, os
from common import get_tool_sigs, init_b1_cve_info
from common import read_log_file, parse_fuzz_log, collect_found_times
from common import plot_count_over_time, print_median_time
from common import IB
from plot_b1_cve import analyze_dir, analyze_targ

def main():
    if len(sys.argv) < 2:
        print("Usage: %s [result dirs ...]" % sys.argv[0])
        exit(1)

    if sys.argv[1] in ["--sfuzz", "--mythril"]:
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

    print_median_time(IB_sig, targ_list, time_map_list)

if __name__ == "__main__":
    main()
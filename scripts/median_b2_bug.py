import sys, os
from statistics import median
from common import get_tool_sigs, init_b2_bug_info
from common import read_log_file, parse_fuzz_log, collect_found_times
from common import plot_count_over_time, print_median_time
from common import BD, ME, RE
from plot_b2_bug import analyze_dir, analyze_targ, classify_targets

def main():
    if len(sys.argv) < 2:
        print("Usage: %s [result dirs ...]" % sys.argv[0])
        exit(1)

    if sys.argv[1] in ["--sfuzz", "--mythril"]:
        sig_set = "smartian-" + sys.argv[1][2:] # e.g., "smartian-ilf"
        result_dirs = sys.argv[2:]
    else:
        sig_set = "default"
        result_dirs = sys.argv[1:]

    bug_sigs = get_tool_sigs(sig_set, [BD, ME, RE])
    BD_sig, ME_sig, RE_sig = bug_sigs
    bug_info = init_b2_bug_info(BD_sig, ME_sig, RE_sig)
    targ_list = os.listdir(result_dirs[0])
    targ_list.sort()

    time_map_list = []
    for result_dir in result_dirs:
        time_map = analyze_dir(bug_info, result_dir, targ_list)
        time_map_list.append(time_map)

    BD_list, ME_list, RE_list = classify_targets(bug_info, targ_list, bug_sigs)
    print_median_time(BD_sig, BD_list, time_map_list)
    print("===================================")
    print_median_time(ME_sig, ME_list, time_map_list)
    print("===================================")
    print_median_time(RE_sig, RE_list, time_map_list)

if __name__ == "__main__":
    main()

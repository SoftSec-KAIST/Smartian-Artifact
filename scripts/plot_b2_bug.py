import sys, os
from common import get_tool_sigs, init_b2_bug_info
from common import read_log_file, parse_fuzz_log
from common import print_found_time, plot_count_over_time
from common import BD, ME, RE

def classify_targets(bug_info, targ_list, bug_sigs):
    BD_sig, ME_sig, RE_sig = bug_sigs
    BD_list = []
    ME_list = []
    RE_list = []
    for targ in targ_list:
        if (BD_sig, True) in bug_info[targ]:
            BD_list.append(targ)
        if (ME_sig, True) in bug_info[targ]:
            ME_list.append(targ)
        if (RE_sig, True) in bug_info[targ]:
            RE_list.append(targ)
    return (BD_list, ME_list, RE_list)

def analyze_targ(bug_list, result_dir, targ, time_map):
    buf = read_log_file(result_dir, targ)
    for (bug_sig, exist_flag) in bug_list:
        if not exist_flag:
            continue
        alarm_sig = "%s at" % bug_sig
        found_time = parse_fuzz_log(buf, alarm_sig)
        if found_time is not None:
            time_map[(targ, bug_sig)] = found_time

def analyze_dir(bug_info, result_dir, targ_list):
    time_map = {}
    for targ in targ_list:
        bug_list = bug_info[targ]
        analyze_targ(bug_list, result_dir, targ, time_map)
    return time_map

def main():
    if len(sys.argv) < 2:
        print("Usage: %s [result dirs ...]" % sys.argv[0])
        exit(1)

    if sys.argv[1] in ["--ilf", "--sfuzz", "--manticore", "--mythril"]:
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
    print_found_time(BD_sig, BD_list, time_map_list)
    print("===================================")
    print_found_time(ME_sig, ME_list, time_map_list)
    print("===================================")
    print_found_time(RE_sig, RE_list, time_map_list)
    print("===================================")
    plot_count_over_time(bug_sigs, time_map_list)

if __name__ == "__main__":
    main()

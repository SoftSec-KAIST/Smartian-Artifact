import sys, os
from common import get_tool_sigs, init_b2_bug_info
from common import read_log_file, count_from_log
from common import BD, ME, RE

def incr_count(stat, bug_sig, alarm_class):
    if bug_sig not in stat:
        tp_cnt, fp_cnt, fn_cnt = (0, 0, 0)
    else:
        tp_cnt, fp_cnt, fn_cnt = stat[bug_sig]

    if alarm_class == "TP":
        tp_cnt += 1
    elif alarm_class == "FP":
        fp_cnt += 1
    elif alarm_class == "FN":
        fn_cnt += 1
    stat[bug_sig] = (tp_cnt, fp_cnt, fn_cnt)

    return stat

def analyze_dir(bug_info, result_dir, targ_list):
    stat = { }
    for targ in targ_list:
        buf = read_log_file(result_dir, targ)
        bug_list = bug_info[targ]
        for (bug_sig, exist_flag) in bug_list:
            alarm_sig = "%s at" % bug_sig
            count = count_from_log(buf, alarm_sig, True)
            assert(count in [0, 1])
            if count == 1 and exist_flag: # True positive
                incr_count(stat, bug_sig, "TP")
            elif count == 1 and not exist_flag: # False positive
                print("%s FP from %s" % (bug_sig, targ))
                incr_count(stat, bug_sig, "FP")
            elif exist_flag: # False negative
                print("%s FN from %s" % (bug_sig, targ))
                incr_count(stat, bug_sig, "FN")
    return stat

def print_statistics(stat_list, bug_sigs):
    for bug_sig in bug_sigs:
        tp_cnt_list = []
        fp_cnt_list = []
        fn_cnt_list = []
        for stat in stat_list:
            tp_cnt, fp_cnt, fn_cnt = stat[bug_sig]
            tp_cnt_list.append(tp_cnt)
            fp_cnt_list.append(fp_cnt)
            fn_cnt_list.append(fn_cnt)
        tp = float(sum(tp_cnt_list)) / len(tp_cnt_list)
        fp = float(sum(fp_cnt_list)) / len(fp_cnt_list)
        fn = float(sum(fn_cnt_list)) / len(fn_cnt_list)
        print("%s: TP = %.2f, FP = %.2f, FN = %.2f" % (bug_sig, tp, fp, fn))

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

    bug_sigs = get_tool_sigs(sig_set, [BD, ME, RE])
    BD_sig, ME_sig, RE_sig = bug_sigs
    bug_info = init_b2_bug_info(BD_sig, ME_sig, RE_sig)
    targ_list = os.listdir(result_dirs[0])
    targ_list.sort()

    stat_list = []
    for result_dir in result_dirs:
        stat = analyze_dir(bug_info, result_dir, targ_list)
        stat_list.append(stat)
    print("===================================")
    print_statistics(stat_list, bug_sigs)

if __name__ == "__main__":
    main()

import sys, os
from common import get_tool_sigs
from common import read_log_file, count_from_log
from common import AW, BD, CH, EL, IB, ME, MS, RE, SC, TO

ALL_BUGS = [AW, BD, CH, EL, IB, ME, MS, RE, SC, TO]

def analyze_dir(bug_sigs, result_dir, targ_list):
    total_alarms = 0
    issue_contracts = 0
    count_map = {}
    for bug_sig in bug_sigs:
        count_map[bug_sig] = 0

    for targ in targ_list:
        found_issue = False
        buf = read_log_file(result_dir, targ)
        for bug_sig in bug_sigs:
            alarm_sig = "%s at" % bug_sig
            count = count_from_log(buf, alarm_sig, False)
            count_map[bug_sig] = count_map[bug_sig] + count
            total_alarms += count
            if count > 0:
                found_issue = True
        if found_issue:
            issue_contracts += 1

    for bug_sig in bug_sigs:
        print("%s alarms: %d" % (bug_sig, count_map[bug_sig]))
    print("Total alarms: %d" % total_alarms)
    print("Contracts w/ alarm: %d" % issue_contracts)

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: %s <result dir>" % sys.argv[0])
        exit(1)

    if sys.argv[1] in ["--ilf", "--sfuzz", "--manticore", "--mythril"]:
        sig_set = "smartian-" + sys.argv[1][2:] # e.g., "smartian-ilf"
        result_dir = sys.argv[2]
    else:
        sig_set = "default"
        result_dir = sys.argv[1]


    bug_sigs = get_tool_sigs(sig_set, ALL_BUGS)
    targ_list = os.listdir(result_dir)
    targ_list.sort()

    analyze_dir(bug_sigs, result_dir, targ_list)

if __name__ == "__main__":
    main()

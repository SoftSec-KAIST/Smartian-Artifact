import sys, os
from common import get_tool_sigs
from common import read_log_file, count_from_log
from common import IB

def analyze_dir(IB_sig, result_dir, targ_list):
    alarm_count = 0
    for targ in targ_list:
        buf = read_log_file(result_dir, targ)
        alarm_sig = "%s at" % IB_sig
        alarm_count += count_from_log(buf, alarm_sig, False)
    return alarm_count

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
    targ_list = os.listdir(result_dirs[0])
    targ_list.sort()

    alarm_count_list = []
    for result_dir in result_dirs:
        alarm_count = analyze_dir(IB_sig, result_dir, targ_list)
        alarm_count_list.append(alarm_count)

    avg_alarm_count = float(sum(alarm_count_list)) / len(alarm_count_list)

    print("Total %s alarms: %.2f" % (IB_sig, avg_alarm_count))

if __name__ == "__main__":
    main()

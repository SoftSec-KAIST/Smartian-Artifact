import sys, os

LOG_FILE_NAME = "log.txt"
W_DFEED_FILE_NAME = "with_dfeed.txt"
WO_DFEED_FILE_NAME = "without_dfeed.txt"

def get_analysis_time(filepath):
    f = open(filepath, "r")
    buf = f.read()
    f.close()
    idx = buf.find(" Start main fuzzing")
    assert(idx != -1)
    buf = buf[:idx]
    idx = buf.rfind("[00:")
    buf = buf[idx:]
    tokens = buf[1:-1].split(":")
    sec = int(tokens[-1]) + int(tokens[-2]) * 60
    return sec

def get_replay_time(filepath):
    f = open(filepath, "r")
    buf = f.read()
    f.close()
    lines = buf.strip().split("\n")
    return float(lines[-1].split()[-1])

def main():
    if len(sys.argv) != 2:
        print("Usage: python %s <experiment result dir>" % sys.argv[0])
        exit(1)

    result_dir = sys.argv[1]
    targ_list = os.listdir(result_dir)
    analysis_time_list = []
    replay_time_with_dfeed = 0.0
    replay_time_without_dfeed = 0.0
    for targ in targ_list:
        targ_path = os.path.join(result_dir, targ)
        log_path = os.path.join(targ_path, LOG_FILE_NAME)
        analysis_time_list.append(get_analysis_time(log_path))
        with_dfeed_path = os.path.join(targ_path, W_DFEED_FILE_NAME)
        without_dfeed_path = os.path.join(targ_path, WO_DFEED_FILE_NAME)
        replay_time_with_dfeed += get_replay_time(with_dfeed_path)
        replay_time_without_dfeed += get_replay_time(without_dfeed_path)
    avg_analysis_time = sum(analysis_time_list) / len(analysis_time_list)
    max_analysis_time = max(analysis_time_list)
    print("Average analysis time: %d" % avg_analysis_time)
    print("Maximum analysis time: %d" % max_analysis_time)
    print("Replay time w/ data feedback: %.3f" % replay_time_with_dfeed)
    print("Replay time w/o data feedback: %.3f" % replay_time_without_dfeed)

if __name__ == "__main__":
    main()

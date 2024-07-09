import os, sys
import re
import json

OUTDIR = "/home/test/SmarTest-workspace/output"
BUGDIR = "/home/test/SmarTest-workspace/output/bugs"

def parse_disproven(line):
  pattern = r'line (\d+).*?(\d+\.\d+s)'
  matched = re.search(pattern, line)
  if matched:
    line_number = matched.group(1)
    found_time = matched.group(2)
    found_time = str(round(float(found_time[:-1]),2))
    int_part, frac_part = found_time.split('.')
    days = int(int_part) // 86400
    hours = (int(int_part) % 86400) // 3600
    minutes = (int(int_part) % 3600) // 60
    seconds = int(int_part) % 60
    if days == 0 and hours == 0 and minutes == 0 and seconds == 0: seconds = 1
    return (f'[{days:02}:{hours:02}:{minutes:02}:{seconds:02}]', line_number)
  else: return None

def mk_log_file():
  STDOUT = OUTDIR + "/stdout.txt"
  LOG = OUTDIR + "/log.txt"
  std = open(STDOUT, "r")
  log = open(LOG, "w")
  L = std.readlines()
  seq = []
  bugs = []
  i = 0; 
  while i < len(L):
    line = L[i].strip()
    if line != "":
      ret = parse_disproven(line)
      if ret is not None:
        bugs.append(ret)
        _, l_num = ret
        i += 1
        while L[i].strip() != "":
          seq.append(L[i])
          i += 1
        fname = BUGDIR + f"/IO_line_{l_num}"
        with open(fname, "w") as f:
          for t in seq:
            f.write(t)
        seq.clear()
    i += 1
  bugs.sort()
  for found_time, line_number in bugs:
    log.write(f'{found_time} Found IntegerBug at {line_number}\n')
  log.close()
  std.close()
          
if __name__ == '__main__':
    mk_log_file()
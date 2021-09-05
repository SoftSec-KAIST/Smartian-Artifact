import sys
import os
import urllib.request
from bs4 import BeautifulSoup

def get_addr_list(contract_list_file):
    addrs = []
    with open(contract_list_file) as f:
        for line in f.readlines():
            addrs.append(line.strip())
    return addrs

def download_from_etherscan(addr):
    url = "https://etherscan.io/address/" + addr

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    res = urllib.request.urlopen(req)
    bsObject = BeautifulSoup(res, "html.parser")

    # Find a main contract name
    cont = bsObject.find(class_="h6 font-weight-bold mb-0").text

    # Make a solidity code
    source = bsObject.find("pre").text

    return cont, source

def collect_benchmark(contract_list_file, out_dir):
    addrs = get_addr_list(contract_list_file)
    total = len(addrs)
    i = 0
    os.system("mkdir -p %s" % out_dir)
    for addr in addrs:
        i += 1
        if i % 10 == 0:
            print("Progress: %d / %d ..." % (i, total))
        try:
            cont, source = download_from_etherscan(addr)
        except Exception as e:
            print(e)
            print("Continue...")
            continue
        f = open(os.path.join(out_dir, "%s_%s.sol" % (addr, cont)), "w")
        f.write(source)
        f.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: %s <contract list file> <output dir>" % sys.argv[0])
        exit(1)
    contract_list_file = sys.argv[1]
    out_dir = sys.argv[2]
    collect_benchmark(contract_list_file, out_dir)

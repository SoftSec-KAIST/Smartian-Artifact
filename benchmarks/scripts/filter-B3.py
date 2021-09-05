import sys
import os
import json

def setup_workspace(solc_version):
    SOLC_URL = "https://github.com/ethereum/solidity/releases/download/v%s/solc-static-linux"
    os.system("rm -rf ./workspace")
    os.mkdir("./workspace")
    os.mkdir("./workspace/tmp")
    url = SOLC_URL % solc_version
    os.system("wget -O ./workspace/solc %s" % url)
    os.system("chmod +x ./workspace/solc")

def check_binsize(filepath, addr, cont):
    # Prepare directory
    tmp_dir = "./workspace/tmp/%s" % addr
    os.system("mkdir -p %s" % tmp_dir)

    # Compile
    cmd = "./workspace/solc --bin -o %s %s" % (tmp_dir, filepath)
    os.system(cmd)

    # Check bytecode size
    bin_file = "%s/%s.bin" % (tmp_dir, cont)
    if os.path.exists(bin_file):
        f = open(bin_file, "r")
        buf = f.read()
        f.close()
        if "__" in buf:
            print("%s: contract is not self-contained" % addr)
            size = 0
        else:
            size = len(buf)
    else:
        size = 0 # Failed to compile

    return size

def check_noarg(filepath, addr, cont):
    # Prepare directory
    tmp_dir = "./workspace/tmp/%s" % addr
    os.system("mkdir -p %s" % tmp_dir)

    # Compile
    cmd = "./workspace/solc --abi -o %s %s" % (tmp_dir, filepath)
    os.system(cmd)

    # Check bytecode size
    abi_file = "%s/%s.abi" % (tmp_dir, cont)
    if os.path.exists(abi_file):
        f = open(abi_file, "r")
        buf = f.read()
        abi = json.loads(buf)
        f.close()
        for x in abi:
            if x["type"] == "constructor":
                if len(x["inputs"]) == 0:
                    return True
                else:
                    return False
        # When constructor is omitted, this indicate no argument is needed.
        print("No constructor entry in %s" % abi_file)
        return True
    else:
        return False # Failed to compile

def save_big_contracts(contracts, limit):
    print("Total contracts: %d" % len(contracts))
    contracts.sort(key=lambda x: x[3], reverse=True)
    contracts = contracts[:limit]
    os.system("rm -rf ./B3")
    os.system("mkdir ./B3")
    os.system("mkdir ./B3/sol")
    with open("./assets/B3.list", "w") as f:
        for (filepath, addr, cont, _) in contracts:
            os.system("cp %s ./B3/sol/%s.sol" % (filepath, addr))
            f.write("%s,%s\n" % (addr, cont))

def filter_benchmark(download_dir):
    contracts = []
    files = os.listdir(download_dir)
    for filename in files:
        filepath = os.path.join(download_dir, filename)
        addr = filename.split("_")[0]
        cont = filename.split("_")[1].split(".")[0]
        binsize = check_binsize(filepath, addr, cont)
        noarg = check_noarg(filepath, addr, cont)
        if binsize > 0 and noarg:
            contracts.append((filepath, addr, cont, binsize))
    save_big_contracts(contracts, 500)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: %s <download dir> <solc version>" % sys.argv[0])
        exit(1)
    download_dir = sys.argv[1]
    solc_version = sys.argv[2]
    setup_workspace(solc_version)
    filter_benchmark(download_dir)

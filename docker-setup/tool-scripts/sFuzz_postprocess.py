import os, sys
import json

def to_account_list(accounts):
    res = []
    for addr in accounts:
        res.append(accounts[addr])
    return res

def load(contract_name, path):
    with open(path) as f:
        lines = f.readlines()
    lines = list(map(lambda x: x.strip(), lines))

    accounts = {}
    account = {
                'Account': '%040x' % 0xe0,
                'Balance': '%d' % 0xffffffffff,
                'Agent': 'SFuzzAgent',
                'Contract': '%040x' % 0xf0
            }
    accounts[0xe0] = account
    txs = []
    deployer = None

    met_constructor = False
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        assert 'Dump' in line
        if 'Account' in line:
            addr = int(lines[idx + 1])
            balance = int(lines[idx + 2])
            is_sender = int(lines[idx + 3]) == 1
            if addr not in accounts and addr != 0xf0:
                account = {
                            'Account': '%040x' % addr,
                            'Balance': '%d' % balance,
                            'Agent': 'NoAgent',
                            'Contract': ''
                        }
                accounts[addr] = account
            idx += 4
        elif 'Transaction' in line:
            contract_addr = int(lines[idx + 1], 16)
            sender = int(lines[idx + 2])
            value = int(lines[idx + 3])
            if sender not in accounts and sender != 0xf0:
                if value == 0:
                    balance = 0xffffffffff
                else:
                    balance = value * 2
                account = {
                            'Account': '%040x' % sender,
                            'Balance': '%d' % balance,
                            'Agent': 'NoAgent',
                            'Contract': ''
                        }
                accounts[sender] = account
            gas_price = int(lines[idx + 4])
            gas = int(lines[idx + 5])
            data = lines[idx + 6]
            nonce = int(lines[idx + 7])
            block_num = int(lines[idx + 8])
            time_stamp = int(lines[idx + 9])
            tx = {
                    'Function': '',
                    'Timestamp': '%d' % time_stamp,
                    'Blocknum': '%d' % block_num,
                    'From': '%040x' % sender,
                    'To': '%040x' % contract_addr,
                    'Value': '%d' % value,
                    'Data': data,
                    #'GasPrice': gas_price,
                    #'GasLimit': gas
                }
            if not met_constructor:
                deployer = sender
                met_constructor = True
                deployTx = tx
            else:
                txs.append(tx)
            idx += 11
        else:
            print('Invalid Format')
            sys.exit(-1)
    tc = { 'Entities': to_account_list(accounts),
            'TargetDeployer': '%040x' % deployer,
            'TargetContract': '%040x' % 0xf1,
            'DeployTx': deployTx,
            'Txs': txs }
    return tc

def transform(contract_name, dirname):
    for name in os.listdir(dirname):
        path = os.path.join(dirname, name)
        tc = load(contract_name, path)
        with open(path, 'w') as f:
            f.write(json.dumps(tc))

if __name__ == '__main__':
    contract_name = sys.argv[1]
    dirname = sys.argv[2]
    transform(contract_name, dirname)

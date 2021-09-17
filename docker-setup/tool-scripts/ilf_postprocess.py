import os, sys
import json
import binascii
from eth_abi import encode_abi
import web3

def translate_uint(arg):
    return int(arg)

def translate_int(arg):
    return int(arg)

def translate_bool(arg):
    return bool(arg)

def translate_bytes(arg):
    return bytes(list(map(lambda x: int(x), arg)))

def translate_args(ty, arg):
    if ty.endswith('[]'):
        if ty.startswith('uint'):
            return list(map(lambda x: translate_uint(x), arg))
        if ty.startswith('int'):
            return list(map(lambda x: translate_int(x), arg))
        if ty.startswith('address'):
            return arg
        elif ty.startswith('bool'):
            return list(map(lambda x: translate_bool(x), arg))
        elif ty.startswith('bytes'):
            return list(map(lambda x: translate_bytes(x), arg))
        elif ty.startswith('string'):
            return arg
        else:
            print("Unhandled ty", ty)
            sys.exit(-1)
    else:
        if ty.startswith('uint'):
            return translate_uint(arg)
        if ty.startswith('int'):
            return translate_int(arg)
        elif ty == 'address':
            return arg
        elif ty == 'bool':
            return translate_bool(arg)
        elif ty.startswith('bytes'):
            return translate_bytes(arg)
        elif ty.startswith('string'):
            return arg
        else:
            print("Unhandled ty", ty)
            sys.exit(-1)

def load(contract_name, abipath, path):
    with open(path) as f:
        lines = f.readlines()
    deployer = 0x2fE5e54E71755A9719FD5B06c8697CeFa1283165
    CONTRACTADDR = 0x724F259aEe54E29b78536457a05BB992C771D252
    BALANCE = 100000000000000000000000000000
    ACCOUNT0 = 0x2fe5e54e71755a9719fd5b06c8697cefa1283165
    ACCOUNT1 = 0x9b4ffb882b897fd506116cfb02362af19c96512d
    ACCOUNT2 = 0x86c5593ac99644f476986488abaaba94dd00a584
    ACCOUNT3 = 0x0c1d67ee5b4654fe0341e5897ec11d62bc29cf5c
    ACCOUNT4 = 0xf392acadbf35d37f68a3ee991beb593188036763
    accounts = [
        { 'Account': '%040x' % ACCOUNT0, 'Balance': '%d' % BALANCE, 'Agent': 'NoAgent', 'Contract': '' },
            { 'Account': '%040x' % ACCOUNT1, 'Balance': '%d' % BALANCE, 'Agent': 'NoAgent', 'Contract': '' },
            { 'Account': '%040x' % ACCOUNT2, 'Balance': '%d' % BALANCE, 'Agent': 'NoAgent', 'Contract': '' },
            { 'Account': '%040x' % ACCOUNT3, 'Balance': '%d' % BALANCE, 'Agent': 'NoAgent', 'Contract': '' },
            { 'Account': '%040x' % ACCOUNT4, 'Balance': '%d' % BALANCE, 'Agent': 'NoAgent', 'Contract': '' }
            ]
    with open(abipath) as f:
        abi = json.loads(f.read())
    ty_map = {}
    for f in abi:
        if f['type'] == 'fallback' or f['type'] == 'constructor':
            continue
        '''
        elif f['type'] == 'constructor':
            f['name'] = ''
            if 'inputs' in f:
                tys = list(map(lambda x: x['type'], f['inputs']))
            else:
                tys = []
        else:
            tys = list(map(lambda x: x['type'], f['inputs']))
        '''
        tys = list(map(lambda x: x['type'], f['inputs']))
        ty_str = '%s(' % f['name']
        if len(tys) == 0:
            ty_str += ')'
        for i in range(len(tys)):
            if i == len(tys) - 1:
                ty_str += '%s)' % tys[i]
            else:
                ty_str += '%s,' % tys[i]
        w3 = web3.Web3()
        sig = w3.sha3(text=ty_str)[0:4].hex()
        ty_map[f['name']] = (tys, sig)
    deployTx = {
            'Function': '',
            'From': '%040x' % deployer,
            'To': '%040x' % CONTRACTADDR,
            'Value': '0',
            'Data': '' }
    txs = []
    for line in lines:
        line = line.strip()
        tx = json.loads(line)
        if tx['method'] == '':
            continue
        tys, sig = ty_map[tx['method']]
        args = tx['arguments']
        for i in range(len(args)):
            args[i] = translate_args(tys[i], args[i])
        data = sig + binascii.hexlify(encode_abi(tys, args)).decode('ascii')
        tx = {
                'Function': tx['method'],
                'Timestamp': tx['timestamp'],
                'Blocknum': tx['number'],
                'From': accounts[tx['sender']]['Account'],
                'To': '%040x' % int(tx['call_address'], 16),
                'Value': '%d' % tx['amount'],
                'Data': data,
                #'GasPrice': 0,
                #'GasLimit': 0
            }
        txs.append(tx)
    tc = { 'Entities': accounts,
            'TargetDeployer': '%040x' % deployer,
            'TargetContract': '%040x' % CONTRACTADDR,
            'DeployTx': deployTx,
            'Txs': txs }
    return tc

def transform(contract_name, abipath, dirname):
    for name in os.listdir(dirname):
        path = os.path.join(dirname, name)
        tc = load(contract_name, abipath, path)
        with open(path, 'w') as f:
            f.write(json.dumps(tc))

if __name__ == '__main__':
    contract_name = sys.argv[1]
    abipath = sys.argv[2]
    dirname = sys.argv[3]
    transform(contract_name, abipath, dirname)

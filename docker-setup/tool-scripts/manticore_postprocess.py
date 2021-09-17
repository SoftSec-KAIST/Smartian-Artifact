import os, sys
import json

def load(path):
    print(path)
    with open(path) as f:
        j = json.loads(f.read())

    accounts = []
    txs = []

    acc_map = {}
    contract_map = {}
    for tx in j:
        if tx['from_name'] not in acc_map:
            acc_map[tx['from_name']] = tx['from_address']
        if tx['type'] == 'CREATE' and tx['to_name'] not in contract_map:
            contract_map[tx['to_name']] = tx['to_address']
            deployer = '%040x' % tx['from_address']
            target_addr = '%040x' % tx['to_address']
            '''
            if tx['to_name'] == 'contract0':
                deployer = '%040x' % tx['from_address']
                target_addr = '%040x' % tx['to_address']
            else:
                print('Unhandled')
                sys.exit(-1)
            '''
    for name in acc_map:
        addr = acc_map[name]
        balance = 10 ** 10
        account = { 'Account': '%040x' % addr, 'Balance': '%d' % balance, 'Agent': 'NoAgent', 'Contract': '' }
        accounts.append(account)

    met_constructor = False
    for t in j:
        tx = {
                'Function': '',
                'From': '%040x' % t['from_address'],
                'To': '%040x' % t['to_address'],
                'Value': '%d' % t['value'],
                'Data': t['data']
            }
        #if t['type'] == 'CREATE' and t['to_name'] == 'contract0':
        if t['type'] == 'CREATE':
            deploy_tx = tx
        else:
            txs.append(tx)
    tc = { 'Entities': accounts,
            'TargetDeployer': deployer,
            'TargetContract': target_addr,
            'DeployTx': deploy_tx,
            'Txs': txs }
    return tc

def transform(dirname):
    for name in os.listdir(dirname):
        if 'tc_' in name:
            path = os.path.join(dirname, name)
            tc = load(path)
            with open(path, 'w') as f:
                f.write(json.dumps(tc))

if __name__ == '__main__':
    dirname = sys.argv[1]
    transform(dirname)

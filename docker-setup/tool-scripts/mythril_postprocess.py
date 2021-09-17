import os, sys
import json

def has_user(addr, accounts):
    for account in accounts:
        if addr == account['Account']:
            return True
    return False

def load(contract_name, path):
    print(path)
    with open(path) as f:
        j = json.loads(f.read())

    accounts = []
    txs = []

    CREATOR = '0xAFFEAFFEAFFEAFFEAFFEAFFEAFFEAFFEAFFEAFFE'.lower()
    ATTACKER = '0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF'.lower()
    SOMEGUY = '0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'.lower()
    j_accounts = j['initialState']['accounts']
    for addr in j_accounts:
        if addr not in [CREATOR, ATTACKER, SOMEGUY]:
            target_addr = addr[2:]
        balance = j_accounts[addr]['balance']
        account = { 'Account': addr[2:], 'Balance': '%d' % int(balance, 16), 'Agent': 'NoAgent', 'Contract': '' }
        accounts.append(account)

    steps = j['steps']
    for step in steps:
        tx = {
                'Function': '',
                'From': step['origin'][2:],
                'To': step['address'] if len(step['address']) == 0 else step['address'][2:],
                'Value': '%d' % int(step['value'], 16),
                'Data': step['input'][2:]
            }
        if 'number' in step:
            tx['Blocknum'] = step['number']
        if 'timestamp' in step:
            tx['Timestamp'] = step['timestamp']
        if tx['To'] == '':
            deployer = tx['From']
            tx['To'] = target_addr
            deployTx = tx
        else:
            txs.append(tx)
        if not has_user(tx['From'], accounts):
            account = { 'Account': tx['From'], 'Balance': '0', 'Agent': 'NoAgent', 'Contract': '' }
            accounts.append(account)

    tc = { 'Entities': accounts,
            'TargetDeployer': deployer,
            'TargetContract': target_addr,
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

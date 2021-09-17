#!/usr/bin/python3

import os, sys
import os.path as path
import shutil
import argparse
import json
import random

truffle_config_path = '{}/templates/truffle-config.js'.format(path.dirname(__file__))
migrations_sol_path = '{}/templates/Migrations.sol'.format(path.dirname(__file__))
migrations_file_1_path = '{}/templates/1_initial_migration.js'.format(path.dirname(__file__))
DEPLOY_TEMPLATE = '''var my_contract = artifacts.require("%s");

module.exports = function(deployer) {
  deployer.deploy(my_contract);
};'''

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--source', dest='source_path', type=str,
                        default=None, required=True,
                        help='Target Solidity source code path')
    parser.add_argument('--name', dest='contract_name', type=str,
                        default=None, required=True,
                        help='Main contract name')
    parser.add_argument('--proj', dest='proj_path', type=str,
                        default=None, required=True,
                        help='Destination Truffle project path')
    parser.add_argument('--ilf', dest='ilf_path', type=str,
                        default=None, required=True,
                        help='ILF project base directory')

    args = parser.parse_args()
    return args

def init_proj(source_path, proj_path, contract_name):
    # Create base directory
    os.system('mkdir -p {}'.format(proj_path))
    # Copy truffle configuration from templates
    shutil.copy(truffle_config_path,
                path.join(proj_path, "truffle-config.js"))
    # Create Solidity source directory
    contracts_dir = path.join(proj_path, 'contracts')
    os.system('mkdir -p {}'.format(contracts_dir))
    # Copy Solidity source code
    source_name = path.basename(source_path)
    shutil.copy(source_path, path.join(contracts_dir, source_name))
    # Copy deploy-related files except one: 2_deploy_contracts.js
    shutil.copy(migrations_sol_path,
                path.join(contracts_dir, 'Migrations.sol'))
    migrations_dir = path.join(proj_path, 'migrations')
    os.system('mkdir -p {}'.format(migrations_dir))
    shutil.copy(migrations_file_1_path,
                path.join(migrations_dir, '1_initial_migration.js'))
    with open(path.join(migrations_dir, '2_deploy_contracts.js'), 'w') as f:
        f.write(DEPLOY_TEMPLATE % contract_name)

def deploy_contract(ilf_path, proj_path):
    script_path = path.join(ilf_path, 'script', 'extract.py')
    cmd = 'python3 {} --proj {} --port 8545'.format(script_path, proj_path)
    os.system(cmd)

if __name__ == '__main__':
    args = get_args()
    if not os.path.isfile(args.source_path):
        print('Invalid source code path')
        sys.exit(-1)

    proj_path = path.abspath(args.proj_path)
    ilf_path = path.abspath(args.ilf_path)

    init_proj(args.source_path, proj_path, args.contract_name)
    deploy_contract(ilf_path, proj_path)

import sys
import time
import json
from itertools import chain

from manticore.ethereum import ManticoreEVM
from manticore.ethereum.detectors import (
        DetectEnvInstruction,
        DetectInvalid,
        DetectReentrancySimple,
        DetectReentrancyAdvanced,
        DetectIntegerOverflow,
        DetectUnusedRetVal
        )
from manticore.ethereum.plugins import (
        FilterFunctions,
        VerboseTrace
        )
from manticore.utils import config
from manticore.utils.log import RunningTime

MAXTX=3 # Configurable

def init_config():
    config.get_group("smt").timeout=120
    config.get_group("smt").memory=16384
    config.get_group("smt").optimize = False
    config.get_group("evm").oog = "ignore"

def create_EVM(src, name, benchmark):
    RunningTime()

    print('Creating EVM object...')
    m = ManticoreEVM()

    print('Registering detector modules...')
    detectors = {}
    if benchmark == "B1":
        # IB Detector
        ib = DetectIntegerOverflow()
        detectors['IntegerBug'] = ib
        m.register_detector(ib)
    elif benchmark == "B2":
        # BD Detector
        bd = DetectEnvInstruction()
        detectors['BlockstateDependency'] = bd
        m.register_detector(bd)
        # ME Detector
        me = DetectUnusedRetVal()
        detectors['MishandledException'] = me
        m.register_detector(me)
        # RE Detector
        re = DetectReentrancySimple()
        detectors['Reentrancy'] = re
        m.register_detector(re)
    else:
        print('Unexpected benchmark: %s' % benchmark)
        exit(1)

    print('Adding filters...')
    # Avoid all human level tx that has no effect on the storage
    filter_nohuman_constants = FilterFunctions(
        regexp=r".*", depth="human", mutability="constant", include=False
    )
    m.register_plugin(filter_nohuman_constants)

    print('Creating accounts...')
    user_account = m.create_account(balance=10**10)
    contract_account = m.solidity_create_contract(src, owner=user_account, contract_name=name)

    return m, detectors, user_account, contract_account

def save_tc(m, state):
    with state as temp_state:
        txlist = []
        world = temp_state.platform
        for sym_tx in world.human_transactions:
            try: # Caution: we should handle this exception and continue.
                conc_tx = sym_tx.concretize(temp_state)
            except Exception as e:
                print(e)
                print('Skip this test case')
                return
            txlist.append(conc_tx.to_dict(m))

        with open('/home/test/manticore-workspace/output/tc_%0.5f' % state._elapsed, 'w') as f:
            f.write(json.dumps(txlist))

def get_time_str(elapsed):
    s = int(elapsed)
    d = s // 86400
    s = s - (d * 86400)
    h = s // 3600
    s = s - (h * 3600)
    m = s // 60
    s = s - (m * 60)
    time_str = '%02d:%02d:%02d:%02d' % (d, h, m, s)
    return time_str

def dump_bug(state, detectors):
    for bug_type in detectors:
        detector = detectors[bug_type]
        for addr, pc, msg, at_init, cond in detector.get_findings(state):
            if state.can_be_true(cond):
                print('Bug Found')
                time_str = get_time_str(state._elapsed)
                bug_pc = pc - 1 if bug_type == "IntegerBug" else 0
                msg = '[%s] Found %s at %x\n' % (time_str, bug_type, bug_pc)
                with open('/home/test/manticore-workspace/output/log.txt', 'a+') as f:
                    f.write(msg)

def main(timeout, src, name, benchmark):
    print('Contract name: %s' % name)
    init_config()
    m, detectors, user_account, contract_account = create_EVM(src, name, benchmark)

    if contract_account is None:
        print('Failed to create contract ccount')
        return

    handled_killed_states = set()
    print('Start running...')
    with m.kill_timeout(timeout=timeout):
        for _ in range(MAXTX):
            if m.is_killed():
                print('EVM object is killed, exit.')
                break
            symbolic_data = m.make_symbolic_buffer(320)
            symbolic_value = m.make_symbolic_value()
            print('Making transaction...')
            m.transaction(
                caller=user_account, address=contract_account,
                value=symbolic_value, data=symbolic_data
            )

            print('Start handling ready_states')
            total = m.count_ready_states()
            i = 0
            for state in m.ready_states:
                print('save_tc on state %d / %d' % (i, total))
                save_tc(m, state)
                print('dump_bug on state %d / %d' % (i, total))
                dump_bug(state, detectors)
                i += 1

            for state in chain(m.ready_states, m.killed_states):
                print('save_tc on state %d / %d' % (i, total))
                save_tc(m, state)
                i += 1

            print('Start handling killed_states')
            total = m.count_killed_states()
            i = 0
            for state in m.killed_states:
                if state.id not in handled_killed_states:
                    handled_killed_states.add(state.id)
                    print('save_tc on state %d / %d' % (i, total))
                    save_tc(m, state)
                    print('dump_bug on state %d / %d' % (i, total))
                    dump_bug(state, detectors)
                else:
                    print('Skip already handled killed state')
                i += 1

if __name__ == '__main__':
    timeout = int(sys.argv[1])
    src = sys.argv[2]
    name = sys.argv[3]
    benchmark = sys.argv[4]
    main(timeout, src, name, benchmark)

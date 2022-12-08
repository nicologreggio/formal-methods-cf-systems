import sys
from typing import Tuple, List, NewType

import pynusmv
from pynusmv.dd import State, Inputs, BDD
from pynusmv.fsm import BddFsm

from check_inv.symbolic_reachable import check_explain_inv_spec, Trace

Witness = NewType("Witness", List[State | Inputs])


def get_witness(fsm: BddFsm, trace: Trace) -> Witness:
    current_state = fsm.pick_one_state_random(trace[-1])
    witness = [current_state]
    for states in trace[-2::-1]:
        pre_states = fsm.pre(current_state) & states
        pre_state = fsm.pick_one_state_random(pre_states)
        inputs = fsm.get_inputs_between_states(pre_state, current_state)
        witness = [pre_state, fsm.pick_one_inputs(inputs)] + witness
        current_state = pre_state

    return witness


if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "filename.smv")
    sys.exit(1)

pynusmv.init.init_nusmv()
filename = sys.argv[1]
pynusmv.glob.load_from_file(filename)
pynusmv.glob.compute_model()
invtype = pynusmv.prop.propTypes["Invariant"]
fsm = pynusmv.glob.prop_database().master.bddFsm
for prop in pynusmv.glob.prop_database():
    spec = prop.expr
    if prop.type == invtype:
        print("Property", spec, "is an INVARSPEC.")
        res, trace = check_explain_inv_spec(fsm, spec)
        if res == True:
            print("Invariant is respected")
        else:
            print("Invariant is not respected")

            witness = get_witness(fsm, trace)
            for i, el in enumerate(witness):
                if i % 2 == 0:
                    print("%State: ", end="")
                else:
                    print("*Input: ", end="")

                print(el.get_str_values())
    else:
        print("Property", spec, "is not an INVARSPEC, skipped.")

pynusmv.init.deinit_nusmv()

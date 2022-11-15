import pynusmv
import sys
from check_inv.symbolic_reachable import check_explain_inv_spec


def print_counterexample(fsm, trace):
    current_state = fsm.pick_one_state_random(trace[-1])
    counterexample = [current_state]
    for states in trace[-2::-1]:
        pre_states = fsm.pre(current_state)
        current_states = pre_states & states
        current_state = fsm.pick_one_state_random(current_states)
        counterexample.insert(0, current_state)

    for state in counterexample:
        print(state.get_str_values())


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
            print_counterexample(fsm, trace)
    else:
        print("Property", spec, "is not an INVARSPEC, skipped.")

pynusmv.init.deinit_nusmv()

import pynusmv
import sys

from check_inv.symbolic_reachable import check_explain_inv_spec


def get_counterexample(fsm, trace, starting_state):
    current_state = starting_state
    counterexample = [(starting_state, {})]
    for states in trace[-2::-1]:
        pre_states = fsm.pre(current_state) & states
        pre_state = fsm.pick_one_state_random(pre_states)
        inputs = fsm.get_inputs_between_states(pre_state, current_state)
        counterexample = [(pre_state, fsm.pick_one_inputs(inputs))] + counterexample
        current_state = pre_state

    return counterexample


def print_trace(trace):
    for state, inp in trace:
        print((state.get_str_values(), inp.get_str_values() if inp else {}))


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

            counterexample = get_counterexample(
                fsm, trace, fsm.pick_one_state_random(trace[-1])
            )
            print_trace(counterexample)
    else:
        print("Property", spec, "is not an INVARSPEC, skipped.")

pynusmv.init.deinit_nusmv()

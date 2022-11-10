import pynusmv


def print_all_states_bdd(fsm, bdd):
    for state in fsm.pick_all_states(bdd):
        print(state.get_str_values())


def print_one_state_bdd(fsm, bdd):
    print(fsm.pick_one_state(bdd).get_str_values())


def spec_to_bdd(model, spec):
    """
    Return the set of states of `model` satisfying `spec`, as a BDD.
    """
    bddspec = pynusmv.mc.eval_ctl_spec(model, spec)
    return bddspec


def symbolic_reachable(fsm, phi):
    # if fsm.init.intersected(phi): return False, [fsm.init & phi]

    new = fsm.init
    reach = fsm.init
    trace = []
    while fsm.count_states(new):
        if new.intersected(phi):
            trace.append(new & phi)
            return False, trace
        else:
            trace.append(new)
        
        new = (fsm.post(new)).diff(reach)
        reach = reach | new

    return True, None


def check_explain_inv_spec(fsm, spec):
    """
    Return whether the loaded SMV model satisfies or not the invariant
    `spec`, that is, whether all reachable states of the model satisfies `spec`
    or not. Return also an explanation for why the model does not satisfy
    `spec``, if it is the case, or `None` otherwise.

    The result is a tuple where the first element is a boolean telling
    whether `spec` is satisfied, and the second element is either `None` if the
    first element is `True``, or an execution of the SMV model violating `spec`
    otherwise.

    The execution is a tuple of alternating states and inputs, starting
    and ennding with a state. States and inputs are represented by dictionaries
    where keys are state and inputs variable of the loaded SMV model, and values
    are their value.
    """
    specbdd = spec_to_bdd(fsm, spec)
    notspecbdd = specbdd.not_()
    res, trace = symbolic_reachable(fsm, notspecbdd)

    return res, trace
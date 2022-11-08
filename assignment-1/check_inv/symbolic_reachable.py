import pynusmv


def print_bdd(fsm, bdd):
    for state in fsm.pick_all_states(bdd):
        print(state.get_str_values())


def spec_to_bdd(model, spec):
    """
    Return the set of states of `model` satisfying `spec`, as a BDD.
    """
    bddspec = pynusmv.mc.eval_ctl_spec(model, spec)
    return bddspec


def symbolic_reachable(fsm, phi):
    new = fsm.init
    reach = fsm.init

    trace = [new]

    while fsm.pick_all_states(new):
        # print("New: ")
        # print_bdd(fsm, new)
        # print("Reach: ")
        # print_bdd(fsm, reach)
        if new.intersected(phi):
            return False, trace

        # print("Post: ")
        # print_bdd(fsm, fsm.post(new))

        new = (fsm.post(new)).diff(reach)
        reach = reach | new
        trace.append(new)

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
    # print_bdd(fsm, specbdd)
    # res, trace = symbolic_reachable(fsm, specbdd)
    notspecbdd = specbdd.not_()
    # print_bdd(fsm, notspecbdd)
    res, trace = symbolic_reachable(fsm, notspecbdd)

    return res, trace

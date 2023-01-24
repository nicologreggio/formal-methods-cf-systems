import pynusmv
from pynusmv.fsm import BddFsm
from pynusmv.prop import Spec
from pynusmv.dd import BDD, State, Inputs

from pynusmv_lower_interface.nusmv.parser import parser
from collections import deque

from typing import Tuple, List, NewType

Trace = NewType("Trace", List[BDD])
Witness = NewType("Witness", List[State | Inputs])


specTypes = {
    "LTLSPEC": parser.TOK_LTLSPEC,
    "CONTEXT": parser.CONTEXT,
    "IMPLIES": parser.IMPLIES,
    "IFF": parser.IFF,
    "OR": parser.OR,
    "XOR": parser.XOR,
    "XNOR": parser.XNOR,
    "AND": parser.AND,
    "NOT": parser.NOT,
    "ATOM": parser.ATOM,
    "NUMBER": parser.NUMBER,
    "DOT": parser.DOT,
    "NEXT": parser.OP_NEXT,
    "OP_GLOBAL": parser.OP_GLOBAL,
    "OP_FUTURE": parser.OP_FUTURE,
    "UNTIL": parser.UNTIL,
    "EQUAL": parser.EQUAL,
    "NOTEQUAL": parser.NOTEQUAL,
    "LT": parser.LT,
    "GT": parser.GT,
    "LE": parser.LE,
    "GE": parser.GE,
    "TRUE": parser.TRUEEXP,
    "FALSE": parser.FALSEEXP,
}

basicTypes = {
    parser.ATOM,
    parser.NUMBER,
    parser.TRUEEXP,
    parser.FALSEEXP,
    parser.DOT,
    parser.EQUAL,
    parser.NOTEQUAL,
    parser.LT,
    parser.GT,
    parser.LE,
    parser.GE,
}
booleanOp = {parser.AND, parser.OR, parser.XOR, parser.XNOR, parser.IMPLIES, parser.IFF}


def spec_to_bdd(model: BddFsm, spec: Spec) -> BDD:
    """
    Given a formula `spec` with no temporal operators, returns a BDD equivalent to
    the formula, that is, a BDD that contains all the states of `model` that
    satisfy `spec`
    """
    bddspec = pynusmv.mc.eval_simple_expression(model, str(spec))
    return bddspec


def is_boolean_formula(spec: Spec) -> bool:
    """
    Given a formula `spec`, checks if the formula is a boolean combination of base
    formulas with no temporal operators.
    """
    if spec.type in basicTypes:
        return True
    if spec.type == specTypes["NOT"]:
        return is_boolean_formula(spec.car)
    if spec.type in booleanOp:
        return is_boolean_formula(spec.car) and is_boolean_formula(spec.cdr)
    return False


def check_GF_formula(spec: Spec):
    """
    Given a formula `spec` checks if the formula is of the form GF f, where f is a
    boolean combination of base formulas with no temporal operators.
    Returns the formula f if `spec` is in the correct form, None otherwise
    """
    # check if formula is of type GF f_i
    if spec.type != specTypes["OP_GLOBAL"]:
        return False
    spec = spec.car
    if spec.type != specTypes["OP_FUTURE"]:
        return False
    if is_boolean_formula(spec.car):
        return spec.car
    else:
        return None


def parse_react(spec: Spec):
    """
    Visit the syntactic tree of the formula `spec` to check if it is a reactive formula,
    that is wether the formula is of the form

                    GF f -> GF g

    where f and g are boolean combination of basic formulas.

    If `spec` is a reactive formula, the result is a pair where the first element is the
    formula f and the second element is the formula g. If `spec` is not a reactive
    formula, then the result is None.
    """
    # the root of a spec should be of type CONTEXT
    if spec.type != specTypes["CONTEXT"]:
        return None
    # the right child of a context is the main formula
    spec = spec.cdr
    # the root of a reactive formula should be of type IMPLIES
    if spec.type != specTypes["IMPLIES"]:
        return None
    # Check if lhs of the implication is a GF formula
    f_formula = check_GF_formula(spec.car)
    if f_formula == None:
        return None
    # Create the rhs of the implication is a GF formula
    g_formula = check_GF_formula(spec.cdr)
    if g_formula == None:
        return None
    return (f_formula, g_formula)


def find_the_cycle(fsm: BddFsm, recur: BDD, pre_reach: BDD) -> Tuple[State, Trace]:
    s = fsm.pick_one_state(recur)

    found = False
    while not found:
        new = fsm.post(s) & pre_reach
        R = BDD.false(fsm)

        new_frontiers = [new]
        while fsm.count_states(new):
            R = R | new
            new = (fsm.post(new) & pre_reach) - R
            new_frontiers.append(new)

        R = R & recur

        found = s.entailed(R)
        if not found:
            s = fsm.pick_one_state(R)

    return s, new_frontiers


def build_cycle(fsm: BddFsm, recur: BDD, pre_reach: BDD) -> Witness:
    s, new_frontiers = find_the_cycle(fsm, recur, pre_reach)

    k = -1
    for i in range(len(new_frontiers)):
        if s.entailed(new_frontiers[i]):
            k = i
            break

    cycle = [s]
    curr = s
    for i in range(k - 1, -1, -1):
        pre_states = fsm.pre(curr) & new_frontiers[i]
        pre_state = fsm.pick_one_state(pre_states)
        inputs = fsm.get_inputs_between_states(pre_state, curr)
        cycle = [pre_state, fsm.pick_one_inputs(inputs)] + cycle
        curr = pre_state

    inputs = fsm.get_inputs_between_states(s, curr)
    return [s, fsm.pick_one_inputs(inputs)] + cycle


def build_prefix(fsm: BddFsm, trace: Trace, s: State) -> Witness:
    k = -1
    for i in range(len(trace)):
        if s.entailed(trace[i]):
            k = i
            break

    prefix = []
    curr = s
    for i in range(k - 1, -1, -1):
        pre_states = fsm.pre(curr) & trace[i]
        pre_state = fsm.pick_one_state(pre_states)
        inputs = fsm.get_inputs_between_states(pre_state, curr)
        prefix = [pre_state, fsm.pick_one_inputs(inputs)] + prefix
        curr = pre_state

    return prefix


def symbolic_repeatability(
    fsm: BddFsm, f: BDD, g: BDD
) -> Tuple[bool, Witness | None, int]:
    reach = fsm.init
    new = fsm.init

    trace = [new]
    while fsm.count_states(new):
        new = fsm.post(new) - reach
        trace.append(new)
        reach = reach | new

    not_g = ~g

    recur = reach & f & not_g
    while fsm.count_states(recur):
        new = fsm.pre(recur) & not_g
        pre_reach = BDD.false(fsm)

        while fsm.count_states(new):
            pre_reach = pre_reach | new

            if recur.entailed(pre_reach):
                cycle = build_cycle(fsm, recur, pre_reach)
                prefix = build_prefix(fsm, trace, cycle[0])
                return True, prefix + cycle, len(prefix)

            new = (fsm.pre(new) & not_g) - pre_reach

        recur = recur & pre_reach

    return False, None, -1


def check_react_spec(fsm: BddFsm, spec: Spec) -> Tuple[bool, Witness | None, int]:
    """
    Return whether the loaded SMV model satisfies or not the GR(1) formula
    `spec`, that is, whether all executions of the model satisfies `spec`
    or not.
    """
    spec_react = parse_react(spec)

    if spec_react == None:
        return None

    f, g = spec_react
    f_bdd, g_bdd = spec_to_bdd(fsm, f), spec_to_bdd(fsm, g)

    res, witness, i_starting_loop = symbolic_repeatability(fsm, f_bdd, g_bdd)

    return not (res), witness, i_starting_loop

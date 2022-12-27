import pynusmv
from pynusmv.fsm import BddFsm
from pynusmv.prop import Spec
from pynusmv.dd import BDD
from react_mc import spec_to_bdd, parse_react

#def symbolic_repeatable(fsm: BddFsm, phi: BDD) -> Tuple[bool, Trace | None]:

def symbolic_repeatable(fsm, F): 
    new = fsm.init
    reach = fsm.init
    #trace = []
    
    # First phase 
    while fsm.count_states(new):
        new = (fsm.post(new)).diff(reach)
        reach = reach | new
    
    # Second phase 
    recur = reach & F
    while fsm.count_states(recur): 
        # I want to initialize pre_reach as the empty BDD
        pre_reach = BDD.false 
        new = fsm.pre(recur)
        while fsm.count_states(new):
            pre_reach = pre_reach | new 
            if recur.entailed(pre_reach): 
                return True 
            new = (fsm.pre(new)).diff(pre_reach)
        recur = recur & pre_reach
    return False 

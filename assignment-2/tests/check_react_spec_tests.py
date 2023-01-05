import pynusmv
import unittest
import glob, os
from check_react_spec.symbolic_repeatability import (
    check_react_spec as custom_check_react_spec,
)

directory = "./react_examples"
extension = ".smv"


def exact_check_react_spec(_, spec):
    res, trace = pynusmv.mc.check_explain_ltl_spec(spec)
    return res, trace


def check_react_spec_file(filename, check_react_spec):
    with pynusmv.init.init_nusmv():
        pynusmv.glob.load_from_file(filename)
        pynusmv.glob.compute_model()
        type_ltl = pynusmv.prop.propTypes['LTL']
        fsm = pynusmv.glob.prop_database().master.bddFsm
        for prop in pynusmv.glob.prop_database():
            spec = prop.expr
            if prop.type == type_ltl:
                res, _ = check_react_spec(fsm, spec)
                yield res


class CheckReactSpecTest(unittest.TestCase):
    def test_check_react_spec(self):
        os.chdir(directory)
        for filename in glob.glob("*" + extension):
            expected = list(check_react_spec_file(filename, exact_check_react_spec))
            current = list(check_react_spec_file(filename, custom_check_react_spec))
            print(filename)
            print("Expected:", expected)
            print("Current:", current, "\n")
            self.assertEqual(expected, current)


if __name__ == "__main__":
    unittest.main()

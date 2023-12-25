import pynusmv
import unittest
import glob, os
from check_gr1_spec.check_gr1_spec import (
    check_explain_gr1_spec as custom_check_gr1_spec,
)

directory = "./gr1_examples"
extension = ".smv"


def exact_check_gr1_spec(_, spec):
    res, trace = pynusmv.mc.check_explain_ltl_spec(spec)
    return res, trace


def check_gr1_spec_file(filename, check_gr1_spec):
    with pynusmv.init.init_nusmv():
        pynusmv.glob.load_from_file(filename)
        pynusmv.glob.compute_model()
        type_ltl = pynusmv.prop.propTypes["LTL"]
        fsm = pynusmv.glob.prop_database().master.bddFsm
        for prop in pynusmv.glob.prop_database():
            spec = prop.expr
            if prop.type == type_ltl:
                res, *_ = check_gr1_spec(fsm, spec)
                yield res


class CheckGR1SpecTest(unittest.TestCase):
    def test_check_gr1_spec(self):
        os.chdir(directory)
        for filename in glob.glob("*" + extension):
            expected = list(check_gr1_spec_file(filename, exact_check_gr1_spec))
            current = list(check_gr1_spec_file(filename, custom_check_gr1_spec))
            print(filename)
            print("Expected:", expected)
            print("Current:", current, "\n")
            self.assertEqual(expected, current)


if __name__ == "__main__":
    unittest.main()

import pynusmv
import unittest
import glob, os
from check_inv.symbolic_reachable import (
    check_explain_inv_spec as custom_check_explain_inv_spec,
)


directory = "./examples"


def exact_check_explain_inv_spec(_, spec):
    ltlspec = pynusmv.prop.g(spec)
    res, trace = pynusmv.mc.check_explain_ltl_spec(ltlspec)
    return res, trace


def check_inv_file(filename, check_inv):
    with pynusmv.init.init_nusmv():
        pynusmv.glob.load_from_file(filename)
        pynusmv.glob.compute_model()
        invtype = pynusmv.prop.propTypes["Invariant"]
        fsm = pynusmv.glob.prop_database().master.bddFsm
        for prop in pynusmv.glob.prop_database():
            spec = prop.expr
            if prop.type == invtype:
                res, _ = check_inv(fsm, spec)
                yield res


class CheckInvTest(unittest.TestCase):
    def test_check_inv(self):
        os.chdir(directory)
        for filename in glob.glob("*.smv"):
            expected = list(check_inv_file(filename, exact_check_explain_inv_spec))
            current = list(check_inv_file(filename, custom_check_explain_inv_spec))
            # print(filename, expected)
            # print(filename, current)
            self.assertEqual(expected, current)


if __name__ == "__main__":
    unittest.main()

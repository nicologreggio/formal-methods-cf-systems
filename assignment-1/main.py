import pynusmv
import argparse
from enum import Enum

from check_inv.symbolic_reachable import check_explain_inv_spec, get_counterexample


def print_counterexample(counterexample):
    for state in counterexample:
        print(state.get_str_values())


class PrintOptions(Enum):
    all = "all"
    one = "one"

    def __str__(self):
        return self.value


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", type=str, required=True, help="Path to the file to test")
    parser.add_argument(
        "--printoptions",
        type=PrintOptions,
        choices=list(PrintOptions),
        default=PrintOptions.one,
        help="Choose what to print",
    )

    return parser


def main():
    with pynusmv.init.init_nusmv():
        args = init_args().parse_args()

        pynusmv.glob.load_from_file(args.f)
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
                    if args.printoptions == PrintOptions.one:
                        counterexample = get_counterexample(
                            fsm, trace, fsm.pick_one_state_random(trace[-1])
                        )
                        print_counterexample(counterexample)

                    # elif args.printoptions == PrintOptions.all:
                    #     counterexamples = set()
                    #     for state in fsm.pick_all_states(trace[-1]):
                    #         counterexamples.add(get_counterexample(fsm, trace, state))

                    #     for i, counterexample in counterexamples:
                    #         print("Counterexample number", i + 1)
                    #         print_counterexample(counterexample)
            else:
                print("Property", spec, "is not an INVARSPEC, skipped.")


if __name__ == "__main__":
    main()

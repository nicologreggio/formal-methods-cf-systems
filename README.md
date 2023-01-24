# Formal Methods for Cyber-Physical Systems assignments
Assignments for the "Formal Methods for Cyber-Physical Systems" course ; Master's Degree in Computer Science @ UniPd

## Using the compose environment
- provided you have a working installation of docker, you can easily devlop inside an ad-hoc container with a prepared environment
- simply run: `docker compose up --build` to start the env. The first time this will pull the required stuff and build the image. Then a container will be started with the current folder binded in `/code` inside the container
  - leave the window with the compose running open, closing it will stop the container
  - to turn down the environment, simply `CTRL+C` in the compose window
- open a new terminal window and connect to the container `docker exec -ti formal-methods-cf-systems-python-1 bash`
  - now you have a shell with the all the repo mounted in which you can freely operate. This will work as long as the compose is running
  - to quit the shell just type `CTRL+D`

---

# Assignment 1 $-$ Invariant verification
In this assignment you will implement the symbolic algorithm for invariant verification, using BDDs as data structure to represent and manipulate regions.

The attached inv_mc.smv file contains a python script that uses the pynusmv library to verify invariants of SMV programs.

Using the inv_mc.smv script as a starting point, implement a function check_explain_inv_spec (spec) that respects the following specifications:

the function checks if spec is an invariant of the loaded SMV model or not, that is, whether all the reachable states of the model satisfy spec or not.
the function must return an explanation for why the model does not satisfy spec, if it is the case;
the return value is a tuple where the first element is True and the second element is None if the invariant is true. When the invariant is not verified, the first element is False and the second element is an execution of the SMV model that violates spec;
the execution is a tuple of alternating states and inputs, starting and ending with a state. States and inputs are represented by dictionaries where keys are state and inputs variable of the loaded SMV model, and values are their value.

## The pynusmv library
pynusmv is a python wrapper to NuSMV model checking algorithms.The library consists of several modules. To implement the project you can use only the following modules:

init
glob
fsm, except for method reachable_states
prop
dd 
the helper function spec_to_bdd (model, spec) included in inv_mc.py to convert a property to an equivalent BDD.
You can find more information about the pynusmv library at the websites http://lvl.info.ucl.ac.be/Tools/PyNuSMV and https://pynusmv.readthedocs.io.

Binary files to install pynusmv on recent Python versions are available at https://github.com/davidebreso/pynusmv/releases/latest

---

# Assignment 2 $-$ Verification of reactivity properties
In this assignment you will implement a symbolic algorithm for the verification of a special class of LTL formulas, using BDDs as data structure to represent and manipulate regions. The class of formulas considered by the algorithm is called "reactivity" properties and have the special form

◻◊𝑓→◻◊𝑔

where f and g are Boolean combination of base formulas with no temporal operators. Some examples of reactivity properties for the Railroad Controller are listed below.

If the west train is repeatedly waiting, then it will be repeatedly on the bridge:
◻◊𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑤𝑎𝑖𝑡→◻◊𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑏𝑟𝑖𝑑𝑔𝑒
If the west train is repeatedly waiting then repeatedly either the corresponding signal is green or the east train is on the bridge:
◻◊𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑤𝑎𝑖𝑡→◻◊(𝑠𝑖𝑔𝑛𝑎𝑙𝑤=𝑔𝑟𝑒𝑒𝑛∨𝑡𝑟𝑎𝑖𝑛𝑒.𝑚𝑜𝑑𝑒=𝑏𝑟𝑖𝑑𝑔𝑒)
If the west train is repeatedly waiting with the east train off the bridge, then the west train will be repeatedly on the bridge:
◻◊(¬(𝑡𝑟𝑎𝑖𝑛𝑒.𝑚𝑜𝑑𝑒=𝑏𝑟𝑖𝑑𝑔𝑒)∧𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑤𝑎𝑖𝑡)→◻◊𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑏𝑟𝑖𝑑𝑔𝑒
The following formulas are not reactivity properties, and should be discarded by the algorithm:
◻(𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑤𝑎𝑖𝑡→◊𝑠𝑖𝑔𝑛𝑎𝑙𝑤=𝑔𝑟𝑒𝑒𝑛)
◻◊¬(𝑡𝑟𝑎𝑖𝑛𝑒.𝑚𝑜𝑑𝑒=𝑏𝑟𝑖𝑑𝑔𝑒)→◻◊𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑤𝑎𝑖𝑡→◻◊𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑏𝑟𝑖𝑑𝑔𝑒
◻◊𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑤𝑎𝑖𝑡→◻◊(𝑠𝑖𝑔𝑛𝑎𝑙𝑤=𝑔𝑟𝑒𝑒𝑛∧◯𝑡𝑟𝑎𝑖𝑛𝑤.𝑚𝑜𝑑𝑒=𝑏𝑟𝑖𝑑𝑔𝑒)

The attached react_mc.smv file contains a python script that uses the pynusmv library to verify reactivity properties of SMV programs. The script uses the function parse_react(spec) to check if spec is a reactivity formula, and skips all formulas that are not in the correct form. 

Using the react_mc.smv script as a starting point, (re)implement the function check_react_spec (spec), respecting the following specifications:

the function checks if the reactivity formula spec is satisfied by the loaded SMV model or not, that is, whether all the executions of the model satisfy spec or not.
the return value of check_react_spec (spec) is a tuple where the first element is True and the second element is None if the formula is true. When the formula is not verified, the first element is False and the second element is an execution of the SMV model that violates spec. The function returns None if spec is not a reactivity formula;
the execution is a tuple of alternating states and inputs, starting and ending with a state. States and inputs are represented by dictionaries where keys are state and inputs variable of the loaded SMV model, and values are their value;
the execution is looping: the last state should be somewhere else in the sequence to indicate the starting point of the loop. 

## The pynusmv library
pynusmv is a python wrapper to NuSMV model checking algorithms.The library consists of several modules. To implement the project you can use only the following modules:

init
glob
fsm, except for method reachable_states
prop
dd 
the helper function spec_to_bdd (model, spec) included in react_mc.py to convert a property to an equivalent BDD
the helper function parse_react(spec) that checks if spec is in reactivity form or not. If spec is a reactivity formula
◻◊𝑓→◻◊𝑔
the result is a pair where the first element  is the formula f and the second element is the formula g. If spec is not a reactivity formula, the result is None.
You can find more information about the pynusmv library at the websites http://lvl.info.ucl.ac.be/Tools/PyNuSMV and https://pynusmv.readthedocs.io.

Binary files to install pynusmv on recent Python versions are available at https://github.com/davidebreso/pynusmv/releases/latest


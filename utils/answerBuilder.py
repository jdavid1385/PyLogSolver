# -*- coding: utf-8 -*-
import re
from pyswip import Atom, Variable, Functor
from pyswip import *
from pyswip.easy import _unify, _not, _comma

#VAR = 1      |__ Deprecated: for using with deprecated functions
#BINDING = 2  |

VAR = 0
BINDING = 1

PRED = 0
ARGS = 1

LEFT = 0
RIGHT = 1

functor_name = re.compile('(\w+)\(\d+\)')
args = re.compile(r"(?<=,)\w+(?!\(\d+\))?")

# Walk a Binary Tree
# [L R] ==> R = [L' R'] \/ { L and R of arbitrary complexity ==>  ◻ walks_ArgsTree }
def process_conjunctions(T):

    if isinstance(T, Atom):
        return T.chars
    if isinstance(T, Variable):
        return T.chars
    if isinstance(T, Functor):
        if not (T.name.chars == _comma.name.chars):
            L_name = T.name.chars
            return convert(walk_ArgsTree(T, L_name))
    
    # conjunction case
    raw_L = T.args[LEFT]
    L_name = ''
    try: #   ==> Functor case
        L_name = raw_L.name.chars
    except:# ==> Atom | Variable case
        L_name = raw_L.chars
    finally:
        L = convert(walk_ArgsTree(raw_L, L_name))

    return [L, process_conjunctions(T.args[RIGHT])]

#                  .----------.
#                  |          |
#                  V          |
# raw funct ==>tree-walk() ---°
#                  |
#                  |
# [tuple (funct names, args symbol names) | args symbol names ]
#                  |
#                  | .-------.
#                  | |       |
#                  V V       |
#               convert() ---°
#                  |
#                  |
#                  V
#     {Var_i : f_i(args_i)|atom_bind_i}
#

# A :--/\/\/\--> [B] (colon)    : Per each abstract item in A take corresponding action in [B]
# A  --/\/\/\-->  B (no-colon)  : For every take action B

# At [A][2] we have 2 possible options [2 of many] either:
#   + get the type of the atom and take an action accordingly [cases(Type) :--/\/\/\--> [Action]]
#   + (As only 2 cases) Catch an exception  on the first when procceds and act accordingly

def process_bindings(funct):
    # We know that the functor is the unifier '=' (binding functor)
    unifiers = []
    #[A] {
    for raw_unifier in funct:
        unifier_args = []
        # [1] We know the first argument of unifier is a variable -- Known{(raw_unifier = func[i]) & (raw_unifier[0] is Atom)})
        unifier_args.append(raw_unifier.args[VAR].chars)
        # [2] But we don't know about the second argument (atom?, functor?) --  ¬Known{type(raw_unifier[1])}
        try: # ====> Functor case
            unifier_args.append( raw_unifier.args[BINDING].name.chars)
        except:# ==> Atom | Variable case
            try:
                unifier_args.append( raw_unifier.args[BINDING].chars)
            except:
                unifier_args.append('List')
        finally:
            unifiers.append(unifier_args)

    # [RES] unifiers[i] => [var_name_i , binding_name_i ] }

    # Walk the (possible 0-lenght) tree and unfold the arguments as
    # predicates with arguments (pred(args)) when proceeds
    bindings = []
    for iter_unifier, unifier in enumerate(unifiers):
        bindings.append(tuple([unifier[VAR], convert(walk_ArgsTree(funct[iter_unifier].args[BINDING], unifier[BINDING]))]))

    return dict(bindings)

# [T] {
def walk_ArgsTree(symbol, name):
    if isinstance(symbol, Atom): # [1] Edge case
        return name
    if isinstance(symbol, Variable):
        return name
    else:
        childs=[]
        if (name == 'List'):
            args = symbol
        else:
            args = symbol.args

        for iter_Arg, arg in enumerate(args):
            def get_argName(arg):
                try: # ====> Functor case
                    arg_name = arg.name.chars
                except: # ==> List must be handled in a different way
                    try: # ==> Atom | Variable case
                        arg_name = arg.chars
                    except:
                        if (type(arg) is list):
                            arg_name = 'List'
                return arg_name

            arg_name = get_argName(arg)
            if (arg_name == 'List'):
                childs.append(['List', map(lambda a: walk_ArgsTree(a, get_argName(a)) , arg)])
            else:
                childs.append(walk_ArgsTree(args[iter_Arg], arg_name))

        return [name, childs]

# =================================================================
# [Finally] Convert terms to their final representation recursively
def convert(term):
    if type(term) is str:       # [2] It must coincide with [1]
        return term
    else:
        if (term[PRED] == 'List'):
            # args = [convert(atom) for atom in term[ARGS]]
            # functor = '[' + ','.join(args) + ']' Maybe it is better to return a list instead
            functor = [convert(atom) for atom in term[ARGS]]

        else:
            functor = term[PRED] + '('
            args = []
            for atom in term[ARGS]:
                args.append(convert(atom))
            functor += ','.join(args) + ')'
        return functor
# }


# ========[ The regex-based process bindings (deprecated) ========
#
#         .-----------.     .----------.    .----------.
#         | (dropped) |     |          |    |          |
#         |   start   :---->>          :--->>          |
#         °-----------°     °----------°    °----------°
#              Top
# [Functor(336140,2,O,japanese), Functor(336140,2,X,order(5))]
#    Top                          Top


def process_bindings_deprecated(funct): #The top bindings are processed here
    argset = []
    for term in funct:
        argset.append(args.findall(term.__repr__()))
    # How many variables are bound
    bindings = []
    for iter_Arg, arg in enumerate(argset):
        #arg[0] is the arity
        bindings.append(tuple([arg[VAR], convert(walk_ArgsTree(funct[iter_Arg].args[1], arg[BINDING]))]))

    return dict(bindings)

#   Top pred structure preds
# [TERM, ARGS] ==> ARGS = {[TERM_i, ARGS_i]} | Atom | []}
def walk_ArgsTree_deprecated(symbol, name):
    if isinstance(symbol, Atom):
        return name
    else:
        childs=[]
        argset = args.findall(symbol.__repr__())
        for iter_Arg, arg_Name in enumerate(argset[1:]):
            childs.append(walk_ArgsTree(symbol.args[iter_Arg], arg_Name))
        return [name, childs]



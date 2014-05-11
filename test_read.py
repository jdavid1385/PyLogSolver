from pyswip import *


prolog = Prolog()

prolog.consult('test.pl')

a = prolog.query("test:test_atoms(X)", normalize=False)

print a.next()


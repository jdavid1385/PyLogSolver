from pyswip import *
prolog = Prolog()
prolog.consult("Zebra_and_children.pl")
result_query = prolog.query("owns_Zebra(X,O)", normalize=False)
print result_query.next()



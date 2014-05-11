:- module(ex2, [brother_of/2]).
:- multifile test:sld/2.
brother_of(paul, peter).
brother_of(peter, adrian).
brother_of(X,Y) :- brother_of(X,Z), brother_of(Z,Y).
brother_of(X,Y) :- brother_of(Y,X).

test:sld(brother_of/ex2, [X]^brother_of(X,peter)).

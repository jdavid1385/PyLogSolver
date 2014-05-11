:- module(test, [sld_do/2]).
%:- use_module(ex2).

:- multifile sld/2.
:- dynamic files/1, curr_depth/1, forced/0, node_count/1.


% We can not use read_file_to_terms from the dynamic library since the
% readutil.so file has not been properly compiled and some symbols are
% missing like PL_new_atom.

% :- read_file_to_terms('database.pl', [files(X)],[]), assert(files(X)), use_module(X).
% node_count(0).
% node(N,E,N1) :- write(E), 
%                retract(node_count(C)), N1 is C+1, 
%                assert(node_count(N1)), writeln(N->N1).

% answer(_,_).
% root(_,_).
% stop.

forced.
curr_depth(0).

iter_deep(Mod:Goal, Max_Depth) :-
    repeat,
    retract(curr_depth(N1)), N2 is N1+1, assert(curr_depth(N2)),
    ( N2 < Max_Depth -> sld_res(Mod:Goal, N2); true ).

sld_res(Mod:Goal, Max_Depth) :-
    retractall(forced),
    root(Goal, 0),
    prove(Goal, 0-Max_Depth, Mod:Goal),
    assert(forced),
    fail.

sld_res(_,_) :-
    forced,
    stop.

prove(_,_-0,_,_) :- reinit_node_count, !, fail.

prove(true, N-_, _:Goal) :- !, answer(N,Goal), writeln(Goal).

prove((A,B), N-Depth, Mod:Goal):- !,
    New_Depth is Depth-1,
    resolve(A,C,Mod),
    node(N, A, N1),
    left_conjunct(C,B,E), node(N1,E,N2),
    prove(E, N2-New_Depth, Mod:Goal).

prove(A, N-Depth, Mod:Goal) :-
    Depth>0, New_Depth is Depth-1,
    resolve(A,B,Mod),
    node(N,B,N1),
    prove(B, N1-New_Depth, Mod:Goal).

resolve(A, true, _) :-
    predicate_property(A, built_in), !, call(A).

resolve(A,B,Mod) :- Mod:clause(A,B).

left_conjunct(true, Y, Y).
left_conjunct(X,Y,(X,Y)):-
    X\=true,
    X\=(_,_).
left_conjunct((X,Xs),Y,(X,Z)) :-
    left_conjunct(Xs,Y,Z).

test(X,Y) :- repeat,
             hello(X, Y),
             write('Is is '), write(Y), writeln(' in Prolog'),
             Y == 9,
             writeln('done ... \\_0_/').

%sld1(X) :- sld_res(student_of(X,peter), 5).
%sld2 :- sld_res(brother_of(paul,_), 5).

%solve(ex1)

resetCurrDepth :- retractall(curr_depth(_)), assert(curr_depth(0)).

init_all(Pred) :- resetCurrDepth, setof(Y, X^(files(X), member(Y,X)), H),
                  findall(X, sld(X, _), Pred).

test_atoms(Pred) :-  resetCurrDepth, use_module([ex1,ex2]), findall(X, sld(X, _), Pred).
sld_do(Name/Mod, Max_Depth) :- sld(Name/Mod, Vars^Pred), iter_deep(Mod:Pred, Max_Depth). 
%:- test(sld(X, VarPred)).


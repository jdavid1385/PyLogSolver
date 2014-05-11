:- module(ex1, [student_of/2]).
:- multifile test:sld/2.

student_of(X,T) :- follows(X,C), teaches(T,C).
follows(paul, computer_science).
follows(paul, expert_systems).
follows(maria, ai_techniques).
teaches(adrian, expert_systems).
teaches(peter, ai_techniques).
teaches(peter, computer_science).

% sld(Name_Of_Test, Testing_Predicate)
test:sld(student_of_peter/ex1, [X]^student_of(X,peter)).

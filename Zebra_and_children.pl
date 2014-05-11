%% Childs

did_better(child(peter,X),child(Y,red)).
did_better(child(jack,gold),child(X,green)).

whon(child(X,C1)) :- did_better(child(X,C1),child(Y,C2)),did_better(child(Y,C2),child(Z,C3)),C1\=C2,C1\=C3.

%% Houses, owners and pets.

%% Rules for positioning. 

                                        % Clues. Regarding the position of the houses
%



next(X, Y, first , order(X,Y,_,_,_)).   %   |     The program may get this goals with a choice made for Y or 'first' in the prepositional place on the propagated order;                         % --|

next(X, _, middle, order(_,_,X,_,_)).   %   |---  you must leave it where it was. Not all relations indicate the relative place of its neighbour (left-right), you must

next(X, Y, right, order(X,Y,_,_,_)).
next(X, Y, right, order(_,X,Y,_,_)).
next(X, Y, right, order(_,_,X,Y,_)).
next(X, Y, right, order(_,_,_,X,Y)).

next(X, Y, left, O) :- next(Y, X, right, O).

clue1(O)  :- next(owns_house(man(english,S,D),red,P),_,_,O).
clue2(O)  :- next(owns_house(man(spaniard,S,D),C,dog),_,_,O).
clue3(O)  :- next(owns_house(man(X,S,cofee), green, P),_,_,O).
clue4(O)  :- next(owns_house(man(ukranian,S,tea),C,P),_,_,O).
clue5(O)  :- next(owns_house(man(Y,S2,D2), ivory, P2), owns_house(man(X,S1,D1), green, P1), right, O).
clue6(O)  :- next(owns_house(man(X,tennis,D),C,snails),_,_,O).
clue7(O)  :- next(owns_house(man(X,chess,D),yellow,P),_,_,O).
clue8(O)  :- next(owns_house(man(X,S1,milk),C1,P1),_, middle,O).
clue9(O)  :- next(owns_house(man(norwegian,S1,D1), C1, P1),_, first, O).
clue10(O) :- next(owns_house(man(X,rugby,D1),C1,P1), owns_house(man(Y,S,D2),C2,fox),_,O).
clue11(O) :- next(owns_house(man(X,chess,D1), C1, P1), owns_house(man(Y,S,D2), C2, horse),_,O).
clue12(O) :- next(owns_house(man(X,boleyball,orange_juice),C,P),_,_,O).
clue13(O) :- next(owns_house(man(japanese,go,D),C,P),_,_,O).
clue14(O) :- next(owns_house(man(norwegian,S1,D1), C1, P1), owns_house(man(X,S2,D2), blue, P2),_, O).
clue15(O) :- next(owns_house(man(X,S1,tea),C1,P1), owns_house(man(Y,S2,milo),C2,P2),_,O).

owns_Zebra(X,O) :-  clue9(O), clue8(O), clue12(O), clue14(O), clue15(O), clue5(O), clue1(O), 
                    clue2(O),  clue3(O), clue4(O), clue10(O), clue6(O),clue7(O),
                    clue11(O), clue13(O), next(owns_house(man(X,_,_),_,zebra),_,_,O).


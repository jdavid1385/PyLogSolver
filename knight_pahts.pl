%                                 Knight(Path)
%
%                       [<==|   Nothing to say.   |==>]
%
knight([p(X,Y)]).

knight([ p(X,Y) | [p(X1,Y1)|R] ]) :- 
    ( X<8, Y<8  -> X1 is X+1, Y1 is Y+2, append([p(X1,Y1)],R,P), knight(P)).

knight([ p(X,Y) | [p(X1,Y1)|R] ]) :- 
    ( X<8, Y<8  -> X1 is X+2, Y1 is Y+1, append([p(X1,Y1)],R,P), knight(P)).

knight([ p(X,Y) | [p(X1,Y1)|R] ]) :- 
    ( X>2, X<8, Y>1, Y<8  -> X1 is X-2, Y1 is Y-1, append([p(X1,Y1)],R,P), knight(P)).

knight([ p(X,Y) | [p(X1,Y1)|R] ]) :- 
    ( X>1, X<8, Y>2, Y<8  -> X1 is X-1, Y1 is Y-2, append([p(X1,Y1)],R,P), knight(P)).

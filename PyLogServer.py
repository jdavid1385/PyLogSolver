# -*- coding: utf-8 -*-
import jsonrpcdirect
import cPickle
from pyswip import *
from pyswip.easy import registerForeign, getAtomChars, getTerm
from utils.answerBuilder import process_bindings, process_conjunctions
from multiprocessing import Process, Manager, Queue, Event, active_children

from pyswip.core import *
from ctypes import c_int, c_char_p, pointer
import time
import re

#
#     ________			         _______________
#    |        |  [Spawns]       | 	        	|
#    | Server |VVVVVVVVVVVV--->>| Solver_Handler| 
#    |________|                 |_______________|
#
#

TO_SLD_GEN = 0
TO_SERVER = 1

NodeID = 0
NodeFrom = 0


class Server(jsonrpcdirect.Server):
    def __init__(self, services):
        jsonrpcdirect.Server.__init__(self, jsonrpcdirect.JsonRpc10(), jsonrpcdirect.TransportTcpIp(addr=("127.0.0.1",31415), logfunc=jsonrpcdirect.log_stdout))
        map(self.register_function, services)

class SLD_gen(Process):

    def __init__(self, gLink, contEvent):
        Process.__init__(self)
        self.gLink = gLink
        self.link = Queue()#Link()
        self.contEvent = contEvent

    def run(self):

        resolvant_Handler = Process(target = resolvant_handler, args = (self.link, self.contEvent))
        resolvant_Handler.start()

        # Inilitilization
        t = self.link.get()
        self.gLink.put(t)
        time.sleep(0.05) # Sleep for 0.05 seconds to give chance the server of getting the message
        self.gLink.get() # Finish initialization

        # gLink now is a bidirectional channel
        s = 0
        while s != 9:
            while True:
                s, dest = self.gLink.get()
                if (dest != TO_SLD_GEN):
                    self.gLink.put((s, dest))
                    time.sleep(0.05) # Again give 50 miliseconds to server for getting the message
                else:
                    break

            if type(s) is str:   # Case for the predicate handling
                self.link.put(s)
                time.sleep(0.1)

            print "[SLD_gen] ---[{0}]--> resolvant_handler".format(s)
            t = self.link.get()#1)
            print "[SLD_gen] <--[{0}]--- resolvant_handler".format(t)
            self.gLink.put((t,TO_SERVER))
            time.sleep(0.05) # Sleep for 0.05 seconds to give chance the server of getting the message

        self.resolvant_Handler.terminate()

# ======= [ resolvant handler to be spawned in a separate process ] ===========
def resolvant_handler(link, contEvent):
    prolog = Prolog()
    prolog.consult('test.pl')

    def node(*t):
        global NodeID, NodeFrom
        contEvent.wait()
        contEvent.clear()
        # The only term to process here is the second which holds the current goal
        curr_goal = t[1]
        NodeFrom = t[0]
        NodeID = NodeID+1
        #t[2].value = NodeID
        #PL_unify_integer(t[2], int(NodeID))
        t[2].unify(NodeID)
        if not (t[0] == 0):
            print t[0],'->', t[2].value
        else:
            print t[0],'->', t[2].value

        print "[node]", process_conjunctions(curr_goal)
        link.put([ process_conjunctions(curr_goal), t[0], t[2].value])
        return True

    def root(*t):
        contEvent.wait()
        contEvent.clear()
        curr_goal = t[0] # In this case the goal is the first
        #print t
        print "[root]", process_conjunctions(curr_goal)
        link.put(process_conjunctions(curr_goal))
        return True

    def answer(*t):
        global NodeID

        contEvent.wait()
        contEvent.clear()
        curr_goal = t[1]
        NodeID = NodeID + 1

        print "[answer]", process_conjunctions(curr_goal)
        link.put([process_conjunctions(curr_goal), t[0], NodeID] )
        return True

    def reinit_node_count():
        contEvent.wait()
        contEvent.clear()
        global NodeID
        NodeID = 0
        link.put(404)
        return True

    def test(*t):
        print process_conjunctions(t[0])
        print process_conjunctions(t[1])
        return True

    def stop():
        contEvent.wait()
        contEvent.clear()
        link.put(1)
        return True

    root.arity = 2
    node.arity = 3
    stop.arity = 0
    answer.arity = 2
    reinit_node_count.arity = 0

    map(registerForeign, [root, node, stop, answer, reinit_node_count])

    # readutils for pyswip is not properly compiled PL_new_atom has not been defined.
    # mn /path_to_readutils.so marks symbol PL_new_atom as U.

    with file("database.pl") as db:
        modules = [modulename.group() for modulename in re.finditer("[a-z]+[0-9]+", db.readline())]

        swipl_fid = PL_open_foreign_frame()
        modcall = PL_new_term_ref()

        for mod in modules:
            PL_chars_to_term("use_module({0})".format(mod), modcall)
            PL_call(modcall, None)

        PL_chars_to_term("test:assert(files(" + str(modules)+ "))", modcall)
        PL_call(modcall, None)

        PL_discard_foreign_frame(swipl_fid)

    result_query = prolog.query("test:init_all(Pred)", normalize=False)
    all_test_predicates = result_query.next() # It should not hang here.
    all_preds = process_bindings(all_test_predicates)
    link.put(all_preds)
    time.sleep(0.05)
    del result_query

    while True:
        PredToTest = link.get()
        if PredToTest != 9:
            print '[resolvant_handler] ' + str(PredToTest)
            link.put(0)
            try:
                res = prolog.query(u'sld_do('+ unicode(PredToTest) + u' ,5)', normalize=False)
                # It should hang here.
                res.next()
            except:
                print "Something went wrong.. retry"
        else:
            break

    link.put(1) #OK

def query():
    global result_query
    result_query = prolog.query("father(michael,X), hello(X)")
    return 0

def empezar():
    global allTestPred
    return allTestPred

def query_pred(Name):
    gQueue.put((Name, TO_SLD_GEN))
    time.sleep(0.05)

    while True:
        res, dest = gQueue.get()
        print "[Server] <--[{0}]--- [SLD_gen]".format(res)
        if not (dest == TO_SERVER):
            gQueue.put((res, TO_SLD_GEN))
            time.sleep(0.05)
        else:
            break

    return 0

def continuar():
    #global gQueue
    contEvent.set()
    gQueue.put((0,TO_SLD_GEN))
    time.sleep(0.05)
    res = None
    while True:
        res, dest = gQueue.get()
        print "[Server] <--[{0}]--- [SLD_gen]".format(res)
        if (dest != TO_SERVER):
            gQueue.put((0,TO_SLD_GEN))
            time.sleep(0.05)
        else:
            break
    return res

def finalizar():
    #global gQueue
    gQueue.put((9, TO_SLD_GEN))
    time.sleep(0.05)
    if gQueue.get():
        active_children() #Side effect of joinning

    return 'done'

def return_answer():
    global result_query
    return result_query.next()

def echo(s):
    return s

if __name__ == "__main__":

    global allTestPred
    # ====[ Global communication link ]======
    gQueue = Queue()
    contEvent = Event()

    p = SLD_gen(gQueue, contEvent) #SLD_gen spawns the predicate_handler process
    p.start()


    allTestPred = gQueue.get()
    gQueue.put(1) #OK

    services = [echo, query, return_answer, continuar, empezar, query_pred, finalizar]
    server = Server(services)
    server.serve()

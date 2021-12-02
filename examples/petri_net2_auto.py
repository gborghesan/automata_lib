#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from automata_lib.state import State, Transition, config
from automata_lib.petri_net import PetriNet
from functools import partial

from automata_lib.pnviz import plot_pn

def setupState(name ):
    s = State(
            entry=partial(print,"-- "+ name + " entry"),
            exit=partial(print,"-- "+ name + " exit"),
            doo=partial(print,"-- "+ name + " doo"))
    return s
pn=PetriNet()

pn.states={
        's1':setupState('s1'),
        's2a1':setupState('s2a1'),
        's2a2':setupState('s2a2'),
        's2b1':setupState('s2b1'),
        's2b2':setupState('s2b2'),
        's3':setupState('s3'),
        's4a':setupState('s4a'),
        's4b':setupState('s4b'),
        }
pn.auto_transitions={
        'e_start': Transition('s1',['s2a1','s2b1']),
        'e_a': Transition('s2a1','s2a2'),
        'e_b': Transition('s2b1','s2b2'),
        'e_3': Transition(['s2a2','s2b2'],'s3'),
        'e_stop': Transition('s3',['s4a','s4b']),
        }

pn.init_state={'s1':1}


count =0
def mylog(s):
    global count
    count+=1
    print(str(count) +"\tLOG: " +s )
    
config['log']= mylog
#config['debug']= lambda s: None


functions=[]

import os
functions=pn.step()
for step_count in range (5):
    print("\n-------- step {} -------".format(step_count))
    dot=plot_pn(pn)
    os.system('read -s -n 1 -p "Press any key to continue..."')

    functions+=pn.step()


# this is a Digraph, so you can do all the stuff explained here
# https://graphviz.readthedocs.io/en/stable/api.html#graphviz.Digraph
dot.view()

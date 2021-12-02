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
        's2a':setupState('s2a'),
        's2b':setupState('s2b'),
        's3':setupState('s3'),
        's4':setupState('s4'),
        's5':setupState('s5'),
        }
pn.transitions={
        'e_2': Transition('s1',['s2a','s2b']),
        'e_3': Transition(['s2a','s2b'],'s3'),
        'e_4': Transition(['s2a','s2b'],'s4'),
        'e_5': Transition(['s2a','s2b'],'s5'),
        }

pn.init_state={'s1':2}


count =0
def mylog(s):
    global count
    count+=1
    print(str(count) +"\tLOG: " +s )
    
config['log']= mylog
#config['debug']= lambda s: None


functions=[]
events=["e_2",
        "e_2",
        "e_none",
        "e_3",
        "e_4",
        ]


step_count=0

functions=pn.step()
for event in events:
    print("\n-------- step {} -------".format(step_count));step_count+=1
    pn.queque_event(event)
    functions+=pn.step()

dot=plot_pn(pn)
# this is a Digraph, so you can do all the stuff explained here
# https://graphviz.readthedocs.io/en/stable/api.html#graphviz.Digraph
dot.view()

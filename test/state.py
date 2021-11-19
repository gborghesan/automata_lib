#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from automata_lib.state import State, FSM, Transition
import automata_lib.state
from functools import partial


def print_test(text):
    print(text)
    

s1=State(entry=partial(print_test,text=("ENTRY !")),
   exit=partial(print_test,text=("EXIT !")),
  )

s1.entry()
s1.exit()

s2=State()


fsm=FSM()
subfsm=FSM()
subsubfsm=FSM()
subfsm.states={'first_sub':State(entry=partial(print_test,text=("-- first_sub ENTRY !")),
                      exit=partial(print_test,text=("-- first_sub EXIT !")),
                      doo=partial(print_test,text=("-- first_sub DOO !"))),
               'second_sub':State(entry=partial(print_test,text=("-- second_sub ENTRY !")),
                      exit=partial(print_test,text=("-- second_sub EXIT !")),
                      doo=partial(print_test,text=("-- second_sub DOO !"))),
               'subsub':subsubfsm     
                       }
subfsm.entry=partial(print_test,text=("-- PARTIAL ENTRY !"))
subfsm.exit=partial(print_test,text=("-- PARTIAL EXIT !"))
subfsm.init_state='first_sub'     
subfsm.transitions={
        'e_sub_start': Transition('first_sub','second_sub',lambda:  True),
        'e_sub_stop': Transition('second_sub','first_sub'),  
        'e_subsub': Transition('first_sub','subsub'),  
        }

subsubfsm.states={'first_subsub':State(entry=partial(print_test,text=("-- subsub ENTRY !")),
                      exit=partial(print_test,text=("-- subsub EXIT !")),
                      doo=partial(print_test,text=("-- subsub DOO !"))),
               'second_subsub':State(entry=partial(print_test,text=("-- subsub ENTRY !")),
                      exit=partial(print_test,text=("-- subsub EXIT !")),
                      doo=partial(print_test,text=("-- subsub DOO !"))),
                       }
subsubfsm.entry=partial(print_test,text=("--subsub PARTIAL ENTRY !"))
subsubfsm.exit=partial(print_test,text=("-- subsubPARTIAL EXIT !"))
subsubfsm.init_state='first_subsub'     
subsubfsm.transitions={
        'e_subsub_start': Transition('first_subsub','second_subsub',lambda:  True),
        'e_subsub_stop': Transition('second_subsub','first_subsub'),    
        }
   
fsm.states={
        'first':State(entry=partial(print_test,text=("-- First ENTRY !")),
                      exit=partial(print_test,text=("-- First EXIT !")),
                      doo=partial(print_test,text=("-- First DOO !"))),
        'second':State(entry=partial(print_test,text=("-- Second ENTRY !")),
                      exit=partial(print_test,text=("-- Second EXIT !")),
                      doo=partial(print_test,text=("-- Second DOO !"))),
        'compose':subfsm
        }
fsm.transitions={
        'e_start': Transition('first','second',lambda:  True),
        'e_compose': Transition('second','compose'),
        'e_stop': Transition('compose','first')
        }

fsm.init_state='first'
count =0
def mylog(s):
    global count
    count+=1
    print(str(count) +"\tLOG: " +s )

automata_lib.state.log= mylog

automata_lib.state.automatic_execution= True   

functions=[]
events=["e_start",
        "e_none",
        "e_none",
        "e_compose",
        "e_subsub",
        "e_subsub_start",
        "e_stop",
        "e_start",
        "e_compose",
        ]
functions=fsm.step()
for event in events:
    fsm.queque_event(event)
    functions+=fsm.step()
    

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from automata_lib.state import State, Transition, config
from automata_lib.fsm import FSM
from functools import partial


def print_test(text):
    print(text)


s1=State(entry=partial(print_test,text=("ENTRY !")),
   exit=partial(print_test,text=("EXIT !")),
  )
# note: also `entry=partial(print,"ENTRY !")' works


s1.entry()
s1.exit()

s2=State()


fsm=FSM()
subfsm=FSM()

subfsm.states={'first_sub':State(entry=partial(print_test,text=("-- first_sub ENTRY !")),
                      exit=partial(print_test,text=("-- first_sub EXIT !")),
                      doo=partial(print_test,text=("-- first_sub DOO !"))),
               'second_sub':State(entry=partial(print_test,text=("-- second_sub ENTRY !")),
                      exit=partial(print_test,text=("-- second_sub EXIT !")),
                      doo=partial(print_test,text=("-- second_sub DOO !"))),   
                       }
subfsm.entry=partial(print_test,text=("-- PARTIAL ENTRY !"))
subfsm.exit=partial(print_test,text=("-- PARTIAL EXIT !"))
subfsm.init_state='first_sub'     
subfsm.auto_transitions={
        'e_sub_start_false': Transition('first_sub','second_sub',lambda:  False),
        'e_sub_start_true': Transition('first_sub','second_sub',lambda:  True),
        'e_sub_stop': Transition('second_sub','first_sub'),  
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
        'e_start': Transition('first','compose',lambda:  True),
        'e_compose_out': Transition('compose','second'),
        
        }
fsm.auto_transitions={
        
        'e_reset': Transition('second','first')
        }

fsm.init_state='first'



count =0
def mylog(s):
    global count
    count+=1
    print(str(count) +"\tLOG: " +s )
config['log']= mylog
config['debug']= lambda s: None


functions=[]
events=["e_none",
        "e_none",
        "e_start",
        "e_none",
        "e_none",
        "e_compose_out",
        "e_none",
        "e_none",
        "e_start",
        "e_compose_out",
        "e_none",
        ]
functions=[]
step_count=0
ok,message=fsm.check()

if ok:
    for event in events:
        print("\n-------- step {} -------".format(step_count));step_count+=1
        if event!="e_none":
            fsm.queque_event(event)
        functions+=fsm.step()
    

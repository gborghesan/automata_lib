#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 00:17:53 2021

@author: gborghesan
"""

from automata_lib.fsmviz import plot_fsm
import automata_lib.fsmviz
# table of colors: https://graphviz.org/doc/info/colors.html
automata_lib.fsmviz.active_state_color='greenyellow'

from automata_lib.state import State, FSM, Transition
import automata_lib.state

subsubfsm=FSM(states={'s1':State(),'s2':State()},
        auto_transitions={'e_1_2':Transition('s1','s2')},
         init_state='s1')
subfsm=FSM(states={'s1':State(),'s2':State(),'ssub':subsubfsm},
        transitions={'e_1_2':Transition('s1','s2'),
                          'e_s_1':Transition('ssub','s1')},
         init_state='ssub')

fsm=FSM(states={'s1':State(),'s2':State(), 'sub':subfsm},
        transitions={
                'e_1_2':Transition('s1','s2'),
                'e_2_sub':Transition('s2','sub'),
                '2_e_sub':Transition('sub','s2')},
         init_state='sub')
fsm.step()
  
dot=plot_fsm(fsm)
# this is a Digraph, so you can do all the stuff explained here
# https://graphviz.readthedocs.io/en/stable/api.html#graphviz.Digraph
dot.view()

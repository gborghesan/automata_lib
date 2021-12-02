#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import graphviz


plot_arrow_to_init_in_sub=False

active_substate_color=["gray90","gray85","gray80","gray75",
                       "gray70","gray65","gray60","gray55",
                       "gray50","gray45","gray40","gray35"]
active_state_color='yellow'
default_state_color='white'
default_min_lenght='1'
subgrap_min_lenght='2'
level=0


def plot_place (dot,name,current_state):
    
    if name in current_state.keys():
        name_node=name+'('+str( current_state[name])+')'
    else:
        name_node=name
    prop={'fillcolor':default_state_color,'style':'filled','shape':'circle','fixedsize':'true'}
    dot.node(name,name_node,prop)

def plot_transition (dot,name):
    prop={'fillcolor':default_state_color,'style':'filled','shape':'square','fixedsize':'true'}
    dot.node(name,name,prop)


def plot_pn(pn):
    dot = graphviz.Digraph(comment='Root')
    dot.attr(compound='true')
    dot.attr(nodesep='0.5', ranksep='0.5')
    for state in pn.states:
        plot_place(dot, state,pn.current_state)
    for transition_name, transition in pn.transitions.items():
        plot_transition(dot, transition_name)
        for origin in transition.origins:
            dot.edge(origin,transition_name,'')  
        for dest in transition.destinations:
            dot.edge(transition_name,dest,'')  
    
    return dot


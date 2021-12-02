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
def plot_fsm(fsm):
    
    def _plot_fsm(fsm, dot,name=''):     
        global level
        level+=1
        init_prop={'fillcolor':'black','style':'filled','shape':'circle','fixedsize':'true','width':'0.2'}
        
        dot.node(name+'initial','',init_prop)
        
        lhead=''
        if fsm.states[fsm.init_state].composed==False:
            dest_name_init=name+fsm.init_state
            lhead=''
            minlen=default_min_lenght
        else:
           dest_name_init= name+fsm.init_state+'initial'
           minlen=subgrap_min_lenght
           if plot_arrow_to_init_in_sub==False:
               lhead='cluster_'+name+fsm.init_state
    
        dot.edge(name+'initial',dest_name_init,lhead=lhead,penwidth='2',
                 fillcolor='black',minlen=minlen)
        
        for s in fsm.states:
            prop={'fillcolor':default_state_color,'style':'filled'}
            if s==fsm.current_state:
                prop={'fillcolor':active_state_color,'style':'filled'}
            if fsm.states[s].composed==True:
                with dot.subgraph(name='cluster_'+name+s) as subdot:
                    subdot.attr(label= s)
                    subdot.attr(shape= 'square')
                    if s==fsm.current_state:# sub fsm is active
                         subdot.attr(fillcolor=active_substate_color[level])
                         subdot.attr(style='filled')
                    _plot_fsm(fsm.states[s],subdot,name+s)

            else:
                dot.node(name+s,s,prop)
                
        if fsm.transitions is not None:         
            for t_name in fsm.transitions:
                ltail=''
                lhead=''
                minlen=default_min_lenght
                t=fsm.transitions[t_name]
                if fsm.states[t.origins[0]].composed==False:
                    or_name=name+t.origins[0]
                else:
                   or_name=name+t.origins[0]+'initial'
                   ltail='cluster_'+name+t.origins[0]
                   minlen=subgrap_min_lenght
                if fsm.states[t.destinations[0]].composed==False:
                    des_name=name+t.destinations[0]
                else:
                   des_name= name+t.destinations[0]+'initial'
                   minlen=subgrap_min_lenght
                   if not plot_arrow_to_init_in_sub:
                       lhead='cluster_'+name+t.destinations[0]      
                
                dot.edge(or_name,des_name,t_name,ltail=ltail,lhead=lhead,minlen=minlen)  
            
            
        if fsm.auto_transitions is not None:    
            for t_name in fsm.auto_transitions:
                ltail=''
                lhead=''
                t=fsm.auto_transitions[t_name]
                if fsm.states[t.origins[0]].composed==False:
                    or_name=name+t.origins[0]
                else:
                   or_name=name+t.origins[0]+'initial'
                   ltail='cluster_'+name+t.origins[0]
                if fsm.states[t.destinations[0]].composed==False:
                    des_name=name+t.destinations[0]
                else:
                   des_name= name+t.destinations[0]+'initial'
                   if not plot_arrow_to_init_in_sub:
                       lhead='cluster_'+name+t.destinations[0]                   
                
                dot.edge(or_name,des_name,t_name,ltail=ltail,lhead=lhead,penwidth='2',fillcolor='black')  
        level-=1
    #back to main function
    dot = graphviz.Digraph(comment='Root')
    dot.attr(compound='true')
    dot.attr(nodesep='0.5', ranksep='0.5')
    global level
    level=0
    _plot_fsm(fsm, dot,name='')
    return dot
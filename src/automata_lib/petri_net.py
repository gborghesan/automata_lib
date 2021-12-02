#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
from typing import Callable


from automata_lib.state import AbstractAutomata, call_if_not_None, call_if_not_None_always,config
from copy import deepcopy     

allow_sub_states=False


def _decrease_token(current_state,state_name):
    current_state[state_name]-=1;
    if current_state[state_name]==0: # if it reach zero, i delete from the current state
        del current_state[state_name]
        
def _increase_token(current_state,state_name):
    if state_name in current_state.keys():
        current_state[state_name]+=1;
    else:  
        current_state[state_name]=1;

class PetriNet(AbstractAutomata):
    def __init__(self, 
                 entry: Callable=None,
                 exit: Callable=None,
                 states: dict=None,
                 transitions: dict=None,
                 auto_transitions: list=None,
                 init_state: dict=None): # first difference: we can have one or more token for each place
         super().__init__(entry=entry,exit=exit)
         self.states=states
         self.transitions=transitions
         self.auto_transitions=auto_transitions
         self.init_state=init_state
         
         
         self._event_queque=[]
         self._function_queque=[]
         self.composed=True
    
    def cleanup(self):
        #When we leave a state machine as a state, we need to execute the exit function of the current state machine
        config['debug']('state machine cleanup')
        f_ret=[]
        current_state=self.states[self.current_state]
        if allow_sub_states==True and current_state.composed==True:
            f_ret+=call_if_not_None_always(current_state.cleanup)
        f_ret+=call_if_not_None(current_state.exit)
        config['log']("exiting state: `"+ self.current_state+"'")
        self.current_state=None # current state is a dictionary of state name and number of token in the state
        return f_ret
        
        self.exit()        

    
    def _check_transition(self):
        '''
        Consumes one event from the queque of events; Check the transition (pratically if there are enought tokens from all the origins) 
        return: 
            
           make_transition: - True if we need to make the transition, False otherwise
           event_to_sub_automata- None if no event need to be sent to other levels for check, otherwise the event
            
            Note that if a guard function fails, the event is consumed and it the test is blocked for this step.
        '''
        if len(self._event_queque)==0:
            config['debug']('empty event list')
            return None , None
        event=self._event_queque.pop(0)
        config['debug']('checking event ' +event)
        transition=None
        try:
            transition=self.transitions[event]
        except:
            config['debug']("event `"+ event + "' is not in the transition list")
            return False, event
        # in petri net there are we have to check that for each origin, at least one toke should be present
        # first i make a local deep copy of the current state
        states_working_dic=deepcopy(self.current_state)
        for origin in transition.origins:
            if not(origin in states_working_dic.keys()) or states_working_dic[origin]<0 :
                config['log']("Petrinet expected at least a token in place: `" + origin+"'" )
                return False, event
            
            _decrease_token(states_working_dic,origin)# if it reach zero, I delete from the current state
      
        # if i arrive here it means that I have to transition
                
        config['debug']("PN has sufficients tokens to make the transition" )
        
        if transition.guard is not None:
           config['debug']("checking `"+ event + "' guard function")
           if not transition.guard():
               config['debug']("guard function of `"+ event + "' returned False")
               return None, None
           config['debug']("guard function of `"+ event + "' returned True")
        return True, event
    
    
    def _check_auto_transition(self):
        '''
        Check the auto transition;
        return: 
          make_transition: - True if we need to make the transition, False otherwise
          event_to_sub_automata- None if no event need to be sent to other levels for check, otherwise the event
           
          the main difference from previous functon is that if a guard fails, we should continue making the tests.
        '''
        
        if self.auto_transitions == None:
            return [False,None]
        

        for auto_ev, transition in self.auto_transitions.items():  
            config['debug']("checking  auto transition : `"+auto_ev+"'")         
            states_working_dic=deepcopy(self.current_state)
            for origin in transition.origins:
                interrupt=False
                if not(origin in states_working_dic.keys()) or states_working_dic[origin]<0 :
                    interrupt=True
                    continue
                _decrease_token(states_working_dic,origin)
            
            if interrupt:
                config['debug']("check on tokens for transition {} failed".format(auto_ev))
                continue
            config['debug']("PN has sufficients tokens to make the auto transition" )
            
            
            if transition.guard is not None:
               config['debug']("checking `"+ auto_ev + "' guard function")
               if not transition.guard():
                   config['debug']("guard function of `"+ auto_ev + "' returned False")
                   return None, None
               config['debug']("guard function of `"+ auto_ev + "' returned True")
            return True, auto_ev
        
        return False, None
        
        
    def step(self):
         
        #this is the first transition to the init state
        f_ret=[]
        if self.current_state==None:
            for state_name, init_token in self.init_state.items():
                self.checkStateExists(state_name)
            self.current_state=deepcopy(self.init_state) 
            for current_state_name, n_of_tokens in self.current_state.items():
                current_state=self.states[current_state_name]
                for i in range(n_of_tokens):
                    config['log']("entering initial state: `"+ current_state_name+"'")
                    f_ret+= call_if_not_None(current_state.entry)
                    if allow_sub_states==True and current_state.composed==True:
                        call_if_not_None_always(current_state.init)
                        f_ret=f_ret+ self.states[self.current_state].step()
                    f_ret+=call_if_not_None(current_state.doo)
            return f_ret# will return the init state function
        # end of init
        
        # transitions in normal situations; the below function consumes an event 
        [make_transition, event] = self._check_transition()
        if make_transition:
            # if we get here, there will be the transition we check if the target state exists;
            transition=self.transitions[event]
        
        #heck for auto transitions
        if not make_transition:
            [make_transition, event] = self._check_auto_transition()
            if make_transition:
                transition=self.auto_transitions[event]
        
        if make_transition:
            # if we get here, there will be the transition we check if the target state exists;
            
            for destination in transition.destinations:
                config['debug']("checking transition to: `"+destination+"'")
                self.checkStateExists(destination)
            
            # all the destination exists o can make the transition
            config['debug']("Making transition for event `"+event+"'")
            
            # first do the exit functions
            
            config['debug']("state before update:{}".format(self.current_state))
            for origin in transition.origins:
                old_state=self.states[origin]
                
                if allow_sub_states==True and old_state.composed==True:
                    f_ret+=call_if_not_None_always(old_state.cleanup)

                f_ret+=call_if_not_None(old_state.exit)
                config['log']("exiting state: `"+ origin)
                _decrease_token(self.current_state,origin)
                
            for destination in transition.destinations:
                target_state=self.states[destination]
                config['log']("entering state: `{}'".format(destination))
               
                if allow_sub_states==True and  target_state.composed==True:
                    call_if_not_None_always(target_state.init)
                
                f_ret+=call_if_not_None(target_state.entry)
                _increase_token(self.current_state,destination)
                config['log']("entering state: `"+ destination)
                
            config['debug']("state after update: {}".format(self.current_state))
            
            #else:
            # check if we need to send events to states
            
       
        
        # executing the doo
        if make_transition:
            event=None #if i already had a transition, i do not want any more transitions on substates
        
        for current_st_name, token in self.current_state.items():
            current_st=self.states[current_st_name]
            for i in range(token):
                # TODO here i do not consider the number of tokens for each state, 
                # i  think that it makes sense only if one token is possible for each substat  
                if allow_sub_states==True: 
                    for current_st in self.current_state:
                        if self.states[current_st].composed:
                            if event is not None:
                                self.states[current_st].queque_event(event)
                            f_ret=f_ret+ self.states[current_st].step()
                
                
                f_ret+=call_if_not_None(current_st.doo)
        return f_ret
    
    def checkStateExists(self,state_name):
        if not( state_name in self.states.keys()):
            raise (Exception('state name {} does not exists. possible states are {}'.format(state_name,self.states.keys())))
                
#    def check(self, preamble='root: '):
#        # check the initial state
#        if self.init_state==None:
#            return False, preamble+"No initial state assigned"
#        try:
#            self.checkStateExists(self.init_state)
#        except:
#            return False, preamble+"Initial state does not exists"
#        transitions={}
#        if self.transitions!=None:
#            transitions.update(self.transitions)
#        if self.auto_transitions!=None:
#            transitions.update(self.auto_transitions)
#            
#        for t_name in transitions:
#            t=transitions[t_name]
#            if len(t.origins)!=1:
#                return False, preamble+"transition " + t_name + " must have exactly one origin"
#            if len(t.destinations)!=1:
#                return False, preamble+"transition " + t_name + " must have exactly one destination"
#            try:
#                self.checkStateExists(t.origins[0])
#            except:
#                return False, preamble+" Origin  of transition " + t_name + " does not exists; indicated " + t.origins[0]
#            try:
#                self.checkStateExists(t.destinations[0])
#            except:
#                return False, preamble+" Destination  of transition " + t_name + " does not exists; indicated " + t.destinations[0]
#         
#        for s_name in self.states:
#            s=self.states[s_name]
#            if s.composed:
#                ok, message=s.check(s_name+' :')
#                if not ok:
#                    return False, message
#        return True, ''
        
        
            
                    
                    

                
             
                 
            
             
             
             
         
         
    
         
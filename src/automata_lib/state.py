#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
from typing import Callable
from typing import Union

log_active=True
debug_active=False
automatic_execution=True
def log(s):
    ''' General log functiom it can be overwritten by
    import automata_lib.state
    automata_lib.state.log= lambda s: print("hello " +s)
    
    or for more than one line expression
    import automata_lib.state
    def mylog(s):
        print("LOG: " +s )
    automata_lib.state.log= mylog
    '''
    if log_active:
        print("log: " +s)
    

def debug(s):
    if debug_active:
        print("Debug: "+s)

def call_if_not_None(f):
    global automatic_execution
    if f is not None:
        if automatic_execution:
            f()
        return [f]
    return []
def call_if_not_None_always(f):
    if f is not None:
        return f()
    return []

class AbstractState:
    def __init__(self, 
                 entry: Callable=None, 
                 doo: Callable=None, 
                 exit: Callable=None):
        self.entry = entry
        self.exit = exit
        self.doo = doo   
        # theses are for composed states
        self.composed = False



class State(AbstractState):
    '''This is a basic state. it contains only the entry, doo, and exit function'''
    def __init__(self, 
                 entry: Callable=None, 
                 doo: Callable=None, 
                 exit: Callable=None):
        super().__init__(entry=entry,doo=doo,exit=exit)
        #self.__name = nameof(self)
        pass

class Transition:
    '''This is a transition, it can be from 1 to 1 to Many to Many'''
    def __check_state(self,o_d,o_d_name):
        """Check the if the o_d is a list of State, or State
        Returns the State(s), always in a list.
    
        Keyword arguments:
        o_d -- the Origin or Destination State(s)
        o_d_name -- a string olny used in the assert"""
        o_t=type(o_d).__name__
        
        assert isinstance(o_d, (list,str)), o_d_name +'  must be a string or a list of strings (States Names); it is ' + o_t
        if isinstance(o_d, str):
            return [o_d] 
        if isinstance(o_d, list):
            assert all (isinstance(x,str) for x in o_d), 'all '+ o_d_name +' in the list must be strings (State Names)' 
            return o_d

        
    def __init__(self,
                 origins: Union[str,list], 
                 destinations: Union[str,list],
                 guard: Callable=None):
        
        self.origins=self.__check_state(origins,'Origins')
        self.destinations=self.__check_state(destinations,'Destinations')
        self.guard=guard
        
class AbstractAutomata(AbstractState):
    def __init__(self, 
                 entry: Callable=None, 
                 doo: Callable=None, 
                 exit: Callable=None):
        super().__init__(entry=entry,doo=doo,exit=exit)
        self.entry = entry
        self.exit = exit
        self.doo = doo   
        # theses are for composed states
        self.composed = True
        self.current_state=None
    
    def init(self):   
        #we need to reset the initial state everytime we enter the state machine as a state
        debug('Automata initialization')
        self.current_state=None
        return []
    def cleanup(self):
        return []
    def step(self):
        pass
    def checkStateExists(self,state_name):
        try:
            self.states[state_name]
        except:
            raise (Exception('state name {} does not exists'.format(state_name)))
    def queque_event(self,s):
         self._event_queque.append(s)
        
        
        
        
class FSM(AbstractAutomata):
    def __init__(self, 
                 entry: Callable=None,
                 exit: Callable=None,
                 states: dict=None,
                 transitions: dict=None,
                 auto_transitions: list=None,
                 init_state: str=None):
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
        debug('state machine cleanup')
        f_ret=[]
        current_state=self.states[self.current_state]
        if current_state.composed==True:
            f_ret+=call_if_not_None_always(current_state.cleanup)
        f_ret+=call_if_not_None(current_state.exit)
        log("exiting state: `"+ self.current_state+"'")
        self.current_state=None
        return f_ret
        
        self.exit()        

    
    def _check_transition(self):
        '''
        Consumes one event from the queque of events; Check the transition; 
        return: 
            1 -None if no changes have to be made, otherwise return the name of the new state
            2 - None if no event need to be sent to other levels for check, otherwise the event
            Note that if a guard function fails, the event is consumed and it the test is blocked for this step.
        '''
        if len(self._event_queque)==0:
            debug('empty event list')
            return None , None
        event=self._event_queque.pop(0)
        debug('checking event ' +event)
        transition=None
        try:
            transition=self.transitions[event]
        except:
            debug("event `"+ event + "' is not in the list")
            return None, event
        # there is an event to consume in the queque
        if self.current_state!=transition.origins[0]:
           debug("FSM is in not in correct state; it is in`"+ self.current_state + "', expecting: `"+transition.origins[0]+"'")
           return None, event
        debug("FSM is in the correct state `"+ self.current_state + "'")
        if transition.guard is not None:
           debug("checking `"+ event + "' guard function")
           if not transition.guard():
               debug("guard function of `"+ event + "' returned False")
               return None, None
           debug("guard function of `"+ event + "' returned True")
        return transition.destinations[0], None
    
    
    def _check_auto_transition(self):
        '''
        Check the auto transition;
        return: 
            1 -None if no changes have to be made, otherwise return the name of the new state
            2 - Event that has been used from the auto list
        the main difference from previous functon is that if a guard fails, we should continue making the tests.
        '''
        
        if self.auto_transitions == None:
            return [None,None]
        
        auto_tr=None
        next_state=None
        for auto_ev in self.auto_transitions:  
            debug("checking  auto transition : `"+auto_ev+"'")
            transition=self.auto_transitions[auto_ev]
            
            if self.current_state!=transition.origins[0]:
                continue
            
            debug("Auto transition found from state `"+ self.current_state + "'")
            if transition.guard is not None:
               debug("checking `"+ auto_ev + "' (auto transition) guard function")
               if not transition.guard():
                  debug("guard function of `"+ auto_ev + "' (auto transition) returned False - Will continue  checking other auto transition")
                  continue
               debug("guard function of `"+ auto_ev + "' (auto transition) returned True")
            return transition.destinations[0], auto_ev    
        return [next_state, auto_tr]
        
    def step(self):
         
        #this is the first transition to the init state
        f_ret=[]
        if self.current_state==None:
            self.checkStateExists(self.init_state)
            self.current_state=self.init_state 
            log("entering initial state: `"+ self.current_state+"'")
            current_state=self.states[self.current_state]
            f_ret+= call_if_not_None(current_state.entry)
            if current_state.composed==True:
                call_if_not_None_always(current_state.init)
                f_ret=f_ret+ self.states[self.current_state].step()
            f_ret+=call_if_not_None(current_state.doo)
            return f_ret# will return the init state function
        
        # transitions in normal situations; the below function consumes an event 
        [target_state, event] = self._check_transition()
        
        if target_state is None:
            # if there is not explicit transitions to be done, then we check the auto transitions
            [target_state, auto_event] = self._check_auto_transition()
            
        if target_state is not None:
            # if we get here, there will be the transition
            debug("checking transition to: `"+target_state+"'")
            self.checkStateExists(target_state)
            debug("transition to: `"+target_state+"'")
            
            # calling functions         
            old_state=self.states[self.current_state]
            next_state=self.states[target_state]
            
            if old_state.composed==True:
                f_ret+=call_if_not_None_always(old_state.cleanup)
            f_ret+=call_if_not_None(old_state.exit)
            log("exiting state: `"+ self.current_state+"'")
            log("entering state: `"+ target_state+"'")
            if next_state.composed==True:
                call_if_not_None_always(next_state.init)
            f_ret+=call_if_not_None(next_state.entry)
            
            self.current_state=target_state
        #else:
        # check if we need to send events to states
        if self.states[self.current_state].composed:
            if event is not None:
                self.states[self.current_state].queque_event(event)
            f_ret=f_ret+ self.states[self.current_state].step()
        
        
        f_ret+=call_if_not_None(self.states[self.current_state].doo)
        return f_ret
    
    def check(self, preamble='root: '):
        # check the initial state
        if self.init_state==None:
            return False, preamble+"No initial state assigned"
        try:
            self.checkStateExists(self.init_state)
        except:
            return False, preamble+"Initial state does not exists"
        transitions={}
        if self.transitions!=None:
            transitions.update(self.transitions)
        if self.auto_transitions!=None:
            transitions.update(self.auto_transitions)
            
        for t_name in transitions:
            t=transitions[t_name]
            if len(t.origins)!=1:
                return False, preamble+"transition " + t_name + " must have exactly one origin"
            if len(t.destinations)!=1:
                return False, preamble+"transition " + t_name + " must have exactly one destination"
            try:
                self.checkStateExists(t.origins[0])
            except:
                return False, preamble+" Origin  of transition " + t_name + " does not exists; indicated " + t.origins[0]
            try:
                self.checkStateExists(t.destinations[0])
            except:
                return False, preamble+" Destination  of transition " + t_name + " does not exists; indicated " + t.destinations[0]
         
        for s_name in self.states:
            s=self.states[s_name]
            if s.composed:
                ok, message=s.check(s_name+' :')
                if not ok:
                    return False, message
        return True, ''
        
        
            
                    
                    

                
             
                 
            
             
             
             
         
         
    
         
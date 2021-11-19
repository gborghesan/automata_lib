#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# requires module varname 

#from varname import nameof
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
        f()
        return [f]
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
        def init():
            return []
        def cleanup():
            return []
        def step():
            pass

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
        
        assert isinstance(o_d, (list,str)), o_d_name +'  must be a State or a list of strings (States NAme); it is ' + o_t
        if isinstance(o_d, str):
            return [o_d] 
        if isinstance(o_d, list):
            for x in o_d:
                print(x + type(x))
            assert all (isinstance(x,str) for x in o_d), 'all '+ o_d_name +' in the list must be strings (State Names)' 
            return o_d

        
    def __init__(self,
                 origins: Union[str,list], 
                 destinations: Union[str,list],
                 guard: Callable=None):
        
        self.origins=self.__check_state(origins,'Origins')
        self.destinations=self.__check_state(destinations,'Destinations')
        self.guard=guard
        #self.__name = nameof(self)
        
class FSM(AbstractAutomata):
    def __init__(self, 
                 entry: Callable=None,
                 exit: Callable=None,
                 states: dict=None,
                 transitions: dict=None,
                 init_state: str=None):
         super().__init__(entry=entry,exit=exit)
         self.states=states
         self.transitions=transitions;
         self.init_state=init_state
         
         self.current_state=None
         self._event_queque=[]
         self._function_queque=[]
         self.composed=True
    
    def init(self):   
        #we need to reset the initial state everytime we enter the state machine as a state
        debug('state machine init')
        self.current_state=None
        return []

    def cleanup(self):
        #When we leave a state machine as a state, we need to execute the exit function of the current state machine
        debug('state machine cleanup')
        f_ret=[]
        subfsm=self.states[self.current_state]
        if subfsm.composed==True:
            f_ret+=call_if_not_None_always(subfsm.cleanup)
        f_ret+=call_if_not_None(subfsm.exit)
        log("exiting state: `"+ self.current_state+"'")
        return f_ret
            
        
        self.exit()        
    def checkStateExists(self,state_name):
        try:
            self.states[state_name]
        except:
            raise (Exception('state name {} does not exists'.format(state_name)))
    def queque_event(self,s):
         self._event_queque.append(s)
    
    def __check_transition(self):
        '''
        Consumes one event from the queque
        return: 
            1 -None if no changes have to be made, otherwise return the name of the new state
            2 - None if no event need to be sent to other levels for check, otherwise the event
        '''
        if len(self._event_queque)==0:
            debug('empty list')
            return None , None
        event=self._event_queque.pop(0)
        #event=self._event_queque[0]
        debug('checking event ' +event)
        transition=None
        try:
            transition=self.transitions[event]
        except:
            debug("event `"+ event + "' is not in the list")
            return None, event
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
           
        
    def step(self):
         
        #this is the first transition to the init state
        f_ret=[]
        if self.current_state==None:
            self.checkStateExists(self.init_state)
            self.current_state=self.init_state 
            log("entering initial state: `"+ self.current_state+"'")
            current_state=self.states[self.current_state]
            if current_state.composed==True:
                f_ret+=call_if_not_None_always(current_state.init)
            f_ret+= call_if_not_None(current_state.entry)
            f_ret+=call_if_not_None(current_state.doo)
            return f_ret# will return the init state function
        
        # transitions in normal situations; the below function consumes an event 
        [target_state, event] = self.__check_transition()
        
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
                f_ret+=call_if_not_None_always(next_state.init)
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
            
                    
                    

                
             
                 
            
             
             
             
         
         
    
         
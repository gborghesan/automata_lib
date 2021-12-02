#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
from typing import Callable
from typing import Union

def log_default(s):
    ''' General logging function
    '''
    print("log: " +s)
    

def debug_default(s):
    '''debug function; in normal situatuation should be overwritten
    '''
    print("Debug: "+s)

'''
This sdictionary contains global variables and functions for the whole library.
These can be changed to e.g. change the logging style.
'''
config={
    'automatic_execution' : True,
    'log' : log_default,
    'debug' : debug_default
    }

def call_if_not_None(f):
    global config
    if f is not None:
        if config['automatic_execution']:
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
        config['debug']('Automata initialization')
        self.current_state=None
        return []
    def cleanup(self):
        return []
    def step(self):
        pass

    def queque_event(self,s):
         self._event_queque.append(s)
        
                 

             
                 
            
             
             
             
         
         
    
         
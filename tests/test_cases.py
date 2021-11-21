#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 09:50:45 2021

@author: gborghesan
"""
import unittest
from automata_lib.state import State, FSM, Transition
import automata_lib.state
from functools import partial


def set_to_true(flag,l):
    l[flag]=True
def setupState():
    l={}
    l['f_entry']=False
    l['f_doo']=False
    l['f_exit']=False
    s = State(
            entry=partial(set_to_true,flag='f_entry',l=l),
            exit=partial(set_to_true,flag='f_exit',l=l),
            doo=partial(set_to_true,flag='f_doo',l=l))
    return l,s

class StateConstructor(unittest.TestCase):

    def test_check_functions(self):
        [l,s]=setupState()
        # this will set to true the variables in the list
        s.entry()
        self.assertTrue(l['f_entry'])
        s.doo()
        self.assertTrue(l['f_doo'])
        s.exit()
        self.assertTrue(l['f_exit'])
    
class EventConstructor(unittest.TestCase):
    def test_state_names_single_names(self):
        t1=Transition('s1','s2')
        self.assertEqual(t1.origins,['s1'])
        self.assertEqual(t1.destinations,['s2'])
        t2=Transition(['s1'],['s2'])
        self.assertEqual(t2.origins,['s1'])
        self.assertEqual(t2.destinations,['s2'])
        
    def test_state_names_not_list_or_string(self):     
        with self.assertRaises(AssertionError):
            Transition(1,'s2')
        with self.assertRaises(AssertionError):
            Transition('s1',State())
        
    def test_state_names_multiple_names(self):
        t=Transition(['s1','s2'],['s3','s4'])
        self.assertEqual(t.origins,['s1','s2'])
        self.assertEqual(t.destinations,['s3','s4'])
        t=Transition('s2',['s3','s4'])
        self.assertEqual(t.origins,['s2'])
        self.assertEqual(t.destinations,['s3','s4'])
        t=Transition(['s1','s2'],'s4')
        self.assertEqual(t.origins,['s1','s2'])
        self.assertEqual(t.destinations,['s4'])
        
    def test_event_guard(self):
        t_true=Transition('s1','s2',lambda:  True)
        t_false=Transition('s1','s2',lambda:  False)

        self.assertTrue(t_true.guard())
        self.assertFalse(t_false.guard())        
        
class FSMTests(unittest.TestCase):

    def test_check_functions(self):
        [l,s]=setupState()
        fsm=FSM(states={'s':s},
                init_state='s')
        fsm.step()
        self.assertTrue(l['f_entry'])
        self.assertTrue(l['f_doo'])
        self.assertFalse(l['f_exit'])

    def test_check_transitions(self):
        [l1,s1]=setupState()
        [l2,s2]=setupState()
        fsm=FSM(states={'s1':s1,'s2':s2},
                transitions={'e_1':Transition('s1','s2')},
                init_state='s1')
        self.assertEqual(l1,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        fsm.step()
        self.assertEqual(fsm.current_state,'s1')
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False}) 
        fsm.queque_event('e_1')
        fsm.step()
        self.assertEqual(fsm.current_state,'s2')
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': False}) 
        
    def test_check_transitions_no_auto(self):
        automata_lib.state.automatic_execution= False   
        [l1,s1]=setupState()
        [l2,s2]=setupState()
        fsm=FSM(states={'s1':s1,'s2':s2},
                transitions={'e_1':Transition('s1','s2')},
                init_state='s1')
        f_list=fsm.step()
        self.assertEqual(fsm.current_state,'s1')
        self.assertEqual(l1,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        for f in f_list:
            f()
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False}) 
    
        fsm.queque_event('e_1')
        f_list=fsm.step()
        self.assertEqual(fsm.current_state,'s2')
        
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False}) 
        for f in f_list:
            f()
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': False})
       
        
        automata_lib.state.automatic_execution= True   
    
    def test_check_transitions_subfsm(self):
        [l1,s1]=setupState()
        [l2,s2]=setupState()
        [l3,s3]=setupState()
        lsub={'f_entry':False,'f_exit':False}
        subfsm=FSM(states={'s2':s2,'s3':s3},
                   transitions={'e_2_3':Transition('s2','s3')},
                   entry=partial(set_to_true,flag='f_entry',l=lsub),
                   exit=partial(set_to_true,flag='f_exit',l=lsub),
                   init_state='s2')
        fsm=FSM(states={'s1':s1,'s_sub':subfsm},
                transitions={'e_1_sub':Transition('s1','s_sub'),
                             'e_sub_1':Transition('s_sub','s1')},
                init_state='s1')
        fsm.step()
        self.assertEqual(fsm.current_state,'s1')
        self.assertIsNone(subfsm.current_state)
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(l3,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': False, 'f_exit': False})

        fsm.queque_event('e_1_sub')
        fsm.step() 
        self.assertEqual(fsm.current_state,'s_sub')
        self.assertEqual(subfsm.current_state,'s2')
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l3,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': True, 'f_exit': False})
        
        fsm.queque_event('e_2_3')
        fsm.step()   
        self.assertEqual(fsm.current_state,'s_sub')
        self.assertEqual(subfsm.current_state,'s3')
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l3,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': True, 'f_exit': False})
               
        fsm.queque_event('e_sub_1')
        fsm.step()
        self.assertEqual(fsm.current_state,'s1')
        self.assertIsNone(subfsm.current_state)
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l3,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(lsub,{'f_entry': True, 'f_exit': True})
        
    def test_check_transitions_subfsm_no_auto(self):
        '''
        Automatic call of functions are disabled and done manually
        '''
        automata_lib.state.automatic_execution= False   
        [l1,s1]=setupState()
        [l2,s2]=setupState()
        [l3,s3]=setupState()
        lsub={'f_entry':False,'f_exit':False}
        subfsm=FSM(states={'s2':s2,'s3':s3},
                   transitions={'e_2_3':Transition('s2','s3')},
                   entry=partial(set_to_true,flag='f_entry',l=lsub),
                   exit=partial(set_to_true,flag='f_exit',l=lsub),
                   init_state='s2')
        fsm=FSM(states={'s1':s1,'s_sub':subfsm},
                transitions={'e_1_sub':Transition('s1','s_sub'),
                             'e_sub_1':Transition('s_sub','s1')},
                init_state='s1')
        
        
        f_list=fsm.step()
        self.assertEqual(fsm.current_state,'s1')
        self.assertIsNone(subfsm.current_state)

        self.assertEqual(l1,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(l3,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': False, 'f_exit': False})
        for f in f_list:
            f()   
        self.assertEqual(fsm.current_state,'s1')
        self.assertIsNone(subfsm.current_state)
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(l3,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': False, 'f_exit': False})
#---------
        fsm.queque_event('e_1_sub')
        f_list=fsm.step() 
        self.assertEqual(fsm.current_state,'s_sub')
        self.assertEqual(subfsm.current_state,'s2')
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l2,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(l3,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': False, 'f_exit': False})
        for f in f_list:
            f()   
        self.assertEqual(fsm.current_state,'s_sub')
        self.assertEqual(subfsm.current_state,'s2')
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l3,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': True, 'f_exit': False})
 #---------       
        fsm.queque_event('e_2_3')
        f_list=fsm.step()
        self.assertEqual(fsm.current_state,'s_sub')
        self.assertEqual(subfsm.current_state,'s3')
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(l3,{'f_entry': False, 'f_doo': False, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': True, 'f_exit': False})
        for f in f_list:
            f() 
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l3,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': True, 'f_exit': False})
               
        fsm.queque_event('e_sub_1')
        f_list=fsm.step()
        self.assertEqual(fsm.current_state,'s1')
        self.assertIsNone(subfsm.current_state)
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l3,{'f_entry': True, 'f_doo': True, 'f_exit': False})
        self.assertEqual(lsub,{'f_entry': True, 'f_exit': False})
        for f in f_list:
            f()     
        self.assertEqual(l1,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l2,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(l3,{'f_entry': True, 'f_doo': True, 'f_exit': True})
        self.assertEqual(lsub,{'f_entry': True, 'f_exit': True})
        
        automata_lib.state.automatic_execution= True   
    def test_check_transitions_subfsm_no_function_calls(self):
        '''
        Like test_check_transitions_subfsm_no_auto, but the functions are not called (only transition check)
        '''
        automata_lib.state.automatic_execution= False   
        [l1,s1]=setupState()
        [l2,s2]=setupState()
        [l3,s3]=setupState()
        lsub={'f_entry':False,'f_exit':False}
        subfsm=FSM(states={'s2':s2,'s3':s3},
                   transitions={'e_2_3':Transition('s2','s3')},
                   entry=partial(set_to_true,flag='f_entry',l=lsub),
                   exit=partial(set_to_true,flag='f_exit',l=lsub),
                   init_state='s2')
        fsm=FSM(states={'s1':s1,'s_sub':subfsm},
                transitions={'e_1_sub':Transition('s1','s_sub'),
                             'e_sub_1':Transition('s_sub','s1')},
                init_state='s1')
             
        fsm.step()
        self.assertEqual(fsm.current_state,'s1')
        self.assertIsNone(subfsm.current_state)
        
        fsm.queque_event('e_1_sub')
        fsm.step() 
        self.assertEqual(fsm.current_state,'s_sub')
        self.assertEqual(subfsm.current_state,'s2')
        
        fsm.queque_event('e_2_3')
        fsm.step()
        self.assertEqual(fsm.current_state,'s_sub')
        self.assertEqual(subfsm.current_state,'s3')
               
        fsm.queque_event('e_sub_1')
        fsm.step()
        self.assertEqual(fsm.current_state,'s1')
        self.assertIsNone(subfsm.current_state)
        
        automata_lib.state.automatic_execution= True   
if __name__ == '__main__':
    import rostest
    rostest.rosrun('automata_lib', 'test_StateConstructor', StateConstructor)
    rostest.rosrun('automata_lib', 'test_EventConstructor', EventConstructor)
    rostest.rosrun('automata_lib', 'FSMTests', FSMTests)
   
    #unittest.main()        
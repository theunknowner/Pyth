'''
Created on Aug 4, 2016

@author: jason
'''

class State:
    STATE = ["ENTERED", "INSIDE", "OUTSIDE", "EXITED"]
    ENTERED = STATE.index("ENTERED")
    INSIDE = STATE.index("INSIDE")
    OUTSIDE = STATE.index("OUTSIDE")
    EXITED = STATE.index("EXITED")
    
    state = None
    countStateVec = []
    
    def __init__(self, state=OUTSIDE):
        self.state = state
        self.countStateVec = [0] * len(self.STATE)
        
    def currentState(self):
        return self.state
    
    def setSate(self, state):
        self.state = state
        self.countStateVec[state] += 1
        
    def countStateAction(self, state):
        return self.countStateVec[state]
    
    def reset(self):
        self.state = self.OUTSIDE
        self.countStateVec = [0] * len(self.STATE)
    
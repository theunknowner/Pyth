

class Node:
    currPos = ()
    gVal = 0
    fVal = 0
    
    def __init__(self, pos, g, f):
        self.currPos = pos
        self.gVal = g
        self.fVal = f
        
    def getPos(self):
        return self.currPos

    def getGValue(self):
        return self.gVal

    def getFValue(self):
        return self.fVal

    def calculateFValue(self, dest):
        self.fVal = self.getHValue(dest) + self.gVal

    def updateGValue(self, i):
        #this->gVal += (NDIR == 8 ? (i % 2 == 0 ? 10 : 14) : 10);
        self.gVal+=1

    def getHValue(self, dest):
        dist = abs(self.currPos[1]-dest[1]) + abs(self.currPos[0]-dest[0])
        return dist
    
    # Determine FValue (in the priority queue)
    def __lt__(self, other):
        return self.getFValue() > other.getFValue()
    
if __name__ =="__main__":
    n1 = Node((1,1), 0,0)
    n2 = Node((5,5), 1,1)
    print n2 < n1


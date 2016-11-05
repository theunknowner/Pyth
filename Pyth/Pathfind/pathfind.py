import numpy as np
from Queue import PriorityQueue
import cv2

from node import Node

class Pathfind:
    pointVec = []
    pathFound = False
    
    #//! city-block distance
    def manhattanDist(self, pt1, pt2):
        dist = abs(pt1[0]-pt2[0]) + abs(pt1[1]-pt2[1])
        return dist;
    
    # returns vector of Points
    # in python Points are in tuple form (y,x)
    def getAdjacentPoints(self, src, pt):
        adjacentPoints = []
        top = (pt[0]-1, pt[1])
        right = (pt[0], pt[1]+1)
        down = (pt[0]+1,pt[1])
        left = (pt[0],pt[1]-1)
        if(top[1]>=0 and src[top]>0):
            adjacentPoints.append(top)
        if(right[1]<src.shape[1] and src[right]>0):
            adjacentPoints.append(right)
        if(down[0]<src.shape[0] and src[down]>0):
            adjacentPoints.append(down)
        if(left[1]>=0 and src[left]>0):
            adjacentPoints.push_back(left)
    
        return adjacentPoints
    
    def run(self, src, start, end, NDIR=4, steps=-1):
        """ 
        src = ndarray
        start = point tuple (y,x) 
        end = point tuple (y,x)
        NDIR = 4/8, 8 includes diagonals
        steps = Limit number of steps
        """
        iDir = [0] * NDIR
        jDir = [0] * NDIR
        four = 4
        eight = 8
        if(NDIR == four):
            yDir = [1, 0, -1, 0]
            xDir = [0, 1, 0, -1]
            for i in range(0, NDIR):
                iDir[i] = yDir[i]
                jDir[i] = xDir[i]
    
        if(NDIR == eight):
            yDir = [1, 1, 0, -1, -1, -1, 0, 1]
            xDir = [0, 1, 1, 1, 0, -1, -1, -1]
            for i in range(0, NDIR):
                iDir[i] = yDir[i]
                jDir[i] = xDir[i]
    
        openNodes = np.zeros(src.shape, np.int)
        closeNodes = np.zeros(src.shape, np.int)
        # map of directions (0: Right, 1: Up, 2: Left, 3: Down)
        dirMap = np.zeros(src.shape, np.int)
        
        pq1 = PriorityQueue()
        pq2 = PriorityQueue()
        q = [pq1, pq2]
        qi = 0
        row = col = 0
    
        results = cv2.cvtColor(src,cv2.COLOR_GRAY2BGR)
        results[start] = (0,0,255)
        results[end] = (255,0,0)
        self.pointVec = []
        self.pointVec.append(start)
        self.pathFound = False
    
        # create the start node and push into list of open nodes
        pNode1 = Node(start, 0, 0)
        pNode1.calculateFValue(end)
        q[qi].put(pNode1)
    
        while not q[qi].empty():
            # get the current node w/ the lowest FValue
            # from the list of open nodes
            pNode1 = Node( q[qi].queue[0].getPos(), q[qi].queue[0].getGValue(), q[qi].queue[0].getFValue())
            row = pNode1.getPos()[0]
            col = pNode1.getPos()[1]
            #print "{}) {},{} - {},{} - {}, {}".format(i,col,row,jNext,iNext,pNode1.getGValue(),pNode1.getFValue())
            
            if(pNode1.getGValue()==steps):
                return results
    
            # mark the node on the open list
            q[qi].get()
            openNodes[row][col] = 0
    
            # mark it on the closed nodes list
            closeNodes[row][col] = 1
    
            # stop searching when the goal state is reached
            if(row == end[0] and col == end[1]):
                # generate the path from finish to start from dirMap
                while( not (row == start[0] and col == start[1]) ):
                    j = dirMap[row][col]
                    row += iDir[j]
                    col += jDir[j]
    
                    if(row!=start[0] and col!=start[1]):
                        results[row,col] = (0,255,0)
                        self.pointVec.append((row,col))
                self.pointVec.append(end)
    
                # empty the leftover nodes
                while not q[qi].empty():
                    q[qi].get()
    
                self.pathFound = True
                return results
    
            # generate moves in all possible directions
            for i in range(0, NDIR):
                iNext = row + iDir[i]
                jNext = col + jDir[i]
    
                # if not wall (obstacle) nor in the closed list
                if( not (iNext<0 or iNext>src.shape[0]-1 or jNext<0 or jNext>src.shape[1]-1 or
                        src[iNext,jNext]==0 or closeNodes[iNext][jNext] == 1) ):
                    
                    # generate a child node
                    pNode2 = Node( (iNext, jNext), pNode1.getGValue(), pNode1.getFValue())
                    pNode2.updateGValue(i)
                    pNode2.calculateFValue(end)
    
                    # if it is not in the open list then add into that
                    if(openNodes[iNext][jNext] == 0):
                        openNodes[iNext][jNext] = pNode2.getFValue()
                        q[qi].put(pNode2)
                        # mark its parent node direction
                        dirMap[iNext][jNext] = (i + NDIR/2) % NDIR
    
                    # already in the open list
                    elif(openNodes[iNext][jNext] > pNode2.getFValue()):
                        # update the FValue info
                        openNodes[iNext][jNext] = pNode2.getFValue()
    
                        # update the parent direction info,  mark its parent node direction
                        dirMap[iNext][jNext] = (i + NDIR/2) % NDIR
    
                        # replace the node by emptying one q to the other one
                        # except the node to be replaced will be ignored
                        # and the new node will be pushed in instead
                        while( not (q[qi].queue[0].getPos()[0] == iNext and q[qi].queue[0].getPos()[1] == jNext)):
                            q[1-qi].put(q[qi].queue[0])
                            q[qi].get()
    
                        # remove the wanted node
                        q[qi].get()
    
                        # empty the larger size q to the smaller one
                        if(len(q[qi].queue) > len(q[1 - qi].queue)):
                            qi = 1 - qi
                        while not q[qi].empty():
                            q[1 - qi].put(q[qi].queue[0])
                            q[qi].get()
                        qi = 1 - qi
    
                        # add the better node instead
                        q[qi].put(pNode2)
                        
                # end if not obstacle or closed list
            # end for i < NDIR
        # end while not empty
        return results
    
    def getPathPoints(self):
        return self.pointVec
    
    def isPathFound(self):
        return self.pathFound;

if __name__ == "__main__":
    import functions as fn
    pf = Pathfind()
    src = cv2.imread("/home/jason/Desktop/workspace/pic1.png",0)
    results = pf.run(src, (40,39), (66,51), 8)
    pathPoints = pf.getPathPoints()
    print pathPoints
    print pf.isPathFound()
    fn.imgshow(results)
    #dirMap = np.zeros((140,140), np.uint8)
    #for i in range(0, len(pathPoints)):
    #    dirMap[pathPoints[i]] = 255
        
    #fn.imgshow(dirMap)
        

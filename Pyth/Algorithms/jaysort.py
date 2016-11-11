import numpy as np

#//! flag=0: ascending, flag=1: descending
def jaysort(vec, flag=0):
    origPos = []
    vec2d = []
    for i in range(len(vec)):
        tempVec = []
        val = vec[i][0] if(type(vec)==np.ndarray) else vec[i]
        tempVec.append(val)
        tempVec.append(i)
        vec2d.append(tempVec)
    
    vec2d.sort()
    if(flag==1):
        vec2d.reverse()
    sortedVec = []
    for i in range(len(vec2d)):
        sortedVec.append(vec2d[i][0])
        origPos.append(vec2d[i][1])
    
    return sortedVec, origPos

if __name__ == "__main__":
    vec = [[9,4],[2,1],[3,8]]
    sortedVec, origPos = jaysort(vec)
    print sortedVec
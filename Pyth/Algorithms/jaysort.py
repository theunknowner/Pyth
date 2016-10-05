import numpy as np

def jaysort(vec):
    origPos = []
    vec2d = []
    for i in range(len(vec)):
        tempVec = []
        val = vec[i][0] if(type(vec)==np.ndarray) else vec[i]
        tempVec.append(val)
        tempVec.append(i)
        vec2d.append(tempVec)
    
    vec2d.sort()
    sortedVec = []
    for i in range(len(vec2d)):
        sortedVec.append(vec2d[i][0])
        origPos.append(vec2d[i][1])
    
    return sortedVec, origPos

if __name__ == "__main__":
    vec = [[9,4],[2,1],[3,8]]
    sortedVec, origPos = jaysort(vec)
    print sortedVec
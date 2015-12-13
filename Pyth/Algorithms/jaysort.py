
origPos = []

def jaysort(vec):
    vec2d = []
    for i in range(len(vec)):
        tempVec = []
        tempVec.append(vec[i])
        tempVec.append(i)
        vec2d.append(tempVec)
        
    vec2d.sort()
    
    sortedVec = []
    for i in range(len(vec2d)):
        sortedVec.append(vec2d[i][0])
        origPos.append(vec2d[i][1])
    
    return sortedVec
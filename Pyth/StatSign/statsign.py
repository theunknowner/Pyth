import numpy as np
import math

def create(img, relArea):
    statSignVec = np.zeros(1,81)
    statSignVec2 = np.zeros(1,17)
    for y in range(img.shape[0]):
        countConsecWhite = 0
        countConsecBlack = 0
        entered=0
        for x in range(img.shape[1]):
            if(img[y,x]>0 and entered==-1):
                entered = 1
                countConsecWhite += 1
                statSignVec[countConsecBlack+40] += 1
                countConsecBlack=0
            elif(img[y,x]>0):
                entered = 1
                countConsecWhite+=1
            elif(img[y,x]==0 and entered==1):
                entered = -1
                countConsecBlack += 1
                statSignVec[countConsecWhite]+=1
                countConsecWhite=0
            elif(img[y,x]==0 and entered!=0):
                entered=-1
                countConsecBlack+=1
            
        
    
    for i in range(1,len(statSignVec)):
        mul = i
        if(i>40): mul = i-40 
        mul = math.ceil(mul/5.0);
        statSignVec[i] *= math.pow(4.5,mul) * relArea;
        urnNum = math.ceil(i/5.0);
        statSignVec2[urnNum] += statSignVec[i];
    
    statSignVec[0] = np.sum(statSignVec)
    statSignVec2[0] = np.sum(statSignVec2)
    return statSignVec2;

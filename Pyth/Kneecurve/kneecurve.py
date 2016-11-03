import numpy as np
import math


#//! finds the knee of the curve
#//! pass by reference so the original gets sorted
def kneeCurvePoint(vec):
    vec = np.sort(vec)

    vecFromFirst = np.zeros((len(vec),2))
    firstPt = [0.0,0.0]
    lastPt = [0.0,0.0]
    firstPt[0] = 0.0
    firstPt[1] = vec[0]
    lastPt[0] = (len(vec)-1) - firstPt[0]
    lastPt[1] = vec[len(vec)-1] - firstPt[1]
    
    lastPtPow = [0.0,0.0]
    lastPtPow[0] = math.pow(lastPt[0],2.0)
    lastPtPow[1] = math.pow(lastPt[1],2.0)
    
    sqrtSum = math.sqrt(np.sum(lastPtPow))
    lastPtNorm = np.divide(lastPt,sqrtSum)
    
    lastPtNormRep = []
    
    while(len(lastPtNormRep)!=len(vec)):
        lastPtNormRep.append(lastPtNorm)
        
    for i in range(len(vec)):
        vecFromFirst[i][0] = i - firstPt[0]
        vecFromFirst[i][1] = vec[i] - firstPt[1]
        
    scalarProduct = np.zeros((len(vec),1))
                             
    for i in range(len(vecFromFirst)):
        val = np.dot(vecFromFirst[i],lastPtNormRep[i])
        scalarProduct[i] = val
    
    vecFromFirstParallel = np.multiply(scalarProduct,lastPtNorm)
    vecToLine = np.subtract(vecFromFirst,vecFromFirstParallel)
    
    vecToLinePow = vecToLine
    for i in range(len(vecToLine)):
        vecToLinePow[i][0] = math.pow(vecToLine[i][0], 2.0)
        vecToLinePow[i][1] = math.pow(vecToLine[i][1], 2.0)
        
    sumMat = np.zeros((len(vecToLine),1))
    for i in range(len(vecToLinePow)):
        for j in range(len(vecToLinePow[i])):
            sumMat[i] += vecToLinePow[i][j]
            
    distMat = np.sqrt(sumMat)
    
    maxDist = 0.0
    bestIdx = 0
    for i in range(len(distMat)):
        dist = distMat[i]
        if(dist>maxDist):
            maxDist = dist;
            bestIdx = i;
    return bestIdx

def removeOutliers(vec, percent):
    new_vec = np.sort(vec)
    amt = round(len(new_vec) * percent)
    for i in range(0, amt):
        del new_vec[-1]
        del new_vec[0]
    return new_vec
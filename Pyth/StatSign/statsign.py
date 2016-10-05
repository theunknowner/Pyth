import numpy as np
import math
import traceback

urnSize1 = 81
urnSize2 = 17
urnSize = None

def create(img, relArea):
    statSignVec = np.zeros(1,urnSize1)
    statSignVec2 = np.zeros(1,urnSize2)
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
                entered = -1
                countConsecBlack+=1
            
    for i in range(1,len(statSignVec)):
        mul = i
        if(i>40): mul = i-40 
        #mul = math.ceil(mul/5.0);
        #statSignVec[i] *= math.pow(4.5,mul) * relArea;
        #urnNum = math.ceil(i/5.0);
        #statSignVec2[urnNum] += statSignVec[i];
        statSignVec[i] *= math.pow(mul,2);
    
    statSignVec[0] = np.sum(statSignVec)
    statSignVec2[0] = np.sum(statSignVec2)
    urnSize = len(statSignVec)
    return statSignVec;

def dotProduct(statSignVec1, statSignVec2):
    '''
    Scheme 1 for comparing statistical signature
    '''
    
    assert(len(statSignVec1)>0), "statSignVec1 size < 0"
    assert(len(statSignVec2)>0), "statSignVec2 size < 0"
    assert(len(statSignVec1)==len(statSignVec2)), "statSignVec1 size != statSignVec2 size"
    
    if(statSignVec1[0]==0 or statSignVec2[0]==0):
        return 0.0

    statSignVecF1 = np.zeros(1,len(statSignVec1))
    statSignVecF2 = np.zeros(1,len(statSignVec2))
    statSignVecF11 = np.zeros(1,len(statSignVec1))
    statSignVecF22 = np.zeros(1,len(statSignVec2))
    
    sumOfMaxes = 0.0
    ## sum of the max of the urns
    for i in range(1,len(statSignVec1)):
        sumOfMaxes += max(statSignVec1[i], statSignVec2[i])
        
    ## relative proportions of the balls
    for i in range(1,len(statSignVec1)):
        statSignVecF1[i] = statSignVec1[i] / statSignVec1[0]
        statSignVecF2[i] = statSignVec2[i] / statSignVec2[0]
        statSignVecF11[i] = statSignVec1[i] / sumOfMaxes
        statSignVecF22[i] = statSignVec2[i] / sumOfMaxes
    
    numerSum = 0.0
    denomSumUP = 0.0
    denomSumDB = 0.0
    for i in range(1,len(statSignVecF1)):
        numerSum += (statSignVecF11[i] * statSignVecF22[i])
        denomSumUP += math.pow(statSignVecF1[i],2)
        denomSumDB += math.pow(statSignVecF2[i],2)
    
    denomSum = math.sqrt(denomSumUP) * math.sqrt(denomSumDB)
    results = numerSum / denomSum
    return results
    
def proportion(statSignVec1, statSignVec2):
    '''
    Scheme 2 for comparing statistical signature
    '''   
    assert(len(statSignVec1)>0), "statSignVec1 size <= 0"
    assert(len(statSignVec2)>0), "statSignVec2 size <= 0"
    assert(len(statSignVec1)==len(statSignVec2)), "statSignVec1 size != statSignVec2 size"
    totalWhite1 = totalWhite2 = totalBlack1 = totalBlack2 = 0.0
    for i in range(1,len(statSignVec1)):
        if(i > 40):
            totalBlack1 += statSignVec1[i]
            totalBlack2 += statSignVec2[i]
        else:
            totalWhite1 += statSignVec1[i]
            totalWhite2 += statSignVec2[i]
    
    minWhite = min(totalWhite1,totalWhite2)
    maxWhite = max(totalWhite1,totalWhite2)
    minBlack = min(totalBlack1,totalBlack2)
    maxBlack = max(totalBlack1,totalBlack2)
    propWhite = (minWhite / maxWhite) if(maxWhite>0) else 1.0 
    propBlack = (minBlack / maxBlack) if(maxBlack>0) else 1.0
    
    result = propWhite * propBlack
    return result

def adjustValue(value):
    '''
    Adjust the score using inverse tan-hyperbolic function
    '''
    pMark = 0.65; # percentage mark where values gets pushed up or down
    result = value + (1.5*math.atanh(value - pMark)) * value
    upperLimit = 0.9
    lowerLimit = 0.0
    result = min(result,upperLimit)
    result = max(result,lowerLimit)
    return result

def getUrnSize():
    return urnSize

def printStatSignVec(statSignVec):
    assert(len(statSignVec) > 0),"statSignVec size <=0 "
    for i in range(1,len(statSignVec)):
        prop = statSignVec[i] / statSignVec[0]
        try:
            print "L{}: {}({})".format(i,statSignVec[i],prop)
        except Exception as e:
            print "Exception:", e
            print "statSignVec.size: {}".format(len(statSignVec))
            print "i: {}".format(i)
            print traceback.print_exc()
    print "Total: {}".format(statSignVec[0])
    
def printCompare(statSignVec1, statSignVec2):
    assert(len(statSignVec1)>0), "statSignVec1 size <= 0"
    assert(len(statSignVec2)>0), "statSignVec2 size <= 0"
    assert(len(statSignVec1)==len(statSignVec2)), "statSignVec1 size != statSignVec2 size"
    ## sum of the max of the urns
    sumOfMaxes = 0.0
    for i in range(1,len(statSignVec1)):
        sumOfMaxes += max(statSignVec1[i],statSignVec2[i])
        
    for i in range(1,len(statSignVec1)):
        prop1 = statSignVec1[i] / statSignVec1[0]
        prop2 = statSignVec2[i] / statSignVec2[0]
        prop11 = statSignVec1[i] / sumOfMaxes
        prop22 = statSignVec2[i] / sumOfMaxes
        try:
            urn = i-40 if(i>40) else i
            print "L{}: {}({})({}) | L{}: {}({})({})".format(urn,statSignVec1[i],prop1,prop11,urn,statSignVec2[i],prop2,prop22)
        except Exception as e:
            print "Exception:",e
            print "statSignVec1.size: {}".format(len(statSignVec1))
            print "statSignVec2.size: {}".format(len(statSignVec2))
            print "i: {}".format(i)
            print traceback.print_exc()
    
    print "Total: {} | Total: {}".format(statSignVec1[0],statSignVec2[0])
    print "SumOfMaxes: {}".format(sumOfMaxes)
    
def writeCompare(filename, statSignVec1, statSignVec2):
    assert(len(statSignVec1)>0), "statSignVec1 size <= 0"
    assert(len(statSignVec2)>0), "statSignVec2 size <= 0"
    assert(len(statSignVec1)==len(statSignVec2)), "statSignVec1 size != statSignVec2 size"
    ## sum of the max of the urns
    sumOfMaxes = 0.0
    for i in range(1,len(statSignVec1)):
        sumOfMaxes += max(statSignVec1[i],statSignVec2[i])
        
    with open(filename, "w") as f:
        for i in range(1,len(statSignVec1)):
            prop1 = statSignVec1[i] / statSignVec1[0]
            prop2 = statSignVec2[i] / statSignVec2[0]
            prop11 = statSignVec1[i] / sumOfMaxes
            prop22 = statSignVec2[i] / sumOfMaxes
            urn = i-40 if(i>40) else i
            f.write("L{}: {}({})({}) | L{}: {}({})({})\n".format(urn,statSignVec1[i],prop1,prop11,urn,statSignVec2[i],prop2,prop22))
            
        f.write("Total: {} | Total: {}\n".format(statSignVec1[0],statSignVec2[0]))
        f.write("SumOfMaxes: {}\n".format(sumOfMaxes))
    

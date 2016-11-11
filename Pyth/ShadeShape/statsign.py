import math
import traceback

URN_SIZE1 = 81
URN_SIZE2 = 17

#//! creates a statistical signature of a NN3 40x40 image
#//! vector size is 81
#//! pos[0] = total
#//! pos[1] -> pos[40] = White
#//! pos[41] -> pos[80] = Black
def create(img, relArea=1.0):
    statSignVec = [0] * URN_SIZE1
    statSignVec2 = [0] * URN_SIZE2 #> 80/5 = 16
    for y in range(0, img.shape[0]):
        countConsecWhite = 0
        countConsecBlack = 0
        entered = 0
        for x in range(0, img.shape[1]):
            if(img[y,x]>0 and entered==-1):
                entered=1
                countConsecWhite+=1
                statSignVec[countConsecBlack+40]+=1
                countConsecBlack=0
            elif(img[y,x]>0):
                entered=1
                countConsecWhite+=1
            elif(img[y,x]==0 and entered==1):
                entered=-1
                countConsecBlack+=1
                try:
                    statSignVec[countConsecWhite]+=1
                except Exception:
                    print countConsecWhite
                    exit(1)
                countConsecWhite=0
            elif(img[y,x]==0 and entered!=0):
                entered=-1
                countConsecBlack+=1
    for i in range(1, len(statSignVec)):
        mul = i-40 if i>40 else i
#       mul = ceil(mul/5.0);
#       statSignVec.at(i) *= pow(2.5,mul) * relArea;
#       int urnNum = ceil(i/5.0);
#       statSignVec2.at(urnNum) += statSignVec.at(i);
        statSignVec[i] *= pow(mul,2)
    statSignVec[0] = sum(statSignVec)
    statSignVec2[0] = sum(statSignVec2)
    return statSignVec

#//! scheme 1 for comparing statistical signature
def dotProduct(statSignVec1, statSignVec2):
    assert(len(statSignVec1)>0)
    assert(len(statSignVec2)>0)
    assert(len(statSignVec1)==len(statSignVec2))
    if(statSignVec1[0]==0 or statSignVec2[0]==0):
        return 0.0
    
    statSignVecF1 = [0] * len(statSignVec1)
    statSignVecF2 = [0] * len(statSignVec2)
    statSignVecF11 = [0] * len(statSignVec1)
    statSignVecF22 = [0] * len(statSignVec2)
    sumOfMaxes = 0.0
    #> sum of the max of the urns
    for i in range(1, len(statSignVec1)):
        sumOfMaxes += max(statSignVec1[i],statSignVec2[i])
    #> relative proportions of the balls
    for i in range(1, len(statSignVec1)):
        statSignVecF1[i] = float(statSignVec1[i]) / statSignVec1[0]
        statSignVecF2[i] = float(statSignVec2[i]) / statSignVec2[0]
        statSignVecF11[i] = float(statSignVec1[i]) / sumOfMaxes
        statSignVecF22[i] = float(statSignVec2[i]) / sumOfMaxes
    numerSum = 0.0
    denomSumUP = 0.0
    denomSumDB = 0.0
    for i in range(1, len(statSignVecF1)):
        numerSum += (statSignVecF11[i] * statSignVecF22[i])
        denomSumUP += pow(statSignVecF1[i],2)
        denomSumDB += pow(statSignVecF2[i],2)
        
    denomSum = math.sqrt(denomSumUP) * math.sqrt(denomSumDB)
    results = numerSum / denomSum
    return results

#//! scheme 2 for comparing statistical signature
def proportion(statSignVec1, statSignVec2):
    assert(len(statSignVec1)>0 and len(statSignVec2)>0)
    assert(len(statSignVec1)==len(statSignVec2))
    totalWhite1 = totalWhite2 = totalBlack1 = totalBlack2= 0.0
    for i in range(1, len(statSignVec1)):
        if(i>40):
            totalBlack1 += statSignVec1[i]
            totalBlack2 += statSignVec2[i]
        else:
            totalWhite1 += statSignVec1[i]
            totalWhite2 += statSignVec2[i]
    propWhite = min(totalWhite1,totalWhite2) / max(totalWhite1,totalWhite2)
    propBlack = min(totalBlack1,totalBlack2) / max(totalBlack1,totalBlack2)
    if(math.isnan(propWhite)):
        propWhite = 1.0
    if(math.isnan(propBlack)):
        propBlack = 1.0
    if(math.isinf(propWhite)):
        propWhite = 1.0
    if(math.isinf(propBlack)):
        propBlack = 1.0
    result = propWhite * propBlack
    return result

#//! adjust the score using inverse tan-hyperbolic function
def adjustValue(value):
    pMark = 0.65 #> percentage mark where values gets pushed up or down
    result = value + (1.5*math.atanh(value - pMark)) * value
    upperLimit = 0.9
    lowerLimit = 0.0
    result = min(result,upperLimit)
    result = max(result,lowerLimit)
    return result

def printStatSign(statSignVec):
    assert(len(statSignVec)>0)
    for i in range(1, len(statSignVec)):
        prop = statSignVec[i] / statSignVec[0]
        try:
            print("L{}: {}({:.6f})".format(i,statSignVec[i],prop))
        except Exception:
            traceback.print_exc()
            print("statSignVec.size(): {}".format(len(statSignVec)))
            print("i: {}",i)
            exit(1)
    print("Total: {}".format(statSignVec[0]))

def printCompare(statSignVec1, statSignVec2):
    assert(len(statSignVec1)>0 and len(statSignVec2)>0)
    assert(len(statSignVec1)==len(statSignVec2))
    #> sum of the max of the urns
    sumOfMaxes = 0.0
    for i in range(1, len(statSignVec1)):
        sumOfMaxes += max(statSignVec1[i],statSignVec2[i])
    for i in range(1, len(statSignVec1)):
        prop1 = float(statSignVec1[i]) / statSignVec1[0]
        prop2 = float(statSignVec2[i]) / statSignVec2[0]
        prop11 = float(statSignVec1[i]) / sumOfMaxes
        prop22 = float(statSignVec2[i]) / sumOfMaxes
        try:
            urn = i-40 if i>40 else i
            print("L{}: {}({:.6f})({:.6f}) | L{}: {}({:.6f})({:.6f})".format(urn,statSignVec1[i],prop1,prop11,urn,statSignVec2[i],prop2,prop22))
        except Exception:
            traceback.print_exc()
            print("statSignVec1.size(): {}".format(len(statSignVec1)))
            print("statSignVec2.size(): {}".format(len(statSignVec2)))
            print("i: {}".format(i))
            exit(1)
    print("Total: {} | Total: {}".format(statSignVec1[0], statSignVec2[0]))
    print("SumOfMaxes: {}".format(sumOfMaxes))

def writeCompare(name, statSignVec1, statSignVec2):
    assert(len(statSignVec1)>0 and len(statSignVec2)>0)
    assert(len(statSignVec1)==len(statSignVec2))
    #> sum of the max of the urns
    sumOfMaxes = 0.0
    for i in range(1, len(statSignVec1)):
        sumOfMaxes += max(statSignVec1[i],statSignVec2[i])
        
    with open(name,"w") as f:
        for i in range(1, len(statSignVec1)):
            prop1 = statSignVec1[i] / statSignVec1[0]
            prop2 = statSignVec2[i] / statSignVec2[0]
            prop11 = statSignVec1[i] / sumOfMaxes
            prop22 = statSignVec2[i] / sumOfMaxes
            urn = i-40 if i>40 else i
            f.write("L{}: {}({:.6f})({:.6f}) | L{}: {}({:.6f})({:.6f})".format(urn,statSignVec1[i],prop1,prop11,urn,statSignVec2[i],prop2,prop22))
        f.write("Total: {} | Total: {}".format(statSignVec1[0], statSignVec2[0]))
        f.write("SumOfMaxes: {}".format(sumOfMaxes))
        

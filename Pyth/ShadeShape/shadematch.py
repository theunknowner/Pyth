import math
import numpy as np
import traceback
import cv2

from Algorithms.jaysort import jaysort

maxNumOfShades = 0
shadeVec = []
_SHIFT = ["SHIFT_NONE","SHIFT_LEFT","SHIFT_RIGHT"]
SHIFT_NONE=0
SHIFT_LEFT=1
SHIFT_RIGHT=2

featIslIdxStoreVec = []
featIslStored = False

__shadeWeightsVec__ = []

def setMaxShades(shadeVec1, shadeVec2):
    maxNumOfShades = max(len(shadeVec1), len(shadeVec2))

    __shadeWeightsVec__[:] = []
    __shadeWeightsVec__ = [0.0] * maxNumOfShades
    initWeight = 5.0
    weight = initWeight
    shades = int(math.ceil(maxNumOfShades/2.0))
    j = maxNumOfShades-1
    totalWeight = 0.0
    for i in range(0, shades):
        if(i>0):
            weight = initWeight / (i*initWeight)
        __shadeWeightsVec__[i] = weight
        __shadeWeightsVec__[j] = weight
        if(i!=j):
            totalWeight += __shadeWeightsVec__[i] + __shadeWeightsVec__[j]
        else:
            totalWeight += __shadeWeightsVec__[i]
        j-=1
    for i in range(0, len(__shadeWeightsVec__)):
        __shadeWeightsVec__[i] = 1.0 #> set weights to 1 for now

#//! continuous shade_translation1 of islands until shiftType changes
#//! starting with the largest island
def shade_translation1(ss, shiftType, shiftAmt=1):
    if not hasattr(shade_translation1, "prevShiftType"):
        shade_translation1.prevShiftType = 0
    if(_SHIFT[shiftType]=="SHIFT_NONE"):
        shade_translation1.prevShiftType = shiftType
        return True

    if not hasattr(shade_translation1,"areaVec"):
        shade_translation1.areaVec = []
    if not hasattr(shade_translation1,"origPos"):
        shade_translation1.origPos = []
    if not hasattr(shade_translation1,"indexVec"):
        shade_translation1.indexVec = []
    if not hasattr(shade_translation1,"indexVec2d"):
        shade_translation1.indexVec2d = []
        
    if(shade_translation1.prevShiftType != shiftType):
        shade_translation1.areaVec[:] = []
        shade_translation1.origPos[:] = []
        shade_translation1.indexVec[:] = []
        shade_translation1.indexVec2d[:] = []
        
    if(shade_translation1.prevShiftType!=shiftType):
        featIslIdxStoreVec[:] = []
        for i in range(0, ss.numOfFeatures()):
            for j in range(0, ss.feature(i).numOfIslands()):
                area = ss.feature(i).island(j).area()
                shade_translation1.areaVec.append(area)
                shade_translation1.indexVec.append(i)
                shade_translation1.indexVec.append(j)
                shade_translation1.indexVec2d.append(shade_translation1.indexVec)
                shade_translation1.indexVec[:] = []
        shade_translation1.areaVec, shade_translation1.origPos = jaysort(shade_translation1.areaVec)
        
    newShadeIdx = 0
    if not hasattr(shade_translation1, "index"):
        shade_translation1.index = 1
    if(shade_translation1.prevShiftType != shiftType):
        shade_translation1.index = 1
    shade_translation1.prevShiftType = shiftType
    n =  len(shade_translation1.areaVec) - shade_translation1.index
    shade_translation1.index+=1
    if(n>=0):
        pos = featNum = islNum = shade = shadeIdx=0
        newShade=0
        try:
            pos = shade_translation1.origPos[n]
            featNum = shade_translation1.indexVec2d[pos][0]
            islNum = shade_translation1.indexVec2d[pos][1]
            shade = ss.feature(featNum).island(islNum).shade()
            shadeIdx = ss.getIndexOfShade(shade)
            if(_SHIFT[shiftType] == "SHIFT_LEFT"):
                newShadeIdx = max(shadeIdx-shiftAmt,0)
            if(_SHIFT[shiftType] == "SHIFT_RIGHT"):
                newShadeIdx = min(shadeIdx+shiftAmt,maxNumOfShades-1)

            if(newShadeIdx!=shadeIdx):
                newShade = ss.shade(newShadeIdx)
                ss.set_island_shade(featNum,islNum,newShade)
                ss.getImageData().setImage(ss.image())
                featIslIdxStoreVec.append(shade_translation1.indexVec2d[pos])
                featIslStored = True
                return True
            featIslStored = False
            return True
        except Exception:
            traceback.print_exc()
            print("{}".format(_SHIFT[shiftType]))
            print("origPos.size(): {}".format(len(shade_translation1.origPos)))
            print("indexVec2d.size(): {}".format(len(shade_translation1.indexVec2d)))
            print("n: {}".format(n))
            print("pos: {}".format(pos))
            print("shade: {}".format(shade))
            print("shadeInd: {}".format(shadeIdx))
            print("newShadeInd: {}".format(newShadeIdx))
            print("newShade: {}".format(newShade))
            print("maxNumOfShades: {}".format(maxNumOfShades))
            exit(1)
    return True

def getStoredFeatIslIdx():
    return featIslIdxStoreVec

def isFeatIslStored():
    return featIslStored

def SHIFT():
    return _SHIFT

def applyShiftPenalty(ss, score, shiftAmt=1):
    totalRelArea = 0.0
    for i in range(0, len(featIslIdxStoreVec)):
        featNum = featIslIdxStoreVec[i][0]
        islNum = featIslIdxStoreVec[i][1]
        area = ss.feature(featNum).island(islNum).area()
        relArea = float(area) / ss.area()
        totalRelArea += relArea
    penalty = pow(2.0,(-2.0*totalRelArea))
    return score * penalty

#//! shifts all the shades to either left(darker)  or right(lighter)
def shiftShades(islandVec, shiftType):
    if(shiftType==SHIFT_NONE):
        return islandVec
    
    newIslandVec = [[[]] * maxNumOfShades] * len(islandVec)

    for shape in range(0, len(islandVec)):
        for shade in range(0, len(islandVec[shape])):
            #> if SHIFT_LEFT get max, if SHIFT_RIGHT get min
            new_shade = max(int(shade-1),0) if shiftType==SHIFT_LEFT else min(int(shade+1),maxNumOfShades-1)
            try:
                for isl in range(0, len(islandVec[shape][shade])):
                    newIslandVec[shape][new_shade].append(islandVec[shape][shade][isl])
            except Exception:
                traceback.print_exc()
                print("shift_type: {}".format(shiftType))
                print("shade: {}".format(shade))
                print("new_shade: {}".format(new_shade))
                print("newIslVec Size: {}".format(len(newIslandVec)))
                print("newIslVec Size2: {}".format(len(newIslandVec[shape])))
                exit(1)
    return newIslandVec

def applyShadeWeights(shadeLevel):
    return __shadeWeightsVec__[shadeLevel]

#//! shifts the lightest shades darker by one shade
#//! or shifts the darkest shades lighter by one shade
def shade_translation2(ss, shiftType, shiftAmt=1):
    if(shiftType==SHIFT_NONE):
        return False

    featIslIdxStoreVec[:] = []
    indexVec = []
    for i in range(0, ss.numOfFeatures()):
        isShifted = False
        for j in range(0, ss.feature(i).numOfIslands()):
            shade = ss.feature(i).island(j).shade()
            shadeLevel = ss.getIndexOfShade(shade)
            if(shiftType==SHIFT_LEFT and shadeLevel==maxNumOfShades-1):
                new_shade = ss.shade(shadeLevel-shiftAmt)
                ss.set_island_shade(i,j,new_shade)
                isShifted = True
            if(shiftType==SHIFT_RIGHT and shadeLevel==0):
                new_shade = ss.shade(shadeLevel+shiftAmt)
                ss.set_island_shade(i,j,new_shade)
                isShifted = True
            if(isShifted):
                indexVec.append(i)
                indexVec.append(j)
                featIslIdxStoreVec.append(indexVec)
                indexVec[:] = []
            isShifted = False
    ss.getImageData().setImage(ss.image())

    return True

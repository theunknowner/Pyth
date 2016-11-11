import csv
import pkg_resources
import traceback

from Shapes.shapes import Shapes
from Algorithms.jaysort import jaysort

class ShapeMatch():

    __shiftingRules__ = []
    __shiftingPenalties__ = []
    __THRESH_IMPORTED__ = False
    
    __shapeWeightsVec__ = []
    __shapeWeightsVec2__ = []
    
    SHIFT_NONE=0
    SHIFT_LEFT=1
    SHIFT_RIGHT=2
    _SHIFT = ["SHIFT_NONE","SHIFT_START"]

    #/******************* PUBLIC FUNCTIONS ******************/
    
    def __init__(self):
        if not ShapeMatch.__THRESH_IMPORTED__:
            ShapeMatch.__THRESH_IMPORTED__ = self.importThresholds()
    
    def importThresholds(self):
        if not ShapeMatch.__THRESH_IMPORTED__:
            res_mgr = pkg_resources.ResourceManager()
            folderName = "Thresholds"
            file1_read = open(res_mgr.resource_filename(folderName, "shape_shifting_rules.csv"), "r")
            csv_file1 = csv.reader(file1_read)
            file2_read = open(res_mgr.resource_filename(folderName, "shape_penalties.csv"),"r")
            csv_file2 = csv.reader(file2_read)
            file3_read = open(res_mgr.resource_filename(folderName, "shape_weights.csv"),"r")
            csv_file3 = csv.reader(file3_read)
            for row in csv_file1:
                ShapeMatch.__shiftingRules__.append(row[1:])
            file1_read.close()
            next(csv_file2)
            for row in csv_file2:
                ShapeMatch.__shiftingPenalties__.append(row[1:])
            file2_read.close()
            next(csv_file3)
            for row in csv_file3:
                ShapeMatch.__shapeWeightsVec__.append(row[1])
                ShapeMatch.__shapeWeightsVec2__.append(row[2])
            file3_read.close()
            assert(len(Shapes.__shapeNames__)==len(ShapeMatch.__shiftingPenalties__))
            assert(len(Shapes.__shapeNames__)==len(ShapeMatch.__shiftingRules__))
            assert(len(Shapes.__shapeNames__)==len(ShapeMatch.__shapeWeightsVec__))
            assert(len(Shapes.__shapeNames__)==len(ShapeMatch.__shapeWeightsVec2__))
            return True
        return False
    
    def getIslandVecIdxByArea(self, islandVec):
        islandVecIdx = []
        areaVec = []
        for i in range(0, len(islandVec)):
            for j in range(0, len(islandVec[i])):
                idxVec = []
                for k in range(0, len(islandVec[i][j])):
                    area = islandVec[i][j][k].area()
                    areaVec.push_back(area)
                    idxVec.append(i)
                    idxVec.append(j)
                    idxVec.append(k)
                    islandVecIdx.append(idxVec)
        assert(len(areaVec)>0)
        areaVec, origPos = jaysort(areaVec,1)
        islandVecIdxSorted = []
        for i in range(0, len(areaVec)):
            islandVecIdxSorted.append(islandVecIdx[origPos[i]])
        return islandVecIdxSorted
    
    
    #//! shifts island specified by rank, 0=default=largest
    def shape_translation(self, islandVec, shapeNum, newShape, rank=0):
        newIslandVec = islandVec[:]
        islandVecIdxSorted = self.getIslandVecIdxByArea(islandVec)
        shape = islandVecIdxSorted[rank][0]
        shade = islandVecIdxSorted[rank][1]
        isl = islandVecIdxSorted[rank][2]
        assert(shape==shapeNum)
    
        new_shape = newShape
        islandVec[shapeNum][shade][isl].isShapeShifted(True)
        newIslandVec[new_shape][shade].append(islandVec[shapeNum][shade][isl])
        newIslandVec[new_shape][shade][-1].prevShape(shapeNum)
        newIslandVec[new_shape][shade][-1].shape(new_shape)
        del newIslandVec[shapeNum][shade][isl]
        islandVec = newIslandVec
        return True
    
    #//! shifts specified shape to the left
    #//! only shifts the largest shape no matter what shade
    def shape_translation2(self, islandVec, shapeNum, newShape, shiftAmt=1):
        newIslandVec = islandVec[:]
        areaVec = []
        empty = True
        for j in range(0, len(islandVec[shapeNum])):
            if(len(islandVec[shapeNum][j])>0):
                area = islandVec[shapeNum][j][0].area()
                areaVec.append(area)
                empty = False
            else:
                areaVec.append(0)
        if not empty:
            for i in range(0, shiftAmt):
                max_shade_pos = areaVec.index(max(areaVec))
                new_shape = newShape
                if(areaVec[max_shade_pos]>0):
                    islandVec[shapeNum][max_shade_pos][0].isShapeShifted(True)
                    newIslandVec[new_shape][max_shade_pos].append(islandVec[shapeNum][max_shade_pos][0])
                    newIslandVec[new_shape][max_shade_pos][-1].prevShape(shapeNum)
                    newIslandVec[new_shape][max_shade_pos][-1].shape(new_shape)
                    del newIslandVec[shapeNum][max_shade_pos][0]
                    areaVec[max_shade_pos] = 0
            islandVec = newIslandVec
            return True
        return False
    
    def numOfShapes(self):
        return len(Shapes.__shapeNames__)
    
    #//! assigns an island a new shape
    #//! does not re-sort by area
    def moveShape(self, islandVec, shapeNum, shadeNum, islNum, newShape):
        islandVec[newShape][shadeNum].append(islandVec[shapeNum][shadeNum][islNum])
        del islandVec[shapeNum][shadeNum][islNum]
    
    def SHIFT(self):
        return self._SHIFT
    
    def applyShiftPenalty(self, score, shapeNum, shapeNum2):
        penalty = ShapeMatch.__shiftingPenalties__[shapeNum][shapeNum2]
        newScore = score * pow(2.0,penalty)
        return newScore
    
    def getShiftPenalty(self, shapeNum, shapeNum2):
        try:
            weight = ShapeMatch.__shiftingPenalties__[shapeNum][shapeNum2]
            penalty = pow(2.0,weight)
            return penalty
        except Exception:
            traceback.print_exc()
            print("ShapeNum: {}".format(shapeNum))
            print("ShapeNum2: {}".format(shapeNum2))
            print("ShiftPenalty[{}].size(): {}".format(shapeNum,len(ShapeMatch.__shiftingPenalties__[shapeNum])))
            exit(1)
    
    def applyShapeWeight(self, shapeNum):
        try:
            return ShapeMatch.__shapeWeightsVec__[shapeNum]
        except Exception:
            traceback.print_exc()
            print("ShapeNum: {}".format(shapeNum))
            print("ShapeWeightVec.size(): {}".format(len(ShapeMatch.__shapeWeightsVec__)))
            exit(1)

import copy
import traceback

import functions as fn

class Srm:
    relOpLevelSize = 4
    rel_op = ["NULL","INDIR","DIR","SURR_BY_INV","SURR_BY"]
    NONE        = 0
    INDIR       = 1
    DIR         = 2
    SURR_BY_INV = 3
    SURR_BY     = 4

    #/******************** PRIVATE FUNCTIONS **********************/
    def setup_relationMatrix(self, labels):
        assert(len(labels)>0)
        self.relationOpMatrix = fn.createVectorList((labels.size(),labels.size()), 0)
        self.relationCountMatrix = fn.createVectorList((labels.size(),labels.size()), 0)
        self.neighborLevelMatrix = fn.createVectorList((labels.size(),labels.size()), 0)
        self.relationAreaMatrix = fn.createVectorList((labels.size(),labels.size()), 0)
        self.relationTouchCountMatrix = fn.createVectorList((labels.size(),labels.size()), 0)
        self.relationDistanceMatrix = fn.createVectorList((labels.size(),labels.size()), {})
        self.relationCountPercentMatrix = fn.createVectorList((labels.size(),labels.size()), 0.0)

    def mergeLabels(self):
        newLabels = copy.copy(self.labels)
        labelMap = newLabels.getMap()
        merged_labels = {}
        shadeLevelMap = {}
        shapeNumMap = {}
        for key,value in labelMap.items():
            merged_key = key[0:len(key)-4]
            if not merged_labels.has_key(merged_key):
                merged_labels[merged_key] = value
                shadeLevelMap[merged_key] = self.labels.getShadeLevel(key)
                shapeNumMap[merged_key] = self.labels.getShapeNum(key)
            else:
                merged_labels[merged_key][0] += value[0]
                merged_labels[merged_key][1] += value[1]
        newLabels.setLabels(merged_labels)
        newLabels.getShadeLevelMap(shadeLevelMap)
        newLabels.getShapeMap(shapeNumMap)
    
        return newLabels
    
    #/********************* PUBLIC FUNCTIONS ***********************/
    def __init__(self, ss, labels):
        self.max_neighbor_level = 0
        self.labels = labels
        self.setup_relationMatrix(labels)
        self.max_neighbor_level=0
    
    def relation(self, index1, index2, value=None):
        if value!=None:
            self.relationOpMatrix[index1][index2] = value
        return self.relationOpMatrix[index1][index2]
    
    #//! return reference to SRM relalationship count between label1 & label2;
    def relationCount(self, index1, index2, value=None):
        if value!=None:
            self.relationCountMatrix[index1][index2] = value
        return self.relationCountMatrix[index1][index2]
    
    #//! return reference to SRM neighbor level between label1 & label2
    def neighborLevel(self, index1, index2, value=None):
        if value!=None:
            self.neighborLevelMatrix[index1][index2] = value
        return self.neighborLevelMatrix[index1][index2]
    
    #//! return reference to SRM DN touch count between label1 & label2
    def relationTouchCount(self, index1, index2, value=None):
        if value!=None:
            self.relationTouchCountMatrix[index1][index2] = value
        return self.relationTouchCountMatrix[index1][index2]
    
    def relationCountPercent(self, index1, index2, value=None):
        if value!=None:
            self.relationCountPercentMatrix[index1][index2] = value
        return self.relationCountPercentMatrix[index1][index2]
    
    #//! return reference to SRM area between label1 & label2
    def relationArea(self, index1, index2, value=None):
        if value!=None:
            self.relationAreaMatrix[index1][index2] = value
        return self.relationAreaMatrix[index1][index2]
    
    #//! return SRM distance between label1 & label2
    #//! if (degree = -1) function returns sum of the distances
    #//! if (degree = -2) function returns avg of the distances
    def getRelationDistance(self, index1, index2, degree):
        distMap = self.relationDistanceMatrix[index1][index2]
    
        #//> if (degree = -1) return sum
        if(degree==-1.0 or degree==-2.0):
            sum=0.0
            for key, value in distMap.items():
                sum += value
            if(degree==-2.0):
                return sum/len(distMap)
            return sum
    
        #//> return distance at (degree) if found
        if(distMap.has_key(degree)):
            return distMap[degree]
        return 0.0
    
    def setRelationDistance(self, index1, index2, degree, val):
        distMap = self.relationDistanceMatrix[index1][index2]
        distMap[degree] = val
    
    def size(self):
        return len(self.relationOpMatrix)
    
    #//! return max neighbor level
    def maxNeighborLevel(self):
        return self.max_neighbor_level
    
    def writeRelationMatrix(self, labels, name):
        name += "_srm.csv"
        with open(name,"w") as f:
            labelMap = labels.getMap()
            f.write(",")
            for key in labelMap:
                f.write("{},".format(key))
            f.write("\n")
            for i in range(0, len(self.relationOpMatrix)):
                f.write("{},".format(labelMap.keys()[i]))
                for j in range(0, len(self.relationOpMatrix[i])):
                    rel_op_idx = self.relationOpMatrix[i][j]
                    relOp = self.rel_op[rel_op_idx]
                    f.write("{},".format(relOp))
                f.write("\n")
    
    def writeNeighborLevelMatrix(self, labels, name):
        name += "_los.csv"
        with open(name,"w") as f:
            labelMap = labels.getMap()
            f.write(",")
            for key in labelMap:
                f.write("{},".format(key))
            f.write("\n")
            for i in range(0, len(self.relationOpMatrix)):
                f.write("{},".format(labelMap.keys()[i]))
                for j in range(0, len(self.relationOpMatrix[i])):
                    level = self.neighborLevelMatrix[i][j]
                    f.write("{},".format(level))
                f.write("\n")
    
    def writeRelationCountMatrix(self, labels, name):
        name += "_count.csv"
        with open(name, "w") as f:
            labelMap = labels.getMap()
            f.write(",")
            for key in labelMap:
                f.write("{},".format(key))
            f.write("\n")
            for i in range(0, len(self.relationCountMatrix)):
                f.write("{},".format(labelMap.keys()[i]))
                for j in range(0, len(self.relationCountMatrix[i])):
                    count = self.relationCountMatrix[i][j]
                    f.write("{},".format(count))
                f.write("\n")
    
    def downScaleSrm(self):
        labelMap = self.labels.getMap()
        self.mergedLabels = self.mergeLabels()
        merged_labels = self.mergedLabels.getMap()
        
        srmMarkMap = fn.createVectorList((len(merged_labels),len(merged_labels),len(self.rel_op),self.relOpLevelSize), {})
        self.dsSrmCount = fn.createVectorList((len(merged_labels),len(merged_labels),len(self.rel_op),self.relOpLevelSize), 0)
        self.dsSrmArea = fn.createVectorList((len(merged_labels),len(merged_labels),len(self.rel_op),self.relOpLevelSize), (0,0))
        self.mergedLabelContainer = fn.createVectorList((len(merged_labels),len(merged_labels),len(self.rel_op),self.relOpLevelSize), ([],[]))
        self.mergedRelationDistance = fn.createVectorList((len(merged_labels),len(merged_labels),len(self.rel_op),self.relOpLevelSize), [])
        
        for y,(keyY,valueY) in enumerate(labelMap.items()):
            newLabelY = keyY[0:len(keyY)-4]
            y2 = merged_labels.keys().index(newLabelY)
            areaY = valueY[0]
            for x in range(y2,len(merged_labels.keys())):
                keyX = merged_labels.keys()[x]
                valueX = merged_labels[keyX]
                newLabelX = keyX[0:len(keyX)-4]
                x2 = merged_labels.keys().index(newLabelX)
                rel_op_idx = self.relationOpMatrix[y][x]
                neighborNum = self.neighborLevelMatrix[y][x]
                if(rel_op_idx>0): #ignores "NULL" relations
                    try:
                        areaX = valueX[0]
                        self.dsSrmCount[y2][x2][rel_op_idx][neighborNum]+=1
                        equationKey = keyY + "<" + self.rel_op[rel_op_idx] + ">" + keyX
                        if(self.equationMap.has_key(equationKey)==False):
                            self.equationMap[equationKey] = (valueY[0],valueX[0])
                        # for the x label
                        if(srmMarkMap[y2][x2][rel_op_idx][neighborNum].has_key(keyX)==False):
                            self.dsSrmArea[y2][x2][rel_op_idx][neighborNum][1] += areaX
                            srmMarkMap[y2][x2][rel_op_idx][neighborNum][keyX] = 1
                            self.mergedLabelContainer[y2][x2][rel_op_idx][neighborNum][1].append(keyX)
    
                        # for the y label
                        if(srmMarkMap[y2][x2][rel_op_idx][neighborNum].has_key(keyY)==False):
                            self.dsSrmArea[y2][x2][rel_op_idx][neighborNum][0] += areaY
                            srmMarkMap[y2][x2][rel_op_idx][neighborNum][keyY] = 1
                            self.mergedLabelContainer[y2][x2][rel_op_idx][neighborNum][1].append(keyY)
                            
                        distMap = self.relationDistanceMatrix[y][x]
                        for key,value in distMap.items():
                            dist = value
                            self.mergedRelationDistance[y2][x2][rel_op_idx].append(dist)
                    except Exception:
                        traceback.print_exc()
                        exit(1)
    
    def getLabels(self):
        return self.labels
    
    def getMergedLabels(self):
        return self.mergedLabels
    
    def downscaleSrmCount(self):
        return self.dsSrmCount
    
    def downscaleSrmArea(self):
        return self.dsSrmArea
    
    def getIndex(self, label):
        return self.labels.getIndex(label)
    
    def area(self, label):
        return self.labels.area(label)
    

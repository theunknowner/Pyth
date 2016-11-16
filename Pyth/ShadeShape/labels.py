import traceback
import copy

import statsign
import functions as fn
from Shapes.shapes import Shapes

class Labels:
    #/************************* PRIVATE FUNCTIONS ****************************/
    def calcTotalArea(self):
        self.labelTotalArea = 0
        for value in self.labelMap.values():
            self.labelTotalArea += value[0]
    
    #/************************* PUBLIC FUNCTIONS *****************************/
    def __init__(self, islandVec, totalArea, name=""):
        self.labelMap = {} # dict of tuples
        self.labelShapeShiftMap = {}
        self.labelShapeNumMap = {}
        self.labelPrevShapeNumMap = {}
        self.labelShadeLevelMap = {}
        self.labelStatSignMap = {}
        self.labelIslandMap = {}
        self.labelShadeLumMap = {}
        self.labelName = ""
        self.labelTotalArea = 0
        
        self.create(islandVec,totalArea,name)
        self.calcTotalArea()
    
    def create(self, islandVec, totalArea, name=""):
        self.labelName= name
        for i in range(0, len(islandVec)):
            for j in range(0, len(islandVec[i])):
                for k in range(0, len(islandVec[i][j])):
                    isl = islandVec[i][j][k]
                    shape = self.getShapeName(i)
                    label = str(i)+"_"+shape+"_s"+ str(j)+"_"
                    label += fn.addDigitsForLabel(k,"0",3)
                    isl.labelName(label)
    
                    if not self.labelMap.has_key(label):
                        area = islandVec[i][j][k].area()
                        relArea = float(area) / totalArea
                        self.labelMap[label] = (area,relArea)
                        self.labelShapeShiftMap[label] = islandVec[i][j][k].isShapeShifted()
                        self.labelShapeNumMap[label] = islandVec[i][j][k].shape();
                        self.labelPrevShapeNumMap[label] = islandVec[i][j][k].prevShape()
                        self.labelShadeLevelMap[label] = j
                        self.labelIslandMap[label] = islandVec[i][j][k]
                        self.labelShadeLumMap[label] = isl.shade()
    
                        #> to calculate the statistical signature of each label
                        if(label.find("Excavated")>=0 or label.find("Default")>=0):
                            statSignVec = statsign.create(isl.nn_image(),relArea)
                            self.labelStatSignMap[label] = statSignVec
    
                    else:
                        traceback.print_exc()
                        print("Label: {}".format(label))
                        exit(1)
    
    def getMap(self):
        return self.labelMap
    
    def getShadeLevelMap(self, shadeLevelMap=None):
        if shadeLevelMap!=None:
            self.labelShadeLevelMap = shadeLevelMap
        return self.labelShadeLevelMap
    
    def getShapeMap(self, shapeMap=None):
        if shapeMap!=None:
            self.labelShapeNumMap = shapeMap
        return self.labelShapeNumMap
    
    def setLabels(self, labels):
        self.labelMap = labels
        self.calcTotalArea()
    
    def area(self, label=None, num=None):
        assert(label!=None or num!=None)
        if label!=None and self.labelMap.has_key(label):
            return self.labelMap[label][0]
        if(num!=None):
            for i,key in enumerate(self.labelMap):
                if(i==num):
                    return self.labelMap[key][0]
        return 0
    
    def totalArea(self):
        return self.labelTotalArea
    
    def relativeArea(self, label=None, num=None):
        assert(label!=None or num!=None)
        if label!=None and self.labelMap.has_key(label):
            return self.labelMap[label][1]
        if(num!=None):
            for i,key in enumerate(self.labelMap):
                if(i==num):
                    return self.labelMap[key][1]
        return 0.0
    
    def size(self):
        return len(self.labelMap)
    
    def at(self, num):
        """
        Returns the key of the label map given the index
        """
        for i,key in enumerate(self.labelMap):
            if(i==num):
                return key
        return ""
    
    def copy(self):
        return copy.copy(self)
    
    def name(self):
        return self.labelName
    
    #//! prints the labels and their areas;
    def printLabels(self):
        for i,key in enumerate(self.labelMap):
            print("{}) {}: {}({:0.6f})".format(i, key, self.labelMap[key][0], self.labelMap[key][1]))
    
    def getIndex(self, label):
        if self.labelMap.has_key(label):
            return self.labelMap.keys().index(label)
        return -1
    
    def getShape(self, label):
        for i in range(0, len(Shapes.__shapeNames__)):
            if(label.find(self.getShapeName(i))>=0):
                return self.getShapeName(i)
        return ""
    
    def getShade(self, label):
        if(self.labelShadeLumMap.has_key(label)):
            return self.labelShadeLumMap[label]
        return -1
    
    def getShadeLevel(self, label):
        if(self.labelShadeLevelMap.has_key(label)):
            return self.labelShadeLevelMap[label]
        return -1
    
    def setShadeLevel(self, label, level):
        self.labelShadeLevelMap[label] = level
    
    
    def isShapeShifted(self, label):
        if(self.labelShapeShiftMap.has_key(label)):
            return self.labelShapeShiftMap[label]
        return False
    
    def getShapeNum(self, label):
        if(self.labelShapeNumMap.has_key(label)):
            return self.labelShapeNumMap[label]
        return -1
    
    def getPrevShapeNum(self, label):
        if(self.labelPrevShapeNumMap.has_key(label)):
            return self.labelPrevShapeNumMap[label]
        return -1
    
    #//! returns the statistical signature of each label/urn/feature.
    #//! The total number of balls is stored in statSign[0].
    def getStatSign(self, label):
        if(self.labelStatSignMap.has_key(label)):
            return self.labelStatSignMap[label]
        return None
    
    def getStatSignMap(self):
        return self.labelStatSignMap
    
    def getIsland(self, label):
        return self.labelIslandMap[label]
    
    def hasIsland(self, label):
        if(self.labelIslandMap.has_key(label)):
            return True
        return False
    
    def printCompareLabels(self, labels1, labels2, score=-1.0, markShifted=0):
        labelMap1 = labels1.getMap()
        labelMap2 = labels2.getMap()
        i=0
        for (key1,v1), (key2,v2) in zip(labelMap1.items(), labelMap2.items()):
            isShifted = labels1.isShapeShifted(key1)
            if(markShifted==0 or not isShifted):
                print("{}) {}: {}({:.6f}) | {}: {}({:.6f})".format(i,key1,v1[0],v1[1],key2,v2[0],v2[1]))
            else:
                print("{}) *{}: {}({:.6f}) | {}: {}({:.6f})".format(i,key1,v1[0],v1[1],key2,v2[0],v2[1]))
            i+=1
        if(score>=0):
            print("Results: {}".format(score))
    
    def writeCompareLabels(self, name, labels1, labels2, score=-1.0, markShifted=0):
        filename = name+".txt"
        with open(filename, "w") as f:
            labelMap1 = labels1.getMap()
            labelMap2 = labels2.getMap()
            i=0
            for (key1,v1), (key2,v2) in zip(labelMap1.items(), labelMap2.items()):
                isShifted = labels1.isShapeShifted(key1)
                if(markShifted==0 or not isShifted):
                    f.write("{}) {}: {}({:.6f}) | {}: {}({:.6f})".format(i,key1,v1[0],v1[1],key2,v2[0],v2[1]))
                else:
                    prevShape = labels1.getPrevShapeNum(key1)
                    f.write("{}) {}->{}: {}({:.6f}) | {}: {}({:.6f})".format(i,prevShape,key1,v1[0],v1[1],key2,v2[0],v2[1]))
            if(score>=0):
                f.write("Results: {}".formate(score))
    

import cv2
import numpy as np

class Islands:
    islArea = 0
    islShadeLevel = 0
    islShape = 0
    islSubShape = 0
    islShapeName = ""
    islandImg = [[]]
    nn_prepared_img =[[]]
    NN_Results = []
    NN_Score = 0.0
    islPt = [0,0]
    _centerOfMass = [0,0]
    coordMap = {}
    _labelName = ""
    is_shape_shifted = False
    prev_shape = 0
    
    def determineIslandShape(self, islandImg):
        something_here = 1;
        #needs TestML before implementation
        
    def getIslandPoints(self, islandImg):
        nonZeroCoord = cv2.findNonZero(islandImg);
        # gets the center of mass and stores all the coords in a map
        xCenter = 0
        yCenter = 0
        for i in range(len(nonZeroCoord)):
            x = nonZeroCoord[i][0][1]
            y = nonZeroCoord[i][0][0]
            coords = str(y)+","+str(x)
            if(self.coordMap.has_key(coords)==False):
                self.coordMap[coords] = (y,x)
            
            xCenter += x
            yCenter += y
            
        xCenter /= len(nonZeroCoord)
        yCenter /= len(nonZeroCoord)
        self._centerOfMass = [xCenter,yCenter]

        # gets the start point of the island
        self.islPt = nonZeroCoord[0][0]
        
    def __init__(self,islandImg):
        self.islSubShape = -1
        self.islArea = cv2.countNonZero(islandImg)
        self.islShadeLevel = islandImg.max()
        self.islandImg = islandImg;
        self.determineIslandShape(islandImg);
        self.getIslandPoints(islandImg);
        self._labelName = "";
        self.is_shape_shifted = False;
        self.prev_shape = -1;
        
    def area(self):
        return self.islArea
    
    def shade(self):
        return self.islShadeLevel
    
    def image(self):
        return self.islandImg
    
    def nn_image(self):
        return self.nn_prepared_img
    
    def shape(self, set_shape=""):
        if(set_shape!=""):
            self.islShape = set_shape
        return self.islShape
    
    def shape_name(self, set_shape_name=""):
        if(set_shape_name!=""):
            self.islShapeName = set_shape_name
        return self.islShapeName
    
    def nn_results(self):
        return self.NN_Results
    
    def nn_score(self):
        return self.NN_Score
    
    def startPt(self):
        return self.islPt
    
    def set_island_shade(self,shade):
        for i in range(len(self.islandImg)):
            for j in range(len(self.islandImg[i])):
                coords = str(i) + "," + str(j)
                if(self.islandImg[i,j]>0 and self.coordMap.has_key(coords)):
                    self.islandImg[i,j] = shade;
                else:
                    self.islandImg[i,j] = 0;
        
    def centerOfMass(self):       
        return self._centerOfMass
    
    def coordinates(self):
        return self.coordMap
    
    def containsCoordinates(self,coords,pt=()):
        if(coords!=""):
            if(self.coordMap.has_key(coords)):
                return True
        
            return False
        
        coords = str(pt[0]) + "," + str(pt[1])
        if(self.coordMap.has_key(coords)):
            return True
    
        return False;
    
    def labelName(self):
        return self._labelName
    
    def isEmpty(self):
        return not self.islandImg.any()
    
    def isShapeShifted(self):
        return self.is_shape_shifted
    
    def prevShape(self):
        return self.prev_shape
    
    
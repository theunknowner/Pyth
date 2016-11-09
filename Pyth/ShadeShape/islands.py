import cv2
import numpy as np

from Shapes.shapemorph import ShapeMorph
from NeuralNetwork.ann import ANN
import functions as fn

class Islands:
    
    def __init__(self,islandImg):
        self.islArea = 0
        self.islShadeLevel = 0
        self.islShape = 0
        self.islSubShape = 0
        self.islShapeName = ""
        self.islandImg = [[]]
        self.nn_prepared_img =[[]]
        self.NN_Results = []
        self.NN_Score = 0.0
        self.islPt = [0,0]
        self._centerOfMass = [0,0]
        self.coordMap = {}
        self._labelName = ""
        self.is_shape_shifted = False
        self.prev_shape = 0
        
        self.subIslandVec = []
        self.islName = ""
        self.NN_Results2 = []
        self.NN_Score_2 = 0.0
        self.arc_length = 0
    
        self.islSubShape = -1
        self.islArea = cv2.countNonZero(islandImg)
        self.islShadeLevel = islandImg.max()
        self.islandImg = islandImg;
        self.determineIslandShape(islandImg);
        self.getIslandPoints(islandImg);
        self._labelName = "";
        self.is_shape_shifted = False;
        self.prev_shape = -1;
        
    def determineIslandShape(self, islandImg):
        ml = ANN()
        sampleVec = []
        sample = islandImg.copy()
        sample[sample > 0] = 255
        sample = ml.prepareImage(sample,ml.getSize())
        sampleVec.append(sample)
    
        results = ml.runANN2(sampleVec)
        self.NN_Results = results
        max_elem = results[0].max()
        labelNum = results[0].tolist().index(max_elem)
        thresh = 0.0
        if(max_elem<thresh):
            labelNum = ml.getShapeIndex2("Default")
        shapeName = ml.getShapeName2(labelNum)
        if(labelNum==0 or labelNum==1 or labelNum==3):
            results = ml.runANN2b(sampleVec,labelNum)
            self.NN_Results2 = results
            self.NN_Score_2 = results[0,0]
            if(labelNum==0 or labelNum==1):
                if(results[0,0]>0.0):
                    shapeName = "Comp-" + shapeName
                else:
                    shapeName = "Incomp-" + shapeName
            else:
                if(results[0,0]>0.0):
                    shapeName = "Fused-Donuts"
        labelNum = ml.getShapeIndex(shapeName)
        self.NN_Score = max_elem
        self.islShape = labelNum
        self.islShapeName = shapeName
        self.nn_prepared_img = sample
        
    def getIslandPoints(self, islandImg):
        nonZeroCoord = cv2.findNonZero(islandImg) #this function returns points in ndarray form [x,y]
        # gets the center of mass and stores all the coords in a map
        xCenter = 0
        yCenter = 0
        for i in range(len(nonZeroCoord)):
            x = nonZeroCoord[i][0][0]
            y = nonZeroCoord[i][0][1]
            coords = str(y)+","+str(x)
            if(self.coordMap.has_key(coords)==False):
                self.coordMap[coords] = (y,x)
                
            xCenter += x
            yCenter += y
            
        xCenter /= len(nonZeroCoord)
        yCenter /= len(nonZeroCoord)
        self._centerOfMass = [yCenter,xCenter]

        # gets the start point of the island
        self.islPt = nonZeroCoord[0][0]
        
    def extractSubIslands(self, islandImg):
        sm = ShapeMorph()
        littleIslands = sm.liquidFeatureExtractionInverse(islandImg)
        return littleIslands

    def storeSubIslands(self, subIsland):
        self.subIslandVec.append(subIsland)
        
    def name(self):
        return self.islName

        
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
    
    def nn_results2(self):
        return self.NN_Results2
    
    def nn_score(self):
        return self.NN_Score
    
    def nn_score_2(self):
        return self.NN_Score_2
    
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
    
    def coordinates(self, coordMap=None):
        if coordMap!=None:
            self.coordMap = coordMap
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
    
    def arcLength(self):
        return self.arc_length

    def subIsland(self, subIslNum):
        return self.subIslandVec[subIslNum]
    
    def numOfSubIslands(self):
        return len(self.subIslandVec)

    def getSubIslandWithPoint(self, pt):
        for i in range(self.numOfSubIslands()):
            sub_island = self.subIsland(i)
            if(sub_island.containsCoordinate(pt)):
                return self.subIsland(i)
        return None
    
    def onMouseCheckSubIslands(self, event, x, y, flags, param):
        island = param
        img = island.image().copy()
        if not hasattr(self.onMouseCheckSubIslands, "ml"):
            ml = ANN()
        if  ( event == cv2.EVENT_LBUTTONDOWN ):
            subIsland = island.getSubIslandWithPoint((y,x))
            if not subIsland.isEmpty():
                lum = img[y,x]
                area = subIsland.area()
                nnResult = max(subIsland.nn_results())
                img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
                for value in subIsland.coordinates().values():
                    x = value[1]
                    y = value[0]
                    img[y,x] = (0,255,0)
                shade_shape = subIsland.shape_name()
                text = "({},{}) | Lum: {} | Area: {} | ShadeShape: {} | NN: {}".format(x,y,lum,area,shade_shape,nnResult)
                cv2.displayStatusBar(island.name(),text)
                nnResults = subIsland.nn_results()
                textScore = "[{:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}]".format(nnResults[0,0],nnResults[0,1],nnResults[0,2],nnResults[0,3],nnResults[0,4],nnResults[0,5])
                cv2.namedWindow("SubIsland", cv2.WINDOW_NORMAL)
                cv2.imshow("SubIsland",subIsland.image())
                cv2.namedWindow("SubIsland_NN", cv2.WINDOW_NORMAL)
                cv2.displayStatusBar("SubIsland_NN",textScore)
                cv2.imshow("SubIsland_NN",subIsland.nn_image())
        if(event == cv2.EVENT_LBUTTONUP):
            img = island.image().copy()
        cv2.imshow(island.name(),img)

    def showInteractiveSubIslands(self):
        cv2.namedWindow(self.islName, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.islName,self.onMouseCheckSubIslands, self)
        cv2.imshow(self.islName,self.islandImg)
        cv2.waitKey(0)

    
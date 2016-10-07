import numpy as np
import cv2
from islands import Islands
import functions as fn

class Features:
    parentId = object #ImageData parentID

    islandVec = []
    shadeVec = []
    featureImg = [[]]
    featArea = 0
    numOfIsls = 0
    featShape = 0
    featShapeName = ""
    NN_Results = []
    NN_Score = 0.0
    
    def __init__(self,featureImg,parentId):
        self.parentId = parentId
        thresh = 0
        self.featureImg = featureImg
        self.featArea = cv2.countNonZero(featureImg)
        littleIslands = self.extractIslands(featureImg, thresh)
        for i in range(len(littleIslands)):
            island = Islands(littleIslands.at(i))
            crop_img = fn.cropImage(island.image());
            frameArea = (crop_img.shape[0]*crop_img.shape[1]) / (island.image().shape[0]*island.image().shape[1]);
        if(frameArea>0.01 and (island.shape_name().find("Excavated")>=0 or island.shape_name().find("Default")>=0)):
            containsRegularShape = False
            islandVec2 = []
            littleIslands2 = self.disconnectIslands(island.image())
            for j in range(len(littleIslands2)):
                island2 = Islands(littleIslands2.at(j))
                islandVec2.append(island2)
                if(island2.shape_name().find("Disc")>=0 or island2.shape_name().find("Donut")>=0):
                    area = island2.area() / island.area();
                    if(area>0.02):
                        containsRegularShape = True;
                        
            if(containsRegularShape):
                self.appendIslands(islandVec2);
            else:
                self.storeIsland(island);
            
        else:
            self.storeIsland(island);
    
        self.numOfIsls = len(self.islandVec);
        self.determineFeatureShape(featureImg);
        self.getShadesOfIslands();
        
    def island(self,islNum):
        return self.islandVec[islNum]
    
    def image(self):
        return self.featureImg
    
    def area(self):
        return self.featArea
    
    def numOfIslands(self):
        return self.numOfIsls
    
    def shape(self):
        return self.featShape
    
    def shape_name(self):
        return self.featShapeName
    
    def nn_results(self):
        return self.NN_Results
    
    def numOfShades(self):
        return len(self.shadeVec)
    
    def shade(self,num):
        return self.shadeVec[num]
    
    def release(self):
        self.islandVec = []
    
    ########### PRIVATE FUNCTIONS ############
    def extractIslands(self,featureImg, thresh):
        something_here = 1
        #needs shapemorph class to implement
        return something_here
        
    def disconnectIslands(self,featureImg):
        something_here = 1
        #needs shapemorph class to implement
        return something_here
        
    def storeIsland(self,island):
        self.islandVec.append(island)
        
    def appendIslands(self,islandVec):
        self.islandVec.extend(islandVec)
        
    def determinFeatureShape(self,featureImg):
        something_here = 1
        #needs TestML to implement
        
    def getShadesOfIslands(self):
        maxVal = self.featureImg.max()
        shadeVec = np.zeros(maxVal+1)
        for i in range(self.numOfIsls):
            try:
                shadeVec[self.islandVec[i].shade()]+=1
            except IndexError:
                print "MaxVal: %d\n" % (maxVal)
                print "ShadeVec.size(): %d\n" % (len(shadeVec))
                print "Island: %d, Shade: %d\n" % (i,self.island(i).shade());
                exit(1);
        
        for i in range(len(shadeVec)):
            if(shadeVec[i]>0):
                self.shadeVec.append(i)
        
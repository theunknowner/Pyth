import numpy as np
import cv2

from islands import Islands
import functions as fn
#from Shapes.shapes import Shapes

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
    
    def __init__(self,featureImg,parentId,disconnectIslands=True):
        self.parentId = parentId
        self.featureImg = featureImg
        self.featArea = cv2.countNonZero(featureImg)
        thresh = 0.001
        littleIslands = self.extractIslands(featureImg, thresh)
        for i in range(len(littleIslands)):
            island = Islands(littleIslands.at(i))
            crop_img = fn.cropImage(island.image());
            frameArea = crop_img.size
            
            if(frameArea<=50):
                #shapes = Shapes()
                #island.shape_name("Unknown")
                #island.shape(shapes.getShapeIndex(island.shape_name()))
                pass # TODO
            if(disconnectIslands):
                crop_img = fn.cropImage(island.image())
                frameArea = float(crop_img.size) / island.image().size
                newIslandImg = np.copy(island.image())
                if(frameArea>0.01 and (island.shape_name().find("Excavated")>=0 or island.shape_name().find("Default")>=0)):
                    islandVec2 = []
                    littleIslands2 = self.disconnectIslands(island.image())
                    for j in range(len(littleIslands2)):
                        island2 = Islands(littleIslands2.at(j))
                        if(island2.shape_name().find("Fused-Donuts")>=0 and island2.shape_name().find("Comp-Donut")>=0):
                            crop_img2 = fn.cropImage(island2.image())
                            relArea = float(island2.area())/island.area()
                            frameArea = float(crop_img2.size) / crop_img.size
                            bigFrameArea = float(crop_img2.size) / island.image().size
                            count = fn.countPositive(island2.nn_results())
                            if(relArea>0.01 and frameArea>0.01 and bigFrameArea>0.01 and count==1):
                                islandVec2.append(island2);
                                newIslandImg = newIslandImg - island2.image();
                                
                    if(len(islandVec2)>0):
                        self.appendIslands(islandVec2)
                        island = Islands(newIslandImg)
                        
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
        shadeVec = [0] * (maxVal+1)
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
        
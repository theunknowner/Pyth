import numpy as np
import cv2

from islands import Islands
import functions as fn
from Shapes.shapes import Shapes
from Shapes.shapemorph import ShapeMorph
from NeuralNetwork.ann import ANN

class Features:
    
    def __init__(self,featureImg,parentId,disconnectIslands=True):
        self.islandVec = []
        self.shadeVec = []
        self.featShape = 0
        self.featShapeName = ""
        self.NN_Results = []
        self.NN_Score = 0.0
        
        self.parentId = parentId
        self.featureImg = featureImg
        self.featArea = cv2.countNonZero(featureImg)
        thresh = 0.001
        littleIslands = self.extractIslands(featureImg, thresh)
        for i in range(len(littleIslands)):
            island = Islands(littleIslands[i])
            crop_img = fn.cropImage(island.image())
            frameArea = crop_img.size
            if(frameArea<=50):
                shapes = Shapes()
                island.shape_name("Unknown")
                island.shape(shapes.getShapeIndex(island.shape_name()))
            if(disconnectIslands):
                crop_img = fn.cropImage(island.image())
                frameArea = float(crop_img.size) / island.image().size
                newIslandImg = np.copy(island.image())
                if(frameArea>0.01 and (island.shape_name().find("Excavated")>=0 or island.shape_name().find("Default")>=0)):
                    islandVec2 = []
                    littleIslands2 = self.disconnectIslands(island.image())
                    for j in range(len(littleIslands2)):
                        island2 = Islands(littleIslands2[j])
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
                        
            self.storeIsland(island)
        self.numOfIsls = len(self.islandVec)
        self.determineFeatureShape(featureImg)
        self.getShadesOfIslands()
        
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
        sm = ShapeMorph()
        islandVec = []
        ptsVec = {}
        for row in range(0, featureImg.shape[0]):
            for col in range(0, featureImg.shape[1]):
                val = featureImg[row,col]
                if(val>0):
                    if not ptsVec.has_key(val):
                        ptsVec[val] = []
                    ptsVec[val].append((row,col))
        #> prev size of image before resizing to 140x140
        prevSize = self.parentId.prevSize()
        #> magnification factor == (140 x 140) / (L x W)
        m = featureImg.size / (float(prevSize[1]) * float(prevSize[0]))
        for key in ptsVec:
            shadeShape = np.zeros(featureImg.shape, np.uint8)
            if(len(ptsVec[key])>0):
                for k in range(0, len(ptsVec[key])):
                    shadeShape[ptsVec[key][k]] = key
                # helps connect islands that should be together
                shadeShape = sm.densityConnector(shadeShape, 0.999999, m)
                littleIslands = sm.liquidFeatureExtraction(shadeShape,0,0,0)
                for k in range(0, len(littleIslands)):
                    relArea = cv2.countNonZero(littleIslands[k]) / float(self.parentId.area())
                    if(relArea>thresh):
                        islandVec.append(littleIslands[k])
        return islandVec
        
    def disconnectIslands(self,featureImg):
        sm = ShapeMorph()
        islandVec = []
        shadeShape = sm.densityDisconnector(featureImg,0.999999)
        littleIslands = sm.liquidFeatureExtraction(shadeShape,0,0,0)
        for k in range(0, len(littleIslands)):
            if(cv2.countNonZero(littleIslands[k])>5):
                islandVec.append(littleIslands[k])
        return islandVec
        
    def storeIsland(self,island):
        self.islandVec.append(island)
        
    def appendIslands(self,islandVec):
        self.islandVec.extend(islandVec)
        
    def determineFeatureShape(self,featureImg):
        ml = ANN()
        sampleVec = []
        sample = featureImg.copy()
        sample *= 255
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
        if(labelNum==0 or labelNum==1):
            results = ml.runANN2b(sampleVec,labelNum)
            if(results[0,0]>0.0):
                shapeName = "Comp-" + shapeName
            else:
                shapeName = "Incomp-" + shapeName
        labelNum = ml.getShapeIndex(shapeName)
        self.NN_Score = max_elem
        self.featShape = labelNum
        self.featShapeName = shapeName
        
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
        
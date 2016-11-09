#include "shadeshape.h"
#include "../Shape/shapemorph.h"
#include "../functions.h"
#include "../Math/maths.h"
#include "islands.h"
#include "features.h"
#include "../neuralnetworks/testml.h"
#include "../ImageData/imagedata.h"

import cv2
import math
import numpy as np

from features import Features
from Mymath import mymath
import functions as fn
from NeuralNetwork.ann import ANN
from Shapes.shapemorph import ShapeMorph

class ShadeShape:
    winName = ""
    winName2 = "Extracted"
    winName3 = "40x40"
    
    def __init__(self, imgdata, disconnectIslands=False, debugSym=0):
        self.ss_name = ""
        self.featureVec = []
        self.shadeVec = []
        self.areaVec = []
        self.numOfFeats = 0
        self.ssArea = 0
        self.ssAreaPostDensityConnector = 0
        self.img = None
        self.imgdata = None
        
        self.extract(imgdata, disconnectIslands,debugSym)
    
    def onMouseCheckIslands(self, event, x, y, flags, param):
        #ss = param
        img = self.image().copy()
        if not hasattr(self.onMouseCheckSubIslands, "ml"):
            ml = ANN()
        if  ( event == cv2.EVENT_LBUTTONDOWN ):
            island = self.getIslandWithPoint((y,x))
            if island!=None and not island.isEmpty():
                lum = img[y,x]
                area = island.area()
                shadeNum = self.getIndexOfShade(island.shade())
                nnResult = max(island.nn_results()[0])
                img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
                for value in island.coordinates().values():
                    col = value[1]
                    row = value[0]
                    img[row,col] = (0,255,0)
                shade_shape = island.shape_name() + "_s" + str(shadeNum)
                text = "({},{}) | Lum: {} | Area: {} | ShadeShape: {} | NN: {}".format(x,y,lum,area,shade_shape,nnResult)
                cv2.displayStatusBar(self.winName,text)
                nnResults = island.nn_results()
                textScore = "[{:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}]".format(nnResults[0,0],nnResults[0,1],nnResults[0,2],nnResults[0,3],nnResults[0,4])
                textScore2 = "{:.5f}".format(island.nn_score_2())
                cv2.namedWindow(self.winName2, cv2.WINDOW_NORMAL)
                cv2.displayStatusBar(self.winName2,textScore)
                cv2.imshow(self.winName2,island.image())
                cv2.namedWindow(self.winName3, cv2.WINDOW_NORMAL)
                cv2.displayStatusBar(self.winName3,textScore2)
                cv2.imshow(self.winName3,island.nn_image())
        if(event == cv2.EVENT_LBUTTONUP):
            img = self.image().copy()
        cv2.imshow(self.winName,img)


    def onMouseCheckSubIslands(self, event, x, y, flags, param):
        ss = param
        img = ss.image().copy()
        if not hasattr(self.onMouseCheckSubIslands, "ml"):
            ml = ANN()
        islandExist = False
        if  ( event == cv2.EVENT_LBUTTONDOWN ):
            island = ss.getIslandWithPoint((y,x))
            if not island.isEmpty():
                lum = img[y,x]
                area = island.area()
                shadeNum = ss.getIndexOfShade(island.shade())
                nnResult = max(island.nn_results())
                img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
                for value in island.coordinates().values():
                    x = value[1]
                    y = value[0]
                    img[y,x] = (0,255,0)
                shade_shape = island.shape_name() + "_s" + str(shadeNum)
                text = "({},{}) | Lum: {} | Area: {} | ShadeShape: {} | NN: {} | {}".format(x,y,lum,area,shade_shape,nnResult,ss.area())
                cv2.displayStatusBar(self.winName,text)
                islandExist = True
        if(event == cv2.EVENT_LBUTTONUP):
            img = ss.image().copy()
        cv2.imshow(self.winName,img)
        if(islandExist):
            island.showInteractiveSubIslands()

    #/******************** PRIVATE FUNCTIONS **********************/
    def isOnTheEdge(self,src, x, y):
        size = [3,3]
        beginCol = x - math.floor(size[0]/2)
        beginRow = y - math.floor(size[1]/2)
        endCol = x + math.floor(size[0]/2)
        endRow = y + math.floor(size[1]/2)
        if(beginCol<0): beginCol = x
        if(beginRow<0): beginRow = y
        if(endCol>=src.shape[1]): endCol = x
        if(endRow>=src.shape[0]): endRow = y
        rec = src[beginRow:beginRow+size[1], beginCol:beginCol+size[0]]
        leftEdge = cv2.countNonZero(rec[:,0])
        rightEdge = cv2.countNonZero(rec[:,[rec.shape[1]-1]])
        topEdge = cv2.countNonZero(rec[0,:])
        bottomEdge = cv2.countNonZero(rec[[rec.shape[0]-1],:])
        if(leftEdge==0): return True
        if(rightEdge==0): return True
        if(topEdge==0): return True
        if(bottomEdge==0): return True
        return False
    
    def isUnitBridged(self, src, x, y):
        size = [3,3]
        ptArr = [[[0,0], [2,2]],
                 [[1,0], [1,2]],
                 [[2,0], [0,2]],
                 [[0,1], [2,1]]]
    
        beginCol = x - 1
        beginRow = y - 1
        endCol = x + 1
        endRow = y + 1
        rec = np.zeros(size,np.uint8)
        if(beginCol<0):
            for n in range(0,size[1]):
                rec[n,0] = 1
            beginCol = x;
        if(endCol>=src.shape[1]):
            for n in range(0,size[1]):
                rec[n,2] = 1
            endCol = x
        if(beginRow<0):
            for m in range(0,size[0]):
                rec[0,m] = 1
            beginRow = y
        if(endRow>=src.rows):
            for m in range (0,size[0]):
                rec[2,m] = 1
            endRow = y
        for i in range(beginRow,endRow+1):
            for j in range(beginCol,endCol+1):
                rec[i-beginRow,j-beginCol] = src[i,j]
        for i in range(0,4):
            val1 = rec[ptArr[i][0]]
            val2 = rec[ptArr[i][1]]
            if(val1>0 and val2>0): return True
    
        return False
    
    #//! should only be used if isUnitBridged() returns true
    def isBridgeWeak(self, src, x, y):
        size = [3,3]
        beginCol = x - math.floor(size[0]/2)
        beginRow = y - math.floor(size[1]/2)
        endCol = x + math.floor(size[0]/2)
        endRow = y + math.floor(size[1]/2)
        if(beginCol<0): beginCol = x
        if(beginRow<0): beginRow = y
        if(endCol>=src.shape[1]): endCol = x
        if(endRow>=src.shape[0]): endRow = y
        thresh = 2.55
        kernel = np.zeros(size,np.float32)
        for i in range(0,kernel.shape[0]):
            for j in range(0,kernel.shape[1]):
                dist = np.linalg.norm([j-i]-[1,1])
                dist = mymath.eucDist([j,i], [1,1])
                if(dist!=0):
                    val = 1.0/(dist*2.0)
                    kernel[i,j] = round(val,2)
        total = sum = 0
        for i in range(beginRow,endRow+1):
            for j in range(beginCol,endCol):
                total += kernel[i-beginRow,j-beginCol]
                if(src[i,j]>0):
                    sum+= kernel[i-beginRow,j-beginCol]
        if(sum<=0.75*total):
            return True
    
        return False
    
    def extractFeatures(self, src):
        sm = ShapeMorph()
        featureVec = sm.liquidFeatureExtraction(src,0,0,0)
        return featureVec
    
    def storeFeature(self,feature):
        self.featureVec.append(feature)
    
    #//! gets the unique shade values of the islands and stores them in a vector
    def getShadesOfFeatures(self, src, debugSym=0):
        maxVal = src.max()
        shadeVec = [0] * (maxVal+1)
        for i in range(0,self.numOfFeats):
            for j in range(0,self.feature(i).numOfIsls):
                shadeVec[self.feature(i).island(j).shade()]+=1
        for i in range(0,len(shadeVec)):
            if(shadeVec[i]>0):
                self.shadeVec.append(i)
        if(debugSym==1):
            print(len(self.shadeVec))
    
    def removeDuplicatePointsFromIslands(self):
        img = self.img
        src = np.zeros(img.shape, np.uint8)
        for i in range(0, self.numOfFeats):
            for j in range(0, self.feature(i).numOfIsls):
                isl = self.feature(i).island(j)
                coordMap = isl.coordinates()
                for key,value in coordMap.items():
                    col = value[1]
                    row = value[0]
                    val = img[row,col]
                    src[value] = (255)
                    if(isl.shade()!=val):
                        coordMap.pop(key, None)
                #self.feature(i).island(j).coordinates(coordMap)
    
    def storeIslandAreas(self):
        for i in range(0,self.numOfFeats):
            for j in range(0,self.feature(i).numOfIsls):
                isl = self.feature(i).island(j)
                self.areaVec.append(isl.area())
    
    #/******************** PUBLIC FUNCTIONS *********************/
    
    #//! extracts the features from the image
    def extract(self, imgdata, disconnectIslands=False, debugSym=0):
        self.imgdata = imgdata
        self.ss_name = fn.getFileName(imgdata.name())
        self.img = imgdata.image().copy()
        self.ssArea = cv2.countNonZero(self.img)
        featureVec = self.extractFeatures(self.img)
        for i in range(0,len(featureVec)):
            feature = Features(featureVec[i],self.imgdata,disconnectIslands)
            self.storeFeature(feature)
        self.numOfFeats = len(self.featureVec)
        self.getShadesOfFeatures(self.img)
        self.storeIslandAreas()
        self.ssAreaPostDensityConnector = sum(self.areaVec)
        self.removeDuplicatePointsFromIslands()
    
    #//! returns feature of [index]
    def feature(self, featNum):
        return self.featureVec[featNum]
    
    #//! returns number of features in image
    def numOfFeatures(self):
        return self.numOfFeats
    
    #//! returns shade value of [index]
    def shade(self, num):
        return self.shadeVec.at(num)
    
    #//! returns numbers of shades
    def numOfShades(self):
        return len(self.shadeVec)
    
    def getIndexOfShade(self, shade):
        index = self.shadeVec.index(shade)
        return index
    
    def area(self):
        return self.ssArea
    
    #//! returns total area of all islands post densityConnector()
    def areaPostDensityConnector(self):
        return self.ssAreaPostDensityConnector
    
    def image(self):
        return self.img
    
    def name(self):
        return self.ss_name
    
    def get_shades(self):
        return self.shadeVec
    
    # in python pt is a point tuple in form (y,x)
    def getIslandWithPoint(self, pt):
        coords = str(pt[0])+","+str(pt[1])
        for i in range(0, self.numOfFeats):
            for j in range(0, self.feature(i).numOfIsls):
                island = self.feature(i).island(j)
                if(island.coordinates().has_key(coords)):
                    return self.feature(i).island(j)
        return None
    
    #//! returns the largest area of all the islands
    def getMaxArea(self):
        return max(self.areaVec)
    
    def set_island_shade(self, featNum, islNum, newShade):
        island = self.feature(featNum).island(islNum)
        for i in range(0, island.image().shape[0]):
            for j in range(0, island.image().shape[1]):
                coords = str(i) + "," + str(j)
                if(island.coordinates().has_key(coords) and island.image()[i,j]>0):
                    self.img[i,j] = newShade
                    island.image()[i,j] = newShade
                else:
                    island.image()[i,j] = 0
    
    def getImageData(self):
        return self.imgdata
    
    def isolateConnectedFeatures(self, src):
        size = [3,3]
        ptsVec = []
    
        for row in range(0, src.shape[0]):
            for col in range(0, src.shape[1]):
                if(src[row,col]>0):
                    edged = self.isOnTheEdge(src,col,row)
                    bridged = self.isUnitBridged(src,col,row)
                    if (not edged and bridged):
                        weak = self.isBridgeWeak(src,col,row)
                        if(weak):
                            ptsVec.append((row,col))
        results = src.copy()
        for i in range(0, len(ptsVec)):
            results[ptsVec[i][0], ptsVec[i][1]] = 0
        fn.imgshow(src)
        fn.imgshow(results)
        
        sm = ShapeMorph()
        isolatedFeatures = sm.liquidFeatureExtraction(results)
        return isolatedFeatures
    
    def showInteractiveIslands(self):
        self.winName = self.ss_name;
        cv2.namedWindow(self.winName, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.winName,self.onMouseCheckIslands,self)
        cv2.imshow(self.winName,self.img)
        cv2.waitKey(0)
    
    def showInteractiveSubIslands(self):
        winName = self.ss_name
        cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(winName,self.onMouseCheckSubIslands, self)
        cv2.imshow(winName,self.img)
        cv2.waitKey(0)
        
if __name__ == "__main__":
    from ImageData.imagedata import ImageData
    filename = "/home/jason/Desktop/workspace/Test_Runs/Nov_3_2016/lph4/lph4_lph4_max_match_image_n0_shd0_shp-1-1.png"
    img = cv2.imread(filename,0)
    imgdata = ImageData(img,"lph4_lph4_max_match_image_n0_shd0_shp-1-1",0,filename)
    fn.prepareImage(imgdata,(140,140))
    ss = ShadeShape(imgdata)
    #isl = ss.getIslandWithPoint((23,50))
    ss.showInteractiveIslands()

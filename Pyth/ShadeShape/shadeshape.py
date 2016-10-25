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

winName = "Interactive Islands"
winName2 = "Extracted"
winName3 = "40x40"
'''
def onMouseCheckIslands(event, x, y, flags, param):
    ShadeShape &ss = *((ShadeShape*)param);
    Mat img = ss.image().clone();
    Islands island;
    static TestML ml;
    if  ( event == EVENT_LBUTTONDOWN ){
        island = ss.getIslandWithPoint(Point(x,y));
        if(!island.isEmpty()) {
            char text[100];
            int lum = img.at<uchar>(y,x);
            int area = island.area();
            int shadeNum = ss.getIndexOfShade(island.shade());
            float nnResult = *max_element(island.nn_results().begin<float>(),island.nn_results().end<float>());
            cvtColor(img,img,CV_GRAY2BGR);
            for(auto it=island.coordinates().begin(); it!=island.coordinates().end(); it++) {
                int x = it->second.x;
                int y = it->second.y;
                img.at<Vec3b>(y,x) = Vec3b(0,255,0);
            }
            String shade_shape = island.shape_name() + "_s" + toString(shadeNum);
            sprintf(text,"(%d,%d) | Lum: %d | Area: %d | ShadeShape: %s | NN: %f",x,y,lum,area,shade_shape.c_str(),nnResult);
            cv::displayStatusBar(winName,text);
            char textScore[100];
            char textScore2[20];
            Mat nnResults = island.nn_results();
            sprintf(textScore,"[%.5f, %.5f, %.5f, %.5f, %.5f]",nnResults.at<float>(0,0),nnResults.at<float>(0,1),nnResults.at<float>(0,2),nnResults.at<float>(0,3),nnResults.at<float>(0,4));
            sprintf(textScore2,"[%.5f]",island.nn_score_2());
            namedWindow(winName2, CV_WINDOW_FREERATIO | CV_GUI_EXPANDED);
            cv::displayStatusBar(winName2,textScore);
            imshow(winName2,island.image());
            namedWindow(winName3, CV_WINDOW_FREERATIO | CV_GUI_EXPANDED);
            cv::displayStatusBar(winName3,textScore2);
            imshow(winName3,island.nn_image());
        }
    }
    if(event == EVENT_LBUTTONUP) {
        img = ss.image().clone();
    }
    imshow(winName,img);
}
'''

'''
void onMouseCheckSubIslands(int event, int x, int y, int flags, void* param) {
    ShadeShape &ss = *((ShadeShape*)param);
    Mat img = ss.image().clone();
    Islands island;
    static TestML ml;
    bool islandExist = false;
    if  ( event == EVENT_LBUTTONDOWN ){
        island = ss.getIslandWithPoint(Point(x,y));
        if(!island.isEmpty()) {
            char text[100];
            int lum = img.at<uchar>(y,x);
            int area = island.area();
            int shadeNum = ss.getIndexOfShade(island.shade());
            float nnResult = *max_element(island.nn_results().begin<float>(),island.nn_results().end<float>());
            cvtColor(img,img,CV_GRAY2BGR);
            for(auto it=island.coordinates().begin(); it!=island.coordinates().end(); it++) {
                int x = it->second.x;
                int y = it->second.y;
                img.at<Vec3b>(y,x) = Vec3b(0,255,0);
            }
            String shade_shape = island.shape_name() + "_s" + toString(shadeNum);
            sprintf(text,"(%d,%d) | Lum: %d | Area: %d | ShadeShape: %s | NN: %f | %d",x,y,lum,area,shade_shape.c_str(),nnResult,ss.area());
            cv::displayStatusBar(winName,text);
            //char textScore[100];
            //Mat nnResults = island.nn_results();
            //sprintf(textScore,"[%.5f, %.5f, %.5f, %.5f, %.5f]",nnResults.at<float>(0,0),nnResults.at<float>(0,1),nnResults.at<float>(0,2),nnResults.at<float>(0,3),nnResults.at<float>(0,4));
            //namedWindow(winName3, CV_WINDOW_FREERATIO | CV_GUI_EXPANDED);
            //imshow(winName3,island.image());
            //namedWindow(winName2, CV_WINDOW_FREERATIO | CV_GUI_EXPANDED);
            //cv::displayStatusBar(winName2,textScore);
            //imshow(winName2,island.nn_image());
            islandExist = true;
        }
    }
    if(event == EVENT_LBUTTONUP) {
        img = ss.image().clone();
    }
    imshow(winName,img);
    if(islandExist) {
        island.showInteractiveSubIslands();
    }
}
'''

class ShadeShape:
    ss_name = ""
    featureVec = []
    shadeVec = []
    areaVec = []
    numOfFeats = 0
    ssArea = 0
    ssAreaPostDensityConnector = 0
    img = None
    id = None

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
                if(src[i,j]>0): sum+= kernel[i-beginRow,j-beginCol]
        if(sum<=0.75*total):
            return True
    
        return False
    
    def extractFeatures(self, src):
        #ShapeMorph sm;
        #vector<ImageData> featureVec = sm.liquidFeatureExtraction(src,0,0,0);
        #return featureVec;
        pass
    
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
        for i in range(0, self.numOfFeats):
            for j in range(0, self.feature(i).numOfIsls):
                isl = self.feature(i).island(j)
                coordMap = isl.coordinates()
                for key,value in coordMap.items():
                    col = value[0]
                    row = value[1]
                    val = img[row,col]
                    if(isl.shade()!=val):
                        coordMap.pop(key, None)
                        
                for key,value in coordMap.items():
                    col = value[0]
                    row = value[1]
                    val = img[row,col]
                    if(isl.shade()!=val):
                        coordMap.pop(key, None)
    
    def storeIslandAreas(self):
        for i in range(0,self.numOfFeats):
            for j in range(0,self.feature(i).numOfIsls):
                isl = self.feature(i).island(j)
                self.areaVec.append(isl.area())
    
    #/******************** PUBLIC FUNCTIONS *********************/
    
    def __init__(self, id, disconnectIslands=False, debugSym=0):
        self.extract(id, disconnectIslands,debugSym)
        
    #//! extracts the features from the image
    def extract(self, id, disconnectIslands=False, debugSym=0):
        self.id = id
        self.ss_name = fn.getFileName(id.name())
        self.img = np.copy(id.image())
        self.ssArea = cv2.countNonZero(self.img)
        featureVec = self.extractFeatures(self.img)
        for i in range(0,len(featureVec)):
            feature = Features(featureVec.at(i),self.id,disconnectIslands)
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
    
    ''' TODO
    def showInteractiveIslands(self):
        winName = self.ss_name;
        cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(winName,onMouseCheckIslands, self)
        cv2.imshow(winName,self.img)
        cv2.waitKey(0)
    '''
    
    def set_island_shade(self, featNum, islNum, newShade):
        island = self.feature(featNum).island(islNum)
        for i in range(0, island.image().shape[0]):
            for j in range(0, island.image().shape[1]):
                coords = str(j) + "," + str(i)
                if(island.coordinates().has_key(coords) and island.image()[i,j]>0):
                    self.img[i,j] = newShade
                    island.image()[i,j] = newShade
                else:
                    island.image()[i,j] = 0
    
    def getImageData(self):
        return self.id
    
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
                            ptsVec.append([col,row])
        results = np.copy(src)
        for i in range(0, len(ptsVec)):
            results[ptsVec[i][1], ptsVec[i][0]] = 0
        fn.imgshow(src)
        fn.imgshow(results)
        
        ### TODO
        #ShapeMorph sm
        #vector<Mat> isolatedFeatures = sm.liquidFeatureExtraction(results);
        #return isolatedFeatures;
    
    ''' TODO
    def showInteractiveSubIslands(self):
        winName = self.ss_name
        cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(winName,onMouseCheckSubIslands, self)
        cv2.imshow(winName,self.img)
        cv2.waitKey(0)
    '''
    

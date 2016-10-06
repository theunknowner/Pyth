'''
Created on Oct 5, 2016

@author: jason
'''

import numpy as np
import math
import cv2
from cluster import Cluster

class PeakCluster:
    isOutliersRemoved = False
    
    def convert2Vec(self, src):
        data_vec = []
        for i in range(0,src.shape[0]):
            for j in range(0,src.shape[1]):
                val = src[i,j]
                if(val>0):
                    data_vec.append(val)
                    
        return data_vec;
    
    def getMinMaxVal(self, data_vec):
        self.minVal = min(data_vec)
        self.maxVal = max(data_vec)

    def getPeakClusters(self, src):
        data_vec = self.convert2Vec(src)
        self.getMinMaxVal(data_vec);
    
        uniq_map = dict()
        for i in range(0,len(data_vec)):
            if not uniq_map.has_key(data_vec[i]):
                uniq_map[data_vec[i]] = 1
                
        changeThresh = 1.13
        changeCountThresh = 3
        maxShades = 5
        error = 2
        maxClusters = min(8,len(uniq_map))
        densityVec = []
        for i in range(0,maxClusters):
            clst = Cluster()
            clst.kmeansCluster(data_vec,i+1)
            totalPts = 0
            totalDensity = 0.0
            for j in range(0,clst.getNumOfClusters()):
                totalPts += clst.getSizeOfCluster(j)
                
            for j in range(0,clst.getNumOfClusters()):
                numPts = clst.getSizeOfCluster(j)
                minVal = clst.getMin(j)
                maxVal = clst.getMax(j)
                density = numPts/(maxVal-minVal)
                if(math.isinf(density)): density = 1000.0
                totalDensity += (float(numPts)/totalPts) * density
                center = clst.getCenter(j)
                #printf("Clst: %d, Center: %.0f, Min: %.0f, Max: %.0f, Range: %.0f, Size: %d, Density: %f\n",j+1,center,minVal,maxVal,maxVal-minVal,numPts,density);
    
            #cout << "-------------------------------------------" << endl;
            densityVec.append(totalDensity)
            
        changeVec = []
        change = -1.0
        for i in range(0,len(densityVec)):
            if(i>0):
                change = densityVec[i]/densityVec[i-1]
                changeVec.append(change)
                #printf("%d) Density: %f, Change: %f\n",i+1,densityVec.at(i),change);
            else:
                #printf("%d) Density: %f, Change: %f\n",i+1,densityVec.at(i),change);
                changeVec.append(change)

        changeCount = 0
        peakPos = 1
        for i in range(0, len(changeVec)):
            change = changeVec[i]
            if(change<=changeThresh and change>=0): changeCount+=1
            else: changeCount = 0
            #printf("%d: %f, %d\n",i+1,change,changeCount);
            if(changeCount>=changeCountThresh or i==(maxClusters-1)):
                peakPos = max((i-changeCountThresh),0)
                peakPos+=1
                break

        if(peakPos==1):
            peakPos = changeVec.index(max(changeVec)) + 1
            
        peakPos = min(peakPos+error,maxShades)
        return peakPos

    def removeShadeOutliers(self, discreteImg, origImg, thresh):
        '''
        return new image after removing shade outliers base on discreteImg
        '''
        shadeMap = dict()
        pointMap = dict()
        newImg = origImg.copy()
        for i in range(0,discreteImg.shape[0]):
            for j in range(0,discreteImg.shape[1]):
                val = discreteImg[i,j]
                if(val>0):
                    shadeMap[val]+=1
                    if not pointMap.has_key(val):
                        pointMap[val] = []
                    pointMap[val].append((j,i))
        area = cv2.countNonZero(discreteImg)
        for key in shadeMap:
            relArea = shadeMap[key] / float(area)
            if(relArea<=thresh):
                val = key
                for i in range(0,len(pointMap[val])):
                    pt = pointMap[val][i]
                    newImg[pt] = 0
                
                self.isOutliersRemoved = True
            
        if(self.isOutliersRemoved):
            data_vec = self.convert2Vec(newImg)
            self.getMinMaxVal(data_vec)

        return newImg;

if __name__ == "__main__":
    cluster = Cluster()
    img = cv2.imread("/home/jason/Desktop/Programs/Crop_Features/acne1_discrete.png",0)
    centers = cluster.kmeansCluster(img,4,0,255)
    print centers
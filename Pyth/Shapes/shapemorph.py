#include "shapemorph.h"
#include "../functions.h"
#include "../run.h"
#include "../Algorithms/jaysort.h"
#include "../Math/maths.h"
#include "../Cluster/cluster.h"
#include "../KneeCurve/kneecurve.h"
#include "../Poly/poly.h"
#include "../Algorithms/write.h"
#include "../ImageData/imagedata.h"
#include "../Pathfind/pathfind.h"
#include "../hsl/hsl.h"

import cv2
import numpy as np
import math
import traceback

import kneecurve as kc
from Algorithms import jaysort

class ShapeMorph:
    debugMode = False
    RECT = 0
    CIRCLE = 1

    def setDebugMode(self, mode):
        self.debugMode = mode
    
    def isDebugModeOn(self):
        return self.debugMode
    
    #//check to invert image
    def prepareImage(self, src):
        if(src.dtype!=np.uint8):
            src = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY);
        srcRight = cv2.flip(src,1)
        srcTop = cv2.transpose(src)
        srcTop = cv2.flip(srcTop,0)
        srcBottom = cv2.flip(srcTop,1)
        lightToDarkFlag = 0
        darkToLightFlag = 0
        leftFlag = rightFlag = topFlag = bottomFlag=0
        size = [3,3]
        dkThresh = 0.22;
        darkToLiteThresh = 1.03;
        liteToDarkThresh = 0.97;
        totalDK = avgDK = dkRatio = cumulativeDK=0
        totalDkRight = avgDkRight = dkRatioRight = cumulativeDkRight=0
        totalDkTop = avgDkTop = dkRatioTop = cumulativeDkTop=0
        totalDkBottom = avgDkBottom = dkRatioBottom = cumulativeDkBottom=0
        row = col=0
        countDK = countDkRight = countDkTop = countDkBottom=0
        begin = []
        drkMat = np.zeros((src.shape[0],src.shape[1]), np.float32)
        drkMatRight = np.zeros((src.shape[0],src.shape[1]), np.float32)
        drkMatTop = np.zeros((src.shape[0],src.shape[1]), np.float32)
        drkMatBottom = np.zeros((src.shape[0],src.shape[1]), np.float32)
        mapLeft = np.zeros((src.shape[0],src.shape[1],3), np.uint8)
        mapRight = np.zeros((src.shape[0],src.shape[1],3), np.uint8)
        mapTop = np.zeros((src.shape[0],src.shape[1],3), np.uint8)
        mapBottom = np.zeros((src.shape[0],src.shape[1],3), np.uint8)
        while(row<src.shape[0]):
            while(col<src.shape[1]):
                begin=[col-math.floor(size[0]/2),row-math.floor(size[1]/2)]
                for i in range(begin[1], begin[1]+size[1]):
                    for j in range(begin[0], begin[0]+size[0]):
                        if(j>=0 and i>=0 and j<src.shape[1] and i<src.shape[0]):
                            try:
                                totalDK += src[i,j]
                                totalDkRight += srcRight[i,j]
                                totalDkTop += srcTop[i,j]
                                totalDkBottom += srcBottom[i,j]
                                countDK+=1
                                countDkRight+=1
                                countDkTop+=1
                                countDkBottom+=1
                            except Exception:
                                traceback.print_exc()
                                print("ShapeMorph::prepareImage() out of range!")
                                print("src.size(): {}x{}".format(src.shape[0],src.shape[1]))
                                print("srcRight.size(): {}x{}".format(srcRight.shape[0],srcRight.shape[1]))
                                print("srcTop.size(): {}x{}".format(srcTop.shape[0],srcTop.shape[1]))
                                print("srcBottom.size(): {}x{}".format(srcBottom.shape[0],srcBottom.shape[1]))
                                print("Point({},{})".format(j,i))
                                exit(1)
                avgDK = float(totalDK)/countDK
                avgDkRight = float(totalDkRight)/countDkRight;
                avgDkTop = float(totalDkTop)/countDkTop;
                avgDkBottom = float(totalDkBottom)/countDkBottom;
                if(countDK==0): avgDK=0
                if(countDkRight==0): avgDkRight=0
                if(countDkTop==0): avgDkTop=0
                if(countDkBottom==0): avgDkBottom=0
                drkMat[row,col] = avgDK
                drkMatRight[row,col] = avgDkRight
                drkMatTop[row,col] = avgDkTop
                drkMatBottom[row,col]= avgDkBottom
                if(row<15 or src.shape[0]-row<=15):
                    boundaryLeft=15
                    boundaryRight = src.shape[1]-boundaryLeft
                else:
                    boundaryLeft=2
                    boundaryRight = src.shape[1]-boundaryLeft
                if(col>=boundaryLeft and col<=boundaryRight):
                    dkRatio = drkMat[row,col]/drkMat[row,col-1]
                    dkRatioRight = drkMatRight[row,col]/drkMatRight[row,col-1]
                    dkRatioTop = drkMatTop[row,col]/drkMatTop[row,col-1]
                    dkRatioBottom = drkMatBottom[row,col]/drkMatBottom[row,col-1]
                    cumulativeDK += dkRatio - 1.0
                    cumulativeDkRight += dkRatioRight - 1.0
                    cumulativeDkTop += dkRatioTop - 1.0
                    cumulativeDkBottom += dkRatioBottom - 1.0
                    if(leftFlag==0 and (cumulativeDK>=dkThresh or dkRatio>=darkToLiteThresh)):
                        darkToLightFlag+=1
                        leftFlag=1
                        mapLeft[row,col] = [0,0,255]
                    if(leftFlag==0 and (cumulativeDK<(-dkThresh) or dkRatio<=liteToDarkThresh)):
                        lightToDarkFlag+=1
                        leftFlag=1
                        mapLeft[row,col] = [0,255,0]
                    if(rightFlag==0 and (cumulativeDkRight>=dkThresh or dkRatioRight>=darkToLiteThresh)):
                        darkToLightFlag+=1
                        rightFlag=1
                        mapRight[row,col] = [0,0,255]
                    if(rightFlag==0 and (cumulativeDkRight<(-dkThresh) or dkRatioRight<=liteToDarkThresh)):
                        lightToDarkFlag+=1
                        rightFlag=1
                        mapRight[row,col] = [0,255,0]
                    if(topFlag==0 and (cumulativeDkTop>=dkThresh or dkRatioTop>=darkToLiteThresh)):
                        darkToLightFlag+=1
                        topFlag=1
                        mapTop[row,col] = [0,0,255]
                    if(topFlag==0 and (cumulativeDkTop<(-dkThresh) or dkRatioTop<=liteToDarkThresh)):
                        lightToDarkFlag+=1
                        topFlag=1
                        mapTop[row,col] = [0,255,0]
                    if(bottomFlag==0 and (cumulativeDkBottom>=dkThresh or dkRatioBottom>=darkToLiteThresh)):
                        darkToLightFlag+=1
                        bottomFlag=1
                        mapBottom[row,col] = [0,0,255]
                    if(bottomFlag==0 and (cumulativeDkBottom<(-dkThresh) or dkRatioBottom<=liteToDarkThresh)):
                        lightToDarkFlag+=1
                        bottomFlag=1
                        mapBottom[row,col] = [0,255,0]
                    if(leftFlag==1 and rightFlag==1 and topFlag==1 and bottomFlag==1):
                        break
                totalDK=0
                countDK=0
                totalDkRight=0
                countDkRight=0
                totalDkTop=0
                countDkTop=0
                totalDkBottom=0
                countDkBottom=0
                col+=1
            leftFlag=0
            rightFlag=0
            topFlag=0
            bottomFlag=0
            totalDK=0
            countDK=0
            totalDkRight=0
            countDkRight=0
            totalDkTop=0
            countDkTop=0
            totalDkBottom=0
            countDkBottom=0
            cumulativeDK=0
            cumulativeDkRight=0
            cumulativeDkTop=0
            cumulativeDkBottom=0
            col=0
            row+=1
    
        if(lightToDarkFlag>darkToLightFlag):
            result = 255 - src
        else:
            result = np.copy(src)
        return result
    
    #//! detects whether feature is light or dark
    #//! and returns the mask of feature
    def isFeatureLighter(self, src, src_map):
        imgGray = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
        lumGap = 8 # absolute thresh for the eye
        countLighter = 0
        countDarker = 0
        for i in range(0, imgGray.shape[0]):
            count = 0
            start = False
            for j in range(0, imgGray.shape[1]):
                if(src_map[i,j]>0):
                    lc = imgGray[i,j]
                    if(lc>0 and not start):
                        start = True
                        j+=1
                    if(start and j<imgGray.shape[1]):
                        lc = imgGray[i,j]
                        if(lc>0):
                            lc0 = imgGray[i,j-1]
                            if((lc-lc0)>lumGap):
                                countLighter+=1
                                count+=1
                            elif((lc0-lc)>lumGap):
                                countDarker+=1
                                count+=1
                    if(count>=10):
                        break
        if(countLighter>countDarker):
            return True
    
        return False
    
    #//! filter curve on original grayscale image
    def origFilter(self, src, shift=1.0):
        img = self.prepareImage(src)
        # removing stuff on edge
        mapEdgeRemoval = self.removeNoiseOnBoundary(img)
    
        # get lum values
        afterRemoval = cv2.bitwise_and(img,img,mapEdgeRemoval)
        #imgshow(afterRemoval);
        yVec = []
        for i in range(0,afterRemoval.shape[0]):
            for j in range(0, afterRemoval.shape[1]):
                lum = afterRemoval[i,j]
                if(lum>5):
                    yVec.append(lum)
        #filter the remaining image after removal of noise and outliers
        yVec = kc.removeOutliers(yVec,0.025)
        #writeSeq2File(yVec,"yVec");
        xVec = []
        for i in range(0,len(yVec)):
            xVec.append(i)
        coeffs = np.polyfit(xVec,yVec,1)
        p_val = np.polyval(coeffs,xVec)
        #MSE
        sum = 0.0
        for i in range(0,len(p_val)):
            val = (yVec[i]-p_val[i])/yVec[i]
            val = pow(val,2)
            sum += val
        sum = math.sqrt(sum)
        if(sum<2.5):
            del yVec[:len(yVec)/2]
    
        bestIdx = kc.kneeCurvePoint(yVec)
        bestIdx *= shift
        thresh = yVec[bestIdx]
        #cout << bestIdx << endl;
        #cout << thresh << endl;
        result = np.copy(afterRemoval)
        for i in range(0,afterRemoval.shape[0]):
            for j in range(0,afterRemoval.shape[1]):
                lum = afterRemoval[i,j]
                if(lum<thresh):
                    result[i,j] = 0
        return result
    
    #//! filter using close(Img) - Img
    def closeFilter(self, src, elementSize, shift=1.0):
        element = cv2.getStructuringElement(cv2.MORPH_RECT,elementSize)
        img = cv2.morphologyEx(src,cv2.MORPH_CLOSE,element)
        img2 = img - src

        #get darkest area from Close(img)-img
        yVec1 = []
        for i in range(0,img.shape[0]):
            for j in range(0,img.shape[1]):
                lum = img2[i,j]
                if(lum>5):
                    yVec1.append(lum)
        yVec1 = kc.removeOutliers(yVec1,0.025)
        bestIdx = kc.kneeCurvePoint(yVec1)
        thresh = yVec1[bestIdx]
        _img2 = np.copy(img2)
        for i in range(0,img2.shape[0]):
            for j in range(0,img2.shape[1]):
                lum = img2[i,j]
                if(lum<thresh):
                    _img2[i,j] = 0
    
        #edge removal for Close(img)-img Only
        mapEdgeRemoval = np.full((img.shape[0],img.shape[1]),255,np.uint8)
        size = [5,5]
        row = col = 0
        colLimit = img2.shape[1]
        while(row<img2.rows):
            _size = size
            if(row>15 or (img2.shape[0]-row)>15):
                colLimit = 15
            while(col<=colLimit):
                window1 = _img2[row:row+_size[1],col+_size[0]+_size[0]]
                window2 = _img2[row:row+_size[1],col+_size[0]]
                avg1 = avg2 = 0
                count1 = count2 = 0
                for i in range(0,window1.shape[0]):
                    for j in range(0,window1.shape[1]):
                        val1 = float(window1[i,j])
                        val2 = float(window2[i,j])
                        if(val1>5.0):
                            avg1 += val1
                            count1+=1
                        if(val2>5.0):
                            avg2 += val2;
                            count2+=1
                avg1 /= count1
                avg2 /= count2
                if((avg1-avg2)<=-16.0):
                    for i in range(row,row+window2.shape[0]):
                        for j in range(col,col+window2.shape[1]):
                            mapEdgeRemoval[i,j] = 0
                col+=1
            col=0
            row+=size.height
        img3 = cv2.bitwise_and(img2,img2,mapEdgeRemoval)
        #knee of curve filtering after edge removal
        yVec2 = []
        for i in range(0,img3.shape[0]):
            for j in range(0,img3.shape[1]):
                lum = img3[i,j]
                if(lum>5):
                    yVec2.append(lum)
        yVec2 = kc.removeOutliers(yVec2,0.025)
        bestIdx = kc.kneeCurvePoint(yVec2)
        bestIdx *= shift
        thresh = yVec2[bestIdx]
        result = np.copy(img3)
        for i in range(0, img3.shape[0]):
            for j in range(0,img3.shape[1]):
                lum = img3[i,j]
                if(lum<thresh):
                    result[i,j] = 0
        return result
    
    #//! using origFilter
    #//! returns islands/features into vector
    def lumFilter1(self, src, featuresToHold=1):
        img1 = self.origFilter(src)
        img2 = self.densityConnector(img1,0.9)
        featureVec = self.liquidFeatureExtraction(img2)
    
        #remove features clinging to image boundary
        m=0
        while(m<len(featureVec)):
            edges = np.zeros(img2.shape,np.uint8)
            contour = self.findBoundary(featureVec[m])
            cv2.drawContours(edges,contour,-1,(255))
            count = self.countEdgeTouching(edges,10,15)
            total = cv2.countNonZero(edges)
            percent = float(count)/total
            featurePixCount = cv2.countNonZero(featureVec[m])
            imagePixCount = cv2.countNonZero(img2)
            percentOfImage = float(featurePixCount)/imagePixCount
            #printf("%d/%d: %f, %f\n",count,total,percent,percentOfImage);
            #imgshow(edges);
            if(percent>=0.47 and percentOfImage<0.40):
                del featureVec[m:]
                featureVec.erase(featureVec.begin()+m)
            else:
                m+=1
    
        countPix = 0
        countVec = []
        for i in range(0,len(featureVec)):
            countPix = cv2.countNonZero(featureVec[i])
            countVec.append(countPix)
        countVec, idxVec = jaysort.jaysort(countVec)
        matVec = []
        element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        n=1
        while(True):
            try:
                result = cv2.morphologyEx(featureVec[idxVec[len(idxVec)-n]],cv2.MORPH_CLOSE,element)
                matVec.append(np.copy(result))
                #imwrite("img"+toString(n)+".png",matVec.at(matVec.size()-1));
                n+=1
                if(len(matVec)>=featuresToHold):
                    break
                if(n>len(idxVec)):
                    break
            except Exception:
                traceback.print_exc()
                print("Catch #1: ShapeMorph::lumFilter1() out of range!")
                print("n: {}".format(n))
                print("featureVec.size() = {}".format(len(featureVec)))
                print("idxVec.size() = {}".format(len(idxVec)))
                exit(1)
        return matVec
    
    #//! using closeFilter
    #//! returns islands/features into vector
    def lumFilter2(self, src, featuresToHold=1):
        img1 = self.closeFilter(src,(17,17))
        img2 = self.densityConnector(img1,0.9)
        featureVec = self.liquidFeatureExtraction(img2)
        countPix = 0
        countVec = []
        #sorts the features from largest to smallest
        for i in range(0,len(featureVec)):
            countPix = cv2.countNonZero(featureVec[i])
            countVec.append(countPix)
        countVec, idxVec = jaysort.jaysort(countVec)
        matVec = []
        element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        n=1
        while(True):
            try:
                result = cv2.morphologyEx(featureVec[idxVec[len(idxVec)-n]],cv2.MORPH_CLOSE,element)
                matVec.append(np.copy(result))
                #imgshow(matVec.at(matVec.size()-1));
                #imwrite("img"+toString(n)+".png",matVec.at(matVec.size()-1));
                n+=1
                if(len(matVec)>=featuresToHold):
                    break
                if(n>len(idxVec)):
                    break
            except Exception:
                traceback.print_exc()
                print("Catch #1: ShapeMorph::lumFilter2() out of range!")
                print("n: {}".format(n))
                print("featureVec.size() = {}".format(len(featureVec)))
                print("idxVec.size() = {}".format(len(idxVec)))
                exit(1)
        return matVec
    
    def getStructElem(self, size, shape):
        result = np.zeros(size,np.uint8)
        if(shape==ShapeMorph.CIRCLE):
            cv2.circle(result,((result.shape[1]-1)/2,(result.shape[0]-1)/2),int(round(size[0]/2)),(1),-1)
        elif(shape==ShapeMorph.RECT):
            cv2.rectangle(result,(0,0),(result.shape[1]-1,result.shape[0]-1),(1),-1)
        return result
    
    def elementaryDilation(self, origImg, scaleImg):
        result = np.copy(scaleImg)
        for i in range(0,result.shape[0]):
            for j in range(0,result.shape[1]):
                if(j==0):
                    val = max(result[i,j],result[i,j+1])
                    val = min(val,origImg[i,j+1])
                    result[i,j+1] = val
                elif(j==(scaleImg.shape[1]-1)):
                    val = max(result[i,j],result[i,j-1])
                    val = min(val, origImg[i,j-1])
                    result[i,j-1] = val
                else:
                    val = max(result[i,j],result[i,j-1])
                    val = min(val,origImg[i,j-1])
                    result[i,j-1] = val
    
                    val = max(result[i,j],result[i,j+1])
                    val = min(val,origImg[i,j+1])
                    result[i,j+1] = val
        return result
    
    #Ands the two images/ Assigns min of two images
    def custAnd(self, origImg, scaleImg, src_map):
        results = np.zeros(origImg.shape,np.uint8)
        if src_map.size>0:
            flag = rmin = 0
            for i in range(0,scaleImg.shape[0]):
                ptVec = []
                for j in range(0,scaleImg.shape[1]):
                    if(scaleImg[i,j]>0):
                        ptVec.append(j)
                for j in range(0, scaleImg.shape[1]):
                    if(flag==0):
                        rmin = origImg[i,j]
                    if(src_map[i,j]==255):
                        flag = 1
                    if(src_map[i,j]==0):
                        flag = 0
                    for k in range(0,len(ptVec)):
                        if(k<len(ptVec)-1):
                            if(j==ptVec[k]):
                                results[i,j] = min(rmin,origImg[i,j])
                                break
                            elif(j>ptVec[k] and j<ptVec[k+1]):
                                if(flag==1):
                                    results[i,j] = min(rmin,origImg[i,j])
                                else:
                                    val1 = origImg[i,ptVec[k]]
                                    val2 = origImg[i,ptVec[k+1]]
                                    val = origImg[i,j]
                                    rmin = max(val1,val2)
                                    results[i,j] = min(rmin,val)
                                break
                            elif(j<ptVec[k]):
                                if(flag==1):
                                    results[i,j] = min(rmin,origImg[i,j])
                                else:
                                    val1 = origImg[i,ptVec[k]]
                                    val = origImg[i,j]
                                    rmin = val1
                                    results[i,j] = min(val1,val)
                                break
                        else:
                            if(j>ptVec[k]):
                                if(flag==1):
                                    results[i,j] = min(rmin,origImg[i,j])
                                else:
                                    val1 = origImg[i,ptVec[k]]
                                    val = origImg[i,j]
                                    rmin=val1
                                    results[i,j] = min(val1,val)
                                break
        else:
            for i in range(0,scaleImg.shape[0]):
                ptVec = []
                for j in range(0,scaleImg.shape[1]):
                    if(scaleImg[i,j]>0):
                        ptVec.append(j)
                for j in range(0,scaleImg.shape[1]):
                    for k in range(0,len(ptVec)):
                        if(k<len(ptVec)-1):
                            if(j==ptVec[k]):
                                scaleImg[i,j] = origImg[i,j]
                                break
                            elif(j>ptVec[k] and j<ptVec[k+1]):
                                val1 = origImg[i,ptVec[k]]
                                val2 = origImg[i,ptVec[k+1]]
                                val = origImg[i,j]
                                results[i,j] = min(max(val1,val2),val)
                                break
                            elif(j<ptVec[k]):
                                val1 = origImg[i,ptVec[k]]
                                val = origImg[i,j]
                                results[i,j] = min(val1,val)
                                break
                        else:
                            if(j>ptVec[k]):
                                val1 = origImg[i,ptVec[k]]
                                val = origImg[i,j]
                                results[i,j] = min(val1,val)
                                break
        return results
    
    #thresh = discernible thresh; set sort = -1;1 -> Ascending;Descending
    def liquidFeatureExtraction(self, src, lcThresh=0, sort=0, numOfPtsThresh=10):
        src_map = np.zeros(src.shape, np.uint8)
        numFeatures = []
        row = col = 0
        while(row<src.shape[0]):
            while(col<src.shape[1]):
                if(src[row,col]>0 and src_map[row,col]==0):
                    ptVec = []
                    temp = []
                    ptVec.append([col,row])
                    src_map[row,col] = 255
                    temp.append([col,row])
                    while(len(temp)>0):
                        up = (temp[0][0],temp[0][1]-1)
                        left = (temp[0][0]-1,temp[0][1])
                        right = (temp[0][0]+1,temp[0][1])
                        down = (temp[0][0],temp[0][1]+1)
                        downLeft = (temp[0][0]-1,temp[0][1]+1)
                        downRight = (temp[0][0]+1,temp[0][1]+1)
                        if(up[1]>=0):
                            if(src_map[up]==0 and src[up]>lcThresh):
                                ptVec.append(up)
                                src_map[up]=255
                                temp.append(up)
                        if(left[0]>=0):
                            if(map[left]==0 and src[left]>lcThresh):
                                ptVec.append(left)
                                src_map[left]=255
                                temp.append(left)
                        if(right[0]<src.shape[1]):
                            if(map[right]==0 and src[right]>lcThresh):
                                ptVec.append(right)
                                src_map[right]=255
                                temp.append(right)
                        if(down[1]<src.shape[0]):
                            if(src_map[down]==0 and src[down]>lcThresh):
                                ptVec.append(down)
                                src_map[down]=255
                                temp.append(down)
                        if(down[1]<src.shape[0] and left[0]>=0):
                            if(src_map[downLeft]==0 and src[downLeft]>lcThresh):
                                ptVec.append(downLeft)
                                src_map[downLeft]=255
                                temp.append(downLeft)
                        if(down[1]<src.shape[0] and right[0]<src.shape[1]):
                            if(src_map[downRight]==0 and src[downRight]>lcThresh):
                                ptVec.append(downRight)
                                src_map[downRight]=255
                                temp.append(downRight)
                        del temp[0]
                    numFeatures.append(ptVec)
                col+=1
            col=0
            row+=1
    
        featureVec = []
        for i in range(0,len(numFeatures)):
            feature = np.zeros(src.shape, np.uint8)
            if(len(numFeatures[i])>=numOfPtsThresh):
                for j in range(0,len(numFeatures[i])):
                    feature[numFeatures[i][j]] = src[numFeatures[i][j]]
                featureVec.append(feature)
        if(sort==1):
            countVec = []
            tempVec = []
            for i in range(0,len(featureVec)):
                countPix = cv2.countNonZero(featureVec[i])
                countVec.append(countPix)
            countVec,idxVec = jaysort.jaysort(countVec)
            for i in range(len(idxVec)-1,-1,-1):
                try:
                    tempVec.append(featureVec[idxVec[i]])
                except Exception:
                    traceback.print_exc()
                    print("idxVec.size(): {}".format(len(idxVec)))
                    print("featureVec.size(): {}".format(len(featureVec)))
                    print("i:{}".format(i))
                    print("idx:{}".format(idxVec[i]))
                    exit(1)
            featureVec = tempVec
        if(sort==-1):
            countVec = []
            tempVec = []
            for i in range(0,len(featureVec)):
                countPix = cv2.countNonZero(featureVec[i])
                countVec.append(countPix)
            countVec,idxVec = jaysort.jaysort(countVec)
            for i in range(0,len(idxVec)):
                try:
                    tempVec.append(featureVec[idxVec[i]])
                except Exception:
                    traceback.print_exc()
                    print("idxVec.size(): {}".format(len(idxVec)))
                    print("featureVec.size(): {}".format(len(featureVec)))
                    print("i:{}".format(i))
                    print("idx:{}".format(idxVec[i]))
                    exit(1)
            featureVec = tempVec
        return featureVec
    
    #//! Nearest neighbor connector base on density
    #//! q = probability of connecting to a neighboring unit
    def densityConnector(self, src, q, coeff=1.0, increment=0.0):
        if not src.size:
            print("ShapeMorph::densityConnector() src is empty")
            print("src.size: {}x{}".format(src.shape[0],src.shape[1]))
            exit(1)
        lineVal = src.max()
        size = (5,5)
        C = 1.0
        alpha = 1.0
        beta = 0.0
        row = col=0
        fnVec = []
        absDiscernThresh=5.0
        while(row<src.shape[0]):
            while(col<src.shape[1]):
                density = countDk = avgDk=0
                for i in range(row,row+size[1]):
                    for j in range(col,col+size[0]):
                        if(j>=0 and i>=0 and j<src.shape[1] and i<src.shape[0]):
                            lc = src[i,j]
                            if(lc>absDiscernThresh):
                                density+=1
                                avgDk += lc
                                countDk+=1
                density /= (size[0] * size[1])
                avgDk /= countDk
                if(countDk==0):
                    avgDk = 0
                fx = C * pow(density,alpha) * pow(avgDk,beta)
                if(fx>0):
                    fnVec.append(fx)
                col+=1
            col=0
            row+=1
    
        #calculate knee of curve for fx for filtering
        fxThresh=0.0
        if(len(fnVec)>0):
            try:
                bestIdx = kc.kneeCurvePoint(fnVec)
                percent = round(float(bestIdx)/len(fnVec),2)
                if(percent<=0.05000001):
                    bestIdx = 0.25 * len(fnVec)
                if(percent>=0.8999999):
                    bestIdx = 0.75 * len(fnVec)
                #fx threshold filtering
                fxThresh = fnVec[bestIdx]
            except Exception:
                traceback.print_exc()
                print("ShapeMorph::densityConnector() out of range!")
                print("fnVec.size: {}".format(len(fnVec)))
                print("BestIdx: {}".format(bestIdx))
                exit(1)
        #connect nearest neighbors
        b = fxThresh
        a = pow(-coeff*math.log(1.0-q)/(3.14159 * b),0.5) + increment
        result = np.zeros(src.shape, np.uint8)
        row = col=0
        a = math.ceil(a)
        square = (a,a)
        while(row<src.shape[0]):
            while(col<src.shape[1]):
                lc = src[row,col]
                if(lc>0):
                    begin = (col-square[0],row-square[1])
                    end = (col+square[0],row+square[1])
                    for i in range(begin[1],end[1]):
                        for j in range(begin[0],end[0]):
                            if(j>=0 and i>=0 and j<src.shape[1] and i<src.shape[0]):
                                lc = src[i,j]
                                dist = abs(j-col) + abs(i-row)
                                if(dist<=a and lc>absDiscernThresh):
                                    if((j,i)!=(col,row)):
                                        cv2.line(result,(j,i),(col,row),(lineVal),1)
                col+=1
            col=0;
            row+=1
        return result
    
    def findBoundary(self, src):
        contour, hierarchy = cv2.findContours(src, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contour
    
    #//! for edges & corners of different sizes
    def countEdgeTouching(self, src, sideEdgeSize, cornerEdgeSize):
        _src = np.copy(src)
        topEdge = _src[cornerEdgeSize:cornerEdgeSize+src.shape[1]-cornerEdgeSize*2, 0:sideEdgeSize]
        bottomEdge = _src[cornerEdgeSize:cornerEdgeSize+src.shape[1]-cornerEdgeSize*2, src.rows-sideEdgeSize]
        Mat bottomEdge = _src(Rect(cornerEdgeSize,src.rows-sideEdgeSize,src.cols-cornerEdgeSize*2,sideEdgeSize));
        Mat leftEdge = _src(Rect(0,cornerEdgeSize,sideEdgeSize,src.rows-cornerEdgeSize*2));
        Mat rightEdge = _src(Rect(src.cols-sideEdgeSize,cornerEdgeSize,sideEdgeSize,src.rows-cornerEdgeSize*2));
        Mat topLeftEdge = _src(Rect(0,0,cornerEdgeSize,cornerEdgeSize));
        Mat topRightEdge = _src(Rect(src.cols-cornerEdgeSize,0,cornerEdgeSize,cornerEdgeSize));
        Mat bottomLeftEdge = _src(Rect(0,src.rows-cornerEdgeSize,cornerEdgeSize,cornerEdgeSize));
        Mat bottomRightEdge = _src(Rect(src.cols-cornerEdgeSize,src.rows-cornerEdgeSize,cornerEdgeSize,cornerEdgeSize));
        //int totalPix = countNonZero(src);
        int topEdgePix = countNonZero(topEdge);
        int leftEdgePix = countNonZero(leftEdge);
        int bottomEdgePix = countNonZero(bottomEdge);
        int rightEdgePix = countNonZero(rightEdge);
        int topLeftEdgePix = countNonZero(topLeftEdge);
        int topRightEdgePix = countNonZero(topRightEdge);
        int bottomLeftEdgePix = countNonZero(bottomLeftEdge);
        int bottomRightEdgePix = countNonZero(bottomRightEdge);
        int totalEdgePix = topEdgePix+leftEdgePix+bottomEdgePix+rightEdgePix+
                topLeftEdgePix+topRightEdgePix+bottomLeftEdgePix+bottomRightEdgePix;
        return totalEdgePix;
    }
    
    //returns map where noise is masked out
    Mat ShapeMorph::removeNoiseOnBoundary(Mat src) {
        Poly poly;
        KneeCurve kc;
        vector<double> vec;
        Mat darkestStuff(src.rows,src.cols,CV_8U,Scalar(255));
        for(int i=0; i<src.rows; i++) {
            for(int j=0; j<src.cols; j++) {
                double lum = src.at<uchar>(i,j);
                vec.push_back(lum);
            }
        }
        vector<double> xVec;
        sort(vec.begin(),vec.end());
        for(unsigned int i=0; i<vec.size(); i++) {
            xVec.push_back((double)i);
        }
        vector<double> p = poly.polyfit(xVec,vec,1);
        vector<double> y1 = poly.polyval(p,xVec);
        //MSE
        double sum=0;
        for(unsigned int i=0; i<y1.size(); i++) {
            double val = (vec.at(i)-y1.at(i))/vec.at(i);
            val = pow(val,2);
            sum += val;
        }
        sum = sqrt(sum);
        if(sum<2.5)
            vec.erase(vec.begin(),vec.begin()+(vec.size()/2));
        int index = kc.kneeCurvePoint(vec);
        double thresh = vec.at(index);
        for(int i=0; i<src.rows; i++) {
            for(int j=0; j<src.cols; j++) {
                double lum = src.at<uchar>(i,j);
                if(lum<thresh)
                    darkestStuff.at<uchar>(i,j) = 0;
            }
        }
        vector<Mat> islandsVec = this->liquidFeatureExtraction(darkestStuff,5.0);
        Mat mapEdgeRemoval(src.rows, src.cols, CV_8U, Scalar(255));
        for(unsigned int i=0; i<islandsVec.size(); i++) {
            Mat edges(darkestStuff.size(),CV_8U,Scalar(0));
            vector<vector<Point> > contour = this->findBoundary(islandsVec.at(i).clone());
            drawContours(edges,contour,-1,Scalar(255));
            int count = this->countEdgeTouching(edges,6,12);
            int total = countNonZero(edges);
            double percent = (double)count/total;
            int featurePixCount = countNonZero(islandsVec.at(i));
            double percentOfImage = (double)featurePixCount/darkestStuff.total();
            if(percent>=0.47 and percentOfImage<0.15) {
                for(int j=0; j<islandsVec.at(i).rows; j++) {
                    for(int k=0; k<islandsVec.at(i).cols; k++) {
                        int val = islandsVec.at(i).at<uchar>(j,k);
                        if(val==255)
                            mapEdgeRemoval.at<uchar>(j,k) = 0;
                    }
                }
            }
        }
    
        return mapEdgeRemoval;
    }
    
    //! returns map of image after noise removal
    //! input is a 5x5 smoothed image using Func::smooth()
    Mat ShapeMorph::removeNoiseOnBoundary2(Mat src) {
        Hsl hsl;
        vector<double> HSL;
        vector<double> vec;
        vector<double> lumVec;
        Size size(5,5);
        for(int i=0; i<=(src.rows-size.height); i+=size.height) {
            for(int j=0; j<=(src.cols-size.width); j+=size.width) {
                Vec3b RGB = src.at<Vec3b>(i,j);
                vector<double> HSL = hsl.rgb2hsl(RGB[2],RGB[1],RGB[0]);
                HSL.at(1) = round(HSL.at(1) * 100);
                HSL.at(2) = round(HSL.at(2) * 100);
                float val = (100.0 - HSL.at(1)) - HSL.at(2);
                vec.push_back(val);
                lumVec.push_back(HSL.at(2));
            }
        }
        KneeCurve kc;
        int idx = kc.kneeCurvePoint(vec);
        double thresh = vec.at(idx);
        int lumThreshIdx = kc.kneeCurvePoint(lumVec);
        int lumThresh = lumVec.at(lumThreshIdx) * 0.90;
    
        Mat map(src.size(),CV_8U,Scalar(255));
        Mat mask = Mat::zeros(size,CV_8U);
        for(int i=0; i<=(src.rows-size.height); i+=size.height) {
            for(int j=0; j<=(src.cols-size.width); j+=size.width) {
                int flag = 0;
                Vec3b RGB = src.at<Vec3b>(i,j);
                vector<double> HSL = hsl.rgb2hsl(RGB[2],RGB[1],RGB[0]);
                HSL.at(1) = round(HSL.at(1) * 100);
                HSL.at(2) = round(HSL.at(2) * 100);
                float val = (100.0 - HSL.at(1)) - HSL.at(2);
                for(int y=(i-size.height); y<=(i+size.height); y+=size.height) {
                    for(int x=(j-size.width); x<=(j+size.width); x+=size.width) {
                        if(y!=i and x!=j) {
                            if(x<0 || y<0 || x>=src.cols || y>=src.rows) {
                                flag = 1;
                            } else if(map.at<uchar>(y,x)==0) {
                                flag = 1;
                            }
                        }
                    }
                }
                if(val>thresh and HSL.at(2)<lumThresh and flag==1) {
                    mask.copyTo(map(Rect(j,i,mask.cols,mask.rows)));
                }
            }
        }
        return map;
    }
    
    Mat ShapeMorph::densityDisconnector(Mat src, double q, double coeff) {
        if(src.empty()) {
            printf("ShapeMorph::densityDisconnector() src is empty\n");
            printf("src.size: %dx%d\n",src.rows,src.cols);
            exit(1);
        }
        Mat map(src.rows,src.cols,CV_8U,Scalar(0));
        Size size(5,5);
        const double C=1.0;
        const double alpha=1.0;
        const double beta=0.0;
        int row=0, col=0;
        deque<double> fnVec;
        double density=0, countDk=0, avgDk=0;
        double absDiscernThresh=5.0;
        while(row<src.rows) {
            while(col<src.cols) {
                for(int i=row; i<(row+size.height); i++) {
                    for(int j=col; j<(col+size.width); j++) {
                        if(j>=0 and i>=0 and j<src.cols and i<src.rows) {
                            int lc = src.at<uchar>(i,j);
                            if(lc>absDiscernThresh) {
                                density++;
                                avgDk += lc;
                                countDk++;
                            }
                        }
                    }
                }
                density /= size.area();
                avgDk /= countDk;
                if(countDk==0) avgDk = 0;
                double fx = C * pow(density,alpha) * pow(avgDk,beta);
                if(fx>0)
                    fnVec.push_back(fx);
                avgDk=0;
                density=0;
                countDk=0;
                //col+=size.width;
                col++;
            }
            col=0;
            //row+=size.height;
            row++;
        }
    
        //calculate knee of curve for fx for filtering
        KneeCurve kc;
        int bestIdx;
        float fxThresh=0.0;
        if(fnVec.size()>0) {
            try {
                bestIdx = kc.kneeCurvePoint(fnVec);
                //fx threshold filtering
                fxThresh = fnVec.at(bestIdx);
            } catch(const std::out_of_range &oor) {
                printf("ShapeMorph::densityConnector() out of range!\n");
                printf("fnVec.size: %lu\n",fnVec.size());
                printf("BestIdx: %d\n",bestIdx);
                exit(1);
            }
        }
        //connect nearest neighbors
        double b = fxThresh;
        double a = pow(-coeff*log(1.0-q)/(3.14159 * b),0.5);
        Mat result = src.clone();
        Mat temp = src.clone();
        row=0; col=0;
        a = round(a) + 1;
        //if(*max_element(src.begin<uchar>(),src.end<uchar>())==163) {
        //cout << a << endl;
        //a = 7;
        //}
        double cutLength = a;
    
        Pathfind pf;
        while(row<src.rows) {
            while(col<src.cols) {
                int lc = src.at<uchar>(row,col);
                bool isDisconnected = false;
                if(lc>0) {
                    if((row-1>=0 and result.at<uchar>(row-1,col)==0) || (row+1<src.rows and result.at<uchar>(row+1,col)==0)) {
                        //> going vertical down
                        double length = 0.0;
                        vector<Point> seed_vec;
                        bool leftCheck=false, rightCheck=false;
                        for(int i=row-1; i<(row+a+1); i++) {
                            if(temp.at<uchar>(i,col-1)>0) {
                                length++;
                            }
                            if(col-1>=0) {
                                if(temp.at<uchar>(i,col-1)>0 and leftCheck==false) {
                                    seed_vec.push_back(Point(col-1,i));
                                    leftCheck=true;
                                }
                            }
                            if(col+1<src.cols) {
                                if(temp.at<uchar>(i,col+1)>0 and rightCheck==false) {
                                    seed_vec.push_back(Point(col+1,i));
                                    rightCheck=true;
                                }
                            }
                        }
                        cutLength = min(a,length);
                        for(int i=row-1; i<(row+cutLength+1); i++) {
                            if(i<src.rows) {
                                temp.at<uchar>(i,col) = 0;
                            }
                        }
                        if(seed_vec.size()>1) {
                            Mat pathMap = pf.run(temp,seed_vec.at(0),seed_vec.at(1),8,50);
                            bool crossover = pf.isPathFound();
                            if(!crossover) {
                                result = temp.clone();
                                isDisconnected = true;
                            } else {
                                temp = result.clone();
                            }
                        } else {
                            temp = result.clone();
                        }
                    }
                    if(!isDisconnected) {
                        if((col-1>=0 and result.at<uchar>(row,col-1)==0) || (col+1<src.cols and result.at<uchar>(row,col+1)==0)) {
                            //> going horizontal right
                            double length = 0.0;
                            vector<Point> seed_vec2;
                            bool topCheck=false, bottomCheck=false;
                            for(int j=col-1; j<(col+a+1); j++) {
                                if(temp.at<uchar>(row-1,j)>0) {
                                    length++;
                                }
                                if(row-1>=0) {
                                    if(temp.at<uchar>(row-1,j)>0 and topCheck==false) {
                                        seed_vec2.push_back(Point(j,row-1));
                                        topCheck=true;
                                    }
                                }
                                if(row+1<src.rows) {
                                    if(temp.at<uchar>(row+1,j)>0 and bottomCheck==false) {
                                        seed_vec2.push_back(Point(j,row+1));
                                        bottomCheck=true;
                                    }
                                }
                            }
                            cutLength = min(a,length);
                            for(int j=col; j<(col+cutLength); j++) {
                                if(j<src.cols)
                                    temp.at<uchar>(row,j) = 0;
                            }
    
                            if(seed_vec2.size()>1) {
                                Mat pathMap2 = pf.run(temp,seed_vec2.at(0),seed_vec2.at(1),8,50);
                                bool crossover2 = pf.isPathFound();
                                if(!crossover2) {
                                    result = temp.clone();
                                } else {
                                    temp = result.clone();
                                }
                            } else {
                                temp = result.clone();
                            }
                        }
                    }
                }
                col++;
            }
            col=0;
            row++;
        }
        return result;
    }
    
    //! gets the black discs within a feature
    vector<Mat> ShapeMorph::liquidFeatureExtractionInverse(Mat src) {
        vector<vector<Point> > contours;
        vector<Vec4i> hierarchy;
        cv::findContours(src,contours,hierarchy, CV_RETR_TREE, CV_CHAIN_APPROX_NONE);
        vector<Mat> vecMat;
        for(unsigned int i=0; i< contours.size(); i++ ) {
            if(hierarchy.at(i)[3]>=0) {
                Mat drawing = Mat::zeros(src.size(),CV_8U);
                drawContours( drawing, contours, i, Scalar(255), CV_FILLED, 8, hierarchy, 0, Point() );
                vecMat.push_back(drawing);
            }
        }
        return vecMat;
    }
    

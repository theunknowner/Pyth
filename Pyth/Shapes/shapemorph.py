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

class ShapeMorph:
    debugMode = False

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
    def isFeatureLighter(self, src, map):
        imgGray = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
        lumGap = 8 # absolute thresh for the eye
        countLighter = 0
        countDarker = 0
        for i in range(0, imgGray.shape[0]):
            count = 0
            start = False
            for(int j=0; j<imgGray.cols; j++) {
                if(map.at<uchar>(i,j)>0) {
                    int lc = imgGray.at<uchar>(i,j);
                    if(lc>0 && !start) {
                        start = true;
                        j++;
                    }
                    if(start && j<imgGray.cols) {
                        lc = imgGray.at<uchar>(i,j);
                        if(lc>0) {
                            int lc0 = imgGray.at<uchar>(i,j-1);
                            if((lc-lc0)>lumGap) {
                                countLighter++;
                                count++;
                            } else if((lc0-lc)>lumGap) {
                                countDarker++;
                                count++;
                            }
                        }
                    }
                    if(count>=10) break;
                }
            } // end j
        }// end i
        if(countLighter>countDarker) return true;
    
        return false;
    }
    
    //! filter curve on original grayscale image
    Mat ShapeMorph::origFilter(Mat src, double shift) {
        KneeCurve kc;
        Poly poly;
        Mat img = this->prepareImage(src);
        //removing stuff on edge
        Mat mapEdgeRemoval = this->removeNoiseOnBoundary(img);
    
        // get lum values
        Mat afterRemoval;
        img.copyTo(afterRemoval,mapEdgeRemoval);
        //imgshow(afterRemoval);
        vector<double> yVec;
        for(int i=0; i<afterRemoval.rows; i++) {
            for(int j=0; j<afterRemoval.cols; j++) {
                double lum = afterRemoval.at<uchar>(i,j);
                if(lum>5) {
                    yVec.push_back(lum);
                }
            }
        }
        //filter the remaining image after removal of noise and outliers
        kc.removeOutliers(yVec,0.025);
        //writeSeq2File(yVec,"yVec");
        vector<double> xVec;
        for(unsigned int i=0; i<yVec.size(); i++) {
            xVec.push_back((double)i);
        }
        vector<double> p = poly.polyfit(xVec,yVec,1);
        vector<double> y1 = poly.polyval(p,xVec);
        //MSE
        double sum=0;
        for(unsigned int i=0; i<y1.size(); i++) {
            double val = (yVec.at(i)-y1.at(i))/yVec.at(i);
            val = pow(val,2);
            sum += val;
        }
        sum = sqrt(sum);
        if(sum<2.5)
            yVec.erase(yVec.begin(),yVec.begin()+(yVec.size()/2));
    
        int bestIdx = kc.kneeCurvePoint(yVec);
        bestIdx *= shift;
        double thresh = yVec.at(bestIdx);
        //cout << bestIdx << endl;
        //cout << thresh << endl;
        Mat result=afterRemoval.clone();
        for(int i=0; i<afterRemoval.rows; i++) {
            for(int j=0; j<afterRemoval.cols; j++) {
                double lum = afterRemoval.at<uchar>(i,j);
                if(lum<thresh)
                    result.at<uchar>(i,j) = 0;
            }
        }
        return result;
    }
    
    //! filter using close(Img) - Img
    Mat ShapeMorph::closeFilter(Mat src, Size elementSize, double shift) {
        KneeCurve kc;
        //Poly poly;
        Mat img;
        Mat element = getStructuringElement(MORPH_RECT,elementSize);
        morphologyEx(src,img,MORPH_CLOSE,element);
        Mat img2 = img - src;
    
        //get darkest area from Close(img)-img
        vector<double> yVec1;
        for(int i=0; i<img.rows; i++) {
            for(int j=0; j<img.cols; j++) {
                double lum = img2.at<uchar>(i,j);
                if(lum>5)
                    yVec1.push_back(lum);
            }
        }
        kc.removeOutliers(yVec1,0.025);
        int bestIdx = kc.kneeCurvePoint(yVec1);
        double thresh = yVec1.at(bestIdx);
        Mat _img2=img2.clone();
        for(int i=0; i<img2.rows; i++) {
            for(int j=0; j<img2.cols; j++) {
                double lum = img2.at<uchar>(i,j);
                if(lum<thresh)
                    _img2.at<uchar>(i,j) = 0;
            }
        }
    
        //edge removal for Close(img)-img Only
        Mat mapEdgeRemoval(img2.rows,img2.cols,CV_8U,Scalar(255));
        Size size(5,5);
        Mat window1, window2;
        int row=0, col=0, colLimit=img2.cols;
        while(row<img2.rows) {
            Size _size = size;
            if(row>15 || (img2.rows-row)>15) colLimit = 15;
            while(col<=colLimit) {
                window1 = _img2(Rect(col+_size.width,row,_size.width,_size.height));
                window2 = _img2(Rect(col,row,_size.width,_size.height));
                double avg1=0, avg2=0;
                int count1=0, count2=0;
                for(int i=0; i<window1.rows; i++) {
                    for(int j=0; j<window1.cols; j++) {
                        double val1 = window1.at<uchar>(i,j);
                        double val2 = window2.at<uchar>(i,j);
                        if(val1>5.0) {
                            avg1 += val1;
                            count1++;
                        }
                        if(val2>5.0) {
                            avg2 += val2;
                            count2++;
                        }
                    }
                }
                avg1 /= count1;
                avg2 /= count2;
                if((avg1-avg2)<=-16.0) {
                    for(int i=row; i<(row+window2.rows); i++) {
                        for(int j=col; j<(col+window2.cols); j++) {
                            mapEdgeRemoval.at<uchar>(i,j) = 0;
                        }
                    }
                }
                col++;
            }
            col=0;
            row+=size.height;
        }
        Mat img3;
        img2.copyTo(img3,mapEdgeRemoval);
        //knee of curve filtering after edge removal
        vector<double> yVec2;
        for(int i=0; i<img3.rows; i++) {
            for(int j=0; j<img3.cols; j++) {
                double lum = img3.at<uchar>(i,j);
                if(lum>5)
                    yVec2.push_back(lum);
            }
        }
        kc.removeOutliers(yVec2,0.025);
        bestIdx = kc.kneeCurvePoint(yVec2);
        bestIdx *= shift;
        thresh = yVec2.at(bestIdx);
        Mat result=img3.clone();
        for(int i=0; i<img3.rows; i++) {
            for(int j=0; j<img3.cols; j++) {
                double lum = img3.at<uchar>(i,j);
                if(lum<thresh)
                    result.at<uchar>(i,j) = 0;
            }
        }
        return result;
    }
    
    //! using origFilter
    //! returns islands/features into vector
    vector<Mat> ShapeMorph::lumFilter1(Mat src, int featuresToHold) {
        Mat img1 = this->origFilter(src);
        Mat img2 = this->densityConnector(img1,0.9);
        vector<Mat> featureVec = this->liquidFeatureExtraction(img2);
    
        //remove features clinging to image boundary
        unsigned int m=0;
        while(m<featureVec.size()) {
            Mat edges(img2.size(),CV_8U,Scalar(0));
            vector<vector<Point> > contour = this->findBoundary(featureVec.at(m).clone());
            drawContours(edges,contour,-1,Scalar(255));
            int count = this->countEdgeTouching(edges,10,15);
            int total = countNonZero(edges);
            double percent = (double)count/total;
            int featurePixCount = countNonZero(featureVec.at(m));
            int imagePixCount = countNonZero(img2);
            double percentOfImage = (double)featurePixCount/imagePixCount;
            //printf("%d/%d: %f, %f\n",count,total,percent,percentOfImage);
            //imgshow(edges);
            if(percent>=0.47 && percentOfImage<0.40) {
                featureVec.erase(featureVec.begin()+m);
            }
            else
                m++;
        }
    
        int countPix=0, idx=0;
        deque<int> countVec;
        deque<int> idxVec;
        for(unsigned int i=0; i<featureVec.size(); i++) {
            countPix = countNonZero(featureVec.at(i));
            idx = i;
            countVec.push_back(countPix);
        }
        jaysort(countVec,idxVec);
        Mat result;
        vector<Mat> matVec;
        Mat element = getStructuringElement(MORPH_RECT,Size(3,3));
        unsigned int n=1;
        while(true) {
            try {
                morphologyEx(featureVec.at(idxVec.at(idxVec.size()-n)),result,MORPH_CLOSE,element);
                matVec.push_back(result.clone());
                //imwrite("img"+toString(n)+".png",matVec.at(matVec.size()-1));
                n++;
                if(matVec.size()>=featuresToHold) break;
                if(n>idxVec.size()) break;
            }
            catch(const std::out_of_range &oor) {
                printf("Catch #1: ShapeMorph::lumFilter1() out of range!\n");
                printf("n: %d\n", n);
                printf("featureVec.size() = %lu\n",featureVec.size());
                printf("idxVec.size() = %lu\n", idxVec.size());
                exit(1);
            }
        }
        return matVec;
    }
    
    //! using closeFilter
    //! returns islands/features into vector
    vector<Mat> ShapeMorph::lumFilter2(Mat src, int featuresToHold) {
        Mat img1 = this->closeFilter(src,Size(17,17));
        Mat img2 = this->densityConnector(img1,0.9);
        vector<Mat> featureVec = this->liquidFeatureExtraction(img2);
        int countPix=0, idx=0;
        deque<int> countVec;
        deque<int> idxVec;
        //sorts the features from largest to smallest
        for(unsigned int i=0; i<featureVec.size(); i++) {
            countPix = countNonZero(featureVec.at(i));
            idx = i;
            countVec.push_back(countPix);
        }
        jaysort(countVec,idxVec);
        Mat result;
        vector<Mat> matVec;
        Mat element = getStructuringElement(MORPH_RECT,Size(3,3));
        unsigned int n=1;
        while(true) {
            try {
                morphologyEx(featureVec.at(idxVec.at(idxVec.size()-n)),result,MORPH_CLOSE,element);
                matVec.push_back(result.clone());
                //imgshow(matVec.at(matVec.size()-1));
                //imwrite("img"+toString(n)+".png",matVec.at(matVec.size()-1));
                n++;
                if(matVec.size()>=featuresToHold) break;
                if(n>idxVec.size()) break;
            }
            catch(const std::out_of_range &oor) {
                printf("Catch #1: ShapeMorph::lumFilter2() out of range!\n");
                printf("n: %d\n", n);
                printf("featureVec.size() = %lu\n",featureVec.size());
                printf("idxVec.size() = %lu\n", idxVec.size());
                exit(1);
            }
        }
        return matVec;
    }
    
    //! shape={MORPH_RECT, MORPH_ELLIPSE, MORPH_CROSS}
    Mat ShapeMorph::dilation(Mat src, Size size, int shape, Point anchor) {
        /*
        Mat dst = Mat::zeros(src.rows,src.cols, CV_8U);
        Functions fn;
        int row=0, col=0, lum=0;
        int max_rows = src.rows - size.height;
        int max_cols = src.cols - size.width;
        while(row<=max_rows) {
            while(col<=max_cols) {
                Mat window = src(Rect(col,row,size.width,size.height));
                lum = fn.getMax(window);
                dst.at<uchar>(row+size.height-1,col) = lum;
                col++;
            }
            col=0;
            row++;
        }*/
        Mat result;
        Mat element = getStructuringElement(shape,size,anchor);
        dilate(src,result,element,anchor);
        return result;
    }
    
    //! shape={MORPH_RECT, MORPH_ELLIPSE, MORPH_CROSS}
    Mat ShapeMorph::erosion(Mat src, Size size, int shape, Point anchor) {
        /*
        Mat results = Mat::zeros(src.rows,src.cols, src.type());
        Functions fn;
        int row=0, col=0, lum=0;
        int max_rows = src.rows - size.height;
        int max_cols = src.cols - size.width;
        while(row<=max_rows) {
            while(col<=max_cols) {
                Mat window = src(Rect(col,row,size.width,size.height));
                lum = fn.getMin(window);
                results.at<uchar>(row+size.height-1,col) = lum;
                col++;
            }
            col=0;
            row++;
        }
        dst = results;*/
        Mat results;
        Mat element = getStructuringElement(shape,size,anchor);
        erode(src,results,element,anchor);
        return results;
    }
    
    Mat ShapeMorph::getStructElem(Size size, int shape) {
        Mat result = Mat::zeros(size,CV_8U);
        if(shape==CIRCLE) {
            circle(result,Point((result.cols-1)/2,(result.rows-1)/2),round(size.width/2),Scalar(1),-1);
        }
        else if(shape==RECT) {
            rectangle(result,Point(0,0),Point(result.cols-1,result.rows-1),Scalar(1),-1);
        }
        return result;
    }
    
    Mat ShapeMorph::elementaryDilation(Mat origImg, Mat scaleImg) {
        Mat result = scaleImg.clone();
        for(int i=0; i<result.rows; i++) {
            for(int j=0; j<result.cols; j++) {
                if(j==0) {
                    int val = max(result.at<uchar>(i,j),result.at<uchar>(i,j+1));
                    val = min(val,(int)origImg.at<uchar>(i,j+1));
                    result.at<uchar>(i,j+1) = val;
                }
                else if(j==(scaleImg.cols-1)) {
                    int val = max(result.at<uchar>(i,j),result.at<uchar>(i,j-1));
                    val = min(val,(int)origImg.at<uchar>(i,j-1));
                    result.at<uchar>(i,j-1) = val;
                }
                else {
                    int val = max(result.at<uchar>(i,j),result.at<uchar>(i,j-1));
                    val = min(val,(int)origImg.at<uchar>(i,j-1));
                    result.at<uchar>(i,j-1) = val;
    
                    val = max(result.at<uchar>(i,j),result.at<uchar>(i,j+1));;
                    val = min(val,(int)origImg.at<uchar>(i,j+1));
                    result.at<uchar>(i,j+1) = val;
                }
            }
        }
        return result;
    }
    
    //Ands the two images/ Assigns min of two images
    Mat ShapeMorph::custAnd(Mat origImg, Mat scaleImg, Mat map) {
        deque<int> ptVec;
        Mat results(origImg.rows,origImg.cols, CV_8U, Scalar(0));
        if(!map.empty()) {
            int flag=0, rmin=0;
            for(int i=0; i<scaleImg.rows; i++) {
                for(int j=0; j<scaleImg.cols; j++) {
                    if(scaleImg.at<uchar>(i,j)>0) {
                        ptVec.push_back(j);
                    }
                }
                for(int j=0; j<scaleImg.cols; j++) {
                    if(flag==0) rmin = origImg.at<uchar>(i,j);
                    if(map.at<uchar>(i,j)==255) flag=1;
                    if(map.at<uchar>(i,j)==0) flag=0;
                    for(unsigned int k=0; k<ptVec.size(); k++) {
                        if(k<ptVec.size()-1) {
                            if(j==ptVec.at(k)) {
                                results.at<uchar>(i,j) = min(rmin,(int)origImg.at<uchar>(i,j));
                                break;
                            }
                            else if(j>ptVec.at(k) && j<ptVec.at(k+1)) {
                                if(flag==1) {
                                    results.at<uchar>(i,j) = min(rmin,(int)origImg.at<uchar>(i,j));
                                }
                                else {
                                    int val1 = origImg.at<uchar>(i,ptVec.at(k));
                                    int val2 = origImg.at<uchar>(i,ptVec.at(k+1));
                                    int val = origImg.at<uchar>(i,j);
                                    rmin = max(val1,val2);
                                    results.at<uchar>(i,j) = min(rmin,val);
                                }
                                break;
                            }
                            else if(j<ptVec.at(k)) {
                                if(flag==1) {
                                    results.at<uchar>(i,j) = min(rmin,(int)origImg.at<uchar>(i,j));
                                }
                                else {
                                    int val1 = origImg.at<uchar>(i,ptVec.at(k));
                                    int val = origImg.at<uchar>(i,j);
                                    rmin = val1;
                                    results.at<uchar>(i,j) = min(val1,val);
                                }
                                break;
                            }
                        }
                        else {
                            if(j>ptVec.at(k)) {
                                if(flag==1) {
                                    results.at<uchar>(i,j) = min(rmin,(int)origImg.at<uchar>(i,j));
                                }
                                else {
                                    int val1 = origImg.at<uchar>(i,ptVec.at(k));
                                    int val = origImg.at<uchar>(i,j);
                                    rmin=val1;
                                    results.at<uchar>(i,j) = min(val1,val);
                                }
                                break;
                            }
                        }
                    }
                }
                ptVec.clear();
            }// end for row i
        }
        else {
            for(int i=0; i<scaleImg.rows; i++) {
                for(int j=0; j<scaleImg.cols; j++) {
                    if(scaleImg.at<uchar>(i,j)>0) {
                        ptVec.push_back(j);
                    }
                }
                for(int j=0; j<scaleImg.cols; j++) {
                    for(unsigned int k=0; k<ptVec.size(); k++) {
                        if(k<ptVec.size()-1) {
                            if(j==ptVec.at(k)) {
                                scaleImg.at<uchar>(i,j) = origImg.at<uchar>(i,j);
                                break;
                            }
                            else if(j>ptVec.at(k) && j<ptVec.at(k+1)) {
                                int val1 = origImg.at<uchar>(i,ptVec.at(k));
                                int val2 = origImg.at<uchar>(i,ptVec.at(k+1));
                                int val = origImg.at<uchar>(i,j);
                                results.at<uchar>(i,j) = min(max(val1,val2),val);
                                break;
                            }
                            else if(j<ptVec.at(k)) {
                                int val1 = origImg.at<uchar>(i,ptVec.at(k));
                                int val = origImg.at<uchar>(i,j);
                                results.at<uchar>(i,j) = min(val1,val);
                                break;
                            }
                        }
                        else {
                            if(j>ptVec.at(k)) {
                                int val1 = origImg.at<uchar>(i,ptVec.at(k));
                                int val = origImg.at<uchar>(i,j);
                                results.at<uchar>(i,j) = min(val1,val);
                                break;
                            }
                        }
                    }
                }
                ptVec.clear();
            }// end for row i
        }
        return results;
    }
    
    Mat ShapeMorph::grayscaleReconstruct(Mat src, Mat scaleImg) {
        Mat _scaleImg = scaleImg.clone();
        Mat tempImg;
        Mat compareMat = Mat::zeros(src.rows,src.cols,CV_8U);
        while(true) {
            tempImg = this->elementaryDilation(src,_scaleImg);
            compareMat = _scaleImg==tempImg;
            if(countNonZero(compareMat)==src.total()) break;
            _scaleImg = tempImg.clone();
        }
        Mat result = src - tempImg;
        return result;
    }
    
    Mat ShapeMorph::custGrayscaleRecon(Mat src) {
        Mat scaleImg = src.clone()-1;
        Mat rmins = this->grayscaleReconstruct(src,scaleImg);
        Mat _src = 255 - src; //invert image for LC values
        Mat mask = custAnd(_src,rmins);
        Mat result = this->grayscaleReconstruct(_src,mask);
        return result;
    }
    
    Mat ShapeMorph::gsReconUsingRmin1(Mat src) {
        Mat scaleImg = src.clone()-1;
        Mat rmins = this->grayscaleReconstruct(src,scaleImg);
        Mat _src = 255 - src; //invert image for LC values
        Mat mask = custAnd(_src,rmins);
        Mat gsr = this->grayscaleReconstruct(_src,mask);
        Mat map = this->customFn(gsr);
        mask = this->custAnd(_src,rmins,map);
        Mat result = this->grayscaleReconstruct(_src,mask);
        return result;
    }
    
    Mat ShapeMorph::gsReconUsingRmin2(Mat src) {
        Mat scaleImg = src.clone()-1;
        Mat rmins = this->grayscaleReconstruct(src,scaleImg);
        Mat _src = 255 - src; //invert image for LC values
        Mat map = this->customFn2(_src);
        Mat mask = custAnd(_src,rmins,map);
        Mat result = this->grayscaleReconstruct(_src,mask);
        return result;
    }
    
    //thresh = discernible thresh; set sort = -1;1 -> Ascending;Descending
    vector<Mat> ShapeMorph::liquidFeatureExtraction(Mat src, double lcThresh, int sort,int numOfPtsThresh) {
        Mat map(src.rows, src.cols, CV_8U, Scalar(0));
        deque<deque<Point> > numFeatures;
        deque<Point> ptVec;
        deque<Point> temp;
        int row=0, col=0;
        while(row<src.rows) {
            while(col<src.cols) {
                if(src.at<uchar>(row,col)>0 && map.at<uchar>(row,col)==0) {
                    ptVec.push_back(Point(col,row));
                    map.at<uchar>(row,col) = 255;
                    temp.push_back(Point(col,row));
                    while(temp.size()>0) {
                        Point up(temp.at(0).x,temp.at(0).y-1);
                        Point left(temp.at(0).x-1,temp.at(0).y);
                        Point right(temp.at(0).x+1,temp.at(0).y);
                        Point down(temp.at(0).x,temp.at(0).y+1);
                        Point downLeft(temp.at(0).x-1,temp.at(0).y+1);
                        Point downRight(temp.at(0).x+1,temp.at(0).y+1);
                        if(up.y>=0) {
                            if(map.at<uchar>(up)==0 && src.at<uchar>(up)>lcThresh) {
                                ptVec.push_back(up);
                                map.at<uchar>(up)=255;
                                temp.push_back(up);
                            }
                        }
                        if(left.x>=0) {
                            if(map.at<uchar>(left)==0 && src.at<uchar>(left)>lcThresh) {
                                ptVec.push_back(left);
                                map.at<uchar>(left)=255;
                                temp.push_back(left);
                            }
                        }
                        if(right.x<src.cols) {
                            if(map.at<uchar>(right)==0 && src.at<uchar>(right)>lcThresh) {
                                ptVec.push_back(right);
                                map.at<uchar>(right)=255;
                                temp.push_back(right);
                            }
                        }
                        if(down.y<src.rows) {
                            if(map.at<uchar>(down)==0 && src.at<uchar>(down)>lcThresh) {
                                ptVec.push_back(down);
                                map.at<uchar>(down)=255;
                                temp.push_back(down);
                            }
                        }
                        if(down.y<src.rows && left.x>=0) {
                            if(map.at<uchar>(downLeft)==0 && src.at<uchar>(downLeft)>lcThresh) {
                                ptVec.push_back(downLeft);
                                map.at<uchar>(downLeft)=255;
                                temp.push_back(downLeft);
                            }
                        }
                        if(down.y<src.rows && right.x<src.cols) {
                            if(map.at<uchar>(downRight)==0 && src.at<uchar>(downRight)>lcThresh) {
                                ptVec.push_back(downRight);
                                map.at<uchar>(downRight)=255;
                                temp.push_back(downRight);
                            }
                        }
                        temp.pop_front();
                    }
                    numFeatures.push_back(ptVec);
                    ptVec.clear();
                    temp.clear();
                }
                col++;
            }//end while col
            col=0;
            row++;
        }//end while row
    
        vector<Mat> featureVec;
        for(unsigned int i=0; i<numFeatures.size(); i++) {
            Mat feature(src.rows, src.cols, CV_8U,Scalar(0));
            if(numFeatures.at(i).size()>=numOfPtsThresh) {
                for(unsigned int j=0; j<numFeatures.at(i).size(); j++) {
                    feature.at<uchar>(numFeatures.at(i).at(j)) = src.at<uchar>(numFeatures.at(i).at(j));
                }
                featureVec.push_back(feature);
            }
        }
        if(sort==1) {
            int countPix, idx;
            deque<int> countVec;
            deque<int> idxVec;
            vector<Mat> tempVec;
            for(unsigned int i=0; i<featureVec.size(); i++) {
                countPix = countNonZero(featureVec.at(i));
                idx = i;
                countVec.push_back(countPix);
            }
            jaysort(countVec,idxVec);
            for(int i=idxVec.size()-1; i>=0; --i) {
                try {
                    tempVec.push_back(featureVec.at(idxVec.at(i)));
                } catch(const std::out_of_range &oor) {
                    printf("idxVec.size(): %lu\n",idxVec.size());
                    printf("featureVec.size(): %lu\n",featureVec.size());
                    printf("i:%d\n",i);
                    printf("idx:%d\n",idxVec.at(i));
                    exit(1);
                }
            }
            featureVec = tempVec;
        }
        if(sort==-1) {
            int countPix, idx;
            deque<int> countVec;
            deque<int> idxVec;
            vector<Mat> tempVec;
            for(unsigned int i=0; i<featureVec.size(); i++) {
                countPix = countNonZero(featureVec.at(i));
                idx = i;
                countVec.push_back(countPix);
            }
            jaysort(countVec,idxVec);
            for(unsigned int i=0; i<idxVec.size(); i++) {
                try {
                    tempVec.push_back(featureVec.at(idxVec.at(i)));
                } catch(const std::out_of_range &oor) {
                    printf("idxVec.size(): %lu\n",idxVec.size());
                    printf("featureVec.size(): %lu\n",featureVec.size());
                    printf("i:%d\n",i);
                    printf("idx:%d\n",idxVec.at(i));
                    exit(1);
                }
            }
            featureVec = tempVec;
        }
        return featureVec;
    }
    
    //thresh = discernible thresh; set sort = -1;1 -> Descending;Ascending
    vector<ImageData> ShapeMorph::liquidFeatureExtraction(ImageData &id, double lcThresh, int sort,int numOfPtsThresh) {
        Mat src = id.image();
        Mat map(src.rows, src.cols, CV_8U, Scalar(0));
        deque<deque<Point> > numFeatures;
        deque<Point> ptVec;
        deque<Point> temp;
        int row=0, col=0;
        while(row<src.rows) {
            while(col<src.cols) {
                if(src.at<uchar>(row,col)>0 && map.at<uchar>(row,col)==0) {
                    ptVec.push_back(Point(col,row));
                    map.at<uchar>(row,col) = 255;
                    temp.push_back(Point(col,row));
                    while(temp.size()>0) {
                        Point up(temp.at(0).x,temp.at(0).y-1);
                        Point left(temp.at(0).x-1,temp.at(0).y);
                        Point right(temp.at(0).x+1,temp.at(0).y);
                        Point down(temp.at(0).x,temp.at(0).y+1);
                        Point downLeft(temp.at(0).x-1,temp.at(0).y+1);
                        Point downRight(temp.at(0).x+1,temp.at(0).y+1);
                        if(up.y>=0) {
                            if(map.at<uchar>(up)==0 && src.at<uchar>(up)>lcThresh) {
                                ptVec.push_back(up);
                                map.at<uchar>(up)=255;
                                temp.push_back(up);
                            }
                        }
                        if(left.x>=0) {
                            if(map.at<uchar>(left)==0 && src.at<uchar>(left)>lcThresh) {
                                ptVec.push_back(left);
                                map.at<uchar>(left)=255;
                                temp.push_back(left);
                            }
                        }
                        if(right.x<src.cols) {
                            if(map.at<uchar>(right)==0 && src.at<uchar>(right)>lcThresh) {
                                ptVec.push_back(right);
                                map.at<uchar>(right)=255;
                                temp.push_back(right);
                            }
                        }
                        if(down.y<src.rows) {
                            if(map.at<uchar>(down)==0 && src.at<uchar>(down)>lcThresh) {
                                ptVec.push_back(down);
                                map.at<uchar>(down)=255;
                                temp.push_back(down);
                            }
                        }
                        if(down.y<src.rows && left.x>=0) {
                            if(map.at<uchar>(downLeft)==0 && src.at<uchar>(downLeft)>lcThresh) {
                                ptVec.push_back(downLeft);
                                map.at<uchar>(downLeft)=255;
                                temp.push_back(downLeft);
                            }
                        }
                        if(down.y<src.rows && right.x<src.cols) {
                            if(map.at<uchar>(downRight)==0 && src.at<uchar>(downRight)>lcThresh) {
                                ptVec.push_back(downRight);
                                map.at<uchar>(downRight)=255;
                                temp.push_back(downRight);
                            }
                        }
                        temp.pop_front();
                    }
                    numFeatures.push_back(ptVec);
                    ptVec.clear();
                    temp.clear();
                }
                col++;
            }//end while col
            col=0;
            row++;
        }//end while row
    
        vector<ImageData> featureVec;
        for(unsigned int i=0; i<numFeatures.size(); i++) {
            Mat feature(src.rows, src.cols, CV_8U,Scalar(0));
            if(numFeatures.at(i).size()>=numOfPtsThresh) {
                for(unsigned int j=0; j<numFeatures.at(i).size(); j++) {
                    feature.at<uchar>(numFeatures.at(i).at(j)) = src.at<uchar>(numFeatures.at(i).at(j));
                }
                ImageData id(feature,"",0);
                featureVec.push_back(id);
            }
        }
        if(sort==1) {
            int countPix, idx;
            deque<int> countVec;
            deque<int> idxVec;
            vector<ImageData> tempVec;
            for(unsigned int i=0; i<featureVec.size(); i++) {
                countPix = countNonZero(featureVec.at(i).image());
                idx = i;
                countVec.push_back(countPix);
            }
            jaysort(countVec,idxVec);
            for(int i=idxVec.size()-1; i>=0; --i) {
                try {
                    tempVec.push_back(featureVec.at(idxVec.at(i)));
                } catch(const std::out_of_range &oor) {
                    printf("idxVec.size(): %lu\n",idxVec.size());
                    printf("featureVec.size(): %lu\n",featureVec.size());
                    printf("i:%d\n",i);
                    printf("idx:%d\n",idxVec.at(i));
                    exit(1);
                }
            }
            featureVec = tempVec;
        }
        if(sort==-1) {
            int countPix, idx;
            deque<int> countVec;
            deque<int> idxVec;
            vector<ImageData> tempVec;
            for(unsigned int i=0; i<featureVec.size(); i++) {
                countPix = countNonZero(featureVec.at(i).image());
                idx = i;
                countVec.push_back(countPix);
            }
            jaysort(countVec,idxVec);
            for(unsigned int i=0; i<idxVec.size(); i++) {
                try {
                    tempVec.push_back(featureVec.at(idxVec.at(i)));
                } catch(const std::out_of_range &oor) {
                    printf("idxVec.size(): %lu\n",idxVec.size());
                    printf("featureVec.size(): %lu\n",featureVec.size());
                    printf("i:%d\n",i);
                    printf("idx:%d\n",idxVec.at(i));
                    exit(1);
                }
            }
            featureVec = tempVec;
        }
        return featureVec;
    }
    
    vector<Mat> ShapeMorph::filterFeatures(vector<Mat> featureVec) {
        vector<Mat> results;
        vector<double> lcVec;
        double lcThresh = 100.0;
        int pixelCountThresh = 30;
        for(unsigned int n=0; n<featureVec.size(); n++) {
            double avgLC=0;
            int countPix = countNonZero(featureVec.at(n));
            for(int i=0; i<featureVec.at(n).rows; i++) {
                for(int j=0; j<featureVec.at(n).cols; j++) {
                    avgLC += featureVec.at(n).at<uchar>(i,j);
                }
            }
            avgLC /= countPix;
            if(countPix>=pixelCountThresh && avgLC>lcThresh) {
                results.push_back(featureVec.at(n));
            }
        }
        return results;
    }
    
    
    //filters noise and connects shape of image
    Mat ShapeMorph::filterNoise(Mat src, int radius) {
        int threshCount = 25;
        int threshQuadrant = 18;
        Mat results = src.clone();
        int dist = (radius*2)+1;
        Size size(dist,dist);
        int pixels_top=0, pixels_bottom=0, pixels_left=0, pixels_right=0;
        int pixelsTL=0, pixelsTR=0, pixelsBL=0, pixelsBR=0;
        Point begin;
        Mat window = Mat::zeros(size.height, size.width, CV_8U);
        int row=0, col=0;
        while(row<src.rows) {
            while(col<src.cols) {
                int flagTL=0, flagTR=0, flagBL=0, flagBR=0;
                int flagL=0, flagR=0, flagT=0, flagB=0;
                window = Mat::zeros(size.height, size.width, CV_8U);
                begin = Point(col-floor(size.width/2),row-floor(size.height/2));
                for(int i=0; i<size.height; i++) {
                    for(int j=0; j<size.width; j++) {
                        if(i+begin.y>=0 && j+begin.x>=0)
                            window.at<uchar>(i,j) = src.at<uchar>(i+begin.y,j+begin.x);
                    }
                }
                Mat roiTL = window(Rect(0,0,ceil(size.width/2.),ceil(size.height/2.)));
                Mat roiTR = window(Rect(floor(size.width/2.),0,ceil(size.width/2.),ceil(size.height/2.)));
                Mat roiBL = window(Rect(0,floor(size.height/2.),ceil(size.width/2.),ceil(size.height/2.)));
                Mat roiBR = window(Rect(floor(size.width/2.),floor(size.height/2.),ceil(size.width/2.),ceil(size.height/2)));
                pixelsTL = countNonZero(roiTL);
                pixelsTR = countNonZero(roiTR);
                pixelsBL = countNonZero(roiBL);
                pixelsBR = countNonZero(roiBR);
                pixels_top = pixelsTL + pixelsTR;
                pixels_bottom = pixelsBL + pixelsBR;
                pixels_left = pixelsTL + pixelsBL;
                pixels_right = pixelsTR + pixelsBR;
                //int totalPix = pixels_top+pixels_bottom;
                //debug printf info
                /*
                if(col==66 && row==47) {
                    printf("TL: %d\n",pixelsTL);
                    printf("TR: %d\n",pixelsTR);
                    printf("BL: %d\n",pixelsBL);
                    printf("BR: %d\n",pixelsBR);
                    printf("Left: %d\n",pixels_left);
                    printf("Right: %d\n",pixels_right);
                    printf("Top: %d\n",pixels_top);
                    printf("Bottom: %d\n",pixels_bottom);
                    printf("Total: %d\n",totalPix);
                    //namedWindow("roi",CV_WINDOW_FREERATIO | CV_GUI_EXPANDED);
                    //imshow("roi",window);
                    //waitKey(0);
                }
                 */
                if(pixelsTL>=threshQuadrant) flagTL=1;
                if(pixelsTR>=threshQuadrant) flagTR=1;
                if(pixelsBL>=threshQuadrant) flagBL=1;
                if(pixelsBR>=threshQuadrant) flagBR=1;
                if(pixels_left>=threshCount) flagL=1;
                if(pixels_right>=threshCount) flagR=1;
                if(pixels_top>=threshCount) flagT=1;
                if(pixels_bottom>=threshCount) flagB=1;
    
                if((flagL+flagR+flagT+flagB<=2)&&(flagTL+flagTR+flagBL+flagBR<=2)) {
                    results.at<uchar>(row,col) = 0;
                }
                col++;
            }
            col=0;
            row++;
        }
        //imfill(results);
        return results;
    }
    
    //draw a line from point to every point after
    Mat ShapeMorph::connectImage(Mat src, Size size, double dist) {
        Mat results = src.clone();
        deque<Point> ptVec;
        int row=0, col=0;
        while(row<src.rows) {
            while(col<src.cols) {
                for(int i=row; i<(row+size.height); i++) {
                    for(int j=col; j<(col+size.width); j++) {
                        if((i<src.rows && j<src.cols))
                            if(results.at<uchar>(i,j)>0)
                                ptVec.push_back(Point(j,i));
                    }
                }
                for(unsigned int i=0; i<ptVec.size(); i++) {
                    for(unsigned int j=i; j<ptVec.size(); j++) {
                        if(MyMath::eucDist(ptVec.at(i),ptVec.at(j))<dist) {
                            line(results,ptVec.at(i),ptVec.at(j),Scalar(255));
                        }
                    }
                }
                ptVec.clear();
                col+=(int)dist;
            }
            col=0;
            row+=(int)dist;
        }
        return results;
    }
    
    //returns luminance based heat map using Point density
    Mat ShapeMorph::detectHeat(Mat src, Size size) {
        float sensitivity = 0.08; //weight of each point with D distance
        Mat kernel = Mat::zeros(size.height, size.width,CV_32F);
        Point origin(floor(size.width/2),floor(size.height/2));
        for(int i=0; i<kernel.rows; i++) {
            for(int j=0; j<kernel.cols; j++) {
                double dist = MyMath::eucDist(Point(i,j),origin);
                double weight = 1.0 - (dist*sensitivity);
                kernel.at<float>(i,j) = weight;
            }
        }
        int row=0, col=0;
        Point begin;
        Mat heatMap = Mat::zeros(src.rows,src.cols,CV_32F);
        double total=0;
        while(row<src.rows) {
            while(col<src.cols) {
                begin = Point(col-floor(size.width/2),row-floor(size.height/2));
                for(int i=0; i<kernel.rows; i++) {
                    for(int j=0; j<kernel.cols; j++) {
                        int x = j+begin.x;
                        int y = i+begin.y;
                        if(y>=0 && x>=0 && y<src.rows && x<src.cols) {
                            if(src.at<uchar>(y,x)>5)
                                total += kernel.at<float>(i,j);
                        }
                    }
                }
                heatMap.at<float>(row,col) = total/kernel.total();
                total=0;
                col++;
            }
            col=0;
            row++;
        }
        Mat results(heatMap.rows, heatMap.cols, CV_8U,Scalar(0));
        for(int i=0; i<heatMap.rows; i++) {
            for(int j=0; j<heatMap.cols; j++) {
                int value = round(heatMap.at<float>(i,j) * 255);
                if(value>25 && src.at<uchar>(i,j)>0)
                    results.at<uchar>(i,j) = 255;
            }
        }
        return results;
    }
    
    //returns mask using kmeans clustering of LC values
    Mat ShapeMorph::kmeansClusterLC(Mat src) {
        static unsigned int defaultSeed = theRNG().state;
        theRNG().state = defaultSeed; //reset RNG seed for kmeans initial centroids
    
        deque<int> dataVec;
        deque<int> uniqueLum(256,0);
        deque<int> lumVec;
        deque<Point> ptVec;
        for(int i=0; i<src.rows; i++) {
            for(int j=0; j<src.cols; j++) {
                int lum = src.at<uchar>(i,j);
                if(lum>0) {
                    dataVec.push_back(lum);
                    uniqueLum.at(lum)++;
                    ptVec.push_back(Point(j,i));
                }
            }
        }
        for(unsigned int i=0; i<uniqueLum.size(); i++) {
            if(uniqueLum.at(i)>0) {
                lumVec.push_back(i);
            }
        }
        Mat samples(dataVec.size(), 1, CV_32F);
        for(unsigned int i=0; i<dataVec.size(); i++) {
            samples.at<float>(i,0) = dataVec.at(i);
        }
        int lumRange = lumVec.at(lumVec.size()-1) - lumVec.at(0);
        int clusterCount = round(sqrt(lumRange/2))<lumVec.size() ? round(sqrt(lumRange/2)) : lumVec.size();
        clusterCount = min(11,clusterCount);
        Mat labels;
        int attempts = 5;
        Mat centers;
        printf("Min Lum: %d, Max Lum: %d, Range: %d\n",lumVec.at(0),lumVec.at(lumVec.size()-1), lumRange);
        cout << "Initial clusters: " << clusterCount << endl;
        cout << "Input size: " << dataVec.size() << endl;
        cout << "Unique Lum size: " << uniqueLum.size() << endl;
        cout << "Unique Lum considered: " << lumVec.size() << endl;
        double compact = kmeans(samples,clusterCount,labels,TermCriteria(CV_TERMCRIT_ITER|CV_TERMCRIT_EPS, 10000, 0.0001), attempts, KMEANS_PP_CENTERS, centers);
        //cout << "compactness: " << compact << endl;
        deque<int> centerCount(clusterCount,0);
        deque<deque<int> > ranges(clusterCount,deque<int>(2,0));
        for(unsigned int i=0; i<ranges.size(); i++) {
            for(unsigned int j=0; j<ranges.at(i).size(); j++) {
                if(j==0) {
                    ranges.at(i).at(j) = uniqueLum.size();
                }
                else if(j==1) {
                    ranges.at(i).at(j) = 0;
                }
            }
        }
        Mat origPos;
        jaysort(centers,origPos);
        for(int i=0; i<labels.rows; i++) {
            int idx = labels.at<int>(i,0);
            for(int j=0; j<origPos.rows; j++) {
                if(idx==origPos.at<int>(j,0)) {
                    idx = j;
                    labels.at<int>(i,0) = idx;
                    break;
                }
            }
            centerCount.at(idx)++;
            if(dataVec.at(i)>ranges.at(idx).at(1)) {
                ranges.at(idx).at(1) = dataVec.at(i);
            }
            else if(dataVec.at(i)<ranges.at(idx).at(0)) {
                ranges.at(idx).at(0) = dataVec.at(i);
            }
        }
        for(int i=0; i<centers.rows; i++) {
            printf("%d) %f - %d - Min: %d, Max: %d\n",i,centers.at<float>(i,0),centerCount.at(i),ranges.at(i).at(0),ranges.at(i).at(1));
        }
        Mat result = Mat::zeros(src.rows, src.cols, src.type());
        Mat clusterImg = Mat::zeros(src.rows,src.cols,CV_8UC3);
        int idxThresh = ceil(clusterCount*0.5); //! threshold for cluster filtering
        printf("idxThresh: %d\n",idxThresh);
        for(unsigned int i=0; i<ptVec.size(); i++) {
            int idx = labels.at<int>(i,0);
            if(idx>idxThresh) {
                result.at<uchar>(ptVec.at(i).y,ptVec.at(i).x) = 255;
            }
        }
        return result;
    }
    
    Mat ShapeMorph::kmeansClusterPt(Mat src) {
        deque<Point> dataVec;
        for(int i=0; i<src.rows; i++) {
            for(int j=0; j<src.cols; j++) {
                int lum = src.at<uchar>(i,j);
                if(lum>0) {
                    dataVec.push_back(Point(j,i));
                }
            }
        }
        Mat samples(dataVec.size(), 2, CV_32F);
        for(unsigned int i=0; i<dataVec.size(); i++) {
            samples.at<float>(i,0) = dataVec.at(i).x;
            samples.at<float>(i,1) = dataVec.at(i).y;
        }
        //int clusterCount = round(sqrt(dataVec.size()/2));
        int clusterCount = round(sqrt(src.cols/2));
        //int clusterCount = 4;
        Mat labels;
        int attempts = 1;
        Mat centers;
        int compact = kmeans(samples,clusterCount,labels,TermCriteria(CV_TERMCRIT_ITER|CV_TERMCRIT_EPS, 10000, 0.0001), attempts, KMEANS_PP_CENTERS, centers);
        cout << "Initial clusters: " << clusterCount << endl;
        cout << "Input size: " << dataVec.size() << endl;
        cout << "compactness: " << compact << endl;
        deque<int> centerCount(clusterCount,0);
        deque<deque<Point> > ranges(clusterCount,deque<Point>(2,Point(-1,-1)));
        for(unsigned int i=0; i<ranges.size(); i++) {
            for(unsigned int j=0; j<ranges.at(i).size(); j++) {
                if(j==0) {
                    ranges.at(i).at(j) = Point(src.cols,src.rows);
                }
                else if(j==1) {
                    ranges.at(i).at(j) = Point(-1,-1);
                }
            }
        }
        Mat origPos;
        jaysort(centers,origPos);
        for(int i=0; i<labels.rows; i++) {
            int idx = labels.at<int>(i,0);
            for(int j=0; j<origPos.rows; j++) {
                if(idx==origPos.at<int>(j,0)) {
                    idx = j;
                    labels.at<int>(i,0) = idx;
                    break;
                }
            }
            centerCount.at(idx)++;
            /*if(dataVec.at(i)>ranges.at(idx).at(1)) {
                ranges.at(idx).at(1) = dataVec.at(i);
            }
            else if(dataVec.at(i)<ranges.at(idx).at(0)) {
                ranges.at(idx).at(0) = dataVec.at(i);
            }*/
        }
    
        for(int i=0; i<centers.rows; i++) {
            printf("%f,%f - %d - Min: (%d,%d), Max: (%d,%d)\n",centers.at<float>(i,0),centers.at<float>(i,1),centerCount.at(i),ranges.at(i).at(0).x,ranges.at(i).at(0).y,ranges.at(i).at(1).x,ranges.at(i).at(1).y);
        }
        Mat result = Mat::zeros(src.rows, src.cols, CV_8U);
        Mat clusterImg = Mat::zeros(src.rows,src.cols,CV_8UC3);
        int idxThresh = ceil(clusterCount*0.5); //! threshold for cluster filtering
        RNG rng;
        vector<Vec3b> colorVec;
        for(int i=0; i<centers.rows; i++) {
            Vec3b color(rng.uniform(0,255),rng.uniform(0,255),rng.uniform(0,255));
            colorVec.push_back(color);
        }
        for(unsigned int i=0; i<dataVec.size(); i++) {
            int idx = labels.at<int>(i,0);
            //if(idx>idxThresh) {
            clusterImg.at<Vec3b>(dataVec.at(i).y,dataVec.at(i).x) = colorVec.at(idx);
            //printf("%d,%d - %d\n",dataVec.at(i).x,dataVec.at(i).y, idx);
            //}
        }
        return clusterImg;
    }
    
    //! entry/exit map of edges
    Mat ShapeMorph::customFn(Mat src) {
        Mat map(src.rows, src.cols, CV_8U, Scalar(0));
        Size size(5,5);
        const int minLCThresh = 5;
        const double minDNThresh = round(size.area() * 0.15);
        double enterDKThresh = 0.6;
        double enterDNThresh = 3.5;
        double exitDKThresh = 0.6;
        double exitDNThresh = 3.5;
        int entryFlag=0;
        double totalDK=0, totalDN=0;
        double avgDK=0, density=0;
        double dkRatio=0, dnRatio=0;
        double cumulativeDK=0, cumulativeDN=0;
        int row=0, col=0;
        int countDK=0;
        Point begin;
        Mat drkMat(src.rows,src.cols,CV_32F,Scalar(0));
        Mat dnMat(src.rows,src.cols,CV_32F,Scalar(0));
        while(row<src.rows) {
            while(col<src.cols) {
                begin=Point(col-floor(size.width/2),row-floor(size.height/2));
                for(int i=begin.y; i<(begin.y+size.height); i++) {
                    for(int j=begin.x; j<(begin.x+size.width); j++) {
                        if(j>=0 && i>=0 && j<src.cols && i<src.rows) {
                            if(src.at<uchar>(i,j)>minLCThresh) {
                                totalDK += src.at<uchar>(i,j);
                                countDK++;
                            }
                            if(src.at<uchar>(i,j)>minLCThresh)
                                totalDN++;
                        }
                    }
                }
                avgDK = totalDK/countDK;
                if(countDK==0) avgDK=0;
                density = totalDN/size.area();
                drkMat.at<float>(row,col) = avgDK;
                dnMat.at<float>(row,col) = density;
                if(col>0 && drkMat.at<float>(row,col-1)>minLCThresh && totalDN>minDNThresh) {
                    dkRatio = drkMat.at<float>(row,col)/drkMat.at<float>(row,col-1);
                    dnRatio = dnMat.at<float>(row,col)/dnMat.at<float>(row,col-1);
                    cumulativeDK += dkRatio - 1.0;
                    cumulativeDN += dnRatio - 1.0;
                    /*if(row==36) {
                        //printf("DK: %d,%d: %.f, %d, %f\n",col,row,totalDK,countDK,avgDK);
                        printf("DK: %d,%d: %f,%f,%f,%f,  ",col,row,drkMat.at<float>(row,col-1),drkMat.at<float>(row,col),dkRatio,cumulativeDK);
                        printf("DN: %d,%d: %f,%f,%f,%f\n",col,row,dnMat.at<float>(row,col-1),dnMat.at<float>(row,col),dnRatio,cumulativeDN);
                    }*/
                    if(cumulativeDK>=enterDKThresh || cumulativeDN>=enterDNThresh) {
                        entryFlag=1;
                    }
                    else if(cumulativeDK<=exitDKThresh || cumulativeDN<=exitDNThresh) {
                        entryFlag=0;
                    }
                    if(entryFlag==1)
                        map.at<uchar>(row,col) = 255;
                }
                totalDK=0;
                totalDN=0;
                countDK=0;
                col++;
            }
            cumulativeDK=0;
            cumulativeDN=0;
            col=0;
            row++;
        }
        return map;
    }
    
    //! returns entry/exit map of edges
    Mat ShapeMorph::customFn2(Mat src) {
        Mat map(src.rows, src.cols, CV_8U, Scalar(0));
        Size size(5,5);
        double enterDKThresh = 0.1;
        double exitDKThresh = 0.1;
        double enterDKThresh2 = 1.03;
        double exitDKThresh2 = 1.0;
        int entryFlag=0;
        double totalDK=0;
        double avgDK=0;
        double dkRatio=0;
        double cumulativeDK=0;
        int row=0, col=0;
        int countDK=0;
        Point begin;
        Mat drkMat(src.rows,src.cols,CV_32F,Scalar(0));
        Mat dnMat(src.rows,src.cols,CV_32F,Scalar(0));
        while(row<src.rows) {
            while(col<src.cols) {
                begin=Point(col-floor(size.width/2),row-floor(size.height/2));
                for(int i=begin.y; i<(begin.y+size.height); i++) {
                    for(int j=begin.x; j<(begin.x+size.width); j++) {
                        if(j>=0 && i>=0 && j<src.cols && i<src.rows) {
                            totalDK += src.at<uchar>(i,j);
                            countDK++;
                        }
                    }
                }
                avgDK = totalDK/countDK;
                if(countDK==0) avgDK=0;
                drkMat.at<float>(row,col) = avgDK;
                if(col>0) {
                    dkRatio = drkMat.at<float>(row,col)/drkMat.at<float>(row,col-1);
                    cumulativeDK += dkRatio - 1.0;
                    if(avgDK>=180)
                        entryFlag=1;
                    if(entryFlag==0 && avgDK<180) {
                        if(cumulativeDK>=enterDKThresh)
                            entryFlag=1;
                        if(dkRatio>=enterDKThresh2) {
                            entryFlag=1;
                            cumulativeDK=enterDKThresh;
                        }
                    }
                    if(entryFlag==1 && avgDK<180) {
                        if(cumulativeDK<exitDKThresh)
                            entryFlag=0;
                        if(dkRatio<exitDKThresh2) {
                            entryFlag=0;
                            cumulativeDK=0;
                        }
                    }
                    //if(row==37) {
                    //printf("DK: %d,%d: %.f, %d, %f\n",col,row,totalDK,countDK,avgDK);
                    //    printf("DK: %d,%d: %f,%f,%f,%f,  ",col,row,drkMat.at<float>(row,col-1),drkMat.at<float>(row,col),dkRatio,cumulativeDK);
                    //    printf("Flag: %d\n",entryFlag);
                    //}
                    if(entryFlag==1)
                        map.at<uchar>(row,col) = 255;
                }
                totalDK=0;
                countDK=0;
                col++;
            }
            cumulativeDK=0;
            col=0;
            row++;
        }
        return map;
    }
    
    //! Nearest neighbor connector base on density
    //! q = probability of connecting to a neighboring unit
    Mat ShapeMorph::densityConnector(Mat src, double q, double coeff, double increment) {
        //Mat map = src.clone();
        if(src.empty()) {
            printf("ShapeMorph::densityConnector() src is empty\n");
            printf("src.size: %dx%d\n",src.rows,src.cols);
            exit(1);
        }
        int lineVal = *max_element(src.begin<uchar>(),src.end<uchar>());
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
                        if(j>=0 && i>=0 && j<src.cols && i<src.rows) {
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
                float percent = ip::roundDecimal((float)bestIdx/fnVec.size(),2);
                if(percent<=0.05000001)
                    bestIdx = 0.25 * fnVec.size();
                if(percent>=0.8999999)
                    bestIdx = 0.75 * fnVec.size();
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
        double a = pow(-coeff*log(1.0-q)/(3.14159 * b),0.5) + increment;
        Mat result(src.rows,src.cols,CV_8U,Scalar(0));
        row=0; col=0;
        a = ceil(a);
        /*if(*max_element(src.begin<uchar>(),src.end<uchar>())==144 && countNonZero(src)>3000) {
            cout << a << endl;
            cout << b << endl;
        }*/
        Size square(a,a);
        while(row<src.rows) {
            while(col<src.cols) {
                int lc = src.at<uchar>(row,col);
                if(lc>0) {
                    Point begin = Point(col-square.width,row-square.height);
                    Point end = Point(col+square.width,row+square.height);
                    for(int i=begin.y; i<end.y; i++) {
                        for(int j=begin.x; j<end.x; j++) {
                            if(j>=0 && i>=0 && j<src.cols && i<src.rows) {
                                lc = src.at<uchar>(i,j);
                                //double dist = eucDist(Point(j,i),Point(col,row));
                                double dist = abs(j-col) + abs(i-row);
                                if(dist<=a && lc>absDiscernThresh) {
                                    if(Point(j,i)!=Point(col,row)) {
                                        line(result,Point(j,i),Point(col,row),Scalar(lineVal),1);
                                    }
                                }
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
    
    vector<vector<Point> > ShapeMorph::findBoundary(Mat src) {
        vector<vector<Point> > contour;
        findContours(src, contour, RETR_EXTERNAL, CV_CHAIN_APPROX_NONE);
        return contour;
    }
    
    //! for edges & corners of different sizes
    int ShapeMorph::countEdgeTouching(Mat src, int sideEdgeSize, int cornerEdgeSize) {
        Mat _src = src.clone();
        Mat topEdge = _src(Rect(cornerEdgeSize,0,src.cols-cornerEdgeSize*2,sideEdgeSize));
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
            if(percent>=0.47 && percentOfImage<0.15) {
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
                        if(y!=i && x!=j) {
                            if(x<0 || y<0 || x>=src.cols || y>=src.rows) {
                                flag = 1;
                            } else if(map.at<uchar>(y,x)==0) {
                                flag = 1;
                            }
                        }
                    }
                }
                if(val>thresh && HSL.at(2)<lumThresh && flag==1) {
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
                        if(j>=0 && i>=0 && j<src.cols && i<src.rows) {
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
                    if((row-1>=0 && result.at<uchar>(row-1,col)==0) || (row+1<src.rows && result.at<uchar>(row+1,col)==0)) {
                        //> going vertical down
                        double length = 0.0;
                        vector<Point> seed_vec;
                        bool leftCheck=false, rightCheck=false;
                        for(int i=row-1; i<(row+a+1); i++) {
                            if(temp.at<uchar>(i,col-1)>0) {
                                length++;
                            }
                            if(col-1>=0) {
                                if(temp.at<uchar>(i,col-1)>0 && leftCheck==false) {
                                    seed_vec.push_back(Point(col-1,i));
                                    leftCheck=true;
                                }
                            }
                            if(col+1<src.cols) {
                                if(temp.at<uchar>(i,col+1)>0 && rightCheck==false) {
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
                        if((col-1>=0 && result.at<uchar>(row,col-1)==0) || (col+1<src.cols && result.at<uchar>(row,col+1)==0)) {
                            //> going horizontal right
                            double length = 0.0;
                            vector<Point> seed_vec2;
                            bool topCheck=false, bottomCheck=false;
                            for(int j=col-1; j<(col+a+1); j++) {
                                if(temp.at<uchar>(row-1,j)>0) {
                                    length++;
                                }
                                if(row-1>=0) {
                                    if(temp.at<uchar>(row-1,j)>0 && topCheck==false) {
                                        seed_vec2.push_back(Point(j,row-1));
                                        topCheck=true;
                                    }
                                }
                                if(row+1<src.rows) {
                                    if(temp.at<uchar>(row+1,j)>0 && bottomCheck==false) {
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
    

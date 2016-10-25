
#include "rules.h"
#include "intensity.h"
#include "../functions.h"
#include "../FileData/filedata.h"
#include "../rgb/rgb.h"
#include "../hsl/hsl.h"
#include "../Color/color.h"
#include "../Shades/shades.h"
#include "../Algorithms/write.h"
#include "../Math/maths.h"

import traceback
import math
import numpy as np

from rgb import Rgb
from hsl import Hsl
from color import Color
from Shades.shades import Shades
from Mymath import mymath
import functions as fn

ruleCount = 11
ruleFlags = [1] * ruleCount

def rule1(fd, newShade):
    ''' general rule #1 - Shade Contrast with IndexChange'''
    flag = False
    ruleNum = 1.0
    c = Color()
    sh = Shades()
    localScanSize = 10
    indexChangeThresh = 2.25 #thresh for next shade level per indexChange
    pt = fd.pt
    ccCurr=0
    deg0CC = deg45CC = deg90CC=0
    deg0MinMaxVec = []
    deg45MinMaxVec = []
    deg90MinMaxVec = []

    if(pt[0]>0 and pt[1]>0):
        try:
            ccCurr = fd.smoothIntensityVec[pt[1]][pt[0]]
            j=pt[0]-1
            x = j
            endY = (pt[1]-localScanSize)
            #loops going outwards from start point(x,y)
            for i in range(pt[1]-1, endY-1, -1):
                if(x<0 and j<0 and i<0): break
                if(x>=0):
                    deg0CC = fd.smoothIntensityVec[pt[1]][x]
                    deg0MinMaxVec.append(deg0CC)
                x-=1
                if(j>=0 and i>=0):
                    deg45CC = fd.smoothIntensityVec[i][j]
                    deg45MinMaxVec.append(deg45CC)
                j-=1
                if(i>=0):
                    deg90CC = fd.smoothIntensityVec[i][pt[0]]
                    deg90MinMaxVec.append(deg90CC)
        except Exception:
            traceback.print_exc()
            print("Rule 1 out of range!")
            print("smoothIntensityVec.Size: {}".format(len(fd.smoothIntensityVec)))
            print("Point({},{})".format(fd.pt[0],fd.pt[1]))
            exit(1)

        deg0Index = deg45Index = deg90Index=0
        deg0Gradient = deg45Gradient = deg90Gradient=0
        deg0Gradient = ccCurr - deg0MinMaxVec[0]
        deg45Gradient = ccCurr - deg45MinMaxVec[0]
        deg90Gradient = ccCurr - deg90MinMaxVec[0]
        if(deg0Gradient<=0):
            deg0Index = deg0MinMaxVec.index(max(deg0MinMaxVec))
        else:
            deg0Index = deg0MinMaxVec.index(min(deg0MinMaxVec))
            
        if(deg45Gradient<=0):
            deg45Index = deg45MinMaxVec.index(max(deg45MinMaxVec))
        else:
            deg45Index = deg45MinMaxVec.index(min(deg45MinMaxVec))

        if(deg90Gradient<=0):
            deg90Index = deg90MinMaxVec.index(max(deg90MinMaxVec))
        else:
            deg90Index = deg90MinMaxVec.index(min(deg90MinMaxVec))

        try:
            deg0CC = deg0MinMaxVec[deg0Index]
            deg45CC = deg45MinMaxVec[deg45Index]
            deg90CC = deg90MinMaxVec[deg90Index]
        except Exception:
            traceback.print_exc()
            print("Rule 1 out of range!")
            print("Point({},{})".format(fd.pt[0],fd.pt[1]))
            print("deg0MinMaxVec.size(): {}; Index: {}".format(len(deg0MinMaxVec),deg0Index))
            print("deg45MinMaxVec.size(): {}; Index: {}".format(len(deg45MinMaxVec),deg45Index))
            print("deg90MinMaxVec.size(): {}; Index: {}".format(len(deg90MinMaxVec),deg90Index))
            exit(1)
        
        _range = fd.maxIntensity - fd.minIntensity
        newInterval = _range/fd.totalShades
        deg0IndexChange = mymath.myRound(ccCurr-deg0CC)/newInterval
        deg45IndexChange = mymath.myRound(ccCurr-deg45CC)/newInterval
        deg90IndexChange = mymath.myRound(ccCurr-deg90CC)/newInterval
        indexChange = max(deg0IndexChange, deg45IndexChange, deg90IndexChange)
        if(abs(indexChange)>=indexChangeThresh):
            index = sh.getShadeIndex(newShade)
            index += (indexChange/indexChangeThresh)
            newShade = sh.getShade(index)
            flag = True
            
    if(flag==True): return ruleNum, newShade

    return 0, newShade

def rule2(fd, newPix):
    ''' General rule #2 - Assigning Gray+Color '''
    ruleNum = 2
    flag = False
    hsl = Hsl()
    c = Color()
    rgb = Rgb()
    pThreshMove = 1.15
    index = -1
    hslStr = fd.hslMat[fd.pt[1]][fd.pt[0]].split(";")
    hue = float(hslStr[0])
    sat = float(hslStr[1])
    lum = float(hslStr[2])
    fSat = fSat2 = 0
    color, index = hsl.getHslColor(hue,sat,lum, index)
    grayLevel = rgb.getGrayLevel1(newPix)
    colorLevel = rgb.getColorLevel(newPix)
    try:
        fSat = (sat-Hsl.__satThresh__[index][1])
        fSat /= (Hsl.__satThresh__[index][1]-Hsl.__satThresh__[index][0])
        fSat *= pThreshMove
    except Exception:
        traceback.print_exc()
        print("Rule2: Index Out of bounds!")
        print("Point({},{})".format(fd.pt[0],fd.pt[1]))
        print("HSL({:.0f},{:.2f},{:.2f})".format(hue,sat,lum))
        exit(1)
    
    try:
        if((index-1)>=0):
            grey = Hsl.__hslColors__[index-1]
    except Exception:
        traceback.print_exc()
        print("Rule2: Index Out of bounds!")
        print("Index({}) out of bounds!",index-1)
        print("Point({},{})".format(fd.pt[0],fd.pt[1]))
        print("HSL({:.0f},{:.2f},{:.2f})".format(hue,sat,lum))
        exit(1)
    
    if not c.containsColor(color,"Grey","White","Black","Zero"):
        if(grey=="Grey"):
            fSat2 = sat - Hsl.__satThresh__[index-1][1]
            if(fSat<(-1) or fSat2<=0.02):
                newPix = str(grayLevel)+"Grey" + color+ str(colorLevel)
                flag = True

    if(flag==True): return ruleNum, newPix

    return 0, newPix

def rule3(fd, newPix, newShade):
    ''' rule#3 - contrast rule for Brown/BrownPink/Pink '''
    ruleNum = 3
    flag = False
    c = Color()
    rgb = Rgb()
    sh = Shades()
    pt = fd.pt
    pix=""
    grayLevel = rgb.getGrayLevel1(newPix)
    colorLevel = rgb.getColorLevel(newPix)
    localScanSize = 20
    color = c.getMainColor(newPix)
    HSL = [0] * 3
    try:
        hslStr = fd.hslMat[fd.pt[1]][fd.pt[0]].split(";")
        HSL[0] = float(hslStr[0])
        HSL[1] = float(hslStr[1])*100
        HSL[2] = float(hslStr[2])*100
    except Exception:
        traceback.print_exc()
        print("Rule3: Try/Catch #1 Out of Range!")
        print("fd.hslMat.size(): {}".format(len(fd.hslMat)))
        print("Point({},{})".format(pt[0],pt[1]))
    
    HSL[0] = int(HSL[0] - math.floor(HSL[0]/180.) * 360)
    HSL[1] = 100-HSL[1];
    currCumHSL = HSL[0] + HSL[1] + HSL[2]
    fd.cumHslMat[pt[1]][pt[0]] = currCumHSL
    HSL_0 = [ [0]*3 for i in range(2) ]
    HSL_45 = [ [0]*3 for i in range(2) ]
    HSL_90 = [ [0]*3 for i in range(2) ]
    hslPt_0 = [[0,0],[0,0]]
    hslPt_45 = [[0,0],[0,0]]
    hslPt_90 = [[0,0],[0,0]]
    unitThresh = [6.0, 5.0, 4.0]
    minMaxBucket0 = []
    minMaxBucket45 = []
    minMaxBucket90 = []
    minMaxBucketPts0 = []
    minMaxBucketPts45 = []
    minMaxBucketPts90 = []
    prevColor_0 = prevColor_45 = prevColor_90 = ""
    deltaHSL_0 = [ [0]*3 for i in range(2) ]
    deltaHSL_45 = [ [0]*3 for i in range(2) ]
    deltaHSL_90 = [ [0]*3 for i in range(2) ]
    measuredContrast_0 = [0,0]
    measuredContrast_45 = [0,0]
    measuredContrast_90 = [0,0]

    shade0 = shade45 = shade90 = ""
    shadeIndex0 = shadeIndex45 = shadeIndex90 = -1
    currShadeIndex = sh.getShadeIndex(newShade)
    flag0 = flag45 = flag90 = 0

    if((color=="BrownPink" or color=="Brown" or color=="BrownOrange") and HSL[0]<30 and pt[1]>0):
        j=pt[0]-1
        x = j
        endY = (pt[1]-localScanSize)
        for i in range(pt[1]-1,endY-1,-1):
            if(x<0 and j<0 and i<0): break
            currHSL = 0
            if(x>=0):
                hslStr = fd.hslMat[pt[1]][x].split(";")
                HSL_0[0][0] = float(hslStr[0])
                HSL_0[0][1] = float(hslStr[1])*100
                HSL_0[0][2] = float(hslStr[2])*100
                HSL_0[0][0] = int(HSL_0[0][0] - math.floor(HSL_0[0][0]/180.) * 360)
                HSL_0[0][1] = 100-HSL_0[0][1]
                currHSL = HSL_0[0][0] + HSL_0[0][1] + HSL_0[0][2]
                minMaxBucket0.append(currHSL)
                minMaxBucketPts0.append([x,pt[1]])
            x-=1
            if(j>=0 and i>=0):
                hslStr = fd.hslMat[i][j].split(";")
                HSL_45[0][0] = float(hslStr[0])
                HSL_45[0][1] = float(hslStr[1])*100
                HSL_45[0][2] = float(hslStr[2])*100
                HSL_45[0][0] = int(HSL_45[0][0] - math.floor(HSL_45[0][0]/180.) * 360)
                HSL_45[0][1] = 100-HSL_45[0][1]
                currHSL = HSL_45[0][0] + HSL_45[0][1] + HSL_45[0][2]
                minMaxBucket45.append(currHSL)
                minMaxBucketPts45.append([j,i])
            j-=1
            if(i>=0):
                hslStr = fd.hslMat[i][pt[0]].split(";")
                HSL_90[0][0] = float(hslStr[0])
                HSL_90[0][1] = float(hslStr[1])*100
                HSL_90[0][2] = float(hslStr[2])*100
                HSL_90[0][0] = int(HSL_90[0][0] - math.floor(HSL_90[0][0]/180.) * 360)
                HSL_90[0][1] = 100-HSL_90[0][1]
                currHSL = HSL_90[0][0] + HSL_90[0][1] + HSL_90[0][2]
                minMaxBucket90.append(currHSL)
                minMaxBucketPts90.append([pt[0],i]);

        minIndex = maxIndex=-1
        # getMin|getMax returns -1 when bucket is empty due to being at
        # col=0 or row=0
        val, minIndex = fn.getMin(minMaxBucket0)
        if(minIndex<0): hslPt_0[0] = [pt[0],pt[1]]
        else: hslPt_0[0] = minMaxBucketPts0[minIndex]
        
        val, minIndex = fn.getMin(minMaxBucket45)
        if(minIndex<0): hslPt_45[0] = [pt[0],pt[1]]
        else: hslPt_45[0] = minMaxBucketPts45[minIndex]

        val, minIndex = fn.getMin(minMaxBucket90)
        if(minIndex<0): hslPt_90[0] = [pt[0],pt[1]]
        else: hslPt_90[0] = minMaxBucketPts90[minIndex]

        val, maxIndex = fn.getMax(minMaxBucket0)
        if(maxIndex<0): hslPt_0[1] = [pt[0],pt[1]]
        else: hslPt_0[1] = minMaxBucketPts0[maxIndex]

        val, maxIndex = fn.getMax(minMaxBucket45)
        if(maxIndex<0): hslPt_45[1] = [pt[0],pt[1]]
        else: hslPt_45[1] = minMaxBucketPts45[maxIndex]

        val, maxIndex = fn.getMax(minMaxBucket90)
        if(maxIndex<0): hslPt_90[1] = [pt[0],pt[1]]
        else: hslPt_90[1] = minMaxBucketPts90[maxIndex]

        tempHSL_0 = [ [0]*3 for i in range(2) ]
        tempHSL_45 = [ [0]*3 for i in range(2) ]
        tempHSL_90 = [ [0]*3 for i in range(2) ]
        for i in range(0,2):
            hslStr0 = fd.hslMat[hslPt_0[i][1]][hslPt_0[i][0]].split(";")
            hslStr45 = fd.hslMat[hslPt_45[i][1]][hslPt_45[i][0]].split(";")
            hslStr90 = fd.hslMat[hslPt_90[i][1]][hslPt_90[i][0]].split(";")
            for j in range(0,3):
                tempHSL_0[i][j] = hslStr0[j]
                tempHSL_45[i][j] = hslStr45[j]
                tempHSL_90[i][j] = hslStr90[j]
                if(j==0):
                    HSL_0[i][j] = int(tempHSL_0[i][j] - math.floor(tempHSL_0[i][j]/180.) * 360)
                    HSL_45[i][j] = int(tempHSL_45[i][j] - math.floor(tempHSL_45[i][j]/180.) * 360)
                    HSL_90[i][j] = int(tempHSL_90[i][j] - math.floor(tempHSL_90[i][j]/180.) * 360)
                if(j==1):
                    HSL_0[i][j] = round(100-(tempHSL_0[i][j]*100))
                    HSL_45[i][j] = round(100-(tempHSL_45[i][j]*100))
                    HSL_90[i][j] = round(100-(tempHSL_90[i][j]*100))
                if(j==2):
                    HSL_0[i][j] = round(tempHSL_0[i][j]*100)
                    HSL_45[i][j] = round(tempHSL_45[i][j]*100)
                    HSL_90[i][j] = round(tempHSL_90[i][j]*100)
                    
                deltaHSL_0[i][j] = HSL[j] - HSL_0[i][j]
                deltaHSL_45[i][j] = HSL[j]- HSL_45[i][j]
                deltaHSL_90[i][j] = HSL[j] - HSL_90[i][j]
                measuredContrast_0[i] += (deltaHSL_0[i][j]/unitThresh[j])
                measuredContrast_45[i] += (deltaHSL_45[i][j]/unitThresh[j])
                measuredContrast_90[i] += (deltaHSL_90[i][j]/unitThresh[j])
                
        #entering pink
        if(fn.countLesser(-2,measuredContrast_0[1],measuredContrast_45[1],measuredContrast_90[1])>=2):
            if(HSL[1]<=70):
                if(fn.countGreater(0,round(abs(deltaHSL_0[1][0]/unitThresh[0])),round(abs(deltaHSL_45[1][0]/unitThresh[0])),round(abs(deltaHSL_90[1][0]/unitThresh[0])))>=2):
                    if(color=="Brown"): pix="BrownPink"
                    if(color=="BrownOrange"): pix="BrownPink"
                    if(color=="BrownPink"): pix = "Pink"
                    flag=True
                    ruleNum = 3.1
            elif(HSL[1]<=78):
                if(fn.countLesser(-10,deltaHSL_0[1][0],deltaHSL_45[1][0],deltaHSL_90[1][0])>=2):
                    if(color=="Brown"): pix="BrownPink"
                    if(color=="BrownOrange"): pix="BrownPink"
                    if(color=="BrownPink"): pix = "Pink"
                    flag=True
                    ruleNum = 3.12
  
        #in Pink/BrownPink
        if(fn.countGreaterEqual(-2,measuredContrast_0[1],measuredContrast_45[1],measuredContrast_90[1])>=2 and 
           fn.countLesserEqual(2,measuredContrast_0[1],measuredContrast_45[1],measuredContrast_90[1])>=2):
            if(fn.countLesser(1,measuredContrast_0[0],measuredContrast_45[0],measuredContrast_90[0])>=2):
                if(HSL[1]<=70):
                    prevColor_0 = c.getMainColor(fd.colorVec[hslPt_0[1][1]][hslPt_0[1][0]])
                    prevColor_45 = c.getMainColor(fd.colorVec[hslPt_45[1][1]][hslPt_45[1][0]])
                    prevColor_90 = c.getMainColor(fd.colorVec[hslPt_90[1][1]][hslPt_90[1][0]])
                    if(fn.countEqual("Pink",prevColor_0.c_str(),prevColor_45.c_str(),prevColor_90.c_str())>=2):
                        if(color=="Brown"): pix="BrownPink"
                        if(color=="BrownOrange"): pix="BrownPink"
                        if(color=="BrownPink"): pix = "Pink"
                        flag=True
                        ruleNum = 3.2
                    elif(fn.countEqual("BrownPink",prevColor_0.c_str(),prevColor_45.c_str(),prevColor_90.c_str())>=2):
                        shade0 = c.extractShade(fd.colorVec[hslPt_0[1][1]][hslPt_0[1][0]])
                        shade45 = c.extractShade(fd.colorVec[hslPt_45[1][1]][hslPt_45[1][0]])
                        shade90 = c.extractShade(fd.colorVec[hslPt_90[1][1]][hslPt_90[1][0]])
                        shadeIndex0 = sh.getShadeIndex(shade0)
                        shadeIndex45 = sh.getShadeIndex(shade45)
                        shadeIndex90 = sh.getShadeIndex(shade90)
                        if((shadeIndex0-currShadeIndex)>=1 and (shadeIndex0-currShadeIndex)<=2): flag0=1
                        if((shadeIndex45-currShadeIndex)>=1 and (shadeIndex45-currShadeIndex)<=2): flag45=1
                        if((shadeIndex90-currShadeIndex)>=1 and (shadeIndex90-currShadeIndex)<=2): flag90=1
                        if(fn.countEqual(1,flag0,flag45,flag90)>=2):
                            if(fn.countLesserEqual(-3,deltaHSL_0[1][0],deltaHSL_45[1][0],deltaHSL_90[1][0])>=2):
                                if(color=="Brown"): pix="BrownPink"
                                if(color=="BrownOrange"): pix="BrownPink"
                                if(color=="BrownPink"): pix = "Pink"
                                flag=True
                                ruleNum = 3.21
                else:
                    ratioDeltaHSL0 = [0] * 3
                    ratioDeltaHSL45 = [0] * 3
                    ratioDeltaHSL90 = [0] * 3
                    ratioDeltaFlag = [0] * 3
                    for a in range(0,3):
                        ratioDeltaHSL0[a] = round(abs(deltaHSL_0[0][a]/unitThresh[a]))
                        ratioDeltaHSL45[a] = round(abs(deltaHSL_45[0][a]/unitThresh[a]))
                        ratioDeltaHSL90[a] = round(abs(deltaHSL_90[0][a]/unitThresh[a]))
                        ratioDeltaFlag[a] = fn.countEqual(0,ratioDeltaHSL0[a],ratioDeltaHSL45[a],ratioDeltaHSL90[a])
                    if(fn.countGreaterEqual(2,ratioDeltaFlag[0],ratioDeltaFlag[1],ratioDeltaFlag[2])>=2):
                        if(color=="Brown"): pix="BrownPink"
                        if(color=="BrownOrange"): pix="BrownPink"
                        if(color=="BrownPink"): pix = "Pink"
                        flag=True
                        ruleNum = 3.22

        strCon = "("+str(measuredContrast_0[0])+";"+str(measuredContrast_0[1])+")"
        strCon += "("+str(measuredContrast_45[0])+";"+str(measuredContrast_45[1])+")"
        strCon += "("+str(measuredContrast_90[0])+";"+str(measuredContrast_90[1])+")"
        fd.m_ContrastMat[pt[1]][pt[0]] = strCon
        strHsl = "Min("+str(deltaHSL_0[0][0])+";"+str(deltaHSL_0[0][1])+";"+str(deltaHSL_0[0][2])+")"
        strHsl += ";("+str(deltaHSL_45[0][0])+";"+str(deltaHSL_45[0][1])+";"+str(deltaHSL_45[0][2])+")"
        strHsl += ";("+str(deltaHSL_90[0][0])+";"+str(deltaHSL_90[0][1])+";"+str(deltaHSL_90[0][2])+")"
        strHsl += "Max("+str(deltaHSL_0[1][0])+";"+str(deltaHSL_0[1][1])+";"+str(deltaHSL_0[1][2])+")"
        strHsl += ";("+str(deltaHSL_45[1][0])+";"+str(deltaHSL_45[1][1])+";"+str(deltaHSL_45[1][2])+")"
        strHsl += ";("+str(deltaHSL_90[1][0])+";"+str(deltaHSL_90[1][1])+";"+str(deltaHSL_90[1][2])+")"
        fd.d_HslMat[pt[1]][pt[0]] = strHsl
        ptStr = "Min({};{});({};{});({};{})".format(hslPt_0[0][0],hslPt_0[0][1],hslPt_45[0][0],hslPt_45[0][1],hslPt_90[0][0],hslPt_90[0][1])
        ptStr2 = "Max({};{});({};{});({};{})".format(hslPt_0[1][0],hslPt_0[1][1],hslPt_45[1][0],hslPt_45[1][1],hslPt_90[1][0],hslPt_90[1][1])
        ptStr += ptStr2
        fd.hslPtMat[pt[1]][pt[0]] = ptStr
        minMaxHslStr = "Min("+fd.hslMat[hslPt_0[0][1]][hslPt_0[0][0]]+")"
        minMaxHslStr += ";("+fd.hslMat[hslPt_45[0][1]][hslPt_45[0][0]]+")"
        minMaxHslStr += ";("+fd.hslMat[hslPt_90[0][1]][hslPt_90[0][0]]+")"
        minMaxHslStr += "Max("+fd.hslMat[hslPt_0[1][1]][hslPt_0[1][0]]+")"
        minMaxHslStr += ";("+fd.hslMat[hslPt_45[1][1]][hslPt_45[1][0]]+")"
        minMaxHslStr += ";("+fd.hslMat[hslPt_90[1][1]][hslPt_90[1][0]]+")"
        fd.minMaxHslMat[pt[1]][pt[0]] = minMaxHslStr
    # end if(brownpink)

    elif(color=="Pink" and HSL[0]<30 and pt[1]>0):
        j=pt[0]-1
        x = j
        endY = (pt[1]-localScanSize)
        for i in range(pt[1]-1, endY-1, -1):
            if(x<0 and j<0 and i<0): break
            currI = 0
            if(x>=0):
                currI = fd.smoothIntensityVec[pt[1]][x]
                minMaxBucket0.append(currI)
                minMaxBucketPts0.append([x,pt[1]])
            x-=1
            if(j>=0 and i>=0):
                currI = fd.smoothIntensityVec[i][j]
                minMaxBucket45.append(currI)
                minMaxBucketPts45.append([j,i])
            j-=1
            if(i>=0):
                currI = fd.smoothIntensityVec[i][pt.x]
                minMaxBucket90.append(currI)
                minMaxBucketPts90.append([pt.x,i])
        maxIndex=-1
        # getMin|getMax returns -1 when bucket is empty due to being at
        # col=0 or row=0
        val, maxIndex = fn.getMax(minMaxBucket0)
        if(maxIndex<0): hslPt_0[1] = [pt[0],pt[1]]
        else: hslPt_0[1] = minMaxBucketPts0[maxIndex]

        val, maxIndex = fn.getMax(minMaxBucket45)
        if(maxIndex<0): hslPt_45[1] = [pt[0],pt[1]]
        else: hslPt_45[1] = minMaxBucketPts45[maxIndex]

        val, maxIndex = fn.getMax(minMaxBucket90)
        if(maxIndex<0): hslPt_90[1] = [pt[0],pt[1]]
        else: hslPt_90[1] = minMaxBucketPts90[maxIndex]

        hslPt_0[0] = [pt[0],pt[1]]
        hslPt_45[0] = [pt[0],pt[1]]
        hslPt_90[0] = [pt[0],pt[1]]

        tempHSL_0 = [ [0]*3 for i in range(2) ]
        tempHSL_45 = [ [0]*3 for i in range(2) ]
        tempHSL_90 = [ [0]*3 for i in range(2) ]
        for i in range(0,2):
            for j in range(0,3):
                hslStr0 = fd.hslMat[hslPt_0[i][1]][hslPt_0[i][0]].split(";")
                hslStr45 = fd.hslMat[hslPt_45[i][1]][hslPt_45[i][0]].split(";")
                hslStr90 = fd.hslMat[hslPt_90[i][1]][hslPt_90[i][0]].split(";")
                tempHSL_0[i][j] = hslStr0[j]
                tempHSL_45[i][j] = hslStr45[j]
                tempHSL_90[i][j] = hslStr90[j]
                if(j==0):
                    HSL_0[i][j] = int(tempHSL_0[i][j] - math.floor(tempHSL_0[i][j]/180.) * 360)
                    HSL_45[i][j] = int(tempHSL_45[i][j] - math.floor(tempHSL_45[i][j]/180.) * 360)
                    HSL_90[i][j] = int(tempHSL_90[i][j] - math.floor(tempHSL_90[i][j]/180.) * 360)
                if(j==1):
                    HSL_0[i][j] = round(100-(tempHSL_0[i][j]*100))
                    HSL_45[i][j] = round(100-(tempHSL_45[i][j]*100))
                    HSL_90[i][j] = round(100-(tempHSL_90[i][j]*100))
                if(j==2):
                    HSL_0[i][j] = round(tempHSL_0[i][j]*100)
                    HSL_45[i][j] = round(tempHSL_45[i][j]*100)
                    HSL_90[i][j] = round(tempHSL_90[i][j]*100)
                deltaHSL_0[i][j] = HSL[j] - HSL_0[i][j]
                deltaHSL_45[i][j] = HSL[j]- HSL_45[i][j]
                deltaHSL_90[i][j] = HSL[j] - HSL_90[i][j]
                measuredContrast_0[i] += (deltaHSL_0[i][j]/unitThresh[j])
                measuredContrast_45[i] += (deltaHSL_45[i][j]/unitThresh[j])
                measuredContrast_90[i] += (deltaHSL_90[i][j]/unitThresh[j])

        prevColor_0 = c.getMainColor(fd.windowVec[hslPt_0[1][1]][hslPt_0[1][0]])
        prevColor_45 = c.getMainColor(fd.windowVec[hslPt_45[1][1]][hslPt_45[1][0]])
        prevColor_90 = c.getMainColor(fd.windowVec[hslPt_90[1][1]][hslPt_90[1][0]])

        thresh = 20

        if(prevColor_0=="Pink"):
            shade0 = c.extractShade(fd.colorVec[hslPt_0[1][1]][hslPt_0[1][0]])
            shadeIndex0 = sh.getShadeIndex(shade0)
            if((shadeIndex0-currShadeIndex)>1 and (shadeIndex0-currShadeIndex)<3 and abs(deltaHSL_0[1][1])<=thresh): flag0=1
        if(prevColor_45=="Pink"):
            shade45 = c.extractShade(fd.colorVec[hslPt_45[1][1]][hslPt_45[1][0]])
            shadeIndex45 = sh.getShadeIndex(shade45)
            if((shadeIndex45-currShadeIndex)>1 and (shadeIndex45-currShadeIndex)<3 and abs(deltaHSL_45[1][1])<=thresh): flag45=1
        if(prevColor_90=="Pink"):
            shade90 = c.extractShade(fd.colorVec[hslPt_90[1][1]][hslPt_90[1][0]])
            shadeIndex90 = sh.getShadeIndex(shade90)
            if((shadeIndex90-currShadeIndex)>1 and (shadeIndex90-currShadeIndex)<3 and abs(deltaHSL_90[1][1])<=thresh): flag90=1

        if(fn.countEqual(1,flag0,flag45,flag90)>=2):
            pix = "PinkRed"
            flag=True
            ruleNum = 3.3

        strCon = "("+str(measuredContrast_0[0])+";"+str(measuredContrast_0[1])+")"
        strCon += "("+str(measuredContrast_45[0])+";"+str(measuredContrast_45[1])+")"
        strCon += "("+str(measuredContrast_90[0])+";"+str(measuredContrast_90[1])+")"
        fd.m_ContrastMat[pt[1]][pt[0]] = strCon
        strHsl = "Min("+str(deltaHSL_0[0][0])+";"+str(deltaHSL_0[0][1])+";"+str(deltaHSL_0[0][2])+")"
        strHsl += ";("+str(deltaHSL_45[0][0])+";"+str(deltaHSL_45[0][1])+";"+str(deltaHSL_45[0][2])+")"
        strHsl += ";("+str(deltaHSL_90[0][0])+";"+str(deltaHSL_90[0][1])+";"+str(deltaHSL_90[0][2])+")"
        strHsl += "Max("+str(deltaHSL_0[1][0])+";"+str(deltaHSL_0[1][1])+";"+str(deltaHSL_0[1][2])+")"
        strHsl += ";("+str(deltaHSL_45[1][0])+";"+str(deltaHSL_45[1][1])+";"+str(deltaHSL_45[1][2])+")"
        strHsl += ";("+str(deltaHSL_90[1][0])+";"+str(deltaHSL_90[1][1])+";"+str(deltaHSL_90[1][2])+")"
        fd.d_HslMat[pt[1]][pt[0]] = strHsl
        ptStr = "Min({};{});({};{});({};{})".format(hslPt_0[0][0],hslPt_0[0][1],hslPt_45[0][0],hslPt_45[0][1],hslPt_90[0][0],hslPt_90[0][1])
        ptStr2 = "Max({};{});({};{});({};{})".format(hslPt_0[1][0],hslPt_0[1][1],hslPt_45[1][0],hslPt_45[1][1],hslPt_90[1][0],hslPt_90[1][1])
        ptStr += ptStr2
        fd.hslPtMat[pt[1]][pt[0]] = ptStr
        minMaxHslStr = "Min("+fd.hslMat[hslPt_0[0][1]][hslPt_0[0][0]]+")"
        minMaxHslStr += ";("+fd.hslMat[hslPt_45[0][1]][hslPt_45[0][0]]+")"
        minMaxHslStr += ";("+fd.hslMat[hslPt_90[0][1]][hslPt_90[0][0]]+")"
        minMaxHslStr += "Max("+fd.hslMat[hslPt_0[1][1]][hslPt_0[1][0]]+")"
        minMaxHslStr += ";("+fd.hslMat[hslPt_45[1][1]][hslPt_45[1][0]]+")"
        minMaxHslStr += ";("+fd.hslMat[hslPt_90[1][1]][hslPt_90[1][0]]+")"
        fd.minMaxHslMat[pt[1]][pt[0]] = minMaxHslStr

        '''
        else if(color.find("Purple")==string::npos && color.find("Violet")==string::npos && HSL[1]>=75 && pt.y>0) {
            int colorCount0=0, colorCount45=0, colorCount90=0;
            flag0=0;flag45=0;flag90=0;
            int currHSL0[3]={0},currHSL45[3]={0},currHSL90[3]={0};
            int deltaHSL0[3]={0},deltaHSL45[3]={0},deltaHSL90[3]={0};
            String origColor0,origColor45,origColor90;
            int j=pt.x-1;
            int x = j;
            int endY = (pt.y-localScanSize);
            for(int i=(pt.y-1); i>=endY; i--) {
                if(x<0 && j<0 && i<0) break;
                if(x>=0) {
                    prevColor_0 = c.getMainColor(fd.colorVec.at(pt.y).at(x));
                    currHSL0[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(pt.y).at(x),';',1);
                    currHSL0[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(pt.y).at(x),';',3)*100;
                    currHSL0[0] = (int)(currHSL0[0] - floor(currHSL0[0]/180.) * 360);
                    deltaHSL0[0] = abs(HSL[0]-currHSL0[0]);
                    deltaHSL0[2] = abs(HSL[2]-currHSL0[2]);
                    if(deltaHSL0[0]<10 && deltaHSL0[2]<=8 && (prevColor_0.find("Violet")!=string::npos || prevColor_0.find("Purple")!=string::npos)) {
                        ++colorCount0;
                    }
                }
                if(j>=0 && i>=0) {
                    prevColor_45 = c.getMainColor(fd.colorVec.at(i).at(j));
                    currHSL45[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',1);
                    currHSL45[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',3)*100;
                    currHSL45[0] = (int)(currHSL45[0] - floor(currHSL45[0]/180.) * 360);
                    deltaHSL45[0] = abs(HSL[0]-currHSL45[0]);
                    deltaHSL45[2] = abs(HSL[2]-currHSL45[2]);
                    if(deltaHSL45[0]<10 && deltaHSL45[2]<=8 && (prevColor_45.find("Violet")!=string::npos || prevColor_45.find("Purple")!=string::npos)) {
                        ++colorCount45;
                    }
                }
                if(i>=0) {
                    prevColor_90 = c.getMainColor(fd.colorVec.at(i).at(pt.x));
                    currHSL90[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(pt.x),';',1);
                    currHSL90[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(pt.x),';',3)*100;
                    currHSL90[0] = (int)(currHSL90[0] - floor(currHSL90[0]/180.) * 360);
                    deltaHSL90[0] = abs(HSL[0]-currHSL90[0]);
                    deltaHSL90[2] = abs(HSL[2]-currHSL90[2]);
                    if(deltaHSL90[0]<10 && deltaHSL90[2]<=8 && (prevColor_90.find("Violet")!=string::npos || prevColor_90.find("Purple")!=string::npos)) {
                        ++colorCount90;
                    }
                }
                --x; --j;
            }
    
            if(colorCount0>=10) flag0=1;
            if(colorCount45>=10) flag45=1;
            if(colorCount90>=10) flag90=1;
    
            if(fn.countEqual(4,flag0,flag45,flag90,1)>=2) {
                newPix = "GreyPurple";
                flag=true;
                ruleNum = 3.4;
            }
        }
        '''
    else:
        fd.m_ContrastMat[pt[1]][pt[0]] = color
        fd.d_HslMat[pt[1]][pt[0]] = color
        fd.hslPtMat[pt[1]][pt[0]] = color

    if(pix!=""):
        newPix = str(grayLevel)+"Gray"+pix+str(colorLevel)
    if(flag==True):
        ruleFlags[9] = 0
        return ruleNum

    return 0

#rule#4 - contrast rule 2 for Grey that looks Violet/Purple
def rule4(fd, newPix, newShade):
    ruleNum=4
    flag = False
    c = Color()
    rgb = Rgb()
    pt = fd.pt
    pix=""
    grayLevel = rgb.getGrayLevel1(newPix)
    colorLevel = rgb.getColorLevel(newPix)
    localScanSize = 20
    color = c.getMainColor(newPix)
    prevColor_0 = prevColor_45 = prevColor_90 = ""
    colorCount0 = colorCount45 = colorCount90 = 0
    flag0 = flag45 = flag90=0
    HSL = [0] * 3
    hslStr = fd.hslMat[pt[1]][pt[0]].split(";")
    HSL[0] = hslStr[0]
    HSL[1] = hslStr[1]*100;
    HSL[2] = hslStr[2]*100;
    if((color.find("Grey")>=0 or newShade.find("Dark")>=0) and HSL[1]<=25 and pt[1]>0):
        j=pt[0]-1
        x = j
        endY = (pt[1]-localScanSize)
        for i in range(pt[1]-1, endY-1, -1):
            if(x<0 and j<0 and i<0): break
            if(x>=0):
                prevColor_0 = c.getMainColor(fd.colorVec[pt[1]][x])
                if(prevColor_0.find("Violet")>=0):
                    colorCount0+=1
            x-=1
            if(j>=0 and i>=0):
                prevColor_45 = c.getMainColor(fd.colorVec[i][j])
                if(prevColor_45.find("Violet")>=0):
                    colorCount45+=1
            j-=1
            if(i>=0):
                prevColor_90 = c.getMainColor(fd.colorVec[i][pt[0]]);
                if(prevColor_90.find("Violet")>=0):
                    colorCount90+=1

        if(colorCount0>=10): flag0=1
        if(colorCount45>=10): flag45=1
        if(colorCount90>=10): flag90=1

        if(fn.countGreaterEqual(1,flag0,flag45,flag90)>=2):
            pix = "Purple"
            flag=True
    if(pix!=""):
        newPix = str(grayLevel)+"Gray"+pix+str(colorLevel)
    if(flag==True): return ruleNum, newPix;

    return 0, newPix;

//rule #5 - Pink -> DarkPink
double rule5(FileData &fd, String &newPix, String &newShade) {
    double ruleNum = 5;
    bool flag=false;
    Color c;
    Hsl hsl;
    Rgb rgb;
    Functions fn;
    String color = c.getMainColor(newPix);
    String pix="";
    double grayLevel = rgb.getGrayLevel1(newPix);
    double colorLevel = rgb.getColorLevel(newPix);
    double HSL[3];
    vector<int> RGB;
    double nextHSL[3];
    vector<int> nextRGB;
    const double H = 0.72;
    const double enterDemarcThresh = -0.0046;
    const double exitDemarcThresh = 0.005;
    String shade = "Dark3";
    static Point enterDemarcPos(-1,-1);
    static Point exitDemarcPos(-1,-1);
    static int demarcFlag=0;
    double currentRelLum =0, nextRelLum=0;
    double tempSlope=0, slope=0;
    unsigned int step=fd.pt.x;
    if(enterDemarcPos.y!=fd.pt.y || (color!="Pink" && color!="PinkRed")) {
        enterDemarcPos = Point(-1,-1);
        exitDemarcPos = Point(-1,-1);
        demarcFlag=0;
    }
    if(color=="Pink" || color=="PinkRed") {
        while((color=="Pink" || color=="PinkRed") && step<(fd.hslMat.at(0).size()-1)) {
            try {
                HSL[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',1);
                HSL[1] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',2);
                HSL[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',3);
                RGB = hsl.hsl2rgb(HSL[0],HSL[1],HSL[2]);
                currentRelLum = rgb.calcPerceivedBrightness(RGB[0],RGB[1],RGB[2])/255.0;
                nextHSL[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step+1),';',1);
                nextHSL[1] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step+1),';',2);
                nextHSL[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step+1),';',3);
                nextRGB = hsl.hsl2rgb(nextHSL[0],nextHSL[1],nextHSL[2]);
                nextRelLum = rgb.calcPerceivedBrightness(nextRGB[0],nextRGB[1],nextRGB[2])/255.0;

                tempSlope = (nextRelLum - currentRelLum);
                slope = (slope * H) + (tempSlope*(1.0-H));
                //printf() for debugging

                printf("(%d,%d) - Curr:%f, Temp:%f, Slope:%f,",step,fd.pt.y,currentRelLum,tempSlope,slope);
                printf(" HSL(%.f,%.2f,%.2f), Flag: %d\n",HSL[0],HSL[1],HSL[2],demarcFlag);

                ///////////////////////
                step++;
                if(slope<=enterDemarcThresh && demarcFlag==0) {
                    demarcFlag=1; //entering DarkPink
                    break;
                }
                if(slope>=exitDemarcThresh) {
                    demarcFlag=1;
                    break;
                }
                color = fd.colorVec.at(fd.pt.y).at(step);
                color = c.getMainColor(color);

            } catch (const std::out_of_range &oor) {
                printf("\nRule5: Try/Catch #1 Out of Range!\n");
                printf("fd.hslMat.size(): %lu\n",fd.hslMat.size());
                printf("fd.hslMat.at(%d).size(): %lu\n",fd.pt.y,fd.hslMat.at(fd.pt.y).size());
                printf("fd.windowVec.size(): %lu\n",fd.colorVec.size());
                printf("fd.windowVec.at(%d).size(): %lu\n",fd.pt.y,fd.colorVec.at(fd.pt.y).size());
                printf("Point(%d,%d)\n",step,fd.pt.y);
                printf("fd.pt(%d,%d)\n",fd.pt.x,fd.pt.y);
                exit(1);
            }
        }
        //printf() for debugging

        HSL[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',1);
        HSL[1] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',2);
        HSL[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',3);
        RGB = hsl.hsl2rgb(HSL[0],HSL[1],HSL[2]);
        currentRelLum = rgb.calcPerceivedBrightness(RGB[0],RGB[1],RGB[2])/255.0;
        printf("(%d,%d) - Curr:%f, Flag: %d\n",step,fd.pt.y,currentRelLum,demarcFlag);

        ///////////////////////
        if(demarcFlag==1) {
            if(slope<=enterDemarcThresh) {
                enterDemarcPos = Point(step,fd.pt.y);
            }
            else if(slope>=exitDemarcThresh) {
                if(enterDemarcPos.x==-1 && enterDemarcPos.y==-1)
                    enterDemarcPos = Point(fd.pt.x,fd.pt.y);
                exitDemarcPos = Point(step,fd.pt.y);
            }
        }

        printf("Flag: %d\n",demarcFlag);
        printf("%d,%d\n",fd.pt.x,fd.pt.y);
        printf("enterDemarcPos - %d,%d\n",enterDemarcPos.x,enterDemarcPos.y);
        printf("exitDemarcPos - %d,%d\n",exitDemarcPos.x,exitDemarcPos.y);

        if(enterDemarcPos.x!=-1 && enterDemarcPos.y!=-1) {
            if(fd.pt.x>=enterDemarcPos.x && fd.pt.y>=enterDemarcPos.y) {
                if(exitDemarcPos.x==-1 && exitDemarcPos.y==-1) {
                    newShade = shade;
                    pix = "Pink";
                    flag=true;
                }
                else if(fd.pt.x<=exitDemarcPos.x && fd.pt.y<=exitDemarcPos.y) {
                    newShade = shade;
                    pix = "Pink";
                    flag=true;
                }
                else {
                    enterDemarcPos = Point(-1,-1);
                    exitDemarcPos = Point(-1,-1);
                    demarcFlag=0;
                }
            }
        }
        /*else {
            if(fd.pt.x<=exitDemarcPos.x && fd.pt.y<=exitDemarcPos.y) {
                newShade = shade;
                flag=true;
            }
            else {
                enterDemarcPos = Point(-1,-1);
                exitDemarcPos = Point(-1,-1);
                demarcFlag=0;
            }
        }*/
    }
    if(pix!="")
        newPix = str(grayLevel)+"Gray"+pix+str(colorLevel);
    if(flag==true) return ruleNum;
    return 0;
}

//rule 5 - Pink to DarkPink
double rule5(FileData &fd) {
    double ruleNum = 5;
    bool flag=false;
    Color c;
    Rgb rgb;
    Functions fn;
    Shades sh;
    String oldPix, newPix,color, shade, oldShade,newShade;
    double grayLevel = rgb.getGrayLevel1(newPix);
    double colorLevel = rgb.getColorLevel(newPix);
    String pix="";
    double HSL[3];
    double nextHSL[3];
    //int *RGB;
    //int *nextRGB;
    const double H = 0.72;
    const double enterDemarcThresh = -0.0046;
    const double exitDemarcThresh = 0.0034;
    String targetShade = "Dark3";
    Point enterDemarcPos(-1,-1);
    Point exitDemarcPos(-1,-1);
    int demarcFlag=0;
    double currentRelLum =0, nextRelLum=0;
    double tempSlope=0, slope=0;
    unsigned int step=0;
    double minSlope=100;
    Point minSlopePt, maxSlopePt;
    Point myPt(1,71);
    int shadeIndex=0;
    int lightShadeIndex = sh.getShadeIndex("Light1");

    for(unsigned int i=0; i<fd.colorVec.size(); i++) {
        for(unsigned int j=0; j<fd.colorVec.at(i).size(); j++) {
            fd.pt = Point(j,i);
            oldPix = c.getMainColor(fd.colorVec.at(i).at(j));
            oldShade = sh.extractShade(fd.colorVec.at(i).at(j));
            newPix = oldPix;
            newShade = oldShade;
            color = newPix;
            shade = newShade;
            step = fd.pt.x;
            minSlope=100;
            enterDemarcPos = Point(-1,-1);
            exitDemarcPos = Point(-1,-1);
            demarcFlag=0;
            slope=0;

            if((color=="Pink" || color=="PinkRed") && step<(fd.colorVec.at(0).size()-1)) {
                while((color=="Pink" || color=="PinkRed") && step<(fd.colorVec.at(0).size()-1)) {
                    try {
                        shadeIndex = sh.getShadeIndex(shade);
                        HSL[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',1);
                        HSL[1] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',2);
                        HSL[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',3);
                        //RGB = hsl.hsl2rgb(HSL[0],HSL[1],HSL[2]);
                        //currentRelLum = rgb.calcPerceivedBrightness(RGB[0],RGB[1],RGB[2])/255.0;
                        currentRelLum = HSL[2];
                        nextHSL[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step+1),';',1);
                        nextHSL[1] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step+1),';',2);
                        nextHSL[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step+1),';',3);
                        //nextRGB = hsl.hsl2rgb(nextHSL[0],nextHSL[1],nextHSL[2]);
                        //nextRelLum = rgb.calcPerceivedBrightness(nextRGB[0],nextRGB[1],nextRGB[2])/255.0;
                        nextRelLum = nextHSL[2];
                        tempSlope = (nextRelLum - currentRelLum);
                        slope = (slope * H) + (tempSlope*(1.0-H));
                        if(slope<minSlope) {
                            minSlope = slope;
                            minSlopePt = Point(step,fd.pt.y);
                        }
                        //printf() for debugging
                        /*
                        debug=true;
                        if(j==myPt.x && i==myPt.y) {
                            printf("(%d,%d) - Curr:%f, Temp:%f, Slope:%f,",step,fd.pt.y,currentRelLum,tempSlope,slope);
                            printf(" HSL(%.f,%.2f,%.2f), %s, Flag: %d",HSL[0],HSL[1],HSL[2],color.c_str(),demarcFlag);
                            printf("%s: %d\n",shade.c_str(),shadeIndex);
                        }
                        /**/
                        ///////////////////////
                        step++;
                        if(slope<=enterDemarcThresh && demarcFlag==0 && shadeIndex<lightShadeIndex) {
                            enterDemarcPos = Point(step,fd.pt.y);
                            demarcFlag=1; //entering DarkPink
                        }
                        if((slope>=exitDemarcThresh && tempSlope>0)) {
                            if(enterDemarcPos.x==-1 && enterDemarcPos.y==-1)
                                enterDemarcPos = minSlopePt;
                            exitDemarcPos = Point(step,fd.pt.y);
                            demarcFlag=1;
                            break;
                        }
                        //if(demarcFlag==1 && HSL[2]>=enterLuminance) {
                        //    exitDemarcPos = Point(step,fd.pt.y);
                        //}
                        color = fd.colorVec.at(fd.pt.y).at(step);
                        shade = sh.extractShade(color);
                        color = c.getMainColor(color);

                    } catch (const std::out_of_range &oor) {
                        printf("\nRule5: Try/Catch #1 Out of Range!\n");
                        printf("fd.hslMat.size(): %lu\n",fd.hslMat.size());
                        printf("fd.hslMat.at(%d).size(): %lu\n",fd.pt.y,fd.hslMat.at(fd.pt.y).size());
                        printf("fd.windowVec.size(): %lu\n",fd.colorVec.size());
                        printf("fd.windowVec.at(%d).size(): %lu\n",fd.pt.y,fd.colorVec.at(fd.pt.y).size());
                        printf("Point(%d,%d)\n",step,fd.pt.y);
                        printf("fd.pt(%d,%d)\n",fd.pt.x,fd.pt.y);
                        exit(1);
                    }
                }//end while color
                if(exitDemarcPos==Point(-1,-1) && demarcFlag==1)
                    exitDemarcPos = Point(step,fd.pt.y);
                //printf() for debugging
                /*
                debug=true;
                if(j==myPt.x && i==myPt.y) {
                    HSL[0] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',1);
                    HSL[1] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',2);
                    HSL[2] = fn.getDelimitedValuesFromString(fd.hslMat.at(fd.pt.y).at(step),';',3);
                    //RGB = hsl.hsl2rgb(HSL[0],HSL[1],HSL[2]);
                    //currentRelLum = rgb.calcPerceivedBrightness(RGB[0],RGB[1],RGB[2])/255.0;
                    currentRelLum = HSL[2];
                    //printf("(%d,%d) - Curr:%f, Flag: %d\n",step,fd.pt.y,currentRelLum,demarcFlag);
                    printf("(%d,%d) - Curr:%f,",step,fd.pt.y,currentRelLum);
                    printf(" HSL(%.f,%.2f,%.2f), %s, Flag: %d\n",HSL[0],HSL[1],HSL[2],color.c_str(), demarcFlag);
                    printf("Flag: %d\n",demarcFlag);
                    printf("%d,%d\n",fd.pt.x,fd.pt.y);
                    printf("enterDemarcPos - %d,%d\n",enterDemarcPos.x,enterDemarcPos.y);
                    printf("exitDemarcPos - %d,%d\n",exitDemarcPos.x,exitDemarcPos.y);
                }
                /**/
                //////////////////////////
                if(enterDemarcPos!=Point(-1,-1)) {
                    for(int k=j; k<exitDemarcPos.x; k++) {
                        if(k>=enterDemarcPos.x && fd.pt.y>=enterDemarcPos.y) {
                            if(k<=exitDemarcPos.x && fd.pt.y<=exitDemarcPos.y) {
                                oldPix = c.getMainColor(fd.colorVec.at(i).at(k));
                                oldShade = sh.extractShade(fd.colorVec.at(i).at(k));
                                newShade = targetShade;
                                pix = "Pink";
                                //pos1 = fd.colorVec.at(i).at(k).find(oldPix);
                                //pos2 = fd.colorVec.at(i).at(k).find(oldShade);
                                //fd.colorVec.at(i).at(k).replace(pos1,oldPix.length(),newPix);
                                //fd.colorVec.at(i).at(k).replace(pos2,oldShade.length(),newShade);
                                fd.colorVec.at(i).at(k) = newShade+pix;
                                flag=true;
                            }
                            else if(newShade.find("Dark")!=string::npos) {
                                newShade = targetShade;
                                pix = "Pink";
                                fd.colorVec.at(i).at(k) = newShade+pix;
                                flag=true;
                            }
                            else {
                                enterDemarcPos = Point(-1,-1);
                                exitDemarcPos = Point(-1,-1);
                                demarcFlag=0;
                                slope=0;
                            }
                        }
                    }
                }
                j=step-1; //step-1 because j++ in next iteration
            }// end if color
        }//end for j
    }//end for i

    if(pix!="")
        newPix = str(grayLevel)+"Gray"+pix+str(colorLevel);
    if(flag==true) return ruleNum;
    return 0;
}

/** rule 6 - Assign Dark Grey **/
double rule6(String& newPix, String& newShade) {
    double ruleNum = 6;
    bool flag = false;
    Rgb rgb;
    Color c;
    String color = c.getMainColor(newPix);
    String pix = "";
    double grayLevel = rgb.getGrayLevel1(newPix);
    double colorLevel = rgb.getColorLevel(newPix);

    if(newShade.find("Dark")!=string::npos) {
        if(grayLevel>=90) {
            if(newShade.find("Dark1")!=string::npos)
                pix = "Black";
            else
                pix = "Grey";
            flag=true;
        }
    }
    /*
    else if(newShade=="High" || newShade=="Low") {
        if(grayLevel>=85) {
            if(color.find("Pink")!=string::npos || color.find("Violet")!=string::npos) {
                if(colorLevel<60 && ratio>1.25) {
                    newPix = "Grey";
                    flag=true;
                }
            }
            else if(color.find("Purple")!=string::npos) {
                if(colorLevel<55 && ratio>1.3) {
                    newPix = "Grey";
                    flag=true;
                }
            }
            else {
                newPix = color;
                flag=true;
            }
        }
    }*/
    if(pix!="")
        newPix = str(grayLevel)+pix+str(colorLevel);
    if(flag==true) return ruleNum;

    return 0;
}

/** P0: General rule 7 - Fix non-existent double colors **/
double rule7(String &newPix) {
    double ruleNum = 7;
    bool flag=false;
    Color c;
    Rgb rgb;
    String color = c.getMainColor(newPix);
    String pix="";
    double grayLevel = rgb.getGrayLevel1(newPix);
    double colorLevel = rgb.getColorLevel(newPix);

    if(color.find("Blue")!=string::npos && color.find("Purple")!=string::npos) {
        pix = "Purple";
        flag=true;
    }
    if(pix!="")
        newPix = str(grayLevel)+"Gray"+pix+str(colorLevel);
    if(flag==true) return ruleNum;

    return 0;
}

/** P1: Special rule 8- Using indexChange to promote colors on boundaries */
double rule8(FileData &fd, String &newPix, int loc) {
    double ruleNum = 8;
    bool flag=false;
    Hsl hsl;
    Rgb rgb;
    Color c;
    Intensity in;
    Functions fn;
    Point pt = fd.pt;
    String color = c.getMainColor(fd.windowVec.at(pt.y).at(pt.x));
    String pix="";
    double grayLevel = rgb.getGrayLevel1(newPix);
    double colorLevel = rgb.getColorLevel(newPix);
    int index=-1;
    double localScanSize = 20;
    double hue = fn.getDelimitedValuesFromString(fd.hslMat.at(pt.y).at(pt.x),';',1);
    double sat = fn.getDelimitedValuesFromString(fd.hslMat.at(pt.y).at(pt.x),';',2);
    double lum = fn.getDelimitedValuesFromString(fd.hslMat.at(pt.y).at(pt.x),';',3);
    double promoteThresh = 1.0/1.75;
    double demoteThresh = 1.75;
    double currCL = rgb.getColorLevel(fd.windowVec.at(pt.y).at(pt.x));
    double localCL_0deg, localCL_45deg=0, localCL_90deg=0;
    double relCL_0deg=0,relCL_45deg=0,relCL_90deg=0;

    int deg0_flag=0; // flag =  -1->demote; 1->promote
    int deg45_flag=0;
    int deg90_flag=0;
    String shade_0deg, shade_45deg, shade_90deg;
    hsl.getHslColor(hue,sat,lum,index);
    if(index<0) {
        printf("Rule8: Index Out of bounds!\n");
        printf("Point(%d,%d)\n",pt.x,pt.y);
        printf("HSL(%0.0f,%0.2f,%0.2f)\n",hue,sat,lum);
        exit(1);
    }
    if(pt.y>0 && color!="Black") {
        int j = pt.x-1; //45deg
        int x = j; //0deg
        int endY = (pt.y-localScanSize);
        for(int i=(pt.y-1); i>=endY; i--) {
            if(x<0 && j<0 && i<0) break;
            if(x>=0) {
                localCL_0deg = rgb.getColorLevel(fd.windowVec.at(pt.y).at(x));
                relCL_0deg = currCL/localCL_0deg;
                if(relCL_0deg<=promoteThresh)
                    deg0_flag += 1;
                else if(relCL_0deg>=demoteThresh)
                    deg0_flag -= 1;
            }
            --x;
            if(j>=0 && i>=0) {
                localCL_45deg = rgb.getColorLevel(fd.windowVec.at(i).at(j));
                relCL_45deg = currCL/localCL_45deg;
                if(relCL_45deg<=promoteThresh)
                    deg45_flag += 1;
                if(relCL_45deg>=demoteThresh)
                    deg45_flag -= 1;
            }
            --j;
            if(i>=0) {
                localCL_90deg = rgb.getColorLevel(fd.windowVec.at(i).at(pt.x));
                relCL_90deg = currCL/localCL_90deg;
                if(relCL_90deg<=promoteThresh)
                    deg90_flag += 1;
                if(relCL_90deg>=demoteThresh)
                    deg90_flag -= 1;
            }
            /*if(pt.x==300 && pt.y==303) {
                printf("%0.2f ; %0.2f ; %0.2f\n",relCL_0deg,relCL_45deg,relCL_90deg);
                //printf("%.0f ; %.0f ; %.0f\n",localCL_0deg,localCL_45deg,localCL_90deg);
                //printf("%d ; %d ; %d\n",deg0_flag,deg45_flag,deg90_flag);
            }*/
            if(abs(deg45_flag)>10 && abs(deg90_flag)>10)
                break;
            if(abs(deg0_flag)>10 && abs(deg90_flag)>10)
                break;
            if(abs(deg0_flag)>10 && abs(deg45_flag)>10)
                break;
        }
        //if(pt.x==300 && pt.y==303)
        //printf("%d ; %d ; %d\n",deg0_flag,deg45_flag,deg90_flag);

    }

    if(deg0_flag<0) deg0_flag = -1;
    if(deg0_flag>0) deg0_flag = 1;
    if(deg45_flag<0) deg45_flag = -1;
    if(deg45_flag>0) deg45_flag = 1;
    if(deg90_flag<0) deg90_flag = -1;
    if(deg90_flag>0) deg90_flag = 1;
    if((deg0_flag+deg45_flag)>=2||(deg0_flag+deg90_flag)>=2||(deg45_flag+deg90_flag)>=2) {
        lum += 0.10;
        if(lum>1) lum = 1;
        pix = hsl.getHslColor(hue,sat,lum,index);
        flag=true;
        ruleNum = 8.1;
    }
    if((deg0_flag+deg45_flag)<=-2||(deg0_flag+deg90_flag)<=-2||(deg45_flag+deg90_flag)<=-2) {
        lum -= 0.10;
        if(lum<0) lum=0;
        pix = hsl.getHslColor(hue,sat,lum,index);
        flag=true;
        ruleNum = 8.2;
    }
    if(pix!="")
        newPix = str(grayLevel)+"Gray"+pix+str(colorLevel);
    if(flag==true) return ruleNum;

    return 0;
}

/** P2: Special rule 9 - GrayIndexChange - for non-grays that look gray **/
double rule9(FileData &fd, String &newPix) {
    double ruleNum = 9;
    bool flag = false;
    Rgb rgb;
    Color c;
    Point pt = fd.pt;
    String color = c.getMainColor(newPix);
    String prevColor_0deg, prevColor_45deg, prevColor_90deg;
    String pix0=newPix,pix45=newPix,pix90=newPix;
    String pix="";
    double grayLevel = rgb.getGrayLevel1(newPix);
    double colorLevel = rgb.getColorLevel(newPix);

    double absRatioThresh = 1.35;
    double relRatioThreshUpper = 1.20;
    double relRatioThreshLower = 1.05;
    double absRatio = roundDecimal(grayLevel/colorLevel,2);
    double glThresh=70;
    double relRatio_0deg;
    double relRatio_45deg=0, relRatio_90deg=0;
    bool relRatio_0deg_flag = false;
    bool relRatio_45deg_flag = false;
    bool relRatio_90deg_flag = false;
    double localRatioScanSize = fd.localRatioScanSize;
    if(colorLevel<40) glThresh = 65;
    if(c.containsColor(str(4),color.c_str(),"Brown","Pink","Blue")) {
        if(pt.y>0) {
            int j=pt.x-1; //45deg
            int x = j; //0deg
            int endY=(pt.y-localRatioScanSize);
            for(int i=(pt.y-1); i>=endY; i--) {
                if(x<0 && j<0 && i<0) break;

                if(relRatio_0deg_flag==false && x>=0) {
                    relRatio_0deg = absRatio/fd.absRatioVec.at(x);
                    relRatio_0deg = roundDecimal(relRatio_0deg,2);
                    prevColor_0deg = fd.colorVec.at(pt.y).at(x);
                    //entering
                    if(relRatio_0deg>relRatioThreshUpper && absRatio>absRatioThresh && grayLevel>=glThresh) {
                        pix0 = "Grey";
                        relRatio_0deg_flag = true;
                    }
                    //inside
                    else if(relRatio_0deg>=relRatioThreshLower&&relRatio_0deg<=relRatioThreshUpper && prevColor_0deg=="Grey" && grayLevel>=glThresh) {
                        pix0 = prevColor_0deg;
                        relRatio_0deg_flag = true;
                    }
                }
                --x;
                if(relRatio_45deg_flag==false && j>=0 && i>=0) {
                    relRatio_45deg = absRatio/fd.absRatioMat.at(i).at(j);
                    relRatio_45deg = roundDecimal(relRatio_45deg,2);
                    prevColor_45deg = fd.colorVec.at(i).at(j);
                    //entering
                    if(relRatio_45deg>relRatioThreshUpper && absRatio>absRatioThresh && grayLevel>=glThresh) {
                        pix45 = "Grey";
                        relRatio_45deg_flag = true;
                    }
                    //inside
                    else if(relRatio_45deg>=relRatioThreshLower&&relRatio_45deg<=relRatioThreshUpper && prevColor_45deg=="Grey" && grayLevel>=glThresh) {
                        pix45 = prevColor_45deg;
                        relRatio_45deg_flag = true;
                    }
                }
                --j;
                if(relRatio_90deg_flag==false && i>=0) {
                    relRatio_90deg = absRatio/fd.absRatioMat.at(i).at(pt.x);
                    relRatio_90deg = roundDecimal(relRatio_90deg,2);
                    prevColor_90deg = fd.colorVec.at(i).at(pt.x);
                    //entering
                    if(relRatio_90deg>relRatioThreshUpper && absRatio>absRatioThresh && grayLevel>=glThresh) {
                        pix90 = "Grey";
                        relRatio_90deg_flag = true;
                    }
                    //inside
                    else if(relRatio_90deg>=relRatioThreshLower&&relRatio_90deg<=relRatioThreshUpper && prevColor_90deg=="Grey" && grayLevel>=glThresh) {
                        pix90 = prevColor_90deg;
                        relRatio_90deg_flag = true;
                    }
                }
                if(relRatio_0deg_flag==true && relRatio_45deg_flag==true && relRatio_90deg_flag==true)
                    break;

                if(pt.x==32 && pt.y==56) {
                    //printf("Abs:%f, [0]:%0.2f(%d,%d); [45]:%0.2f(%d,%d); [90]:%0.2f(%d,%d)\n",absRatio,fd.absRatioVec.at(x+1),x+1,pt.y,fd.absRatioMat.at(i).at(j+1),j+1,i,fd.absRatioMat.at(i).at(pt.x),pt.x,i);
                    printf("GL:%.f, ",grayLevel);
                    printf("Abs:%f, [0]:%0.2f(%d,%d); [45]:%0.2f(%d,%d); [90]:%0.2f(%d,%d), ",absRatio,relRatio_0deg,x+1,pt.y,relRatio_45deg,j+1,i,relRatio_90deg,pt.x,i);
                    printf("%s, %s, %s\n",pix0.c_str(),pix45.c_str(),pix90.c_str());
                    //printf("(%.0f;%.3f;%.0f;%.3f)", gl_0deg,glRatio_0deg,cl_0deg,clRatio_0deg);
                    //printf("(%.0f;%.3f;%.0f;%.3f)", gl_45deg,glRatio_45deg,cl_45deg,clRatio_45deg);
                    //printf("(%.0f;%.3f;%.0f;%.3f)\n", gl_90deg,glRatio_90deg,cl_90deg,clRatio_90deg);
                }
            }
        }
        if(pix0==pix45||pix0==pix90) {
            pix=pix0;
            flag=true;
        }
        else if(pix45==pix90) {
            pix=pix45;
            flag=true;
        }
    }
    if(pix!="")
        newPix = str(grayLevel)+pix+str(colorLevel);
    if(flag==true) return ruleNum;

    return 0;
}

//White to LightGrey
double rule10(String &newPix, String &newShade) {
    bool flag=false;
    double ruleNum = 10;
    Color c;
    Rgb rgb;
    Shades sh;
    String color = c.getMainColor(newPix);
    String pix="";
    double grayLevel = rgb.getGrayLevel1(newPix);
    double colorLevel = rgb.getColorLevel(newPix);
    if(color=="White" || newShade=="White") {
        pix = "Grey";
        newShade = sh.getShade(sh.getShadeCount()-2);
        flag=true;
    }
    if(pix!="")
        newPix = str(grayLevel)+"Gray"+pix+str(colorLevel);
    if(flag==true) return ruleNum;

    return 0;
}

bool specialRules(FileData &fd, String &pix, double &indexChange, String &shade,
        int ratioLoc, int loc, deque<double> &ruleNo) {
    bool flag=false;
    String newShade = shade;
    String newPix = pix;
    deque<double> ruleNumVec;

    if(ruleFlags.at(1)==1)
        ruleNumVec.push_back(rule1(fd, newShade));
    if(ruleFlags.at(2)==1)
        ruleNumVec.push_back(rule2(fd,newPix));
    if(ruleFlags.at(3)==1)
        ruleNumVec.push_back(rule3(fd,newPix,newShade));
    if(ruleFlags.at(6)==1)
        ruleNumVec.push_back(rule6(newPix,newShade));
    //if(ruleFlags.at(9)==1)
    //ruleNumVec.push_back(rule9(fd,newPix));
    if(ruleFlags.at(8)==1)
        ruleNumVec.push_back(rule8(fd,newPix,loc));
    if(ruleFlags.at(7)==1)
        ruleNumVec.push_back(rule7(newPix));
    if(ruleFlags.at(10)==1)
        ruleNumVec.push_back(rule10(newPix,newShade));

    if(ruleNumVec.size()>0) {
        for(unsigned int i=0; i<ruleNumVec.size(); i++) {
            if(ruleNumVec.at(i)!=0) {
                ruleNo.push_back(ruleNumVec.at(i));
                flag=true;
            }
        }
    }
    ruleFlags.clear();
    ruleFlags.resize(ruleCount,1);
    deque<double>().swap(ruleNumVec);
    shade = newShade;
    pix = newPix;
    return flag;
}

//function used for testing rules
void testRules() {
    FileData fd;
    Color c;
    Shades sh;
    String file1 = "/home/jason/Desktop/Programs/Test_Output/vesicles2-5x5.csv";
    String file2 = "/home/jason/Desktop/Programs/Test_Output/vesicles2-ShadeColors-5x5.csv";
    String file3 = "/home/jason/Desktop/Programs/Test_Output/vesicles2-HSL-5x5.csv";
    fd.loadFileMatrix(file1,fd.windowVec);
    fd.loadFileMatrix(file2,fd.colorVec);
    fd.loadFileMatrix(file3,fd.hslMat);
    init_2D_Deque(fd.m_ContrastMat,fd.windowVec.size(),fd.windowVec.at(0).size());
    init_2D_Deque(fd.d_HslMat,fd.windowVec.size(),fd.windowVec.at(0).size());
    init_2D_Deque(fd.hslPtMat,fd.windowVec.size(),fd.windowVec.at(0).size());
    init_2D_Deque(fd.cumHslMat,fd.windowVec.size(),fd.windowVec.at(0).size());
    init_2D_Deque(fd.minMaxHslMat,fd.windowVec.size(), fd.windowVec.at(0).size());
    fd.pt = Point(39,54);
    String newPix = c.getMainColor(fd.windowVec.at(fd.pt.y).at(fd.pt.x));
    String newShade = sh.extractShade(fd.colorVec.at(fd.pt.y).at(fd.pt.x));
    rule3(fd,newPix,newShade);
    printf("HSL(%s)\n",fd.hslMat.at(fd.pt.y).at(fd.pt.x).c_str());
    printf("Color: %s\n",fd.windowVec.at(fd.pt.y).at(fd.pt.x).c_str());
    printf("%s\n",fd.hslPtMat.at(fd.pt.y).at(fd.pt.x).c_str());
    printf("mCon: %s\n",fd.m_ContrastMat.at(fd.pt.y).at(fd.pt.x).c_str());
    printf("dHSL: %s\n",fd.d_HslMat.at(fd.pt.y).at(fd.pt.x).c_str());
    printf("HSLs: %s\n",fd.minMaxHslMat.at(fd.pt.y).at(fd.pt.x).c_str());
    cout << newPix << endl;
}

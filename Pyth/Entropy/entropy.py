'''
Created on Oct 5, 2016

@author: jason
'''

import numpy as np

# deque<deque< deque< deque<double> > > > vec;
# deque<deque< deque< deque<double> > > > vec2;
# deque<deque< deque< deque<int> > > > gTargetCellCount;
# double vecTotal[5] = {0};
# 
# deque<deque<deque<deque<double> > > > gRatio;
# deque<deque<deque< deque<double> > > > gSmoothRatio;
# deque<deque<deque< deque<double> > > > gSmoothRatioRm;
# deque<deque<deque< deque<double> > > > gRatioRm;

class Entropy:
    debugMode = False
    Y_HIGH = 0.0    #upper Y range boundary
    Y_LOW = 0.0    #lower Y range boudnary
    S_HIGH =0.0
    S_LOW = 0.0
    V_HIGH = 0.0
    V_LOW = 0.0
    Y_THRESH = 0.0    #% threshold Y must meet for special conditions
    S_THRESH = 0.0
    V_THRESH = 0.0
    Y_DIST = 0.0    #distance threshold Y must meet for special conditions
    S_DIST = 0.0
    V_DIST = 0.0
    Y_PERCEPTION = 0.0    #threshold in which the eyes starts noticing color
    S_PERCEPTION = 0.0
    Y_LARGE_THRESH = 0.0
    distPass = 0.0
    Y1 = Y2 = 0.0
    colorWeights = [] #holds the weights for color impact - My algo
    colorWeights2 = [] #Dr. Dube's algo

    totalPopulation =  [[]] #Y
    populationDensity = [[]] #S
    densityVariation = [[]] #V
    shapeMetric = [] #T
    
    def eyeFn(FileData &fd, Size ksize, Mat map, String targetColor,String targetShade) {
        int height = fd.colorVec.size()/ksize.height;
        int width = fd.colorVec.at(0).size()/ksize.width;
        int innerHeight = Rgb::allColors.size();
        int innerWidth = Shades::g_Shades2.size();
        vec = createDeque4D(height,width,innerHeight,innerWidth,0.);
        vec2 = createDeque4D(height,width,innerHeight,innerWidth,0.);
        gTargetCellCount = createDeque4D(height,width,innerHeight,innerWidth,0);
        deque<deque<deque<deque<double> > > > ratio(height,deque<deque<deque<double> > >(width,deque<deque<double> >(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0))));
        deque<deque<deque<deque<double> > > > smoothRatio(height,deque<deque<deque<double> > >(width,deque<deque<double> >(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0))));
        Rgb rgb;
        Hsl hsl;
        Color c;
        Shades sh;
        Functions fn;
        String color,shade,pix;
        double h,s,l;
        int shadeIndex,colorIndex;
        int cellSize = ksize.height*ksize.width;
        deque< deque<double> > pShadeColor(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0));
        this->totalPopulation.resize(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0));
        this->populationDensity.resize(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0));
        this->densityVariation.resize(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0));
        double pTotal=0;
        unsigned int row=0, col=0;
        int i=0,j=0, maxRow=0, maxCol=0;
        if(map.empty()) map = map.ones(fd.colorVec.size(),fd.colorVec.at(0).size(),CV_8U);
        try {
            while(row<=(fd.colorVec.size()-ksize.height)) {
                while(col<=(fd.colorVec.at(row).size()-ksize.width)) {
                    if((row+ksize.height+1)>fd.colorVec.size())
                        maxRow = fd.colorVec.size();
                    else
                        maxRow = row+ksize.height;
                    if((col+ksize.width+1)>fd.colorVec.at(row).size())
                        maxCol = fd.colorVec.at(row).size();
                    else
                        maxCol = col+ksize.width;
    
                    for(i=row; i<maxRow; i++) {
                        for(j=col; j<maxCol; j++) {
                            if(map.at<uchar>(i,j)>0) {
                                try {
                                    pix = fd.colorVec.at(i).at(j);
                                    shade = sh.extractShade(pix);
                                    color = c.getMainColor(pix);
                                    color = c.optimizeColor2(color);
                                    /**temporary testing**/
                                    if(shade=="Dark1" && color=="Grey")
                                        color = "Black";
                                    shade = sh.combineShades(shade);
                                    color = c.combineColors(color);
                                    if(color=="Violet" || color =="Purple")
                                        shade = "High";
                                    if(fd.filename.find("acne")!=string::npos)  {
                                        if(color=="Violet")  {
                                            int index=-1;
                                            h = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',1);
                                            s = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',2);
                                            l = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',3);
                                            hsl.getHslColor(h,s,l,index);
                                            color = hsl.getHslColor(index+1);
                                            //color = "BrownRed";
                                        }
                                    }
                                    if(fd.filename.find("psoriasis")!=string::npos)  {
                                        if(color=="Violet")  {
                                            int index=-1;
                                            h = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',1);
                                            s = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',2);
                                            l = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',3);
                                            hsl.getHslColor(h,s,l,index);
                                            color = hsl.getHslColor(index+1);
                                            //color = "BrownRed";
                                        }
                                    }
                                    if(fd.filename.find("herpes")!=string::npos)  {
                                        if(color=="Violet")  {
                                            int index=-1;
                                            h = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',1);
                                            s = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',2);
                                            l = fn.getDelimitedValuesFromString(fd.hslMat.at(i).at(j),';',3);
                                            hsl.getHslColor(h,s,l,index);
                                            color = hsl.getHslColor(index+1);
                                            //color = "BrownRed";
                                        }
                                    }
                                    if(fd.filename.find("herpes5")!=string::npos) {
                                        if(color=="BrownOrange")
                                            color = "BrownPink";
                                    }
                                    /************************************/
                                    shadeIndex = sh.getShadeIndex2(shade);
                                    if(shade.find("Black")!=string::npos || color.find("Black")!=string::npos)
                                        color = "Black";
                                    else if(shade=="White" || color.find("White")!=string::npos)
                                        color = "White";
                                    colorIndex = rgb.getColorIndex(color);
                                    if(color!="Zero" || colorIndex>=0)
                                        ++pShadeColor.at(colorIndex).at(shadeIndex);
                                }
                                catch(const std::out_of_range& oor) {
                                    printf("Entropy::eyeFn() out of range 1!\n");
                                    printf("ColorVec.Size: %lu\n",fd.colorVec.size());
                                    printf("HslMat.Size: %lu\n",fd.hslMat.size());
                                    printf("Point(%d,%d)\n",j,i);
                                    printf("Shade: %s\n",shade.c_str());
                                    printf("ShadeIndex: %d\n",shadeIndex);
                                    printf("Color: %s\n",color.c_str());
                                    printf("ColorIndex: %d\n",colorIndex);
                                    printf("pShadeColor.Size: %lu\n",pShadeColor.size());
                                    printf("pShadeColor(%d,%d)\n",j,i);
                                    exit(1);
                                }
                            }
                        }
                    }
                    for(unsigned int colorRow=0; colorRow<Rgb::allColors.size(); colorRow++) {
                        for(unsigned int shadeCol=0; shadeCol<Shades::g_Shades2.size(); shadeCol++) {
                            try {
                                pTotal = pShadeColor.at(colorRow).at(shadeCol)/cellSize;
                                ratio[row/ksize.height][col/ksize.width][colorRow][shadeCol] = pTotal;
                            }
                            catch (const std::out_of_range &oor) {
                                printf("pShadeColor.Rows: %lu\n", pShadeColor.size());
                                printf("pShadeColor(%d,%d)\n",colorRow,shadeCol);
                                printf("pEntropy(%d,%d)\n",colorRow,shadeCol);
                                exit(1);
                            }
                        }
                    }
                    col+=ksize.width;
                    pShadeColor.clear();
                    pShadeColor.resize(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0));
                }
                row += ksize.height;
                col=0;
            }
        }
        catch (const std::out_of_range &oor) {
            printf("colorVec.Rows: %lu\n",fd.colorVec.size());
            printf("colorVec(%d,%d)\n",col,row);
            exit(1);
        }
    
        deque< deque<int> > cellCount(Rgb::allColors.size(),deque<int>(Shades::g_Shades2.size(),0));
        deque< deque<int> > targetCellCount(Rgb::allColors.size(),deque<int>(Shades::g_Shades2.size(),0));
        deque<deque<deque<Point> > > ratioPtsList(Rgb::allColors.size(), deque<deque<Point> >(Shades::g_Shades2.size(),deque<Point>(1,Point(-1,-1))));
        deque<deque<deque<double> > > ratioSingleList(Rgb::allColors.size(), deque<deque<double> >(Shades::g_Shades2.size(),deque<double>(1,-1)));
        deque<deque<deque<deque<double> > > > smoothRatioOutlierRm(height,deque<deque<deque<double> > >(width,deque<deque<double> >(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0))));
        deque<deque<deque<deque<double> > > > ratioOutlierRm(height,deque<deque<deque<double> > >(width,deque<deque<double> >(Rgb::allColors.size(),deque<double>(Shades::g_Shades2.size(),0))));
        int x1=0,y1=0,minRow=0,minCol=0;
        double count=0, min=0.03;
        double outlierThresh = 0.05;
        for(int y=0; y<height; y++) {
            for(int x=0; x<width; x++) {
                for(int c=0; c<innerHeight; c++) {
                    for(int d=0; d<innerWidth; d++) {
                        if(ratio[y][x][c][d]>min) {
                            /* totalPopulation (Y) = sum of density (Si) */
                            totalPopulation.at(c).at(d) += ratio[y][x][c][d];
                        }
                    }
                }
            }
        }
        while(y1<height) {
            minRow=maxRow=y1;
            if((minRow-1)>=0) minRow-=1;
            if((maxRow+1)<height) maxRow+=1;
            while(x1<width) {
                minCol=maxCol=x1;
                if((minCol-1)>=0) minCol-=1;
                if((maxCol+1)<width) maxCol+=1;
                for(int a=minRow; a<=maxRow; a++)  {
                    for(int b=minCol; b<=maxCol; b++)    {
                        for(int c=0; c<innerHeight; c++) {
                            for(int d=0; d<innerWidth; d++) {
                                if(ratio[y1][x1][c][d]>min) {
                                    smoothRatio[y1][x1][c][d] += ratio[a][b][c][d];
                                }
                            }
                        }
                        ++count;
                    }
                }
                for(int c=0; c<innerHeight; c++) {
                    for(int d=0; d<innerWidth; d++) {
                        smoothRatio[y1][x1][c][d] /=count;
                        if(ratio[y1][x1][c][d]>min) {
                            if(ratioSingleList.at(c).at(d).size()>0) {
                                if(ratioSingleList.at(c).at(d).at(0)==-1) {
                                    ratioSingleList.at(c).at(d).pop_front();
                                    ratioPtsList.at(c).at(d).pop_front();
                                }
                            }
                            ratioSingleList.at(c).at(d).push_back(ratio[y1][x1][c][d]);
                            ratioPtsList.at(c).at(d).push_back(Point(x1,y1));
    
                            cellCount.at(c).at(d)++;
                            /* density(S) = sum( (Si^2) / Y ) */
                            if(ratio[y1][x1][c][d]>min)
                                populationDensity.at(c).at(d) += (ratio[y1][x1][c][d] * ratio[y1][x1][c][d] / totalPopulation.at(c).at(d));
                            if(targetColor!="" && targetShade!="") {
                                int index = rgb.getColorIndex(targetColor);
                                int shadeIndex = sh.getShadeIndex2(targetShade);
                                if(c==index && d==shadeIndex) {
                                    //pt.at(y1).at(x1) = 1;
                                    targetCellCount.at(c).at(d) = cellCount.at(c).at(d);
                                }
                            }
                        }
                        if(targetColor!="" && targetShade!="") {
                            int index = rgb.getColorIndex(targetColor);
                            int shadeIndex = sh.getShadeIndex2(targetShade);
                            if(c==index && d==shadeIndex) {
                                vec[y1][x1][c][d] = totalPopulation.at(c).at(d);
                                vec2[y1][x1][c][d] = populationDensity.at(c).at(d);
                                gTargetCellCount[y1][x1][c][d] = targetCellCount.at(c).at(d);
                            }
                        }
                    }
                }
                count=0;
                ++x1;
            }
            x1=0;
            ++y1;
        }
        //start of standard dev (V)
        ratioOutlierRm = ratio;
        deque<double> sortedList;
        deque<Point> sortedPtsList;
        for(i=0; i<innerHeight; i++) {
            for (j=0; j<innerWidth; j++) {
                if(ratioSingleList.at(i).at(j).size()>0) {
                    if(ratioSingleList.at(i).at(j).at(0)!=-1) {
                        if(sortedList.size()==0) {
                            sortedList.push_back(ratioSingleList.at(i).at(j).at(0));
                            sortedPtsList.push_back(ratioPtsList.at(i).at(j).at(0));
                        }
                        for(unsigned int d=1; d<ratioSingleList.at(i).at(j).size(); d++) {
                            for(unsigned int e=0; e<sortedList.size(); e++) {
                                if((sortedList.size()-e)<=1) {
                                    if(ratioSingleList.at(i).at(j).at(d)>=sortedList.at(e)) {
                                        sortedList.push_back(ratioSingleList.at(i).at(j).at(d));
                                        sortedPtsList.push_back(ratioPtsList.at(i).at(j).at(d));
                                        break;
                                    }
                                    else {
                                        sortedList.push_front(ratioSingleList.at(i).at(j).at(d));
                                        sortedPtsList.push_front(ratioPtsList.at(i).at(j).at(d));
                                        break;
                                    }
                                }
                                else {
                                    if(ratioSingleList.at(i).at(j).at(d)>=sortedList.at(e) && ratioSingleList.at(i).at(j).at(d)<=sortedList.at(e+1)) {
                                        sortedList.insert(sortedList.begin()+e+1,ratioSingleList.at(i).at(j).at(d));
                                        sortedPtsList.insert(sortedPtsList.begin()+e+1,ratioPtsList.at(i).at(j).at(d));
                                        break;
                                    }
                                    if(ratioSingleList.at(i).at(j).at(d)<=sortedList.at(0)) {
                                        sortedList.push_front(ratioSingleList.at(i).at(j).at(d));
                                        sortedPtsList.push_front(ratioPtsList.at(i).at(j).at(d));
                                        break;
                                    }
                                }
                            }
                        }
                        double t = sortedList.size()*outlierThresh;
                        t = round(t);
                        for(int d=0; d<t; d++) {
                            ratioOutlierRm[sortedPtsList.front().y][sortedPtsList.front().x][i][j]=0;
                            ratioOutlierRm[sortedPtsList.back().y][sortedPtsList.back().x][i][j]=0;
                            sortedPtsList.pop_back();
                            sortedPtsList.pop_front();
                            sortedList.pop_back();
                            sortedList.pop_front();
                        }
                        sortedList.clear();
                        sortedPtsList.clear();
                        deque<double>().swap(sortedList);
                        deque<Point>().swap(sortedPtsList);
                    }
                }
            }//end for innerWidth
        }//end for innerHeight
        ratioSingleList.clear();
        ratioSingleList.resize(Rgb::allColors.size(),deque<deque<double> >(Shades::g_Shades2.size(),deque<double>(1,-1)));
        x1=0;y1=0;minRow=0;minCol=0;maxRow=0;maxCol=0;
        while(y1<height) {
            while(x1<width) {
                for(int c=0; c<innerHeight; c++) {
                    for(int d=0; d<innerWidth; d++) {
                        if(ratioOutlierRm[y1][x1][c][d]>min) {
                            if(ratioSingleList.at(c).at(d).size()>0) {
                                if(ratioSingleList.at(c).at(d).at(0)==-1) {
                                    ratioSingleList.at(c).at(d).pop_front();
                                }
                            }
                            ratioSingleList.at(c).at(d).push_back(ratioOutlierRm[y1][x1][c][d]);
                        }
                    }
                }
                ++x1;
            }
            x1=0;
            ++y1;
        }
        for(int c=0; c<innerHeight; c++) {
            for (int d=0; d<innerWidth; d++) {
                if(ratioSingleList.at(c).at(d).size()>0) {
                    if(ratioSingleList.at(c).at(d).at(0)!=-1) {
                        densityVariation.at(c).at(d) = Algos::standardDev(ratioSingleList.at(c).at(d));
                    }
                }
            }
        }
        if(targetColor=="" && targetShade=="") {
            this->writeEntropyFile(fd.filename,fd);
        }
        gRatio = ratio;
        gSmoothRatio = smoothRatio;
        gSmoothRatioRm = smoothRatioOutlierRm;
        gRatioRm = ratioOutlierRm;
        this->totalPopulation.clear();
        this->populationDensity.clear();
        this->densityVariation.clear();
    }
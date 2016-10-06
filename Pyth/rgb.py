import csv
from hsl import Hsl, hueThresh, satThresh, lumThresh, hslColors

mainColors = []
allColors = []

class Rgb:
    def getMainColorIndex(self,color):
        for i in range(len(mainColors)):
            if(color==mainColors[i]):
                return i
        return -1;
            
    def getColorIndex(self,color):
        for i in range(len(allColors)):
            print i
            if(color==allColors[i]):
                return i
        return -1;

    def importThresholds(self):
        folderName = "Thresholds/"
        filename = folderName+"main_colors.csv"
        filename2 = folderName+"colors.csv"
        file1_read = open(filename,"r")
        csv_file1 = csv.reader(file1_read)
        file2_read = open(filename2,"r")
        csv_file2 = csv.reader(file2_read)
        for row in csv_file1:
            for i in range(len(row)):
                mainColors.append(row[i])
        file1_read.close()
        for row in csv_file2:
            for i in range(len(row)):
                allColors.append(row[i])
        file2_read.close()
        
    def checkBlack(self,red,green,blue):
        if(red==0 and green==0 and blue==0):
            return "Zero";
        return "OTHER";
    
    def calcGrayLevel(self,red,green,blue):
        hsl = Hsl()
        HSL = hsl.rgb2hsl(red,green,blue)
        sat = round(HSL[1],2) * 100
        sat = 100 - sat
        return sat
    
    def getGrayLevel1(self, color):
        mainColor="Gray";
        pos = color.find(mainColor);
        if(pos!=-1):
            level = int(color[0:pos]);
        else:
            pos = color.find("Grey")
            if(pos!=-1):
                level = int(color[0:pos])
            else:
                pos = color.find("Black");
                if(pos!=-1):
                    level = int(color[0:pos])
                    
        return level
                
    def getColorLevel(self,pix):
        for i in range(len(mainColors)):
            if (mainColors[i]!="Grey"):
                pos = pix.find(mainColors[i])
                if (pos!=-1):
                    level = int(pix[pos+len(mainColors[i]):len(pix)-pos+len(mainColors[i])])
                    
        return level
    
    def calcPerceivedBrightness(self,red,green,blue):
        lum = (0.299*red) + (0.587*green) + (0.114*blue)
        return round(lum)
    
    def calcColorLevel(self,red,green,blue):
        lum = self.calcPerceivedBrightness(red, green, blue);
        lum /=255.0;
        lum = round(lum,2) * 100;
        lum = 100 - lum;
        return lum;
    
    def calcGrayLumLevel(self,red,green,blue):
        hsl = Hsl()
        HSL = hsl.rgb2hsl(red,green,blue)
        sat = round(HSL[1],2) * 100
        lum = round(HSL[2],2) * 100
        a=4.0
        temp = a*(1.0-(sat/100.0))
        grayLumLevel = (100.0-lum) * temp/(temp+1)

        return round(grayLumLevel);
    
    def calcColor(self,red,green,blue):
        hsl = Hsl()
        color = Color()
        pix = "OTHER"
        HSL = hsl.rgb2hsl(red, green, blue)
        HSL[1] = round(HSL[1],2)
        HSL[2] = round(HSL[2],2)
        grayLevel = self.calcGrayLevel(red,green,blue)
        colorLevel = self.calcColorLevel(red,green,blue)
        grayLumLevel = self.calcGrayLumLevel(red, green, blue)
        for i in range(0,len(hueThresh)):
            try:
                if(HSL[0]>=hueThresh[i][0] and HSL[0]<=hueThresh[i][1]):
                    if(HSL[1]>=satThresh[i][0] and HSL[1]<satThresh[i][1]):
                        if(HSL[2]>=lumThresh[i][0] and HSL[2]<lumThresh[i][1]):
                            pix = hslColors[i]
                            if(grayLevel==0):
                                pix = hslColors[i] + str(int(colorLevel))
                        
                            else:
                                if(pix=="Black" or pix=="White"):
                                    pix += str(colorLevel)
                                elif(pix=="Grey"):
                                    pix += str(colorLevel)
                                else:
                                    pix = "Gray" + str(grayLumLevel) + hslColors[i] + str(colorLevel)
            
                            if(color.countColors(hslColors[i])>=2):
                                pix = color.reassignLevels(pix,red,green,blue)
                            return str(int(grayLevel)) + pix 
            except IndexError:
                print "rgb::calcColor2() out of range!\n"
                print "hueThresh.Size: {}".format(len(hueThresh))
    
from color import Color

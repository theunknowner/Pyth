import csv
import pkg_resources

from hsl import Hsl

class Rgb:
    __THRESH_IMPORTED__ = False
    __mainColors__ = [] # static variable
    __allColors__ = []  # static variable
    
    def __init__(self):
        if not Rgb.__THRESH_IMPORTED__:
            Rgb.__THRESH_IMPORTED__ = self.importThresholds()
        
    def getMainColorIndex(self,color):
        for i in range(len(Rgb.__mainColors__)):
            if(color==Rgb.__mainColors__[i]):
                return i
        return -1;
            
    def getColorIndex(self,color):
        for i in range(len(Rgb.__allColors__)):
            if(color==Rgb.__allColors__[i]):
                return i
        return -1;

    def importThresholds(self):
        if not self.__THRESH_IMPORTED__:
            res_mgr = pkg_resources.ResourceManager()
            folder = "Thresholds"
            file1_read = open(res_mgr.resource_filename(folder, "main_colors.csv"),"r")
            csv_file1 = csv.reader(file1_read)
            file2_read = open(res_mgr.resource_filename(folder, "colors.csv"),"r")
            csv_file2 = csv.reader(file2_read)
            for row in csv_file1:
                for i in range(len(row)):
                    Rgb.__mainColors__.append(row[i])
            file1_read.close()
            for row in csv_file2:
                for i in range(len(row)):
                    Rgb.__allColors__.append(row[i])
            file2_read.close()
            return True
        return True
        
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
        if(pos>=0):
            level = int(color[0:pos]);
        else:
            pos = color.find("Grey")
            if(pos>=0):
                level = int(color[0:pos])
            else:
                pos = color.find("Black");
                if(pos>=0):
                    level = int(color[0:pos])
                    
        return level
                
    def getColorLevel(self,pix):
        for i in range(len(Rgb.__mainColors__)):
            if (Rgb.__mainColors__[i]!="Gray"):
                pos = pix.find(Rgb.__mainColors__[i])
                if (pos>=0):
                    level = int(pix[pos+len(Rgb.__mainColors__[i]):len(pix)])
                    
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
        for i in range(0,len(Hsl.__hueThresh__)):
            try:
                if(HSL[0]>=Hsl.__hueThresh__[i][0] and HSL[0]<=Hsl.__hueThresh__[i][1]):
                    if(HSL[1]>=Hsl.__satThresh__[i][0] and HSL[1]<Hsl.__satThresh__[i][1]):
                        if(HSL[2]>=Hsl.__lumThresh__[i][0] and HSL[2]<Hsl.__lumThresh__[i][1]):
                            pix = Hsl.__hslColors__[i]
                            if(grayLevel==0):
                                pix = Hsl.__hslColors__[i] + str(int(colorLevel))
                        
                            else:
                                if(pix=="Black" or pix=="White"):
                                    pix += str(colorLevel)
                                elif(pix=="Grey"):
                                    pix += str(colorLevel)
                                else:
                                    pix = "Gray" + str(grayLumLevel) + Hsl.__hslColors__[i] + str(colorLevel)
            
                            if(color.countColors(Hsl.__hslColors__[i])>=2):
                                pix = color.reassignLevels(pix,red,green,blue)
                            return str(int(grayLevel)) + pix 
            except IndexError:
                print "rgb::calcColor2() out of range!\n"
                print "__hueThresh__.Size: {}".format(len(Hsl.__hueThresh__))
    
from color import Color

if __name__ == "__main__":
    rgb = Rgb()
    print rgb.getColorLevel("54Grey46Blue54Red45")

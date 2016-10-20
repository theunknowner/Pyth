import numpy as np
import csv
import pkg_resources
import traceback

class Hsl:
    __THRESH_IMPORTED__ = False
    H,S,L = 0.0, 0.0, 0.0
    __hslColors__ = []
    __hueThresh__ = []
    __satThresh__ = []
    __lumThresh__ = []
    
    def __init__(self):
        if not Hsl.__THRESH_IMPORTED__:
            Hsl.__THRESH_IMPORTED__ = self.importHslThresholds()
    
    def importHslThresholds(self):
        if not Hsl.__THRESH_IMPORTED__:
            res_mgr = pkg_resources.ResourceManager()
            folder = "Thresholds"
            file1_read = open(res_mgr.resource_filename(folder, "hslcolor-thresholds2.csv"),"r")
            csv_file1 = csv.reader(file1_read)
            
            next(csv_file1) #skips the header row
            for row in csv_file1:
                thresh = []
                thresh2 = []
                thresh3 = []
                for i in range(0,len(row)):
                    if(i==0): Hsl.__hslColors__.append(row[i])
                    if(i>=1 and i<=2): thresh.append(float(row[i]))
                    if(i>=3 and i<=4): thresh2.append(float(row[i]))
                    if(i>=5 and i<=6): thresh3.append(float(row[i]))
                Hsl.__hueThresh__.append(thresh)
                Hsl.__satThresh__.append(thresh2)
                Hsl.__lumThresh__.append(thresh3)
            
            file1_read.close()
            return True
        return True
    
    def minRGB(self,red,green,blue):
        if(red<=green and red<=blue): return red
        if(green<=blue and green<=red): return green
        return blue
        
    def maxRGB(self,red,green,blue):
        if(red>=green and red>=blue): return red
        if(green>=blue and green>=red): return green
        return blue
    
    def rgb2hsl(self,red,green,blue):
        HSL = [0.0,0.0,0.0];
        r = red/255.0;
        g = green/255.0;
        b = blue/255.0;
        _min = self.minRGB(r,g,b)
        _max = self.maxRGB(r,g,b)
        L = (_max+_min)/2.0;
        delta = _max-_min;
        if(delta==0):
            H, S = 0.0, 0.0
        else:
            if(L>0.5):
                S = (_max-_min)/(2.0-_max-_min)
            else:
                S = (_max-_min)/(_max+_min)
            if(_max==r):
                H = ((g-b)/delta)
            elif(_max==g):
                H = ((b-r)/delta) + 2.0
            else:
                H = ((r-g)/delta) + 4.0
                
            H *= 60.0
            if(H<0): H+=360
            
        HSL[0] = round(H); HSL[1] = S; HSL[2] = L;
        return HSL;
    
    def getHue(self):
        return round(Hsl.H)
    
    def getSat(self):
        return Hsl.S
    
    def getLum(self):
        return Hsl.L

    def calcLum(self,red,green,blue):
        r = red/255.0;
        g = green/255.0;
        b = blue/255.0;
        min_rgb = self.minRGB(r,g,b);
        max_rgb = self.maxRGB(r,g,b);
        lum = (max_rgb+min_rgb)/2.0;
        return lum;
    
    def getHslColor(self,hue, sat, lum, idx):
        colors = "NONE";
        try:
            for i in range(0,len(Hsl.__hslColors__)): 
                if(hue>=Hsl.__hueThresh__[i][0] and hue<=Hsl.__hueThresh__[i][1]):
                    if(sat>=Hsl.__satThresh__[i][0] and sat<Hsl.__satThresh__[i][1]):
                        if(lum>=Hsl.__lumThresh__[i][0] and lum<Hsl.__lumThresh__[i][1]):
                            colors = Hsl.__hslColors__[i]
                            idx = i
                            return colors, idx;
        except IndexError:
            print "hsl::getHslColor(); HSL does not exist!\n"
            print "HSL({0:.0f},{1:.2f},{2:.2f})\n".format(hue,sat,lum)
    
        return colors, idx;
        
    def getHslColorUsingIdx(self,idx):
        return Hsl.__hslColors__[idx]
        
    def hue2rgb(self,var1,var2,vH):
        if(vH<0): 
            vH+=1
        if(vH>1): 
            vH-=1
        if((6*vH)<1): 
            return (var1+(var2-var1)*6*vH)
        if((2*vH)<1): 
            return var2
        if((3*vH)<2): 
            return (var1+(var2-var1)*(0.666-vH)*6)
        return var1

    def hsl2rgb(self,hue,sat,lum):
        RGB = np.zeros(3)
        results = np.zeros(3)
        if(sat==0):
            RGB[0] = (round(lum * 255.0))
            RGB[1] = (round(lum * 255.0))
            RGB[2] = (round(lum * 255.0))
        else:
            temp1 = 0
            temp2 = 0
            if(lum<0.5):
                temp1 = lum*(1.0+sat);
            else:
                temp1 = (lum+sat) - (lum*sat);
                
            temp2 = (2.0*lum) - temp1;
            hue /= 360.0;
            RGB[0] = round(255*self.hue2rgb(temp2,temp1,(hue+(1./3.))));
            RGB[1] = round(255*self.hue2rgb(temp2,temp1,hue));
            RGB[2] = round(255*self.hue2rgb(temp2,temp1,(hue-(1./3.))));

        results[0] = int(RGB[0]);
        results[1] = int(RGB[1]);
        results[2] = int(RGB[2]);
        return results;
    
    def getIndex(self, hue, sat, lum):
        index = -1
        try:
            for i in range(0,len(Hsl.__hslColors__)):
                if(hue>=Hsl.__hueThresh__[i][0] and hue<=Hsl.__hueThresh__[i][1]):
                    if(sat>=Hsl.__satThresh__[i][0] and sat<Hsl.__satThresh__[i][1]):
                        if(lum>=Hsl.__lumThresh__[i][0] and lum<Hsl.__lumThresh__[i][1]):
                            index = i
                            return index
        except Exception:
            traceback.print_exc()
            print("hsl::getHslColor(); HSL does not exist!")
            print("HSL({:.0f},{:.2f},{:.2f})",hue,sat,lum)
        
        return index

import numpy as np
import csv

H,S,L = 0.0, 0.0, 0.0
hslColors = []
hueThresh = []
satThresh = []
lumThresh = []

class Hsl:
    __THRESH_IMPORTED = False
    def isThreshImported(self):
        return self.__THRESH_IMPORTED
    
    def setThreshImported(self,flag):
        self.__THRESH_IMPORTED = flag
        
    def importHslThresholds(self):
        foldername = "Thresholds/";
        filename = foldername+"hslcolor-thresholds2.csv";
        fsThresh = open(filename);
        csv_fsThresh = csv.reader(fsThresh)
        
        thresh = []
        thresh2 = []
        thresh3 = []
        next(csv_fsThresh) #skips the header row
        for row in csv_fsThresh:
            for i in range(0,len(row)):
                if(i==0): hslColors.append(row[i])
                if(i>=1 and i<=2): thresh.append(float(row[i]))
                if(i>=3 and i<=4): thresh2.append(float(row[i]))
                if(i>=5 and i<=6): thresh3.append(float(row[i]))
            hueThresh.append(thresh)
            satThresh.append(thresh2)
            lumThresh.append(thresh3)
            thresh, thresh2, thresh3 = [], [], []
        
        fsThresh.close()
        self.setThreshImported(True);
        return True;
    
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
        return round(H)
    
    def getSat(self):
        return S
    
    def getLum(self):
        return L

    def calcLum(self,red,green,blue):
        r = red/255.0;
        g = green/255.0;
        b = blue/255.0;
        min = self.minRGB(r,g,b);
        max = self.maxRGB(r,g,b);
        lum = (max+min)/2.0;
        return lum;
    
    def getHslColor(self,hue,sat,lum, idx):
        colors = "NONE";
        try:
            for i in range(0,len(hslColors)): 
                if(hue>=hueThresh[i][0] and hue<=hueThresh[i][1]):
                    if(sat>=satThresh[i][0] and sat<satThresh[i][1]):
                        if(lum>=lumThresh[i][0] and lum<lumThresh[i][1]):
                            colors = hslColors[i]
                            idx = i
                            return colors;
        except IndexError:
            print "hsl::getHslColor(); HSL does not exist!\n"
            print "HSL({0:.0f},{1:.2f},{2:.2f})\n".format(hue,sat,lum)
    
        return colors;
        
    def getHslColorUsingIdx(self,idx):
        return hslColors[idx]
        
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
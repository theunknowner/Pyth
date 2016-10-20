
from Shades.shades import Shades

class Color:
    def containsColor(self,*colors):
        argNum = len(colors)
        color1 = colors[0]
        for i in range(1,argNum):
            color2 = colors[i]
            if(color1.find(color2)>=0):
                return True
        
        return False
    
    def containsAllColor(self,*colors):
        argNum = len(colors)
        color1 = colors[0]
        for i in range(1,argNum):
            color2 = colors[i]
            if(color1.find(color2)<0):
                return False
            
        return True
    
    #returns the amount of time color contains main color
    def containsMainColor(self,color,mainColor):
        count = 0
        pos = color.find(mainColor)
        while pos>=0:
            count+=1
            pos+=len(mainColor)
            pos = color.find(mainColor,pos)
            
        return count
    
    def extractColorFromString(self,color,vecColor):
        for i in range(0,len(Rgb.__mainColors__)):
            if(self.containsMainColor(color, Rgb.__mainColors__[i])):
                vecColor.append(Rgb.__mainColors__[i])
                
    def isSameColor(self,color1,color2):
        vec1 = []
        vec2 = []
        self.extractColorFromString(color1, vec1)
        self.extractColorFromString(color2, vec2)
        if(len(vec1)!=len(vec2)): return False
        if(len(vec1)==1 and len(vec2)==1):
            if(vec1[0] == vec2[0]): return True
        
        if(len(vec1)>=3 and len(vec2)>=3):
            if(len(vec1)!=len(vec2)): return False
            
        for i in range(0,len(vec1)):
            for j in range(0,len(vec2)):
                if(vec1[i]!="Gray" and vec2[j]!="Gray"):
                    if(vec1[i]==vec2[j]): return True
                    
        return False
    
    def extractShade(self,pix):
        sh = Shades()
        shadeCount = sh.getShadeCount()
        shade = ""
        if(pix=="Zero"): return pix
        #if(pix.find("Gray")!=string::npos) return "Gray";
        for i in range(0,shadeCount):
            shade = sh.getShade(i)
            if(pix.find(shade)>=0):
                break
            
        return shade;
    
    #returns the amount of different colors in the string    
    def countColors(self,color):
        count=0
        for i in range(0,len(Rgb.__mainColors__)):
            if(color.find(Rgb.__mainColors__[i])>-1):
                count+=1
                
        return count
    
    #gets color and recalculates gray and color levels
    def reassignLevels(self,pix,r,g,b):
        rgb = Rgb()
        colorVec = []
        self.extractColorFromString(pix, colorVec)
        colorLevel = rgb.calcGrayLevel(r, g, b)
        
from rgb import Rgb
from rgb import Rgb
from hsl import Hsl

class PixelData:
    pixColor = ""
    rgbVec = [0, 0, 0]
    hslVec = [0.0, 0.0, 0.0]
    grayLevel = 0
    grayLumLevel = 0
    colorLevel = 0
    def __init__(self,pix):
        red = pix[2]
        green = pix[1]
        blue = pix[0]
        self.pixColor = self.determinePixelColor(red, green, blue)
        self.rgbVec[0] = red
        self.rgbVec[1] = green
        self.rgbVec[2] = blue
        
        hsl = Hsl()
        HSL = hsl.rgb2hsl(red, green, blue)
        self.hslVec[0] = HSL[0]
        self.hslVec[1] = round(HSL[1],2)
        self.hslVec[2] = round(HSL[2],2)
        
        rgb = Rgb()
        self.grayLevel = rgb.calcGrayLevel(red, green, blue)
        self.grayLumLevel = rgb.calcGrayLumLevel(red, green, blue)
        self.colorLevel = rgb.calcColorLevel(red, green, blue)
        
        
    def determinePixelColor(self,red,green,blue):
        rgb = Rgb()
        pixColor = rgb.checkBlack(red, green, blue)
        if(pixColor=="OTHER"): pixColor = rgb.calcColor(red,green,blue)
        return pixColor;
    
    def gray_lum_level(self):
        return self.grayLumLevel
    
    def gray_level(self):
        return self.grayLevel
    
    def color_level(self):
        return self.colorLevel
    
    def color(self):
        return self.pixColor
    
    def rgb(self):
        return self.rgbVec
    
    def hsl(self):
        return self.hslVec
        
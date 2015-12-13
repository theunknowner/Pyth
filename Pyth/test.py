from epoh import epoh
from xyz import Xyz
from cielab import CieLab
from cie import Cie
from hsl import Hsl, hueThresh, satThresh, lumThresh
from color import Color
from rgb import Rgb
import cv2
import numpy as np
from pixeldata import PixelData
from imagedata import ImageData
from functions import Functions
from Algorithms import jaysort as js

#img = cv2.imread("/home/jason/Desktop/workspace/test2.png",0)
#print img.shape[0] * img.shape[1]
arr = [5,1,3,8,2,9]
total = np.sum(arr)
print total

#px = img[0,0]
#print px
'''
rgb = Rgb()
hsl = Hsl()
color = Color()
rgb.importThresholds()
hsl.importHslThresholds()
#print rgb.calcColor(255, 0, 0)

hsl = Hsl()
xyz = Xyz()
lab = CieLab()
cie = Cie()
RGB1 = hsl.hsl2rgb(9, 0.32, 0.71)
RGB2 = hsl.hsl2rgb(14, 0.32, 0.70)
XYZ1 = xyz.rgb2xyz(RGB1[0], RGB1[1], RGB1[2])
XYZ2 = xyz.rgb2xyz(RGB2[0], RGB2[1], RGB2[2])
LAB1 = lab.xyz2lab(XYZ1[0],XYZ1[1],XYZ1[2])
LAB2 = lab.xyz2lab(XYZ2[0],XYZ2[1],XYZ2[2])
#print "LAB1:",LAB1
#print "LAB2:",LAB2
pix = [0,0,255]
pd = PixelData(pix)
print pd.hslVec
'''
'''
color = Color()
color1 = "BrownPink"
color2 = "Brown"
color3 = "Pink"
print color.containsAllColor(color1,color2,color3)
'''

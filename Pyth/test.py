from epoh import epoh
from xyz import Xyz
from cielab import CieLab
from cie import Cie
from hsl import Hsl
from color import Color
from rgb import Rgb
import cv2
import numpy as np
from ImageData.pixeldata import PixelData
from ImageData.imagedata import ImageData
from Algorithms import jaysort as js
from State.state import State
import functions as fn

'''#px = img[0,0]
#print px
rgb = Rgb()
hsl = Hsl()
color = Color()
rgb.importThresholds()
hsl.importHslThresholds()
#print rgb.calcColor(200, 155, 148)

hsl = Hsl()
xyz = Xyz()
lab = CieLab()
cie = Cie()
#RGB1 = hsl.hsl2rgb(9, 0.32, 0.71)
#RGB2 = hsl.hsl2rgb(14, 0.32, 0.70)
XYZ1 = xyz.rgb2xyz(199,158,152)
XYZ2 = xyz.rgb2xyz(195,149,145)
LAB1 = lab.xyz2lab(XYZ1[0],XYZ1[1],XYZ1[2])
LAB2 = lab.xyz2lab(XYZ2[0],XYZ2[1],XYZ2[2])
dE = cie.deltaE76(LAB1, LAB2);
print "LAB1:",LAB1
print "LAB2:",LAB2
print dE'''

'''
color = Color()
color1 = "BrownPink"
color2 = "Brown"
color3 = "Pink"
print color.containsAllColor(color1,color2,color3)
'''

vec = np.zeros((3,3),np.uint8)
vec[1,2] = 1
pts = cv2.findNonZero(vec)
print pts
from epoh import epoh
from xyz import Xyz
from cielab import CieLab
from cie import Cie
from hsl import Hsl, hueThresh, satThresh, lumThresh
from color import Color
from rgb import Rgb
import cv2
import numpy as np

rgb = Rgb()
hsl = Hsl()
color = Color()
rgb.importThresholds()
hsl.importHslThresholds()

'''
hsl = Hsl()
xyz = Xyz()
lab = CieLab()
cie = Cie()
RGB1 = hsl.hsl2rgb(24, 0.32, 0.71)
RGB2 = hsl.hsl2rgb(24, 0.35, 0.69)
XYZ1 = xyz.rgb2xyz(RGB1[0], RGB1[1], RGB1[2])
XYZ2 = xyz.rgb2xyz(RGB2[0], RGB2[1], RGB2[2])
LAB1 = lab.xyz2lab(XYZ1[0],XYZ1[1],XYZ1[2])
LAB2 = lab.xyz2lab(XYZ2[0],XYZ2[1],XYZ2[2])
print "RGB1:",RGB1
print "RGB2:",RGB2
print cie.deltaE76(LAB1, LAB2)
'''
'''
color = Color()
color1 = "BrownPink"
color2 = "Brown"
color3 = "Pink"
print color.containsAllColor(color1,color2,color3)
'''

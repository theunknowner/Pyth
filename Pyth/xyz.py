import numpy as np
import math

class Xyz:
    def rgb2xyz(self,red,green,blue):
        M = np.array([[0.4124564, 0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]])
        RGB = np.array([[red/255.0],[green/255.0],[blue/255.0]])
        for i in range(len(RGB)):
            if(RGB[i][0]>0.04045):
                RGB[i][0] = math.pow((RGB[i][0]+0.055)/1.055,2.4)
            else:
                RGB[i][0] /= 12.92
            RGB[i][0] *= 100.0
            
        XYZ = M.dot(RGB)
        XYZ = [XYZ[0][0],XYZ[1][0],XYZ[2][0]]
        return XYZ

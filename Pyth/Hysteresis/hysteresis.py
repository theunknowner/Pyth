#include "../Color/color.h"
#include "../Intensity/intensity.h"

from filedata import FileData
from rgb import Rgb
from hsl import Hsl

def hysteresis(fd):
    run(fd.getImage(),fd.ksize,fd.filename,fd);

def run(img, size, name, fd):
    #blur(img,img,size);
    rgb = Rgb()
    hsl = Hsl()
    HSL = []
    for i in range(0,img.shape[0]):
        colorWindow = []
        hslVec = []
        for j in range(0,img.shape[1]):
            r = img[i,j][2]
            g = img[i,j][1]
            b = img[i,j][0]
            HSL = hsl.rgb2hsl(r,g,b)
            h = HSL[0]
            s = round(HSL[1],2)
            l = round(HSL[2],2)
            pix = rgb.checkBlack(r,g,b)
            if(pix=="OTHER"):
                pix = rgb.calcColor(r,g,b)
                
            colorWindow.append(pix)
            hslStr = str(h)+";"+str(s)+";"+str(l)
            hslVec.push_back(hslStr);
        
        fd.windowVec.append(colorWindow);
        fd.hslMat.append(hslVec);
        
    #TODO
    Intensity in;
    in.calcMainColorMatrix(fd.getImage(), fd.windowVec, fd.hslMat, fd.filename, fd);
    #rule5(fd);
    cout << "Done!" << endl;
    colorWindow.clear();
    colorWindow.shrink_to_fit();
    hslVec.clear();
    hslVec.shrink_to_fit();

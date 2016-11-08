import cv2
import numpy as np
import math
import os
import traceback

def imgshow(src, flag=0, name=""):
    '''
    flag=0: keep window, flag=1: destroy window
    '''
    
    #static variables
    if "num" not in imgshow.__dict__:
        imgshow.num = 1
    if "setName" not in imgshow.__dict__:
        imgshow.setName = False
        
    if(name==""):
        name = "img" + str(imgshow.num)
        imgshow.num += 1
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    else:
        if not imgshow.setName:
            cv2.namedWindow(name,cv2.WINDOW_NORMAL)
            imgshow.setName = True
    cv2.imshow(name,src);
    cv2.waitKey(0)
    if(flag==1):
        cv2.destroyAllWindows()

#gets image filename from filepath
def getFileName(filename, end=""):
    delimit1 = '/'
    delimit2 = '.'
    name = filename;
    pos=0
    pos2=0
    if(filename.find(delimit2)>=0):
        for i in range(0,len(filename)):
            if(filename[i]==delimit1):
                pos=i+1
            if(filename[i]==delimit2):
                pos2=i
        name = filename[pos:pos2]
        if(end!=""):
            pos = name.find(end)
            name = name[0:pos]

    return name

def cropImage(src):
    ptX = ptY = 0
    roiWidth = roiHeight = 0

    for i in range(src.shape[1]):
        if(cv2.countNonZero(src[:,i])>0):
            ptX = i;
            roiWidth = src.shape[1]-ptX;
            break;
        
    for j in range(src.shape[0]):
        if(cv2.countNonZero(src[j,:])>0):
            ptY = j;
            roiHeight = src.shape[0]-ptY;
            break;
        
    img1 = src[ptY:ptY+roiHeight, ptX:ptX+roiWidth]
    for i in range(img1.shape[1]-1,-1,-1):
        if(cv2.countNonZero(img1[:,i])>0):
            roiWidth = i+1;
            break;
        
    for j in range(img1.shape[0]-1,-1,-1):   
        if(cv2.countNonZero(img1[j,:])>0):
            roiHeight = j+1;
            break;
    
    img2 = img1[0:roiHeight,0:roiWidth];
    return img2

def scaleDownImage(src, size):
    '''
    #! 8bit uchar image only
    '''
    scaledDownImage = np.zeros((size[1],size[0]),np.uint8)
    for x in range(0,size[1]):
        for y in range(0,size[0]):
            yd = int(math.ceil(float(y*src.shape[1])/size[0]))
            xd = int(math.ceil(float(x*src.shape[0])/size[1]))
            scaledDownImage[x,y] = src[xd,yd]

    return scaledDownImage;

def countGreaterEqual(value, *inputs):
    #//! returns number of variables greater than or equal to value
    arr = np.array(inputs)
    return np.sum(arr >= value)

def countGreater(value, *inputs):
    #//! returns number of variables greater than value
    arr = np.array(inputs)
    return np.sum(arr > value)

def countLesser(value, *inputs):
    #//! returns number of variables lesser than value
    arr = np.array(inputs)
    return np.sum(arr < value)
    
def countLesserEqual(value, *inputs):
    #//! returns number of variables lesser or equal to value
    arr = np.array(inputs)
    return np.sum(arr <= value)

def countEqual(value, *inputs):
    #//! returns number of variables equal to value
    arr = np.array(inputs)
    return np.sum(arr == value)

def getMin(vec):
    try:
        val = min(vec)
        min_index = vec.index(val)
        return val, min_index
    except Exception:
        return None, -1
    
def getMax(vec):
    try:
        val = max(vec)
        max_index = vec.index(val)
        return val, max_index
    except Exception:
        return None, -1
    
def countPositive(input):
    count = 0
    for i in range(0, len(input)):
        if(input[i]>0):
            count+=1
    return count

#//! gets the whole path of the directory the file is in
def getFolderPath(filename):
    path = os.path.dirname(filename)
    if path != "":
        path += "/"
    return path

def prepareImage(imgdata, size):
    input = imgdata.image()
    _size = (input.shape[1], input.shape[0])
    if(size[0]>0 and size[1]>0):
        _size = size
    crop_img = cropImage(input)
    # get multiplier base on the biggest side
    maxSize = max(crop_img.shape[1],crop_img.shape[0])
    multiplier = float(size[1]) / maxSize

    # assign new size using multiplier
    newRows = min(math.ceil(crop_img.shape[0] * multiplier),size[1])
    newCols = min(math.ceil(crop_img.shape[1] * multiplier),size[0])
    _size = (int(newCols), int(newRows))
    try:
        img = scaleDownImage(crop_img, _size)
    except Exception:
        traceback.print_exc()
        print("TestML::prepareImage(), runResizeImage() error!")
        print("Crop_img size: {}".format(crop_img.shape))
        print("Size: {}".format(_size))
        print("Max Size: {}".format(maxSize))
        print("Multiplier: {}".format(multiplier))
        exit(1)

    #centers the feature
    newImg = np.zeros((size[1],size[0]), img.dtype)
    centerSize = (int(math.floor(size[0]/2)), int(math.floor(size[1]/2)))
    center = (int(math.floor(img.shape[1]/2)), int(math.floor(img.shape[0]/2)))
    startPt = (centerSize[1]-center[1], centerSize[0]-center[0])
    try:
        newImg[startPt[0]:startPt[0]+img.shape[0], startPt[1]:startPt[1]+img.shape[1]] = img
    except Exception:
        traceback.print_exc()
        print("Orig Img Size: {}".format(crop_img.shape))
        print("Max Size: {}".format(maxSize))
        print("Multiplier: {}".format(multiplier))
        print("New Size: {}".format(_size))
        print("Img Size: {}".format(img.shape))
        print("New Img Size: {}".format(newImg.shape))
        print("CenterSize: {}".format(centerSize))
        print("Center: {}".format(center))
        print("StartPt: {}".format(startPt))
        exit(1)
    imgdata.extract(newImg,imgdata.name(),0,imgdata.getfolderPath())
    imgdata.prevSize(crop_img.shape)
    imgdata.readPrevSize()


if __name__ == "__main__":
    #print func.getFileName("/home/jason/Desktop/Programs/Crop_Features/acne1.png")
    img = cv2.imread("/home/jason/Desktop/Programs/Crop_Features/acne1_discrete.png",0)

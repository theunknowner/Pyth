import cv2
import numpy as np
import math

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
    
    
if __name__ == "__main__":
    #print func.getFileName("/home/jason/Desktop/Programs/Crop_Features/acne1.png")
    img = cv2.imread("/home/jason/Desktop/Programs/Crop_Features/acne1_discrete.png",0)

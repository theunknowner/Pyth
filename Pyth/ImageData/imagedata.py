from ImageData.pixeldata import PixelData
import numpy as np
import csv
import cv2
import functions as fn

class ImageData:
    file_path = ""
    folder_path = ""
    pixelVec = []
    dataVec = []
    hslVec = []
    imgSize = []
    prevImgSize = (0,0)
    imgRows = 0
    imgCols = 0
    matImage = []
    imgName = ""
    imgArea = 0
    
    def __init__(self,img,name="",option=0, filename=""):
        self.extract(img, name, option, filename)
        
    def extract(self,img,name="",option=0, filename=""):
        self.imgName = name
        self.folderPath = fn.getFolderPath(filename)
        self.file_path = filename
        self.matImage = np.copy(img)
        self.imgSize = (img.shape[1],img.shape[0])
        self.prevImgSize = (img.shape[1],img.shape[0])
        self.imgRows = img.shape[0]
        self.imgCols = img.shape[1]
        self.imgArea = cv2.countNonZero(img)
        
        if(option==1):
            self.pixelVec = np.zeros((self.imgRows,self.imgCols),object)
            self.dataVec = np.zeros((self.imgRows,self.imgCols),str)
            self.hslVec = np.zeros((self.imgRows,self.imgCols),str)
            h = 0.0
            s = 0.0
            l = 0.0
            hslStr = ""
            for i in range(self.imgRows):
                for j in range(self.imgCols):
                    pixData = PixelData(img[i,j])
                    self.pixelVec[i][j] = pixData
                    self.dataVec[i][j] = pixData.color();

                    h = pixData.hsl()[0];
                    s = pixData.hsl()[1];
                    l = pixData.hsl()[2];
                    hslStr = str(h)+";"+str(s)+";"+str(l);
                    self.hslVec[i][j] = hslStr;
            
    def name(self):
        return self.imgName
    
    def path(self):
        return self.file_path
    
    def getfolderPath(self):
        return self.folderPath
    
    def size(self):
        return self.imgSize
    
    def prevSize(self, shape=None):
        if shape!=None:
            self.prevImgSize = (shape[1], shape[0])
        return self.prevImgSize
    
    def rows(self):
        return self.imgRows
    
    def cols(self):
        return self.imgCols
    
    def image(self):
        return self.matImage
    
    def setImage(self,img):
        self.matImage = img
        
    def data_matrix(self):
        return self.dataVec
    
    def hsl_matrix(self):
        return self.hslVec
    
    def pixel(self,row,col):
        return self.pixelVec[row][col]
    
    def area(self):
        return self.imgArea
    
    def writePrevSize(self,filename):
        if(filename==""): filename = self.imgName
        filename += "_prev_size.csv"
        with open(filename, "w") as f:
            f.write("{},{}\n".format(self.prevImgSize[0], self.prevImgSize[1]))
        
    def readPrevSize(self):
        prevSizeFile = self.folderPath + self.name() + "_prev_size.csv"
        with open(prevSizeFile,"r") as csv_file:
            csv_read = csv.reader(csv_file)
            for row in csv_read:
                self.prevImgSize = (row[0], row[1])
            
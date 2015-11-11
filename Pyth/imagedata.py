from pixeldata import PixelData
import numpy as np
import csv

class ImageData:
    file_path = ""
    pixelVec = []
    dataVec = []
    hslVec = []
    imgSize = []
    prevImgSize = [0,0]
    imgRows = 0
    imgCols = 0
    matImage = []
    imgName = ""
    def __init__(self,img,name,option):
        self.extract(img, name, option)
        
    def extract(self,img,name,option):
        self.imgName = name
        self.matImage = np.copy(img)
        self.imgSize = [img.shape[0],img.shape[1]]
        self.prevImgSize = [img.shape[0],img.shape[1]]
        self.imgRows = img.shape[0]
        self.imgCols = img.shape[1]
        
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
    
    def size(self):
        return self.imgSize
    
    def prevSize(self):
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
    
    def writePrevSize(self,filename):
        if(filename==""): filename = self.imgName
        filename += "_prev_size.csv"
        csv_file = open(filename,"w")
        csv_file.write("%d,%d\n"%(self.prevImgSize[0],self.prevImgSize[1]))
        csv_file.flush()
        csv_file.close()
        
    def readPrevSize(self):
        filename = self.imgName+"_prev_size.csv"
        csv_file = open(filename)
        csv_read = csv.reader(csv_file)
        for row in range(csv_read):
            self.prevImgSize[0] = row[0]
            self.prevImgSize[1] = row[1]
        
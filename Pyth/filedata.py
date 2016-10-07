import numpy as np
import csv
import os

import functions as func
from color import Color
from rgb import Rgb

class FileData:
    file_path = ""
    dataMatrix = []
    imgSize = ()
    matImage = np.zeros((0,0))
    
    filename = ""
    oldMinShade = None
    newMinShade = None
    oldMaxShade = None
    newMaxShade = None
    minIntensity = None
    maxIntensity = None
    minOutlier = None
    maxOutlier = None
    totalShades = None
    range = None
    ksize = ()
    pt = None # current pt location of the filedata matrices
    localRatioScanSize = None
    localScanSize = None
    windowVec = []
    hslMat = []
    absRatioVec = []
    absRatioMat = []
    colorVec = []
    intensityVec = []
    smoothIntensityVec = []
    shadeVec = []
    rulesMat = []

    m_ContrastMat = []
    d_HslMat = []
    hslPtMat = []
    cumHslMat = []
    minMaxHslMat = []

    shadeColorCount = []
    maxHslValues = [] #max HSL values of each color
    
    def __init__(self, file_path):
        self.setFilePath(file_path)
        self.totalShades = 0
        self.minIntensity = 0
        self.maxIntensity = 0
        self.minOutlier = 0
        self.maxOutlier = 0
        self.ksize = (2,2)
        self.localRatioScanSize = 0
        self.localScanSize=0
        self.range=0
    
        #self.maxHslValues.resize(Rgb::allColors.size(),deque<double>(3,0));
    
    def setFilePath(self, file_path):
        self.file_path = file_path
        self.filename = func.getFileName(file_path)
    
    def getFileMatrix(self):
        # gets the imported data matrix by passing as reference
        return self.dataMatrix

    #sets image and size
    def setImage(self, img):
        self.matImage = img.copy()
        self.imgSize = img.shape

    def getImage(self):
        return self.matImage

    def writeFileMetaData(self):
        filename = self.filename + "_FileData.csv"
        with open(filename, "w") as f:
            f.write("Filename,{}\n".format(filename))
            f.write("Path,{}\n".format(self.file_path))
            f.write("oldMinShade,{}\n".format(self.oldMinShade))
            f.write("oldMaxShade,{}\n".format(self.oldMaxShade))
            f.write("newMinShade,{}\n".format(self.newMinShade))
            f.write("newMaxShade,{}\n".format(self.newMaxShade))
            f.write("minIntensity,{:.2f}\n".format(self.minIntensity))
            f.write("maxIntensity,{:.2f}\n".format(self.maxIntensity))
            f.write("totalShades,{}\n".format(self.totalShades))

    def loadFileMatrix(self, file_path):
        '''
        imports the matrix/csv files 
        '''
        fs = None
        try:
            fs = open(file_path,"r")
        except Exception:
            print("Failed to load File matrix!")
            return None
        
        fs_read = csv.reader(fs)
        vec = []
        for row in fs_read:
            for i in range(len(row)):
                row[i] = row[i][1:-2]
            self.dataMatrix.append(vec)
        fs.close()
        return self.dataMatrix

    def getFilesFromDirectory(self, directory):
        onlyfiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return onlyfiles

    def isFileExist(self, file):
        return os.path.isfile(file)

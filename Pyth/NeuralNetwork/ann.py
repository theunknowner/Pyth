import numpy as np
import cv2
import csv
import math
import traceback
import pkg_resources

import functions as fn
from filedata import FileData

class ANN:
    ''' 
    CALL TestML::clear() function at end of program
    to free dyanmic memory from ANN params
    '''
    
    __THRESH_IMPORTED__ = False
    __shapeNames__ = []
    __shapeNamesMap__ = {}
    __shapeNamesMap2__ = {}
    __img_size__ = [0,0]
    __shapeNames2__ = []
    __cvAnnVec__ = []
    __cvAnnVec2__ = {}
    __importParam__ = False
    __layers__ = []
    
    def __init__(self, _import=True):
        self.__importParam__ = _import
        if not self.__THRESH_IMPORTED__:
            self.__THRESH_IMPORTED__ = self.importThresholds()

    def importThresholds(self):
        try:
            res_mgr = pkg_resources.ResourceManager()
            folder = "Thresholds"
            fs = open(res_mgr.resource_filename(folder,"shape_names.csv"),"r")
            fs2 = open(res_mgr.resource_filename(folder,"ml_nn_size.csv"), "r")
            fs3 = open(res_mgr.resource_filename(folder,"shape_params.csv"),"r")
            fs4 = open(res_mgr.resource_filename(folder,"shape_names2.csv"),"r")
            fs5 = open(res_mgr.resource_filename(folder,"shape_params2.csv"),"r")
            fs6 = open(res_mgr.resource_filename(folder,"ml_layers.csv"),"r")
        except Exception:
            traceback.print_exc()
            return False
        
        fs_read = csv.reader(fs)
        for row in fs_read:
            self.__shapeNames__.append(row[0])
            self.__shapeNamesMap__[row[0]] = len(self.__shapeNames__)-1
        fs.close()
        
        fs2_read = csv.reader(fs2)
        for row in fs2_read:
            self.__img_size__[0] = int(row[0])
            self.__img_size__[1] = int(row[1])
        fs2.close()
        
        if(self.__importParam__):
            fs3_read = csv.reader(fs3)
            for row in fs3_read:
                param_path = "../"+row[0]
                ann = cv2.ANN_MLP()
                ann.load(param_path)
                self.__cvAnnVec__.append(ann)
        fs3.close()
        
        fs4_read = csv.reader(fs4)
        for row in fs4_read:
            self.__shapeNames2__.append(row[0])
            self.__shapeNamesMap2__[row[0]] = len(self.__shapeNames2__)-1
        fs4.close()
        
        if(self.__importParam__):
            fs5_read = csv.reader(fs5)
            num = 0
            for row in fs5_read:
                if(row[0].find(".xml")>=0):
                    param_path = "../"+row[0]
                    ann = cv2.ANN_MLP()
                    ann.load(param_path)
                    self.__cvAnnVec2__[num] = ann
                num+=1
        fs5.close()
        
        fs6_read = csv.reader(fs6)
        for row in fs6_read:
            self.setLayerParams(row)
            
        return True

    def getData(self):
        return self.data;
    
    
    def getLabels(self):
        return self.labels
    
    def setLayerParams(self, layers):
        for l in layers:
            self.__layers__.append(int(l))
    
    def prepareImage(self, sample, size):
        '''
        #crops and fixes binary sample data
        '''
        # size = [width,height] = (cols,rows)
        _size = [sample.shape[1],sample.shape[0]]
        if(size[0]>0 and size[1]>0):
            _size = size;
        #sample = this->convertToBinary(sample,0,255,0,1);
        crop_img = fn.cropImage(sample)
    
        # get multiplier base on the biggest side
        maxSize = max(crop_img.shape[1],crop_img.shape[0])
        multiplier = float(size[1]) / maxSize
    
        # assign new size using multiplier
        newRows = int(min(math.ceil(crop_img.shape[0] * multiplier),size[1]))
        newCols = int(min(math.ceil(crop_img.shape[1] * multiplier),size[0]))
        _size = [newCols,newRows]
        img = None
        try:
            #img = runResizeImage(crop_img,_size);
            img = fn.scaleDownImage(crop_img, _size);
        except Exception:
            traceback.print_exc()
            print("ANN::prepareImage(), runResizeImage() error!")
            print("Crop_img shape: {}".format(crop_img.shape))
            print("Size: {}".format(_size))
            print("Max Size: {}".format(maxSize))
            print("Multiplier: {}".format(multiplier))
            fn.imgshow(crop_img)
            exit(1)
            
        img[img > 0] = 255
        #centers the feature
        newImg = np.zeros((size[1],size[0]),img.dtype)
        centerSize = [int(math.floor(size[0]/2)), int(math.floor(size[1]/2))]
        center = [int(math.floor(img.shape[1]/2)), int(math.floor(img.shape[0]/2))]
        startPt = [centerSize[0]-center[0], centerSize[1]-center[1]]
        try:
            newImg[startPt[1]:startPt[1]+img.shape[0], startPt[0]:startPt[0]+img.shape[1]] = img
        except Exception:
            traceback.print_exc()
            print("Orig Img Shape: {}".format(crop_img.shape))
            print("Max Size: {}".format(maxSize))
            print("Multiplier: {}".format(multiplier))
            print("New Size: ()".format(_size))
            print("Img Shape: {}".format(img.shape))
            print("New Img Size: {}".format(newImg.shape))
            print("CenterSize: {}".format(centerSize))
            print("Center: {}".format(center))
            print("StartPt: {}".format(startPt))
            exit(1)
            
        return newImg;
    
    def prepareMatSamples(self, sampleVec):
        '''
        #converts vector Mat into sample Mat form
        '''
        rows = sampleVec[0].shape[0]
        cols = sampleVec[0].shape[1]
        if((rows*cols)==self.__layers__[0]):
            sampleSet = np.zeros((len(sampleVec),rows*cols),np.float32)
            for i in range(0,len(sampleVec)):
                for j in range(0,rows):
                    for k in range(0,cols):
                        samp = sampleVec[i]
                        sampleSet[i,k+j*cols] = samp[j,k]
            return sampleSet
        else:
            print("ANN::prepareMatSamples() error!")
            print("input size != rows*cols -> {} != {}".format(rows*cols,self.__layers__[0]))
            return None
    
    def importSamples(self, folder, size):
        samples = []
        fd = FileData()
        files = fd.getFilesFromDirectory(folder)
        #sort(files.begin(),files.end());
        for i in range(0,len(files)):
            filename = folder+files[i]
            img = cv2.imread(filename,0)
            if img:
                if(size!=[0,0]):
                    img = self.prepareImage(img,size)
                samples.push_back(img)
                
        return samples
    
    def importLabels(self, path):
        labels = []
        fs = None
        try:
            fs = open(path,"r")
        except Exception:
            print("Cannot open {}".format(path))
            exit(1)
            
        fs_read = csv.reader(fs)
        for row in fs_read:
            with open(row[0],"r") as fs2:
                fs2_read = csv.reader(fs2)
                for row2 in fs2_read:
                    fVec = []
                    for i in range(0,len(row2)):
                        fVec.append(float(row2[i]))
                    mLabels = np.zeros((1,len(fVec)),np.float32)
                    for j in range(0,len(fVec)):
                        mLabels[0][j] = fVec[j]
                    labels.append(mLabels)
        fs.close()
        return labels
    
    #! reads csv file containing path to files/folders
    #! used for importing training data to train ANN
    def importTrainingData(self, samplePath, labelsPath, size):
        with open(samplePath,"r") as fs:
            fs_read = csv.reader(fs)
            for row in fs_read:
                samples = self.importSamples(row[0], size)
            
            labels =  self.importLabels(labelsPath)
            if(len(samples)==len(labels)):
                mData = np.zeros((len(samples),samples[0].size),np.float32)
                mLabels = np.zeros((len(labels),labels[0].size),np.float32)
                x=0
                for i in range(0,len(samples)):
                    samp = samples[i]
                    lbl = labels[i]
                    for j in range(0,samp.shape[0]):
                        for k in range(0,samp.shape[1]):
                            mData[i,x] = samp[j,k]
                            x+=1
                    x=0
                    for n in range(0,lbl.shape[1]):
                        mLabels[i,n] = lbl[0,n]
                self.data = mData
                self.labels = mLabels
    
            else:
                print("TestML::importTrainingData() error!")
                print("Sample size != Label size\n")
                print("Sample size: {}".format(len(samples)))
                print("Label size: {}".format(len(labels)))
                exit(1)
    
    def getShapeName(self, num):
        return self.__shapeNames__[num]
    
    def numOfShapes(self):
        return len(self.__shapeNames__)
    
    def getSize(self):
        return self.__img_size__
    
    def getShapeIndex(self, shape):
        if(self.__shapeNamesMap__.has_key(shape)):
            return self.__shapeNamesMap__[shape]
        return -1
    
    def getShapeIndex2(self, shape):
        if(self.__shapeNamesMap2__.has_key(shape)):
            return self.__shapeNamesMap2__[shape]
        return -1
    
    #! NN3
    def runANN2(self, sampleVec):
        results = np.zeros((len(sampleVec),len(self.__cvAnnVec__)),np.float32)
        for i in range(0,len(self.__cvAnnVec__)):
            sample_set  = self.prepareMatSamples(sampleVec)
            retVal, score = self.__cvAnnVec__[i].predict(sample_set)
            for j in range(0, len(sampleVec)):
                results[j,i] = score[j][0]

        return results
    
    #! NN3
    def getShapeName2(self, num):
        return self.__shapeNames2__[num]
    
    def getIndexContainingShape(self, shape):
        '''
        #! NN3
        #! returns first index containing shape
        '''
        for i in range(0,len(self.__shapeNames__)):
            if(self.__shapeNames__[i].find(shape)>=0):
                return i;
        return -1;
    
    def runANN2b(self, sampleVec, nnShape):
        '''
        #! NN3 Disc/Donut Comp/Incomp
        #! 0=Disc; 1=Donut; 3=REI/Fused-Donuts
        '''
        sample_set  = self.prepareMatSamples(sampleVec)
        retVal, results = self.__cvAnnVec2__[nnShape].predict(sample_set)
        return results
    
    #! free memory
    #*** MUST BE CALLED AT END OF PROGRAM ***
    def clear(self):
        del self.__cvAnnVec__[:]
    
            
if __name__ == "__main__":
    ann = ANN()
    img = cv2.imread("/home/jason/Desktop/workspace/pic1.png",0)
    img2 = ann.prepareImage(img, [40,40])
    sampleVec = []
    sampleVec.append(img2)
    sampleVec.append(img2)
    results = ann.runANN2b(sampleVec,1)
    print results
    
    
    

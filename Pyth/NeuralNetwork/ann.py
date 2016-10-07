import numpy as np
import cv2
import csv
import math
import traceback

import functions as fn
from filedata import FileData

THRESH_IMPORTED = False
PARAM_PATH = "../Thresholds/param-Excavated.xml"
shapeNames = []
shapeNamesMap = {}
shapeNamesMap2 = {}
img_size = [0,0]
shapeNames2 = []
cvAnnVec = []
cvAnnVec2 = {}
importParam = False

class ANN:
    ''' 
    CALL TestML::clear() function at end of program
    to free dyanmic memory from ANN params
    '''
    
    def __init__(self, _import=True):
        global THRESH_IMPORTED
        global importParam
        importParam = _import
        if not THRESH_IMPORTED:
            THRESH_IMPORTED = self.importThresholds()

    def importThresholds(self):
        try:
            fs = open("../Thresholds/shape_names.csv","r")
            fs2 = open("../Thresholds/ml_nn_size.csv", "r")
            fs3 = open("../Thresholds/shape_params.csv","r")
            fs4 = open("../Thresholds/shape_names2.csv","r")
            fs5 = open("../Thresholds/shape_params2.csv","r")
        except Exception:
            print("ANN::importThreshold() failed, shape_names.csv does not exist!")
            return False
        
        fs_read = csv.reader(fs)
        for row in fs_read:
            shapeNames.append(row[0])
            shapeNamesMap[row[0]] = len(shapeNames)-1
        fs.close()
        
        fs2_read = csv.reader(fs2)
        for row in fs2_read:
            img_size[0] = int(row[0])
            img_size[1] = int(row[1])
        fs2.close()
        
        if(importParam):
            fs3_read = csv.reader(fs3)
            for row in fs3_read:
                ann = cv2.ANN_MLP()
                ann.load(row[0])
                cvAnnVec.append(ann)
        fs3.close()
        
        fs4_read = csv.reader(fs4)
        for row in fs4_read:
            shapeNames2.append(row[0])
            shapeNamesMap2[row[0]] = len(shapeNames2)-1
        fs4.close()
        
        if(importParam):
            fs5_read = csv.reader(fs5)
            num = 0
            for row in fs5_read:
                if(row[0].find(".xml")>=0):
                    ann = cv2.ANN_MLP()
                    ann.load(row[0])
                    cvAnnVec2[num] = ann
                num+=1
        fs5.close()
        return True

    def getData(self):
        return self.data;
    
    
    def getLabels(self):
        return self.labels
    
    def setLayerParams(self, layers):
        self.layers = layers
    
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
        if((rows*cols)==self.layers[0,0]):
            sampleSet = np.zeros((len(sampleVec),rows*cols),np.float32)
            for i in range(0,len(sampleVec)):
                for j in range(0,rows):
                    for k in range(0,cols):
                        samp = sampleVec[i]
                        sampleSet[i,k+j*cols] = samp[j,k]
            return sampleSet
        else:
            print("ANN::prepareMatSamples() error!")
            print("input size != rows*cols")
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
    
    def importLabels(self, path, labels):
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
'''  
    Mat TestML::runANN(String param, vector<Mat> sampleVec) {
        CvANN_MLP ann;
        ann.load(param.c_str());
        Mat layers = ann.get_layer_sizes();
        this->setLayerParams(layers);
        Mat sample_set = this->prepareMatSamples(sampleVec);
        Mat results;
        ann.predict(sample_set,results);
        /*for(int i=0; i<results.rows; i++) {
            printf("Sample: %d, ",i+1);
            cout << results.row(i) << endl;
        }*/
        return results;
    }
    
    //! reads csv file containing path to files/folders
    //! used for importing training data to train ANN
    void TestML::importTrainingData(String samplePath, String labelsPath, Size size) {
        fstream fs(samplePath);
        if(fs.is_open()) {
            String folder;
            vector<Mat> samples;
            vector<Mat> labels;
            while(getline(fs,folder)) {
                this->importSamples(folder,samples,size);
            }
            this->importLabels(labelsPath,labels);
            if(samples.size()==labels.size()) {
                Mat mData(samples.size(),samples.at(0).total(),CV_32F,Scalar(0));
                Mat mLabels(labels.size(),labels.at(0).cols,CV_32F,Scalar(0));
                int x=0;
                for(unsigned int i=0; i<samples.size(); i++) {
                    Mat samp = samples.at(i);
                    Mat lbl = labels.at(i);
                    //samp = this->tempFixPrepareImg(samp);
                    for(int j=0; j<samp.rows; j++) {
                        for(int k=0; k<samp.cols; k++) {
                            if(samp.type()==CV_8U)
                                mData.at<float>(i,x) = samp.at<uchar>(j,k);
                            else if(samp.type()==CV_32S)
                                mData.at<float>(i,x) = samp.at<int>(j,k);
                            if(samp.type()==CV_32F)
                                mData.at<float>(i,x) = samp.at<float>(j,k);
                            x++;
                        }
                    }
                    x=0;
                    for(int n=0; n<lbl.cols; n++) {
                        mLabels.at<float>(i,n) = lbl.at<float>(0,n);
                    }
                }
                this->data = mData;
                this->labels = mLabels;
    
            }
            else {
                printf("TestML::importTrainingData() error!\n");
                printf("Sample size != Label size\n");
                printf("Sample size: %lu\n",samples.size());
                printf("Label size: %lu\n",labels.size());
                fs.close();
                exit(1);
            }
            fs.close();
        }
    }
    
    String TestML::getShapeName(int num) {
        return TestML::shapeNames.at(num);
    }
    
    int TestML::numOfShapes() {
        return TestML::shapeNames.size();
    }
    
    Size TestML::getSize() {
        return TestML::img_size;
    }
    
    int TestML::getShapeIndex(String shape) {
        if(TestML::shapeNamesMap.find(shape)!=TestML::shapeNamesMap.end()) {
            return TestML::shapeNamesMap[shape];
        }
        return -1;
    }
    
    int TestML::getShapeIndex2(String shape) {
        if(TestML::shapeNamesMap2.find(shape)!=TestML::shapeNamesMap2.end()) {
            return TestML::shapeNamesMap2[shape];
        }
        return -1;
    }
    
    //! NN3
    Mat TestML::runANN2(vector<Mat> sampleVec) {
        Mat results = Mat::zeros(1,TestML::cvAnnVec.size(),CV_32F);
        Mat score;
        for(unsigned int i=0; i<TestML::cvAnnVec.size(); i++) {
            //String param = TestML::shapeParamPaths.at(i);
            //ann.load(param.c_str());
            //Mat layers = ann.get_layer_sizes();
            Mat layers = TestML::cvAnnVec.at(i)->get_layer_sizes();
            this->setLayerParams(layers);
            Mat sample_set  = this->prepareMatSamples(sampleVec);
            //ann.predict(sample_set,score);
            TestML::cvAnnVec.at(i)->predict(sample_set,score);
            results.at<float>(0,i) = score.at<float>(0,0);
        }
        return results;
    }
    
    //! NN3
    String TestML::getShapeName2(int num) {
        return TestML::shapeNames2.at(num);
    }
    
    //! NN3
    //! returns first index containing shape
    int TestML::getIndexContainingShape(String shape) {
        for(unsigned int i=0; i<TestML::shapeNames.size(); i++) {
            if(TestML::shapeNames.at(i).find(shape)!=string::npos) {
                return i;
            }
        }
        return -1;
    }
    
    //! NN3 Disc/Donut Comp/Incomp
    //! 0=Disc; 1=Donut; 3=REI/Fused-Donuts
    Mat TestML::runANN2b(vector<Mat> sampleVec, int nnShape) {
        Mat results;
        //for(unsigned int i=0; i<TestML::cvAnnVec2.size(); i++) {
        Mat layers = TestML::cvAnnVec2.at(nnShape)->get_layer_sizes();
        this->setLayerParams(layers);
        Mat sample_set  = this->prepareMatSamples(sampleVec);
        TestML::cvAnnVec2.at(nnShape)->predict(sample_set,results);
        //}
        return results;
    }
    
    //! free memory
    /*** MUST BE CALLED AT END OF PROGRAM ***/
    void TestML::clear() {
        for(unsigned int i=0; i<TestML::cvAnnVec.size(); i++) {
            delete TestML::cvAnnVec.at(i);
            TestML::cvAnnVec.at(i) = NULL;
        }
    }
    
'''
            
if __name__ == "__main__":
    ann = ANN()
    img = cv2.imread("/home/jason/Desktop/Programs/Crop_Features/acne1_discrete.png",0)
    img2 = ann.prepareImage(img, [40,40])
    fn.imgshow(img2)

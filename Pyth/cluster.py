import numpy as np
import math
import random
import cv2

from Algorithms.jaysort import jaysort

class Cluster:
    dataRange = 0.0
    clusterCount = 0.0
    dataVec = [] #holds all sample data
    uniqueSamples = [] #count of each unique sample
    sampleData =  [] #unique samples being considered, usually when count>0

    samples = np.zeros((0,0),np.float32)
    centerCount = []
    ranges = np.zeros((0,0),float)
    labels = np.zeros((0,0),int)
    centers = np.zeros((0,0),float)
    
    def kmeansClusterGeneric(self, src, maxVal=0):
        ''' 
        returns mask using kmeans clustering,
        set maxVal>0 for custom max value of samples
        '''
        #get max value of sample data
        if(maxVal==0):
            for i in range(0,src.shape[0]):
                for j in range(0,src.shape[1]):
                    if(src[i,j]>maxVal):
                        maxVal = round(src[i,j])
                        
        dataVec =  [] #holds all sample data
        uniqueSamples = [0]*(maxVal+1) #count of each unique sample
        sampleData = [] #unique samples being considered, usually when count>0
        ptVec = [] #holds (col,row) of each sample
        for i in range(0,src.shape[0]):
            for j in range(0,src.shape[1]):
                val = src[i,j];
                if(val>=0):
                    #storing all sample data when conditions are met
                    dataVec.append(val)
                    #counting amount of each unique sample
                    uniqueSamples[val]+=1
                    #storing point of each sample data
                    ptVec.append((j,i));
                    
        #getting unique samples that are being considered, usually when count>0
        for i in range(0,len(uniqueSamples)):
            if(uniqueSamples[i]>0):
                sampleData.append(i);
                
        #converting deque -> Mat
        samples = np.zeros((len(dataVec),1),np.float32)
        for i in range(0,len(dataVec)):
            samples[i,0] = dataVec[i]
    
        dataRange = sampleData[-1] - sampleData[0]
        clusterCount = round(math.sqrt(dataRange/2)) if round(math.sqrt(dataRange/2)) < len(sampleData) else len(sampleData)
        clusterCount = min(11,clusterCount)
        attempts = 5
        print("Min Val: {}, Max Val: {}, Range: {}\n".format(sampleData.front(),sampleData.back(),dataRange))
        print "Initial clusters:", clusterCount
        print "Input size:", dataVec.size(), "/" , src.size
        print "Unique Samples:", maxVal
        print "Unique samples considered:", len(sampleData)-1
        compactness, labels, centers = cv2.kmeans(samples,clusterCount,(cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 10000, 0.0001),attempts,cv2.KMEANS_PP_CENTERS)
        print "Compactness:", compactness
        centerCount = [0]*clusterCount
        ranges = np.zeros((clusterCount,2))
        for i in range(0,ranges.shape[0]):
            for j in range(0,ranges.shape[1]):
                if(j==0):
                    ranges[i,j] = len(uniqueSamples)
                elif(j==1):
                    ranges[i,j] = 0;
                    
        sortedVec, origPos = jaysort(centers);
        
        for i in range(0,labels.shape[0]):
            idx = labels[i,0]
            for j in range(0,len(origPos)):
                if(idx==origPos.at<int>(j,0)):
                    idx = j
                    labels[i,0] = idx;
                    break
                
            centerCount[idx]+=1
            if(dataVec[i] > ranges[idx,1]):
                ranges[idx,1] = dataVec[i]
            if(dataVec[i] < ranges[idx,0]):
                ranges[idx,0] = dataVec[i]
            
        for i in range(0,len(centers)):
            print("{} - {} - Min: {}, Max: {}".format(centers[i,0],centerCount[i],ranges[i,0],ranges[i,1]))
            
        result = np.zeros(src.shape,np.uint8)
        #idxThresh = math.ceil(clusterCount*0.5) #! threshold for cluster filtering
        idxThresh = 4
        for i in range(len(ptVec)):
            idx = labels[i]
            if(idx>=idxThresh):
                result[ptVec[i]] = 255
                
        #this->centers = centers;
        #this->writeClusterData(centers,"centers",FLOAT);
        #result = this->colorClusters(src,centers,labels,ptVec);
        return result;

    def writeClusterData(self, src, name):
        filename = name+".csv"
        with open(filename,"w") as f:
            for i in range(0,src.shape[0]):
                for j in range(0,src.shape[1]):
                    f.write("{}".format(src[i,j]))
        
                f.write("\n")

    def colorClusters(self, src, centers, labels, ptVec):
        results = np.zeros((src.shape[0],src.shape[1],3),np.uint8)
        colorVec = []
        for i in range(0,len(centers)):
            color = [random.randint(0,255),random.randint(0,255),random.randint(0,255)]
            colorVec.append(color);
            print("[{}, {}, {}]".format(color[2],color[1],color[0]))
            
        for i in range(0,len(ptVec)):
            idx = labels[i]
            results[ptVec[i]] = colorVec[idx];
            
        return results;

    def kmeansCluster(self, src, clusters, minVal=0, maxVal=225):
        '''
        input: ndarray(uint8 image) or a list
        returns the centers in Mat form
        '''
        data_vec = []
        if(type(src)==np.ndarray and src.dtype == np.uint8):
            for i in range(0,src.shape[0]):
                for j in range(0,src.shape[1]):
                    val = src[i,j]
                    if(val>=minVal and val <=maxVal):
                        data_vec.append(float(val));
        else:
            data_vec = src
        
        if(clusters==0): clusters = 3
        self.samples = np.zeros((len(data_vec),1),np.float32)
        data_vec.sort()
        for i in range(0,self.samples.shape[0]):
            self.samples[i,0] = data_vec[i]
            
        #cv::sort(samples,samples,CV_SORT_EVERY_COLUMN+CV_SORT_ASCENDING);
        self.dataRange = data_vec[-1] - data_vec[0]
        self.clusterCount = clusters
        attempts = 5
        compactness, self.labels, self.centers = cv2.kmeans(self.samples,self.clusterCount,(cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 10000, 0.0001), attempts, cv2.KMEANS_PP_CENTERS)
        self.centerCount = [0]*self.clusterCount
        self.ranges = np.zeros((self.clusterCount,2))
        for i in range(0,self.ranges.shape[0]):
            for j in range(0,self.ranges.shape[1]):
                if(j==0):
                    self.ranges[i][j] = data_vec[-1]
                elif(j==1):
                    self.ranges[i][j] = 0
                    
        sortedVec, origPos = jaysort(self.centers);
        for i in range(0, len(self.labels)):
            idx = self.labels[i]
            for j in range(0,len(origPos)):
                if(idx==origPos[j]):
                    idx = j
                    self.labels[i][0] = idx
                    break
                
            self.centerCount[idx]+=1
            if(data_vec[i] > self.ranges[idx][1]):
                self.ranges[idx,1] = data_vec[i]
            if(data_vec[i] < self.ranges[idx][0]):
                self.ranges[idx,0] = data_vec[i]
    
        return self.centers

    def getSizeOfCluster(self, clusterNum):
        '''
        returns the number of points in the specified cluster
        '''
        count = 0
        try:
            count = self.centerCount[clusterNum]
        except Exception:
            print("Cluster::getCenterCount() out of range!")
            print("Input: {}".format(clusterNum))
            print("Num. of clusters: {}".format(len(self.centers)))
            exit(1)
            
        return count

    def getNumOfClusters(self):
        '''
        returns the number of clusters
        '''
        return len(self.centers)

    def getMin(self, clusterNum):
        '''
        returns the min of specified cluster
        '''
        min_val = 0
        try:
            min_val = self.ranges[clusterNum][0]
        except Exception:
            print("Cluster::getMin() out of range!")
            print("Input: {}".format(clusterNum))
            print("Num. of clusters: {}".format(len(self.centers)))
            exit(1)
            
        return min_val

    #! returns the max of specified cluster
    def getMax(self, clusterNum):
        max_val = 0
        try:
            max_val = self.ranges[clusterNum][0]
        except Exception:
            print("Cluster::getMax() out of range!")
            print("Input: {}".format(clusterNum))
            print("Num. of clusters: {}".format(len(self.centers)))
            exit(1)

        return max_val

    def getCenter(self, clusterNum):
        return self.centers[clusterNum][0]

    def printInfo(self):
        print("Min Val: {}, Max Val: {}, Range: {}".format(self.samples[0,0],self.samples[-1,0],self.dataRange))
        print("Initial clusters: {}".format(self.clusterCount))
        print("Input size: {}".format(self.samples.shape[0]))
        for i in range(0,len(self.centers)):
            print("{} - {} - Min: {}, Max: {}".format(self.centers[i,0],self.centerCount[i],self.ranges[i][0],self.ranges[i][1]))

if __name__ == "__main__":
    clst = Cluster()
    img = cv2.imread("/home/jason/Desktop/Programs/Crop_Features/acne1_discrete.png",0)
    centers = clst.kmeansCluster(img, 4, 0, 255)
    print centers
    

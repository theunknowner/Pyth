
import cv2

from NeuralNetwork.ann import ANN


class SubIslands:
    islArea = 0
    islShape = None
    islShapeName = ""
    islandImg = [[]]
    nn_prepared_img = [[]]
    NN_Results = []
    NN_Score = 0.0
    coordMap = {}
    
    #/************** PRIVATE FUNCTIONS ******************/
    def determineIslandShape(self, subIslandImg):
        ml = ANN()
        sampleVec = []
        sample = subIslandImg.copy()
        sample *= 255
        sample = ml.prepareImage(sample,ml.getSize())
        sampleVec.append(sample)
    
        results = ml.runANN2(sampleVec)
        results2 = ml.runANN2b(sampleVec,3) #Fused-Donut NN3
        cv2.hconcat(results,results2,results)
        self.NN_Results = results
        max_elem = max(results)
        labelNum = results.index(max_elem)
        thresh = 0.0
        if(max_elem<thresh):
            labelNum = ml.getShapeIndex2("Default")
        shapeName = ml.getShapeName2(labelNum)
        if(labelNum==0 or labelNum==1):
            results = ml.runANN2b(sampleVec,labelNum)
            if(results[0,0]>0.0):
                shapeName = "Comp-" + shapeName;
            else:
                shapeName = "Incomp-" + shapeName
        labelNum = ml.getShapeIndex(shapeName)
        self.NN_Score = max_elem
        self.islShape = labelNum
        self.islShapeName = shapeName
        self.nn_prepared_img = sample
    
    #get coordinates of non-zero pixels
    def getIslandPoints(self, islandImg):
        nonZeroCoord = cv2.findNonZero(islandImg) #this function returns points in ndarray form [x,y]
        # gets the center of mass and stores all the coords in a map
        for i in range(0,nonZeroCoord.size):
            x = nonZeroCoord[i][0][0]
            y = nonZeroCoord[i][0][1];
            coords = str(y)+","+ str(x)
            if not self.coordMap.has_key(coords):
                self.coordMap[coords] = (y,x)
    
    #/************** PUBLIC FUNCTIONS *******************/
    
    #//! class is used to store the black discs subfeatures inside a feature
    def __init__(self, subIslandImg):
        self.islArea = cv2.countNonZero(subIslandImg)
        self.islandImg = subIslandImg
        self.determineIslandShape(subIslandImg)
        self.getIslandPoints(subIslandImg)
    
    def area(self) :
        return self.islArea
    
    def image(self):
        return self.islandImg
    
    def nn_image(self):
        return self.nn_prepared_img
    
    def shape(self):
        return self.islShape
    
    def shape_name(self):
        return self.islShapeName
    
    def nn_results(self):
        return self.NN_Results
    
    def nn_score(self):
        return self.NN_Score
    
    def coordinates(self):
        return self.coordMap
    
    def containsCoordinates(self,coords,pt=()):
        if(coords!=""):
            if(self.coordMap.has_key(coords)):
                return True
            return False
        
        coords = str(pt[0]) + "," + str(pt[1])
        if(self.coordMap.has_key(coords)):
            return True
    
        return False;
    
    def isEmpty(self):
        return self.islandImg.any()

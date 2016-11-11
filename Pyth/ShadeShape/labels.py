import traceback

import statsign
import functions as fn

class Labels:
    #/************************* PRIVATE FUNCTIONS ****************************/
    def calcTotalArea(self):
        self.labelTotalArea = 0
        for value in self.labelMap.values():
            self.labelTotalArea += value[0]
    
    #/************************* PUBLIC FUNCTIONS *****************************/
    def __init__(self, islandVec, totalArea, name=""):
        self.labelMap = {} # dict of tuples
        self.labelShapeShiftMap = {}
        self.labelShapeNumMap = {}
        self.labelPrevShapeNumMap = {}
        self.labelShadeLevelMap = {}
        self.labelStatSignMap = {}
        self.labelIslandMap = {}
        self.labelShadeLumMap = {}
        self.labelName = ""
        self.labelTotalArea = 0
        
        self.create(islandVec,totalArea,name)
        self.calcTotalArea()
    
    def create(self, islandVec, totalArea, name=""):
        self.labelName= name
        for i in range(0, len(islandVec)):
            for j in range(0, len(islandVec[i])):
                for k in range(0, len(islandVec[i][j])):
                    isl = islandVec[i][j][k]
                    shape = self.getShapeName(i)
                    label = str(i)+"_"+shape+"_s"+ str(j)+"_"
                    label += fn.addDigitsForLabel(k,"0",3)
                    isl.labelName(label)
    
                    if not self.labelMap.has_key(label):
                        area = islandVec[i][j][k].area()
                        relArea = float(area) / totalArea
                        self.labelMap[label] = (area,relArea)
                        self.labelShapeShiftMap[label] = islandVec[i][j][k].isShapeShifted()
                        self.labelShapeNumMap[label] = islandVec[i][j][k].shape();
                        self.labelPrevShapeNumMap[label] = islandVec[i][j][k].prevShape()
                        self.labelShadeLevelMap[label] = j
                        self.labelIslandMap[label] = islandVec[i][j][k]
                        self.labelShadeLumMap[label] = isl.shade()
    
                        #> to calculate the statistical signature of each label
                        if(label.find("Excavated")>=0 or label.find("Default")>=0):
                            statSignVec = statsign.create(isl.nn_image(),relArea)
                            self.labelStatSignMap[label] = statSignVec
    
                    else:
                        traceback.print_exc()
                        print("Label: {}".format(label))
                        exit(1)
    
    def getMap(self):
        return self.labelMap
    
    def getShadeLevelMap(self):
        return self.labelShadeLevelMap
    
    def getShapeMap(self):
        return self.labelShapeNumMap
    
    def setLabels(self, labels):
        self.labelMap = labels
        self.calcTotalArea()
    
    def area(self, label=None, num=None):
        assert(label!=None or num!=None)
        if label!=None and self.labelMap.has_key(label):
            return self.labelMap[label][0]
        if(num!=None):
            for i,key in enumerate(self.labelMap):
                if(i==num):
                    return self.labelMap[key][0]
        return 0
    
    def totalArea(self):
        return self.labelTotalArea
    
    def relativeArea(self, label=None, num=None):
        assert(label!=None or num!=None)
        if label!=None and self.labelMap.has_key(label):
            return self.labelMap[label][1]
        if(num!=None):
            for i,key in enumerate(self.labelMap):
                if(i==num):
                    return self.labelMap[key][1]
        return 0.0
    
    def size(self):
        return len(self.labelMap)
    
    def at(self, num):
        """
        Returns the key of the label map given the index
        """
        for i,key in enumerate(self.labelMap):
            if(i==num):
                return key
        return ""
    
    def name(self):
        return self.labelName
    
    #//! prints the labels and their areas;
    def printLabels(self):
        for i,key in enumerate(self.labelMap):
            print("{}) {}: {}({:0.6f})".format(i, key, self.labelMap[key][0], self.labelMap[key][1]))
    
    def getIndex(self, label):
        if self.labelMap.has_key(label):
            return self.labelMap.keys().index(label)
        return -1
    
    def getShape(self, label):
        for i in range(0, len())
        for(unsigned int i=0; i<ShapeMatch::shapeNames.size(); i++) {
            if(label.find(this->getShapeName(i))!=string::npos) {
                return this->getShapeName(i);
            }
        }
        return "";
    }
    
    int Labels::getShade(String label) {
        if(this->labelShadeLumMap.find(label)!=this->labelShadeLumMap.end()) {
            return this->labelShadeLumMap.at(label);
        }
        return -1;
    }
    
    int Labels::getShadeLevel(String label) {
        if(this->labelShadeLevelMap.find(label)!=this->labelShadeLevelMap.end()) {
            return this->labelShadeLevelMap.at(label);
        }
    
        return -1;
    }
    
    void Labels::setShadeLevel(String label, int level) {
        this->labelShadeLevelMap[label] = level;
    }
    
    
    bool Labels::isShapeShifted(String label) {
        if(this->labelShapeShiftMap.find(label)!=this->labelShapeShiftMap.end()) {
            return this->labelShapeShiftMap.at(label);
        }
    
        return false;
    }
    
    int Labels::getShapeNum(String label) {
        if(this->labelShapeNumMap.find(label)!=this->labelShapeNumMap.end()) {
            return this->labelShapeNumMap.at(label);
        }
    
        return -1;
    }
    
    int Labels::getPrevShapeNum(String label) {
        if(this->labelPrevShapeNumMap.find(label)!=this->labelPrevShapeNumMap.end()) {
            return this->labelPrevShapeNumMap.at(label);
        }
    
        return -1;
    }
    
    //! returns the statistical signature of each label/urn/feature.
    //! The total number of balls is stored in statSign[0].
    vector<float> Labels::getStatSign(String label) {
        if(this->labelStatSignMap.find(label)!=this->labelStatSignMap.end()) {
            return this->labelStatSignMap.at(label);
        }
        vector<float> vec(StatSign::getUrnSize(),0);
        return vec;
    }
    
    map<String,vector<float>>& Labels::getStatSignMap() {
        return this->labelStatSignMap;
    }
    
    
    Islands& Labels::getIsland(String label) {
        return this->labelIslandMap.at(label);
    }
    
    bool Labels::hasIsland(String label) {
        if(this->labelIslandMap.find(label) != this->labelIslandMap.end())
            return true;
    
        return false;
    }
    
    void Labels::printCompareLabels(Labels &labels1, Labels &labels2, float score, int markShifted) {
        auto labelMap1 = labels1.getMap();
        auto labelMap2 = labels2.getMap();
        for(auto it1=labelMap1.begin(), it2=labelMap2.begin(); it1!=labelMap1.end(), it2!=labelMap2.end(); it1++, it2++) {
            int i = distance(labelMap1.begin(),it1);
            bool isShifted = labels1.isShapeShifted(it1->first);
            if(markShifted==0 || !isShifted)
                printf("%d) %s: %d(%f) | %s: %d(%f)\n",i,it1->first.c_str(),it1->second.first,it1->second.second,it2->first.c_str(),it2->second.first,it2->second.second);
            else
                printf("%d) *%s: %d(%f) | %s: %d(%f)\n",i,it1->first.c_str(),it1->second.first,it1->second.second,it2->first.c_str(),it2->second.first,it2->second.second);
        }
        if(score>=0) {
            printf("Results: %f\n",score);
        }
    }
    
    void Labels::writeCompareLabels(String name, Labels &labels1, Labels &labels2, float score, int markShifted) {
        String file = name+".txt";
        FILE * fp;
        fp = fopen(file.c_str(),"w");
        auto labelMap1 = labels1.getMap();
        auto labelMap2 = labels2.getMap();
        for(auto it1=labelMap1.begin(), it2=labelMap2.begin(); it1!=labelMap1.end(), it2!=labelMap2.end(); it1++, it2++) {
            int i = distance(labelMap1.begin(),it1);
            bool isShifted = labels1.isShapeShifted(it1->first);
            if(markShifted==0 || !isShifted)
                fprintf(fp,"%d) %s: %d(%f) | %s: %d(%f)\n",i,it1->first.c_str(),it1->second.first,it1->second.second,it2->first.c_str(),it2->second.first,it2->second.second);
            else {
                int prevShape = labels1.getPrevShapeNum(it1->first);
                fprintf(fp,"%d) %d->%s: %d(%f) | %s: %d(%f)\n",i,prevShape,it1->first.c_str(),it1->second.first,it1->second.second,it2->first.c_str(),it2->second.first,it2->second.second);
            }
        }
        if(score>=0) {
            fprintf(fp,"Results: %f\n",score);
        }
        fclose(fp);
    }
    
    void Labels::printCompareStatSign(Labels &labels1, Labels &labels2, String label) {
        vector<float> statSignVec1 = labels1.getStatSign(label);
        vector<float> statSignVec2 = labels2.getStatSign(label);
        assert(statSignVec1.size()>0 && statSignVec2.size()>0);
        assert(statSignVec1.size()==statSignVec2.size());
        for(unsigned int i=1; i<statSignVec1.size(); i++) {
            float porp1 = (float)statSignVec1.at(i) / statSignVec1.at(0);
            float porp2 = (float)statSignVec2.at(i) / statSignVec2.at(0);
            try {
                printf("L%d: %0.2f(%f) | L%d: %0.2f(%f)\n",i,statSignVec1.at(i),porp1,i,statSignVec2.at(i),porp2);
            } catch(const std::out_of_range &oor) {
                printf("statSignVec1.size(): %lu\n",statSignVec1.size());
                printf("statSignVec2.size(): %lu\n",statSignVec2.size());
                printf("i: %d\n",i);
                exit(1);
            }
        }
        printf("Total: %0.2f | Total: %0.2f\n",statSignVec1.at(0), statSignVec2.at(0));
    }
    
    void Labels::writeCompareStatSign(Labels &labels1, Labels &labels2, String label, String fileType) {
        vector<float> statSignVec1 = labels1.getStatSign(label);
        vector<float> statSignVec2 = labels2.getStatSign(label);
        assert(statSignVec1.size()>0 && statSignVec2.size()>0);
        assert(statSignVec1.size()==statSignVec2.size());
        String file = labels1.name() + "_" + labels2.name() + "_" + label + "_stat_sign_compare." + fileType;
        FILE * fp;
        fp = fopen(file.c_str(),"w");
        for(unsigned int i=1; i<statSignVec1.size(); i++) {
            float porp1 = (float)statSignVec1.at(i) / statSignVec1.at(0);
            float porp2 = (float)statSignVec2.at(i) / statSignVec2.at(0);
            if(fileType=="txt") {
                fprintf(fp,"L%d: %d(%f) | L%d: %d(%f)\n",i,statSignVec1.at(i),porp1,i,statSignVec2.at(i),porp2);
            } else if(fileType=="csv") {
                fprintf(fp,"L%d,%0.2f,%f,L%d,%0.2f,%f\n",i,statSignVec1.at(i),porp1,i,statSignVec2.at(i),porp2);
            }
        }
        if(fileType=="txt") {
            fprintf(fp,"Total: %0.2f | Total: %0.2f\n",statSignVec1.at(0), statSignVec2.at(0));
        } else if(fileType=="csv") {
            fprintf(fp,"Total,%0.2f,Total,%0.2f\n",statSignVec1.at(0), statSignVec2.at(0));
        }
    }

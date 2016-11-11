import csv
import pkg_resources

from Shapes.shapes import Shapes
from Algorithms.jaysort import jaysort

class ShapeMatch():

    __shiftingRules__ = []
    __shiftingPenalties__ = []
    __THRESH_IMPORTED__ = False
    
    __shapeWeightsVec__ = []
    __shapeWeightsVec2__ = []
    
    #/******************* PUBLIC FUNCTIONS ******************/
    
    def __init__(self):
        if not ShapeMatch.__THRESH_IMPORTED__:
            ShapeMatch.__THRESH_IMPORTED__ = self.importThresholds()
    
    def importThresholds(self):
        if not ShapeMatch.__THRESH_IMPORTED__:
            res_mgr = pkg_resources.ResourceManager()
            folderName = "Thresholds"
            file1_read = open(res_mgr.resource_filename(folderName, "shape_shifting_rules.csv"), "r")
            csv_file1 = csv.reader(file1_read)
            file2_read = open(res_mgr.resource_filename(folderName, "shape_penalties.csv"),"r")
            csv_file2 = csv.reader(file2_read)
            file3_read = open(res_mgr.resource_filename(folderName, "shape_weights.csv"),"r")
            csv_file3 = csv.reader(file3_read)
            for row in csv_file1:
                ShapeMatch.__shiftingRules__.append(row[1:])
            file1_read.close()
            next(csv_file2)
            for row in csv_file2:
                ShapeMatch.__shiftingPenalties__.append(row[1:])
            file2_read.close()
            next(csv_file3)
            for row in csv_file3:
                ShapeMatch.__shapeWeightsVec__.append(row[1])
                ShapeMatch.__shapeWeightsVec2__.append(row[2])
            file3_read.close()
            assert(len(Shapes.__shapeNames__)==len(ShapeMatch.__shiftingPenalties__))
            assert(len(Shapes.__shapeNames__)==len(ShapeMatch.__shiftingRules__))
            assert(len(Shapes.__shapeNames__)==len(ShapeMatch.__shapeWeightsVec__))
            assert(len(Shapes.__shapeNames__)==len(ShapeMatch.__shapeWeightsVec2__))
            return True
        return False
    
    def getIslandVecIdxByArea(self, islandVec):
        islandVecIdx = []
        areaVec = []
        for i in range(0, len(islandVec)):
            for j in range(0, len(islandVec[i])):
                idxVec = []
                for k in range(0, len(islandVec[i][j])):
                    area = islandVec[i][j][k].area()
                    areaVec.push_back(area)
                    idxVec.append(i)
                    idxVec.append(j)
                    idxVec.append(k)
                    islandVecIdx.append(idxVec)
        assert(len(areaVec)>0)
        areaVec, origPos = jaysort(areaVec,1)
        islandVecIdxSorted = []
        for i in range(0, len(areaVec)):
            islandVecIdxSorted.append(islandVecIdx[origPos[i]])
        return islandVecIdxSorted
    
    
    #//! shifts island specified by rank, 0=default=largest
    def shape_translation(self, islandVec, shapeNum, newShape, rank=0):
        newIslandVec = islandVec[:]
        islandVecIdxSorted = self.getIslandVecIdxByArea(islandVec)
        shape = islandVecIdxSorted[rank][0]
        shade = islandVecIdxSorted[rank][1]
        isl = islandVecIdxSorted[rank][2]
        assert(shape==shapeNum)
    
        new_shape = newShape
        islandVec[shapeNum][shade][isl].isShapeShifted(True)
        newIslandVec[new_shape][shade].append(islandVec[shapeNum][shade][isl])
        newIslandVec[new_shape][shade][-1].prevShape(shapeNum)
        newIslandVec[new_shape][shade][-1].shape(new_shape)
        del newIslandVec[shapeNum][shade][isl]
        islandVec = newIslandVec
        return True
    
    #//! shifts specified shape to the left
    #//! only shifts the largest shape no matter what shade
    def shape_translation2(self, islandVec, shapeNum, newShape, shiftAmt=1):
        newIslandVec = islandVec[:]
        areaVec = []
        empty = True
        for j in range(0, len(islandVec[shapeNum])):
            if(len(islandVec[shapeNum][j])>0):
                area = islandVec[shapeNum][j][0].area()
                areaVec.append(area)
                empty = False
            else:
                areaVec.append(0)
        if not empty:
            for i in range(0, shiftAmt):
                max_shade_pos = areaVec.index(max(areaVec))
                new_shape = newShape
                if(areaVec[max_shade_pos]>0):
                    islandVec[shapeNum][max_shade_pos][0].isShapeShifted(True)
                    newIslandVec[new_shape][max_shade_pos].append(islandVec[shapeNum][max_shade_pos][0])
                    newIslandVec.at(new_shape).at(max_shade_pos).back().prevShape() = shapeNum;
                    newIslandVec.at(new_shape).at(max_shade_pos).back().shape() = new_shape;
                    newIslandVec.at(shapeNum).at(max_shade_pos).erase(newIslandVec.at(shapeNum).at(max_shade_pos).begin());
                    areaVec.at(max_shade_pos) = 0;
                }
            }
            islandVec = newIslandVec;
            return true;
        }
        return false;
    }
    
    void ShapeMatch::showIslands(vector<vector<vector<Islands> > > &islandVec) {
        for(unsigned int i=0; i<islandVec.size(); i++) {
            for(unsigned int j=0; j<islandVec.at(i).size(); j++) {
                for(unsigned int k=0; k<islandVec.at(i).at(j).size(); k++) {
                    Mat img = islandVec.at(i).at(j).at(k).image();
                    printf("Shade %d: ",i);
                    cout << islandVec.at(i).at(j).at(k).shape_name() << endl;
                    //imgshow(this->upIslandVec.at(i).at(j).image(),1);
                }
            }
        }
    }
    
    void ShapeMatch::printIslandAreas(vector<vector<vector<Islands> > > &islandVec) {
        cout << "**** PRINT ISLANDVEC AREAS ****" << endl;
        for(unsigned int i=0; i<islandVec.size(); i++) {
            printf("shape%d:\n",i);
            for(unsigned int j=0; j<islandVec.at(i).size(); j++) {
                printf("s%d: ",j);
                for(unsigned int k=0; k<islandVec.at(i).at(j).size(); k++) {
                    int area = islandVec.at(i).at(j).at(k).area();
                    printf("%d,",area);
                }
                cout << endl;
            }
        }
    }
    
    int ShapeMatch::numOfShapes() {
        return ShapeMatch::shapeNames.size();
    }
    
    //! assigns an island a new shape
    //! does not re-sort by area
    void ShapeMatch::moveShape(vector<vector<vector<Islands> > > &islandVec, int shapeNum, int shadeNum, int islNum, int newShape) {
        islandVec.at(newShape).at(shadeNum).push_back(islandVec.at(shapeNum).at(shadeNum).at(islNum));
        islandVec.at(shapeNum).at(shadeNum).erase(islandVec.at(shapeNum).at(shadeNum).begin()+islNum);
    }
    
    vector<String> ShapeMatch::SHIFT() {
        return this->_SHIFT;
    }
    
    void ShapeMatch::printRules() {
        for(unsigned int i=0; i<ShapeMatch::shiftingRules.size(); i++) {
            printf("%s: ",ShapeMatch::shapeNames.at(i).c_str());
            for(unsigned int j=0; j<ShapeMatch::shiftingRules.at(i).size(); j++) {
                printf("%s, ",ShapeMatch::shiftingRules.at(i).at(j).c_str());
            }
            printf("\n");
        }
    }
    
    void ShapeMatch::printPenalties() {
        for(unsigned int i=0; i<ShapeMatch::shiftingPenalties.size(); i++) {
            for(unsigned int j=0; j<ShapeMatch::shiftingPenalties.at(i).size(); j++) {
                printf("%0.2f, ",ShapeMatch::shiftingPenalties.at(i).at(j));
            }
            printf("\n");
        }
    }
    
    void ShapeMatch::printWeights() {
        for(unsigned int i=0; i<ShapeMatch::shapeWeightsVec.size(); i++) {
            printf("%s: %f\n",ShapeMatch::shapeNames.at(i).c_str(),ShapeMatch::shapeWeightsVec.at(i));
        }
    }
    
    float ShapeMatch::applyShiftPenalty(float score, int shapeNum, int shapeNum2) {
        float penalty = ShapeMatch::shiftingPenalties.at(shapeNum).at(shapeNum2);
        float newScore = score * pow(2.0,penalty);
        return newScore;
    }
    
    float ShapeMatch::getShiftPenalty(int shapeNum, int shapeNum2) {
        try {
            float weight = ShapeMatch::shiftingPenalties.at(shapeNum).at(shapeNum2);
            float penalty = pow(2.0,weight);
            return penalty;
        } catch (const std::out_of_range &oor) {
            printf("ShapeMatch::getShiftPenalty() out of range!\n");
            printf("ShapeNum: %d\n",shapeNum);
            printf("ShapeNum2: %d\n",shapeNum2);
            printf("ShiftPenalty[%d].size(): %lu\n",shapeNum,ShapeMatch::shiftingPenalties.at(shapeNum).size());
            exit(1);
        }
    }
    
    float ShapeMatch::applyShapeWeight(int shapeNum) {
        try {
            return ShapeMatch::shapeWeightsVec.at(shapeNum);
        } catch (const std::out_of_range &oor) {
            printf("ShapeMatch::applyShapeWeight() out of range!\n");
            printf("ShapeNum: %d\n", shapeNum);
            printf("ShapeWeightVec.size(): %lu\n",ShapeMatch::shapeWeightsVec.size());
            exit(1);
        }
    }

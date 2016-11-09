import csv
import pkg_resources

class Shapes:
    __shapeNames__ = []
    __shapeNames2__ = []
    __SHAPES_IMPORTED__ = False
    
    def __init__(self):
        if not Shapes.__SHAPES_IMPORTED__:
            Shapes.__SHAPES_IMPORTED__ = self.importShapes()

    def importShapes(self):
        if not Shapes.__SHAPES_IMPORTED__:
            res_mgr = pkg_resources.ResourceManager()
            folderName = "Thresholds"
            file1_read = open(res_mgr.resource_filename(folderName, "shape_names.csv"), "r")
            csv_file1 = csv.reader(file1_read)
            file2_read = open(res_mgr.resource_filename(folderName, "shape_names2.csv"), "r")
            csv_file2 = csv.reader(file2_read)
            for row in csv_file1:
                for i in range(len(row)):
                    Shapes.__shapeNames__.append(row[i])
            file1_read.close()
            for row in csv_file2:
                for i in range(len(row)):
                    Shapes.__shapeNames2__.append(row[i])
            file2_read.close()
            return True
        return True
            
    def getShapeName(self, num):
        return Shapes.__shapeNames__[num]
    
    def getShapeName2(self, num):
        return Shapes.__shapeNames2__[num]
    
    def getShapeIndex(self, shape):
        return Shapes.__shapeNames__.index(shape)
    
    def getShapeIndex2(self, shape):
        return Shapes.__shapeNames2__.index(shape)

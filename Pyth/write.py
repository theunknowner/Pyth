import numpy as np

class Write:
    def writeSeq2File(self,vec, name,fmt):
        if(len(vec)==0):
            print "Write Sequence to File failed!"
        else:
            filename = name + ".csv"
            np.savetxt(filename, vec, fmt, ",")
                    
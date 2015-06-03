import numpy as np
import csv
import sys
from filename import get_filename

input_file = sys.argv[1]
output_file = sys.argv[2]
hf_read = open(input_file)
csv_read = csv.reader(hf_read)
hf_write = open(output_file,"w")
csv_write = csv.writer(hf_write)

mat = []
matOrig = []
for row in csv_read:
    X = range(len(row))
    Y = row

    Y = map(float,Y)
    p = np.polyfit(X,Y,4)
    pp = np.polyval(p,X)
    mat.append(pp)
    matOrig.append(row)
        
csv_write.writerows(matOrig)
csv_write.writerows(mat)
hf_read.close()
hf_write.close()
import numpy as np
import csv

'''Data is imported by row'''

hf_read = open("/home/jason/git/WebDerm/WebDerm/count.csv")
csv_read = csv.reader(hf_read)
hf_write = open("/home/jason/git/WebDerm/WebDerm/count_polyfit.csv","w")
csv_write = csv.writer(hf_write)

mat = []
matOrig = []
for row in csv_read:
    X = range(len(row))
    Y = row
    
    Y = map(float,Y)
    p = np.polyfit(X,Y,5)
    pp = np.polyval(p,X)
    mat.append(pp)
    matOrig.append(row)
        
csv_write.writerows(matOrig)
csv_write.writerows(mat)
hf_read.close()
hf_write.close()
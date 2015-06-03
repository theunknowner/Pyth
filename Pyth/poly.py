import numpy as np
import csv

hf_read = open("/home/jason/git/WebDerm/WebDerm/psoriasis1_row(91).csv")
csv_read = csv.reader(hf_read)
hf_write = open("/home/jason/git/WebDerm/WebDerm/psoriasis1_polyfit.csv","w")
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
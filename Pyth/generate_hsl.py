import sys
import cv2
from hsl import Hsl
from filename import get_filename

input_file = sys.argv[1]
name = get_filename(input_file)
output_file = name+"_hsl_list.csv"
csv_write = open(output_file,"w")

img = cv2.imread(input_file);
hsl = Hsl();
mat2d = []
coords = []
csv_write.write("Coord(XY),RGB,HSL\n")
for i in range(0,img.shape[0]):
    for j in range(0,img.shape[1]):
        RGB = []
        RGB.append(img.item(i,j,2))
        RGB.append(img.item(i,j,1))
        RGB.append(img.item(i,j,0))
        HSL = hsl.rgb2hsl(RGB[0], RGB[1], RGB[2])
        HSL[1] = round(HSL[1],2)
        HSL[2] = round(HSL[2],2)
        coordStr = str(j)+" ; "+str(i)
        csv_write.write("(%s),RGB(%d; %d; %d),HSL(%d; %.2f; %.2f)\n"%(coordStr,RGB[0],RGB[1],RGB[2],HSL[0],HSL[1],HSL[2]))
        
import os

directory = "/home/jason/Desktop/Programs/Training Samples/Pairs/"
oldStr = "Pair"
newStr = "pair"


for filename in os.listdir(directory):
    pos = filename.find(oldStr)
    if(pos>-1):
        newFilename = filename.replace(oldStr,newStr)
        oldfile = directory+filename
        newfile = directory+newFilename
        os.rename(oldfile, newfile)
        print newFilename + " renamed!"
        
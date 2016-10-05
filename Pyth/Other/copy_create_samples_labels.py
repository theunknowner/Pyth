'''
Created on May 31, 2016

@author: jason
'''

import csv
import shutil
import os


def func1():
    folder = "/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Circles-Donut-Incomplete/"
    with open("/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Labels/Circles-Donut-Incomplete.csv","r") as csvfile:
        filename = "/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Labels/Circles-Donut-Incomplete2.csv"
        reader = csv.reader(csvfile)
        with open(filename,"w") as f:
            for row in reader:
                file = folder + row[0] + ".png"
                label = row[1]
                name2 = row[0] + " (pycopy)"
                file2 = folder + name2 + ".png"
                label2 = label
                name3 = row[0] + " (pycopy2)"
                file3 = folder + name3 + ".png"
                label3 = label
                shutil.copy(file, file2)
                shutil.copy(file, file3)
                f.write("{},{},{}\n".format(row[0],label,1))
                f.write("{},{},{}\n".format(name2,label2,1))
                f.write("{},{},{}\n".format(name3,label3,1))
                
def func2():
    folder = "/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Circles-Donut-Incomplete/"
    with open("/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Labels/Circles-Donut-Incomplete.csv","r") as csvfile:
        filename = "/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Labels/Circles-Donut-Incomplete2.csv"
        reader = csv.reader(csvfile)
        with open(filename,"w") as f:
            for row in reader:
                file = folder + row[0] + ".png"
                label = row[1]
                if(label=="-1"):
                    os.remove(file)
                else:
                    f.write("{},{},{}\n".format(row[0],label,1))
def func3():
    folder = "/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Circles-Donut-Incomplete/"
    with open("/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Labels/Circles-Donut-Incomplete.csv","r") as csvfile:
        filename = "/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Labels/Circles-Donut-Incomplete2.csv"
        reader = csv.reader(csvfile)
        with open(filename,"w") as f:
            for row in reader:
                copy_amt = int(row[3]) * 3
                file = folder + row[0] + ".png"
                label = row[1]
                f.write("{},{},{}\n".format(row[0],label,1))
                for i in range(0,copy_amt):
                    name2 = row[0] + " (pycopy{})".format(i+1)
                    file2 = folder + name2 + ".png"
                    label2 = label
                    if(os.path.exists(file2)==False):
                        shutil.copy(file, file2)
                        f.write("{},{},{}\n".format(name2,label2,1))
                        
def func4():
    folder = "/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Circles-Donut-Incomplete/"
    with open("/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Labels/Circles-Donut-Incomplete.csv","r") as csvfile:
        filename = "/home/jason/git/WebDerm/WebDerm/NN3-Donut-Comp-Incomp/Training/Labels/Circles-Donut-Incomplete2.csv"
        reader = csv.reader(csvfile)
        with open(filename,"w") as f:
            for row in reader:
                copy_amt = 3
                file = folder + row[0] + ".png"
                label = row[1]
                f.write("{},{},{}\n".format(row[0],label,1))
                if(float(row[4])>1.2):
                    for i in range(0,copy_amt):
                        name2 = row[0] + " (pycopy{})".format(i+1)
                        file2 = folder + name2 + ".png"
                        label2 = label
                        if(os.path.exists(file2)==False):
                            shutil.copy(file, file2)
                            f.write("{},{},{}\n".format(name2,label2,1))
                    
func4()
                
                
                
                
                
                
            
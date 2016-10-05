'''
Created on Oct 5, 2016

@author: jason
'''

import numpy as np

class Entropy:
    debugMode = False
    Y_HIGH = 0.0    #upper Y range boundary
    Y_LOW = 0.0    #lower Y range boudnary
    S_HIGH =0.0
    S_LOW = 0.0
    V_HIGH = 0.0
    V_LOW = 0.0
    Y_THRESH = 0.0    #% threshold Y must meet for special conditions
    S_THRESH = 0.0
    V_THRESH = 0.0
    Y_DIST = 0.0    #distance threshold Y must meet for special conditions
    S_DIST = 0.0
    V_DIST = 0.0
    Y_PERCEPTION = 0.0    #threshold in which the eyes starts noticing color
    S_PERCEPTION = 0.0
    Y_LARGE_THRESH = 0.0
    distPass = 0.0
    Y1 = Y2 = 0.0
    colorWeights = [] #holds the weights for color impact - My algo
    colorWeights2 = [] #Dr. Dube's algo

    totalPopulation =  [[]] #Y
    populationDensity = [[]] #S
    densityVariation = [[]] #V
    shapeMetric = [] #T
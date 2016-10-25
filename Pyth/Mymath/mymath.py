import math

def myRound(value, thresh=8):
    ''' rounds 8 and above (default) or custom round threshold'''
    result = math.trunc(value)
    result = value-result
    if(abs(result)>thresh):
        result = round(value)
    else: 
        result = math.trunc(value)
    return result

def eucDist(pt1, pt2):
    valX = pow(pt1[0]-pt2[0],2)
    valY = pow(pt1[1]-pt2[1],2)
    result = valX+valY
    result = math.sqrt(result)
    return result

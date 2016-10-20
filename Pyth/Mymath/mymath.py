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
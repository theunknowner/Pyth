
def epoh(sat, lum):
    if (lum<=50):
        result = (sat/100.) * (lum/50.)
    else:
        result = (sat/100.) * (100.-lum)/50.
    return result
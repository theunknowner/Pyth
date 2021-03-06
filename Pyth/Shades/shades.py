import csv

from peakcluster import PeakCluster

class Shades(PeakCluster):
    __THRESH_IMPORTED__ = False
    __g_Shades__ = [] #global shades vec
    __g_ShadeThresh__ = [] #global shade thresh vec
    
    #! __g_Shades2__ is for combined shades
    __g_Shades2__ = []
    __g_ShadeThresh2__ = []
    
    def __init__(self):
        if not Shades.__THRESH_IMPORTED__:
            Shades.__THRESH_IMPORTED__ = self.importThresholds();
    
    def importThresholds(self):
        if not self.__THRESH_IMPORTED__:
            folderName = "/home/jason/git/WebDerm/WebDerm/Thresholds/"
            filename = folderName+"shade-thresholds.csv"
            filename2 = folderName+"shade-thresholds2.csv"
            fsThresh = fsThresh2 = None
            try:
                fsThresh = open(filename,"r")
                fsThresh2 = open(filename2,"r")
            except Exception:
                print("Importing Shade Thresholds Failed!")
                return False
            
            if(fsThresh and fsThresh2):
                thresh_read = csv.reader(fsThresh)
                thresh2_read = csv.reader(fsThresh2)
                next(thresh_read)
                for row in thresh_read:
                    thresh = []
                    Shades.__g_Shades__.append(row[0])
                    thresh.append(float(row[1]))
                    thresh.append(float(row[2]))
                    Shades.__g_ShadeThresh__.append(thresh)
                    
                next(thresh2_read)
                for row in thresh2_read:
                    thresh = []
                    Shades.__g_Shades2__.append(row[0])
                    thresh.append(float(row[1]))
                    thresh.append(float(row[2]))
                    Shades.__g_ShadeThresh2__.append(thresh)
                    
                fsThresh.close()
                fsThresh2.close()
                return True
            
        return True
    
    def getShadeCount(self):
        return len(Shades.__g_Shades__)
    
    def extractShadeLevel(self, shade):
        '''
        extracts number at the end of shade only
        '''
        substr = shade[-1]
        return int(substr)
    
    def getShade(self, index):
        shadeCount = self.getShadeCount()
        ind=index
        if(ind<0): ind=0
        if(ind>(shadeCount-1)): ind=(shadeCount-1)
        return Shades.__g_Shades__[ind]
    
    def getShadeIndex(self, shade):
        index=0
        shadeCount = self.getShadeCount()
        for i in range(0,shadeCount):
            if(shade==self.getShade(i)):
                index=i
                break
        return index
    
    def extractShade(self, pix):
        shadeCount = self.getShadeCount()
        shade = ""
        if(pix=="Zero"): return pix
        if(pix.find("White")>=0): return "White"
        if(pix.find("Black")>=0): return self.getShade(0)
        #if(pix.find("Gray")>=0): return "Gray"
        for i in range(0,shadeCount):
            shade = self.getShade(i)
            if(pix.find(shade)>=0):
                break
        return shade
    
    def calcShade(self, intensity):
        for i in range(0,len(Shades.__g_ShadeThresh__)):
            if(intensity<Shades.__g_ShadeThresh__[i][1] and intensity>=Shades.__g_ShadeThresh__[i][0]):
                return Shades.__g_Shades__[i]
            
        return "NONE"
    
    def calcShade2(self, intensity):
        for i in range(0,len(Shades.__g_ShadeThresh2__)):
            if(intensity<Shades.__g_ShadeThresh2__[i][1] and intensity>=Shades.__g_ShadeThresh2__[i][0]):
                return Shades.__g_Shades2__[i]
        return "NONE"
    
    def release_memory(self):
        Shades.__g_Shades__[:] = []
        Shades.__g_ShadeThresh__[:] = []
        Shades.__g_Shades2__[:] = []
        Shades.__g_ShadeThresh2__[:] = []
    
    def shadeDifference(self, shade1, shade2):
        '''
        compares shade1 with shade2 and returns difference
        if diff is <0 -> shade1 is darker, >0 -> shade1 is lighter
        '''
        shadeIndex1 = self.getShadeIndex(shade1)
        shadeIndex2 = self.getShadeIndex(shade2)
        diff = shadeIndex1 - shadeIndex2
        return diff
    
    def getShadeIndex2(self, shade):
        '''
        return index for __g_Shades2__
        '''
        index=0
        shadeCount = len(Shades.__g_Shades2__)
        for i in range(0,shadeCount):
            if(shade==self.getShade2(i)):
                index=i
                break
        return index
    
    def getShade2(self, index):
        shadeCount = len(Shades.__g_Shades2__)
        ind=index
        if(ind<0): ind=0
        if(ind>(shadeCount-1)): ind=(shadeCount-1)
        return Shades.__g_Shades2__[ind]
    
    #custom function for combing shades that might look the same
    def combineShades(self, shade):
        if(shade.find("Dark2")>=0 or shade.find("Dark1")>=0):
            return "Dark2"
        if(shade.find("Dark3")>=0): return "Dark3"
        if(shade.find("High")>=0): return "High"
        if(shade.find("Low")>=0): return "Low"
        if(shade.find("Light")>0): return "Low"
        return shade
    
if __name__ == "__main__":
    sh = Shades()
    sh.importThresholds()
    print Shades.__g_Shades__
    print Shades.__g_Shades2__
    print Shades.__g_ShadeThresh__
    print Shades.__g_ShadeThresh2__
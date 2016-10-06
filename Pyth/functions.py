import cv2

class Functions:
    #gets image filename from filepath
    def getFileName(self, filename, end=""):
        delimit1 = '/'
        delimit2 = '.'
        name = filename;
        pos=0
        pos2=0
        if(filename.find(delimit2)>=0):
            for i in range(0,len(filename)):
                if(filename[i]==delimit1):
                    pos=i+1
                if(filename[i]==delimit2):
                    pos2=i
            name = filename[pos:pos2]
            if(end!=""):
                pos = name.find(end)
                name = name[0:pos]
    
        return name
    
    def cropImage(self,input):
        ptX = ptY = 0
        roiWidth = roiHeight = 0

        for i in range(input.shape[1]):
            if(cv2.countNonZero(input[:,i])>0):
                ptX = i;
                roiWidth = input.shape[1]-ptX;
                break;
            
        for j in range(input.shape[0]):
            if(cv2.countNonZero(input[j,:])>0):
                ptY = j;
                roiHeight = input.shape[0]-ptY;
                break;
            
        img1 = input[ptY:ptY+roiHeight, ptX:ptX+roiWidth]
        for i in range(img1.shape[1]-1,-1,-1):
            if(cv2.countNonZero(img1[:,i])>0):
                roiWidth = i+1;
                break;
            
        for j in range(img1.shape[0]-1,-1,-1):   
            if(cv2.countNonZero(img1[j,:])>0):
                roiHeight = j+1;
                break;
        
        img2 = img1[0:roiHeight,0:roiWidth];
        return img2
    
if __name__ == "__main__":
    func = Functions()
    print func.getFileName("/home/jason/Desktop/Programs/Crop_Features/acne1.png")
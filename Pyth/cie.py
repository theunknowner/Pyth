import math
class Cie:
	def deltaE76(self,LAB1, LAB2):
		if(len(LAB1)!=len(LAB2)):
			return -1
	
		sum=0
		for i in range(len(LAB1)):
			sum += pow(LAB1[i]-LAB2[i],2)
		
		deltaE = math.sqrt(sum);
		return deltaE;
		
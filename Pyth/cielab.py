
class CieLab:
    def xyz2lab(self,x,y,z):
        ref_X =  95.047
        ref_Y = 100.000
        ref_Z = 108.883
        X = x/ref_X
        Y = y/ref_Y
        Z = z/ref_Z
        
        if ( X > 0.008856 ):
            X = pow(X,1/3.)
        else: 
            X = ( 7.787 * X) + (16.0 / 116.0)

        if ( Y > 0.008856 ):
            Y = pow(Y,1/3.)
        else:
            Y = ( 7.787 * Y) + (16. / 116.)

        if ( Z > 0.008856 ): 
            Z = pow(Z, 1/3.)
        else:
            Z = ( 7.787 * Z) + (16. / 116.)

        LAB = []
        LAB.append(116 * Y - 16)
        LAB.append(500 * (X-Y))
        LAB.append(200 * (Y-Z))

        return LAB;
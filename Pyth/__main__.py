from Runenv import runenv
from NeuralNetwork.ann import ANN
import rgb

import pkg_resources

def main():
    print('The rain in Spain falls mainly in the plain.')
    res_mgr = pkg_resources.ResourceManager()
    print(res_mgr.resource_filename('Thresholds', 'shape_names.csv'))
    
if __name__ == "__main__":
    ann = ANN()
    Rgb = rgb.Rgb()
    print rgb.mainColors
    print ann.__shapeNames__
    
    #main()
    
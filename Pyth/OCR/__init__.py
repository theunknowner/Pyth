import cv2
import numpy as np

from ImageData.imagedata import ImageData
from ShadeShape.shadeshape import ShadeShape

img = cv2.imread("/home/jason/Desktop/Bizfi/corpsearch (3).jpg");
img2 = cv2.resize(img,(100,50))
img2 = cv2.resize(img2,(200,100))
bw = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
for i in range(0,bw.shape[1]):
    for j in range(0, bw.shape[0]):
        if(bw[i,j]<=135):
            bw[i,j]=0
bw *= 255
id = ImageData(bw,"captcha")
    ShadeShape ss1(id,"captcha");
    vector<Mat> vec_ch;
    for(int i=0; i<ss1.numOfFeatures(); i++) {
        if(ss1.feature(i).area()>20) {
            vec_ch.push_back(ss1.feature(i).image());
        }
    }
    vector<Mat> sorted_vec_ch;
    vector<int> vec_col;
    for(int i=0; i<vec_ch.size(); i++) {
        int left = 0;
        for(int j=0; j<vec_ch.at(i).cols; j++) {
            if(countNonZero(vec_ch.at(i).col(j))>0) {
                left = j;
            }
        }
        sorted_vec_ch.push_back(vec_ch.at(i));
        vec_col.push_back(left);
        if(i>0) {
            for(int j=0; j<sorted_vec_ch.size()-1; j++) {
                if(left < vec_col.at(j)) {
                    auto it = sorted_vec_ch.begin();
                    auto it_last = sorted_vec_ch.end()-1;
                    std::iter_swap(it+j, it_last);

                    auto it_col = vec_col.begin();
                    auto it_col_last = vec_col.end()-1;
                    std::iter_swap(it_col+j, it_col_last);
                }
            }
        }
    }
    for(int i=0; i<sorted_vec_ch.size(); i++) {
        imgshow(sorted_vec_ch.at(i));
    }
'''from PyQt4 import QtGui
import sys
import cv2

img = cv2.imread("/home/jason/Desktop/Programs/Crop_Features/lph4.png")
cv2.namedWindow('image',cv2.WINDOW_NORMAL)
cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()'''

import requests
from bs4 import BeautifulSoup as bs

sess = requests.Session()
resp = sess.get("https://www.yelp.com/biz/pita-grill-new-york-5")
soup = bs(resp.content,"lxml")
print soup.prettify()
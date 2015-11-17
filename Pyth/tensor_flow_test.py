import tensorflow as tf
import cv2

'''
hello = tf.constant("Hello, World")
sess = tf.Session()
print sess.run(hello)

a = tf.constant(2)
b = tf.constant(3)
c = tf.add(a, b)
print sess.run(c)
'''
img = cv2.imread("/home/jason/Desktop/workspace/test3.png",0)
#filename = "/home/jason/Desktop/workspace/test3.png"
tnsr = tf.convert_to_tensor(img)

#imgTnsr = tf.image.decode_png(tnsr,1)
#print imgTnsr
sess = tf.Session()

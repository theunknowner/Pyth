import tensorflow as tf

hello = tf.constant("Hello, World")
sess = tf.Session()
print sess.run(hello)

a = tf.constant(2)
b = tf.constant(3)
c = tf.add(a, b)
print sess.run(c)
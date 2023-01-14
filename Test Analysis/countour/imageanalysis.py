import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

file = "Test Images/09:30:22/frame670.jpg"
img = cv.imread(cv.samples.findFile(file))
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)



plt.hist(gray.ravel(),256,[5,256])
plt.title("dirty 1 Histogram")
plt.show()


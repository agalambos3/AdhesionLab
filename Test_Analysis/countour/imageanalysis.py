import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("Test_Analysis/utils")
import drive_importing as dimport


file = dimport.drive_import("/Code/Test Analysis/Test Analysis/Flaw Detection/Test Images/07:25:22/4mmflaw.png")
img = cv.imread(cv.samples.findFile(file))
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)



plt.hist(gray.ravel(),256,[5,256])
plt.title("dirty 1 Histogram")
plt.show()


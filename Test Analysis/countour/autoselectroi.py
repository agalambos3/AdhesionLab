import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import math

def get_max_contour(contours):
    maxa = 0
    maxc = None
    for c in contours:
        a = cv.contourArea(c)
        if a > maxa:
            maxa = a
            maxc = c
    return maxc

def get_contour_center(contour):
    M = cv.moments(contour)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    return np.array((cx,cy))


def auto_select_roi(image,visualize=False):
    '''autoselects the roi by figuring out where the edge of the lens is using thresholding with otsu binarization
    @param input image. Should be a numpy array (same input as an image for most cv operations)
    '''
    img = image
    #turn image to grey
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(0,0),11)

    #threshold image using otsu binarization
    val,thresh = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    cv.imshow("threshed",thresh)
    cv.waitKey()
    #find contours of image
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)


    max = get_max_contour(contours) #find max contour
    maxcenter = get_contour_center(max) #get max contour center
    maxleftmost = max[max[:,:,0].argmin()][0] #get max contour leftmost point
    maxrightmost = max[max[:,:,0].argmax()][0] #get max contour rightmost point
    radius = int(np.linalg.norm(maxleftmost-maxrightmost)/2) #get radius of outermost contour

    sqaurelength = int(radius*math.sqrt(2)/2) #find half of side length of inscribed square


    #calculate corners of square 
    topleft= maxcenter+ [-sqaurelength,-sqaurelength]
    bottomright= maxcenter+ [sqaurelength,sqaurelength]

    #crop image
    imcrop = [topleft[1],bottomright[1],topleft[0],bottomright[0]]

    #if visualization is turned on can see calculated points for roi corners and radius of outermost contour as well as contour itself
    if visualize == True:
        visualized_img = img
        cv.circle(visualized_img,topleft,6, (0, 255, 255), -1)
        cv.circle(visualized_img,bottomright,6, (0, 255, 255), -1)
        cv.circle(visualized_img,maxcenter,radius, (0, 255, 0), 1)
        cv.drawContours(visualized_img,[max],-1,(255,0,0),1)

        cv.imshow("roi visualized",visualized_img)
        cv.waitKey()
    
    return imcrop




    
file = "flaw.png"
img =cv.imread(cv.samples.findFile(file))
crop= auto_select_roi(img,visualize=True)

cv.imshow("cropped",img[crop[0]:crop[1],crop[2]:crop[3]])
cv.waitKey()


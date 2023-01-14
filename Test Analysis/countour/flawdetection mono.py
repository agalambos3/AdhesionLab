#This version of the flaw detection program relies on contour detection and contour hierarchies to recognize flaw and contact area

#TODO I really shouldn't even be considering this but what if I just found all contours w/ compactness <1.6 and then just sorted them by size?
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import math
import pandas as pd


def get_max_contour(contours):
    '''Finds the the contour of maximum area in a list of contours. Takes a list of contours as an input, returns the index of the contour of greatest area.'''
    maxa = 0
    maxc = None
    for c in contours:
        a = cv.contourArea(c)
        if a > maxa:
            maxa = a
            maxc = c
    return maxc

def get_contour_center(contour):
    '''Finds the center of a contour using a center mass kind of calculation. Takes a contour (an array of points). Returns the coordinates of the center as an array'''
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


    #threshold image using otsu binarization
    val,thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

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
    imcrop = img[topleft[1]:bottomright[1],topleft[0]:bottomright[0]]

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

def find_level_max(contours,hierarchy,start:int,circularity:bool):
    """finds the contour with the maximum area for a given hierarchy level. returns index of maximum contour
        
        @param contours is the list of contours
        @param hierarchy is the hierarchy list
        @param start is the index of the first contour in a given hierarchy level
        @param circularity determines whether to only consider contours that are close to circular (done by comparing area vs perimeter)
    """

    clist = contours
    hlist = hierarchy[0]    
    loc = start #variable that helps keep track of what point we are currently at in the tree and correspondingly the index in the contours list
    
    hloc = hlist[loc] #current value in hierarchy list
    cloc = clist[loc] #current value in contour list

    amax = 0 #maximum area
    imax = 0 #index in contours list of max area

    #finds maximum area contour in given hierarchy level. 
    while int(loc) != -1:
        area = cv.contourArea(cloc) #area of current contour

        if area > amax:
            if circularity == True:
                try:
                    compactness= (cv.arcLength(cloc,True)**2)/(4*math.pi*area)
                    if compactness <= 1.5:
                        amax =area
                        imax = loc
                except ZeroDivisionError: #TODO find a better way to deal with things when program fucks up
                    pass
            else:
                amax =area
                imax = loc
        loc = hloc[0]
        hloc = hlist[loc]
        cloc = clist[loc]
    return imax


    '''find the center of a contour'''
    M = cv.moments(contour)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    return np.array((cx,cy))

def feature_indices(contours,hierarchy):
    '''finds the indices that corresponds to the important features of the image (flaw and probe contact). 
    The way it finds the features is kinda bizarre but seems to work. 
    Nearly all the images have a large squiggly outer contour which the probe contact area contour is contained in.
    Inside the probe contact area is the flaw contour. Relying on these facts the program finds the largest outermost contour
    and then finds its largest child. In theory this child is the probe contact area. This process is repeated for the child and in
    theory its child is the flaw. I'm not sure why it works but it does. 

    @param contours list
    @param hierarchy list
     '''
    #find max area outermost contour. For this one we don't care about circularity so the last paramter of find_level_max is false
    max = find_level_max(contours,hierarchy,0,False)

    #find first child
    child = hierarchy[0][max][2]
    #find contour in child's level with largest area (that also is circular enough)
    max_child = find_level_max(contours,hierarchy,child,True)

    #find child's child aka grandchild of original
    gchild = hierarchy[0][max_child][2]
    #find contour in grandchild's level with largest area (that also is circular enough)
    max_gchild = find_level_max(contours,hierarchy,gchild,True)

    return (max,max_child,max_gchild) #returns indices for the outermost contour, probe contact, and flaw (in theory if code works )

def process_image(image,crop,visualize=False):
    im = image
    if visualize == True:
        cv.imshow("initial image",im)
        cv.waitKey()

    #crop image if necessary
    if crop == True:
        im = auto_select_roi(im)
        cropped_img = im
        if visualize == True:
            cv.imshow("cropped image",im)
            cv.waitKey()
    else:
        cropped_img = im
    
    #convert image to grayscale
    gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

    #initial gaussian blur
    blur = cv.GaussianBlur(gray,(0,0),5)
    if visualize == True:
        cv.imshow("gaussian blur",blur)
        cv.waitKey()

    #adaptive thresholding of image
    thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_MEAN_C,\
            cv.THRESH_BINARY,101,0
            )
    if visualize == True:
        cv.imshow("thresholded image",thresh)
        cv.waitKey()

    #closing morphological operation to get rid of islands

    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(1,1))
    dimg = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel,iterations=1)

    # kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(3,3))
    # dimg = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel,iterations=4)
    
    # kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5))
    # dimg = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel,iterations=1)
    if visualize == True:
        cv.imshow("closing",dimg)
        cv.waitKey()
    
    #iterated median blur to solidify large regions of black and white
    for i in range(2):
        dimg = cv.medianBlur(dimg, 13)
    if visualize == True:
        cv.imshow("iterated median blur",dimg)
        cv.waitKey()
    return dimg,cropped_img

def get_feature_contours(processed_image,cropped_image,visualize = False):
    dimg= processed_image
    img = cropped_image
    #find contours in processed image
    contours, hierarchy = cv.findContours(dimg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    
    if visualize== True:
        cimg = cv.drawContours(img,contours,-1,(255,255,0),1)
        cv.imshow("contours",cimg)
        cv.waitKey()

    #get indices of contours that are important features (max, probe, and flaw)
    features = feature_indices(contours,hierarchy)

    #get contour and contour center for max
    max = contours[features[0]]
    max_center = get_contour_center(max)

    #get contour and contour center for probe
    probe = contours[features[1]]
    probe_center = get_contour_center(probe)

    #get contour and contour center for flaw
    flaw = contours[features[2]]
    flaw_center = get_contour_center(flaw)

    #calculate distance between probe center and flaw center
    dist = np.linalg.norm(probe_center-flaw_center)

    #visualizes found features on cropped image
    if visualize== True:
        #draw contour and center for outermost largest contour
        cimg=cv.drawContours(img, [max], -1, (0,255,0), 1)
        cv.circle(img,max_center,2, (0, 255, 0), -1)



        #draw contour and center for probe contact
        cimg=cv.drawContours(img, [probe], -1, (255,0,0), 1)
        cv.circle(img,probe_center,2, (255, 0, 0), -1)

        #draw contour and center for flaw
        cimg=cv.drawContours(img, [flaw], -1, (0,0,255), 1)
        cv.circle(img,flaw_center,2, (0, 0, 255), -1)

        #show orginal image with contours and centers of important features overlaid
        cv.imshow("probe and flaw",cimg)
        cv.waitKey()
    return max,probe,flaw

def user_input(visualize=False):
    '''Gives way for user to input what image they would like analyzed. End goal is for program to work like getminmax where it can be opened on lab computer and user can type in image and get back analysis in excel docuement'''
    validInput = False
    while validInput == False:
        try:
            imagename = input("Enter image file name:\n")
            img = cv.imread(cv.samples.findFile(imagename))
            validInput = True
        except:
            print("Invalid image name. Please try again\n")
    
    user_crop =input("Does the image need to be cropped(y/n)?:\n")
    needs_crop = None
    if user_crop == "y":
        needs_crop = True
    else:
        needs_crop = False

    dimg,cropped_img = process_image(img,crop=needs_crop,visualize=True)
    max,probe,flaw = get_feature_contours(dimg,cropped_img,visualize=True)

    probe_center = get_contour_center(probe)
    flaw_center = get_contour_center(flaw)
    pixel_distance = np.linalg.norm(probe_center-flaw_center)
    probe_pxl_area = cv.contourArea(probe)
    flaw_pxl_area = cv.contourArea(flaw)

    probediam = 10
    probe_mm_area = ((probediam/2)**2)*math.pi

    mm2pxl_conversion_factor = probe_mm_area/probe_pxl_area

    flaw_mm_area = mm2pxl_conversion_factor*flaw_pxl_area
    flaw_mm_diam = math.sqrt((flaw_mm_area/math.pi))*2
    mm_distance = mm2pxl_conversion_factor*pixel_distance

    flaw_info_list = [["flaw area (mm^2)",flaw_mm_area],["flaw diameter (mm)",flaw_mm_diam],["flaw probe center separation (mm)",mm_distance]]
    sdf = pd.DataFrame(flaw_info_list)
    excel_title = imagename+"_flaw_info.xlsx"
    sdf.to_excel(excel_title,index=False,header=False)

    cv.drawContours(cropped_img,[max],
    -1,(0,255,0),1)
    cv.drawContours(cropped_img,[probe],-1,(255,0,0),1)
    cv.drawContours(cropped_img,[flaw],-1,(255,0,255),1)

    cv.imshow("Flaw and Probe Outlined",cropped_img)
    cv.waitKey()

if __name__ == "__main__":
    user_input()
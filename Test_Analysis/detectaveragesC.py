import cv2 as cv
import numpy as np
import math as math
import sys 
from utils import autoselectroi as aroi
from utils import drive_importing as dimport

    
class video_analysis():
    '''class used to analyze a single video. Initialize with filename of video, gridsize for analysis, and whether the video should be cropped for analysis'''
    def __init__(self,filename:str,gridsize:tuple,crop:bool) -> None:
        #TODO import video as grayscale if possible so frames have less numbers to average 
        self.vid = cv.VideoCapture(str(filename))
        if (self.vid.isOpened() == False):
            print("Error opening the video file")
        #crop video if the class is initialized with crop == True
        self.crop_region= None
        frame = self.vid.read()[1]
        if crop == True:
            frame= cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            self.crop_region = aroi.auto_select_roi(frame)
            frame = frame[self.crop_region[0]:self.crop_region[1],self.crop_region[2]:self.crop_region[3]]
        
        #tuple for gridsize dimensions in pixels
        self.gridsize = gridsize
        #list for basline values of each region of the video
        self.baselines = []
        #tuple for contact frames. Starts empty but assigned value if calculated
        self.contact_frames = ()
        #video is reset to first frame
        self.vid.set(cv.CAP_PROP_POS_FRAMES, 0)


    def get_video(self):
        """returns the video that is being analyzed"""
        return self.vid
    def get_crop_region(self):
        """returns the cropping region of the video"""
        return self.crop_region
    
    def get_baselines(self):
        """returns the baselines of the video"""
        return self.baselines
    
    def get_contact_frames(self):
        """returns the contact frames of the video """
        return self.contact_frames
    
    def get_gridsize(self):
        """returns the dimensions of the grid being used for analysis"""
        return self.gridsize

    def calc_region_values(self,img):
        '''calculate pxl values of the regions for a given frame'''
        #determine the number of rows and columns in the grid
        dimensions = img.shape
        xres = self.gridsize[0]
        yres = self.gridsize[1]
        rows = math.floor(dimensions[0]/yres)
        columns = math.floor(dimensions[1]/xres)
        
        #initialize empty regions list
        regions = []
        #two for loops go through all the regions in the image and compute the pixel values are in each region
        for i in range(rows):
            row = []
            ystart = yres * i
            yend = yres * (i+1)
            for j in range(columns):
                xstart = xres * j
                xend = xres * (j+1)
                #pixels values of each region
                regionImg = img[ystart:yend, xstart:xend]
                row.append(regionImg)
            regions.append(row)
        return np.array(regions)

    def calc_regionAvg(self,regions):
        '''calculates the average pxl value of each region for an input of pxl regions (usually corresponding to a single frame)'''
        averages = np.zeros(regions.shape[0:2])
        for row in range(regions.shape[0]):
            for col in range(regions.shape[1]):
                avg = np.mean(regions[row, col])
                averages[row, col]=avg
        return averages  

    def calc_Baselines(self, nframes:int,visualize:bool=False):
        """calculates the baselines for a video
        @param nframes - the number of frames to takes the baselines over
        @param visualize - whether to show each frame that he basline is taken of """
        frameavgs = []
        self.vid.set(cv.CAP_PROP_POS_FRAMES, 0)
        #calculate baseline for nframes number of frames
        for i in range(nframes):
            #read frame 
            ret, frame = self.vid.read()
            #crop video if cropping is true        
            if self.crop_region != None:
                frame = frame[self.crop_region[0]:self.crop_region[1],self.crop_region[2]:self.crop_region[3]]
            if visualize == True:
                #show frame that the baseline is being taken of 
                cv.imshow("frame {}".format(i),frame)
                cv.waitKey()
            #get pixel values of a given frame
            frameregions = self.calc_region_values(frame)
            #appen avg of pixel values to frameavgs
            frameavgs.append(self.calc_regionAvg(frameregions))
        #array of all the averaged frames
        frameavgs = np.array(frameavgs)
        #mean of each region 
        regionmeans = np.mean(frameavgs, axis=0)
        #standard deeviation of each region
        regionstdevs = np.std(frameavgs, axis=0)
        self.vid.set(cv.CAP_PROP_POS_FRAMES,0) #sets internal pointer back to the first video frame
        #set baselines to calculated means and stdev
        self.baselines = (regionmeans, regionstdevs)
    
    def calc_contactBool(self,frame,cutoff:int):
        """calculates whether contact is occuring in a given frame
        @param frame - frame that is being checked for contact. Frame should be an opencv image, such as if vid.read() is used on a video
        @param cutoff -cutoff - number of stdevs frame averages differs from baseline averages for a region is considered to be in contact"""
        means = self.baselines[0]
        stdevs = self.baselines[1]
        if self.crop_region != None:
            #crop frame based on crop region calculated during initialization
            frame = frame[self.crop_region[0]:self.crop_region[1],self.crop_region[2]:self.crop_region[3]]
        #get frame region pxl values
        frameregions = self.calc_region_values(frame)
        #get frame regions pxl value averages
        intensities = self.calc_regionAvg(frameregions)
        #see how much frame regions averages differ from baseline region averages
        deviations = means - intensities
        #put deviation in terms of calculated std deviation of baseline regions
        numstdevs = deviations / stdevs
        #find the maximum deviation among the regions
        maxdeviation = np.amax(numstdevs)
        print("max standard deviation is {}".format(maxdeviation))
        #check whether max deviation exceeds cutoff and return True or False accordingly 
        maxdeviation = np.amax(numstdevs)
        if abs(maxdeviation) > cutoff:
            return True
        else:
            return False

    def calc_contactRegions(self,frame,cutoff:int):
        """Returns a bool array of the regions where the region is considered in contact
            @param frame - frame that is being checked for contact. Frame should be an opencv image, such as if vid.read() is used on a video
            @param cutoff - number of stdevs frame averages differ from baselines for a region is considered to be in contact"""
        means = self.baselines[0]
        stdevs = self.baselines[1]
        #crop frame based on crop region calculated during initialization
        if self.crop_region != None:
            frame = frame[self.crop_region[0]:self.crop_region[1],self.crop_region[2]:self.crop_region[3]]
        #get frame regions pxl values
        frameregions = self.calc_region_values(frame)
        #get frame regions pxl value averages
        intensities = self.calc_regionAvg(frameregions)
        #see how much frame regions averages differ from baseline regions averages
        deviations = means - intensities
        #put deviation in terms of calculated std deviation of baseline regions
        numstdevs = abs(deviations / stdevs)
        #Bool array w/ True for region where cutoff is passed and False everywhere else. 
        contactarray = np.where(numstdevs>cutoff,True,False)
        return contactarray
    
    def calc_contactArea(self,boolregions):
        """calculate the contact area for a given frame assuming the contact regions have already been calculated
        @param boolregions - array of bools corresponding to what regions are in contact """
        xres = self.gridsize[0]
        yres= self.gridsize[1]
        contact_regions = np.where(boolregions==True)[0]
        #contact area is number regions in contact multiplied by the area of each region
        contact_area= len(contact_regions)*xres*yres
        return  contact_area
        
        
    def calc_ContactFrame(self,fstart:int, fend:int,cutoff:int):
        """old way of calculating contact frames, use calc_ContactFrameV2 instead"""
        self.vid.set(cv.CAP_PROP_POS_FRAMES, fstart)

        ret, frame = self.vid.read()
        cv.imshow("testing frame",frame)
        cv.waitKey()
        try:
            frame1= cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        except:
            frame1 = frame

        # if self.crop_region != None:
        #     frame1 = frame1[self.crop_region[0]:self.crop_region[1],self.crop_region[2]:self.crop_region[3]]
        #     print(frame1.shape)
        initial = self.calc_contactBool(frame1,cutoff)
        for i in range(fend-(fstart+1)):
            ret, frame = self.vid.read()
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            print("read frame {}".format(self.vid.get(cv.CAP_PROP_POS_FRAMES)))
            # if self.crop_region != None:
            #     frame = frame[self.crop_region[0]:self.crop_region[1],self.crop_region[2]:self.crop_region[3]]
            contact = self.calc_contactBool(frame,cutoff)
            if  contact!= initial:
                contactFrame = fstart + i + 1
                return contactFrame
            else:
                pass
        return

    def binaryapprox_ContactFrame(self,contactframenum,otherframenum,minframe,cutoff):
        """Used to find the contact frame via recursive binary search through the video. Relies on one atleast one frame of search being in contact. 
        @param contactframenum - number of frame that is in contact
        @param otherframenum - number of frame that in first call is not in contact (in deeper recursion calls might end up being in contact
        @param minframe - mininum number of frames between contactframenum and otherframenum before the recursion is stopped"""
        print("binary called")
        framerange = abs(contactframenum-otherframenum)
        firstframe = None
        if contactframenum > otherframenum:
            firstframe = otherframenum
        else:
            firstframe = contactframenum
        
        checkframenum = firstframe+framerange//2
        if framerange > minframe:
            print("checked frame is {}".format(checkframenum))
            self.vid.set(cv.CAP_PROP_POS_FRAMES,checkframenum)
            ret, checkframe = self.vid.read()        
            contact = self.calc_contactBool(checkframe,cutoff)
            if contact == True:
                return self.binaryapprox_ContactFrame(checkframenum,otherframenum,minframe,cutoff)
            else:
                return self.binaryapprox_ContactFrame(contactframenum,checkframenum,minframe,cutoff)
        else:
            return checkframenum

    def approx_ContactFrame(self,initsamples:int,cutoff):
        """samples video at initsamples number of evenly spaced frames to see which ones are in contact. Used to give initial input to binaryapprox_ContactFrame
        @param initsamples - number of evenly spaced frames to sample in video
        @param cutoff - number of stdevs frame averages differs from baseline averages for a region is considered to be in contact  """
        #number of frames in the video
        total_frames = self.vid.get(cv.CAP_PROP_FRAME_COUNT)
        print(total_frames)
        #number of frames in between each frame that is sampled
        initsep = total_frames//(initsamples+1)
        initcontactframes = []
        contactrange = None
        #check contact in each of the evenly spaced frames
        for i in range(1,initsamples+1):
            framenum = (i)*initsep
            self.vid.set(cv.CAP_PROP_POS_FRAMES, framenum)
            frame  = self.vid.read()[1]
            print(i)
            print("read frame {}".format(framenum))
            # cv.imshow("frame {}".format(framenum),frame)
            # cv.waitKey()
            contact = self.calc_contactBool(frame,cutoff)
            if contact == True:
                initcontactframes.append(framenum)
        if initcontactframes[0] == initcontactframes[-1]:
            contactrange = initcontactframes[0]
        else:
            contactrange = (int(initcontactframes[0]),int(initcontactframes[-1]))
        #returns the range of frames in which the contact region lies 
        return contactrange
    
    def calc_ContactFrameV2(self,initsamples:int,cutoff,minframe=1):
        """combines linear search followed by binary search to find frames corresonding to first contact and final seperation in video
        @param initsamples - number of evenly space frames to sample in initial linear search
        @param cutoff - number of stdevs frame averages differs from baseline averages for a region is considered to be in contact  """
        #linear search gives approximate range of frames in which contact and seperation lie 
        contactrange = self.approx_ContactFrame(initsamples,cutoff)
        #total number of frames in video
        total_frames = self.vid.get(cv.CAP_PROP_FRAME_COUNT)
        #binary search to find first contact frame
        firstcontact = va.binaryapprox_ContactFrame(contactrange[0],1,minframe,cutoff)
        #binary search to find final separation frame
        finalseparation =  va.binaryapprox_ContactFrame(contactrange[1],total_frames-1,minframe,cutoff)
        self.contact_frames = (firstcontact,finalseparation)
        return (firstcontact,finalseparation)

    def drawgrid(self,frame,contactregion = None):
        "draws grid on image with given number of rows and columns"
        frame = frame[self.crop_region[0]:self.crop_region[1],self.crop_region[2]:self.crop_region[3]]
        dimensions = frame.shape
        xres = self.gridsize[0]
        yres = self.gridsize[1]
        rows = math.floor(dimensions[0]/yres)
        columns = math.floor(dimensions[1]/xres)

        print("grid width is  {}".format(xres*columns))
        print("grid height is {}".format(yres*rows))
        print("image dimension are {}".format(dimensions[0:2]))
        hlend = xres*columns
        vlend = yres*rows
        
        lpoints = []
        
        for i in range(rows):
            ystart = yres * i
            hline = [(0,ystart),(hlend,ystart)]
            lpoints.append(hline)
            if i == rows-1:
                yend = yres * (i+1)
                hline = [(0,yend),(hlend,yend)]
                lpoints.append(hline)
        for i in range(columns):
            xstart = xres * i
            vline = [(xstart,0),(xstart,vlend)]
            lpoints.append(vline)
            if i == columns-1:
                xend = xres * (i+1)
                vline = [(xend,0),(xend,vlend)]
                lpoints.append(hline)

        
        try:
            dimg = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
        except:
            dimg = frame
        for line in lpoints:
            cv.line(dimg,line[0],line[1],(0,255,0),1)
        
        if type(contactregion) != None:
            rowindex = 0
            for row in contactregion:
                columnindex = 0
                for value in row:
                    if value == True:
                        TopLeft = (columnindex*xres,rowindex*yres)
                        BottomRight = ((columnindex+1)*xres,(rowindex+1)*yres)
                        cv.rectangle(dimg,TopLeft,BottomRight,(0,0,255),1)
                    columnindex += 1
                rowindex += 1
        
        return dimg

if __name__ == "__main__":

    file = dimport.drive_import("/Code/Test Analysis/Test Analysis/Intensity Averaging Method/test_vid_trimmed.mp4")

    va = video_analysis(file,(10,10),True)
    print(va.get_crop_region())
    va.calc_Baselines(100)
    print(va.get_baselines())

    contactframes = va.calc_ContactFrameV2(5,25)



    vid = va.get_video()

    framenum = contactframes[0]
    vid.set(cv.CAP_PROP_POS_FRAMES, framenum)
    frame = vid.read()[1]
    cv.imshow("contact frame (frame {})".format(framenum),frame)
    cv.waitKey()

    vid.set(cv.CAP_PROP_POS_FRAMES, framenum+1)
    frame = vid.read()[1]
    cv.imshow("contact frame +1 (frame {})".format(framenum+1),frame)
    cv.waitKey()

    vid.set(cv.CAP_PROP_POS_FRAMES, framenum+150)
    frame = vid.read()[1]
    cv.imshow("contact frame +150  (frame {})".format(framenum+150),frame)
    cv.waitKey()

    cregion = va.calc_contactRegions(frame,25)
    print("contact area is {} pixels".format(va.calc_contactArea(cregion)))

    cv.imshow("grid",va.drawgrid(frame,contactregion=cregion))
    cv.waitKey()


    # contapprox = va.binaryapprox_ContactFrame(contactrange[1],5413,25,33)
    # print(contapprox)

    framenum = contactframes[1]
    vid.set(cv.CAP_PROP_POS_FRAMES, framenum)
    frame = vid.read()[1]
    cv.imshow("separation frame (frame {})".format(framenum),frame)
    cv.waitKey()


    vid.set(cv.CAP_PROP_POS_FRAMES, framenum+1)
    frame = vid.read()[1]
    cv.imshow("separation frame +1 (frame {})".format(framenum+1),frame)
    cv.waitKey()







    # print(va.calc_ContactFrame(1000,1200,33))


        




    # r = region(f,(10,10))

    # print(r.get_regions().shape)
    # print(r.get_averages().shape)

    # class region():
    #     def __init__(self,img,gridsize) -> None:

    #         dimensions = img.shape
    #         xres = gridsize[0]
    #         yres = gridsize[1]
    #         rows = math.floor(dimensions[0]/yres)
    #         columns = math.floor(dimensions[1]/xres)
        
        
    #     def get_regions(self):
    #         return self.regions
        
    #     def get_averages(self):
    #         averages = np.zeros(self.regions.shape[0:2])
    #         for row in range(self.regions.shape[0]):
    #             for col in range(self.regions.shape[1]):
    #                 avg = np.mean(self.regions[row, col])
    #                 averages[row, col]=avg
    #         return averages
import tkinter as tk
from tkinter import filedialog as fd
import cv2 as cv 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from utils import drive_importing as dimport
import data_analysis as da
import time

def cv2tk(cvimage,width):
    """takes an opencv image and converts it into a tk.Photoimage"""
    scaling = width/cvimage.shape[0]
    height = int(scaling*cvimage.shape[1])
    dim = (height,width)
    img = cv.resize(cvimage, dim, interpolation = cv.INTER_AREA)
    _, im_arr = cv.imencode('.png', img)  # im_arr: image in Numpy one-dim array format.
    im_bytes = im_arr.tobytes()
    return tk.PhotoImage(data=im_bytes)

def viddict(cvvideo:cv.VideoCapture):
    """takes a cvvideo and converts it into a dictionary consisting of framenum:opencv images key value pair entries"""
    vid = cvvideo
    vid.set(cv.CAP_PROP_POS_FRAMES, 1)
    vdic = {}
    for i in range(int(vid.get(cv.CAP_PROP_FRAME_COUNT))):
        vdic[i]= vid.read()[1]
    return vdic
    
        

class analysisGUI:
    """class used to run analysis GUI."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Analysis") #name window
        self.framenum = tk.IntVar(value=1) #framenum var
        self.vidbool = False
        self.databool = False
        self.syncbool = False
        self.syncodic= None

        #defining GUI elements
        self.vidheight = 400
        self.vidlabel = tk.Label(image=None)
        self.bframe= tk.Frame()
        self.leftframe = tk.Frame()
        self.infoframe = tk.Frame(self.leftframe)
        self.fileframe = tk.Frame(self.leftframe)
        self.rightframe= tk.Frame()
        self.rframetext= tk.Label(self.rightframe,text="right frame")
       
        self.plotlabel = tk.Label(image=None)
        self.framenumlabel = tk.Label(self.infoframe,text= "Frame:"+str(self.framenum.get()),width=10)
        self.backbutton = tk.Button(self.bframe,text="<",command=self.backframe,state="disabled")
        self.back50button = tk.Button(self.bframe,text="<<",command=self.back50frame,state="disabled")
        self.forwardbutton = tk.Button(self.bframe,text=">",command=self.nextframe,state="disabled")
        self.forward50button = tk.Button(self.bframe,text=">>",command=self.next50frame,state="disabled")
        self.contactbutton = tk.Button(self.infoframe,text="contact",command=self.contactset,state="disabled")
        self.separationbutton = tk.Button(self.infoframe,text="separation",command=self.separationset,state="disabled")
        self.syncbutton = tk.Button(self.infoframe,text="sync",command= self.guisync,state="disabled")
        self.openvideobutton = tk.Button(self.fileframe,text="open video",command= self.openvideo)
        self.openfilebutton = tk.Button(self.fileframe,text="open file",command= self.openfile)


        self.lastframe = 100
        self.slider = tk.Scale(orient="horizontal",from_=1,to=self.lastframe,variable=self.framenum,resolution=25,command=self.gotoframe,length=20,repeatdelay=50,repeatinterval=5,state="disabled")

    def openvideo(self):
        try:
            vfilename = fd.askopenfilename()
            self.vid = cv.VideoCapture(str(vfilename))
            if (self.vid.isOpened() == False):
                print("Error opening the video file")
            self.viddict = viddict(self.vid)
            frame = self.viddict[1]
            self.tkvidimage = cv2tk(frame,self.vidheight)
            self.vidlabel.configure(image=self.tkvidimage)
            vidwidth = self.vidlabel.winfo_reqwidth()
            self.lastframe = self.vid.get(cv.CAP_PROP_FRAME_COUNT)
            self.slider.configure(to=self.lastframe,length=vidwidth,state="normal")
            self.forwardbutton.configure(state="normal")
            self.backbutton.configure(state="normal")
            self.back50button.configure(state="normal")
            self.forward50button.configure(state="normal")
            self.vidbool = True
            self.root.geometry("")
        except Exception as error:
            print("Video failed to open")
            print(error)

    def openfile(self):
        dfilename = fd.askopenfilename()
        self.anlys = da.analysis(dfilename)
        self.anlys.run_all(10)
        self.trialnum = int(input("which trial is this video associated with?"))
        figdata = self.anlys.FvsT_TK_trial(self.trialnum,vline=None)
        self.fig = cv.imdecode(figdata, cv.IMREAD_COLOR)
        self.timeplot = cv2tk(self.fig,400)
        self.plotlabel.config(image=self.timeplot)
        self.databool = True
        fig = self.anlys.FvsT_gui(self.trialnum,vline=None)

        print("other method started")

        import matplotlib
        matplotlib.use('TkAgg')
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import (
            FigureCanvasTkAgg,
            NavigationToolbar2Tk)
        self.figure_canvas = FigureCanvasTkAgg(fig, self.rightframe)

        # create the toolbar
        NavigationToolbar2Tk(self.figure_canvas, self.rightframe)
        self.figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)



        self.root.geometry("")

    def tkagg(self):
        figdata = self.anlys.FvsT_gui(self.trialnum,vline=None)
        import matplotlib
        matplotlib.use('TkAgg')
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import (
            FigureCanvasTkAgg,
            NavigationToolbar2Tk)
        self.figure_canvas = FigureCanvasTkAgg(self.fig, self.rightframe)

        # create the toolbar
        NavigationToolbar2Tk(self.figure_canvas, self.rightframe)





    def frameupdate(self):
        stime = time.time()
        '''Updates the ui elements to match current frame position. Usually called by tkinter event when user moves to different frame'''
        #update video
        if self.vidbool == True:
            fnum =self.framenum.get()
            frame=self.viddict[fnum]
            self.tkvidimage = cv2tk(frame,self.vidheight)
            self.vidlabel.config(image=self.tkvidimage)
            vtime = time.time()
            # print("video update took {}".format(vtime-stime))
            self.framenumlabel.config(text="Frame:"+str(fnum))
        if self.databool == True:
            #update time plot
            if self.syncbool == True:
                try:
                    datatime = self.syncodic[int(fnum)]
                except Exception as e:
                    datatime = None
                    print("error is {}".format(e))
                figdata = self.anlys.FvsT_TK_trial(self.trialnum,vline=datatime)
                self.fig = cv.imdecode(figdata, cv.IMREAD_COLOR)
                self.timeplot = cv2tk(self.fig,400)
                self.plotlabel.config(image=self.timeplot)
            else:
                datatime = None
                figdata = self.anlys.FvsT_TK_trial(self.trialnum,vline=datatime)
                self.fig = cv.imdecode(figdata, cv.IMREAD_COLOR)
                self.timeplot = cv2tk(self.fig,400)
                self.plotlabel.config(image=self.timeplot)
        # print("plot update took {}".format(time.time()-vtime))
        # print("frame update took {}".format(time.time()-stime))
    
    def guisync(self):
        '''event called when synchronization button is pressed. Synchronizes video frames to force/displacement/time data based on user's contact and separation input'''
        if type(self.contactframe) == int and type(self.separationframe) == int:
            try:
                self.syncodic= self.anlys.sync3(self.trialnum,self.contactframe,self.separationframe)
                self.syncbool = True
                print("Synced!")
                self.frameupdate()
            except:
                print("sync failed")
        else:
            print("contact or separation frame not given")
    
    def contactset(self):
        self.contactframe = self.framenum.get()
        print("contact frame set to {}".format(self.contactframe))
    
    def separationset(self):
        self.separationframe = self.framenum.get()
        print("separation frame set to {}".format(self.separationframe))
    

    def nextframe(self):
        '''event called when the > frame button is pressed. Changes the frame by +1 and updates the GUI accordingly.'''
        fnum = self.framenum.get()
        if fnum < self.lastframe:
            self.framenum.set(value=self.framenum.get()+1) 
        self.frameupdate()
    
    def next50frame(self):
        '''event called when the >> frame button is pressed. Changes the frame by +50 and updates the GUI accordingly.'''
        fnum = self.framenum.get()
        if fnum < self.lastframe:
            self.framenum.set(value=self.framenum.get()+50) 
        self.frameupdate()
    
    def backframe(self):
        '''event called when the < frame button is pressed. Changes the frame by -1 and updates the GUI accordingly.'''
        fnum = self.framenum.get()
        if fnum > 1:
            self.framenum.set(value=fnum-1) 
        self.frameupdate()
    
    def back50frame(self):
        '''event called when the << frame button is pressed. Changes the frame by -50 and updates the GUI accordingly.'''
        fnum = self.framenum.get()
        if fnum < self.lastframe and fnum>50:
            self.framenum.set(value=self.framenum.get()-50) 
        self.frameupdate()
    
    def gotoframe(self,num):
        '''event called when the slider is used to select the frame. Changes the frame based on slide position and updates the GUI accordingly'''
        self.framenum.set(value=num) 
        self.frameupdate()
        
        
        

        

    def main(self):
        '''main method that is called to run the GUI. The GUI is layed out and the mainloop() tkinter method is called.'''
        self.leftframe.grid(row=0,column=0)
        self.infoframe.pack()
        self.fileframe.pack()
        self.rightframe.grid(row=0,column=3)
        # self.rframetext.pack()
        self.openvideobutton.pack()
        self.openfilebutton.pack()
        self.framenumlabel.pack()
        self.contactbutton.pack()
        self.separationbutton.pack()
        self.syncbutton.pack()
        self.vidlabel.grid(row=0,column=1)
        self.plotlabel.grid(row=0,column=2)       
        self.bframe.grid(row=1,column=1)
        self.back50button.pack(side="left")
        self.backbutton.pack(side="left")
        self.forward50button.pack(side="right")
        self.forwardbutton.pack(side="right")
        self.slider.grid(row=2,column=1)
        self.root.mainloop()
        #run mainloop of gui window and set up window the way I want it 


    #function to set video to a specific frame...
        #maybe need tk var to track current video frame 

    #function to advance by one frame when button pressed
    #function to go back by one frame when button pressed
    #function to analyze video when button pressed - include calibration where user adjusts until correct
    #Function to go to specific frame (either by feature or by frame number idk yet)


if __name__ == '__main__':
    gui = analysisGUI()
    gui.main()
    # vim = dimport.drive_import("/Lab Computer/Probe Tack Test Data/Helen/20221102_10_30_holeOnPunch_test/clean/testVideo (6).mp4")
    # stime = time.time()
    # vdic = viddict(cv.VideoCapture(str(vim)))
    # vtime = time.time()
    # print("video opened in {}s".format(vtime-stime))
    # cv.imshow("frame",vdic[100])
    # print("frame shown in {}s".format(time.time()-vtime))
    # cv.waitKey()
    # time100 = time.time()
    # cv.imshow("frame",vdic[1000])
    # print("frame shown in {}s".format(time.time()-time100))
    # cv.waitKey()
    # time1000 = time.time()
    # cv.imshow("frame",vdic[2000])
    # print("frame shown in {}s".format(time.time()-time1000))
    # cv.waitKey()


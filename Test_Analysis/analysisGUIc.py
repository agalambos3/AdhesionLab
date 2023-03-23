import tkinter as tk
import cv2 as cv 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from utils import drive_importing as dimport
import data_analysis as da

def cv2tk(cvimage,width):
    scaling = width/cvimage.shape[0]
    height = int(scaling*cvimage.shape[1])
    dim = (height,width)
    img = cv.resize(cvimage, dim, interpolation = cv.INTER_AREA)
    _, im_arr = cv.imencode('.png', img)  # im_arr: image in Numpy one-dim array format.
    im_bytes = im_arr.tobytes()
    return tk.PhotoImage(data=im_bytes)



class analysisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Analysis")
        self.framenum = tk.IntVar(value=1)
        #specific files for testing
        vidfile = dimport.drive_import("/Lab Computer/Probe Tack Test Data/Helen/20221102_10_30_holeOnPunch_test/clean/testVideo (6).mp4")
        self.vid = cv.VideoCapture(str(vidfile))
        if (self.vid.isOpened() == False):
            print("Error opening the video file")
        datafile = dimport.drive_import("/Lab Computer/Probe Tack Test Data/Helen/20221102_10_30_holeOnPunch_test/clean/pyxpert_experimental_7.xlsx")
        self.anlys = da.analysis(datafile)
        self.anlys.run_all(10)
        t=self.anlys.get_trial(6)
        ze= t.get_zero_region()[1]
        pe=t.get_pulloff_region()[1]
        print(self.anlys.get_npdata()[ze])
        print(self.anlys.get_npdata()[pe])
       
        self.vid.set(cv.CAP_PROP_POS_FRAMES, self.framenum.get())
        frame = self.vid.read()[1]
        self.vidheight = 400
        self.tkvidimage = cv2tk(frame,self.vidheight)
        self.vidlabel = tk.Label(image=self.tkvidimage)
        self.vidwidth = self.vidlabel.winfo_reqwidth()
        self.bframe= tk.Frame()
        self.infoframe = tk.Frame()
        self.plotframe= tk.Frame()
        figdata = self.anlys.FvsT_TK_trial(6,vline=270)
        self.fig = cv.imdecode(figdata, cv.IMREAD_COLOR)

        self.timeplot = cv2tk(self.fig,400)
        self.plotlabel = tk.Label(image=self.timeplot)
        self.framenumlabel = tk.Label(self.infoframe,text= "Frame:"+str(self.framenum.get()),width=10)
        self.backbutton = tk.Button(self.bframe,text="<")
        self.backbutton.bind("<Button-1>",self.backframe)
        self.back50button = tk.Button(self.bframe,text="<<")
        self.back50button.bind("<Button-1>",self.back50frame)
        self.forwardbutton = tk.Button(self.bframe,text=">")
        self.forwardbutton.bind("<Button-1>",self.nextframe)
        self.forward50button = tk.Button(self.bframe,text=">>")
        self.forward50button.bind("<Button-1>",self.next50frame)

        self.lastframe = self.vid.get(cv.CAP_PROP_FRAME_COUNT)
        self.slider = tk.Scale(orient="horizontal",from_=1,to=self.lastframe,variable=self.framenum,resolution=50,command=self.gotoframe,length=self.vidwidth,repeatdelay=50,repeatinterval=50)
        
    def frameupdate(self):
        #update video
        fnum =self.framenum.get()
        self.vid.set(cv.CAP_PROP_POS_FRAMES, fnum)
        frame = self.vid.read()[1]
        self.tkvidimage = cv2tk(frame,self.vidheight)
        self.vidlabel.config(image=self.tkvidimage) 
        #update frame counter
        self.framenumlabel.config(text="Frame:"+str(fnum))
        #update time plot
        datatime = (fnum/52)+243
        figdata = self.anlys.FvsT_TK_trial(6,vline=datatime)
        self.fig = cv.imdecode(figdata, cv.IMREAD_COLOR)
        self.timeplot = cv2tk(self.fig,400)
        self.plotlabel.config(image=self.timeplot)


    def nextframe(self,event):
        fnum = self.framenum.get()
        if fnum < self.lastframe:
            self.framenum.set(value=self.framenum.get()+1) 
        self.frameupdate()
    
    def next50frame(self,event):
        fnum = self.framenum.get()
        if fnum < self.lastframe:
            self.framenum.set(value=self.framenum.get()+50) 
        self.frameupdate()
    
    def backframe(self,event):
        fnum = self.framenum.get()
        if fnum > 1:
            self.framenum.set(value=fnum-1) 
        self.frameupdate()
    
    def back50frame(self,event):
        fnum = self.framenum.get()
        if fnum < self.lastframe:
            self.framenum.set(value=self.framenum.get()-50) 
        self.frameupdate()
    
    def gotoframe(self,num):
        self.framenum.set(value=num) 
        self.frameupdate()
        
        
        

        

    def main(self):
        self.infoframe.grid(row=0,column=0)
        self.framenumlabel.pack()
        self.vidlabel.grid(row=0,column=1)
        self.plotframe.grid(row=0,column=2) 
        self.plotlabel.grid(row=0,column=3)       
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

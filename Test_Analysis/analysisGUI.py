#import tkinter for GUI
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image,ImageTk
from utils import drive_importing as dimport
import detectaveragesC as dc
import cv2 as cv

# file = dimport.find_file()
file= dimport.drive_import("/Code/Test Analysis/Test Analysis/Intensity Averaging Method/test_vid_trimmed.mp4")
va = dc.video_analysis(file,10,crop=True)
tkimg = None

def set_vframe():
    framenum= int(entry.get())
    currentframe.set(framenum)
    print(currentframe.get())      
    numlabel = tk.Label(text=currentframe.get(),background="white",foreground="black")
    numlabel.grid(row=0,column=0)
    vid = va.get_video()
    vid.set(cv.CAP_PROP_POS_FRAMES,framenum)
    frame = vid.read()[1]
    scale_percent = 70 # percent of original size
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    img = cv.resize(frame, dim, interpolation = cv.INTER_AREA)
    _, im_arr = cv.imencode('.png', img)  # im_arr: image in Numpy one-dim array format.
    im_bytes = im_arr.tobytes()
    tkimg1 = tk.PhotoImage(data=im_bytes)
    flabel= tk.Label(image=tkimg1,background="gold",foreground="black")
    flabel.grid(row=0,column=1)
    print("vframe set")

def setframenumber():
    frame= int(entry.get())
    if type(frame) == int:
        currentframe.set(frame)
        print(currentframe.get())      
    numlabel = tk.Label(text=currentframe.get(),background="white",foreground="black")
    numlabel.grid(row=0,column=0)

    








window = tk.Tk()
currentframe = tk.IntVar(value=5000)


# img = Image.open(file)
# print(img.size[0])
# print(img.size[1])
# height = 800
# scale = height/img.size[0]
# print(scale)
# width = int(img.size[1]*scale)
# print(width)
# img = img.resize(size=(height,width))
# img = ImageTk.PhotoImage(img)


rlabel = tk.Label(text = "blah blah",background="blue",foreground="white")
entry = tk.Entry()
enterbutton = tk.Button(text="Enter",command=set_vframe)
rlabel.grid(row=1,column=1)
entry.grid(row=0,column=3)
enterbutton.grid(row=0,column=4)


window.mainloop()
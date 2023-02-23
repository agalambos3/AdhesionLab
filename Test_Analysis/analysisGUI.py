#import tkinter for GUI
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image,ImageTk
from utils import drive_importing as dimport

file = dimport.find_file()
window = tk.Tk()

img = Image.open(file)
print(img.size[0])
print(img.size[1])
height = 800
scale = height/img.size[0]
print(scale)
width = int(img.size[1]*scale)
print(width)
img = img.resize(size=(height,width))
img = ImageTk.PhotoImage(img)



flabel= tk.Label(image= img,background="gold",foreground="black")
rlabel = tk.Label(text = "blah blah",background="blue",foreground="white")

flabel.grid(row=0,column=1)
rlabel.grid(row=1,column=1)

window.mainloop()
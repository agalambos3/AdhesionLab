#import tkinter for GUI
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image,ImageTk
from utils import drive_importing as dimport

file = dimport.find_file()
root = tk.Tk()

# Create a photoimage object of the image in the path
image1 = Image.open("<path/image_name>")
test = ImageTk.PhotoImage(image1)

label1 = tk.tkinter.Label(image=test)
label1.image = test

# Position image
label1.place(x=10, y=10)
root.mainloop()

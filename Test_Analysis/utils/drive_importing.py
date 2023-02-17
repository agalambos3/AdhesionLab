import tkinter as tk

from tkinter.filedialog import askopenfilename
tk.Tk().withdraw() # part of the import if you are not using other tkinter functions

def find_file() -> str: 
    fn = askopenfilename()
    return fn 

#Put the path of the drive directory on your device in here
drive_dir = "/Users/andras/Library/CloudStorage/GoogleDrive-galambosa@carleton.edu/Shared drives/Research"

def drive_import(filepath):
    path = drive_dir+str(filepath)
    return path



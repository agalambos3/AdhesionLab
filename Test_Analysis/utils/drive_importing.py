
def find_file() -> str: 
    import tkinter as tk
    from tkinter.filedialog import askopenfilename
    fn = askopenfilename()
    return fn 

def drive_import(filepath):
    drive_dir = "/Users/andras/Library/CloudStorage/GoogleDrive-galambosa@carleton.edu/Shared drives/Research" #Put the path of the drive directory on your device in here
    path = drive_dir+str(filepath)
    return path



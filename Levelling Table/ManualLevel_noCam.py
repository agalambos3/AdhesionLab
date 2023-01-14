# to make executable: pyinstaller --onefile --hidden-import=pyserial --hidden-import=pynput.keyboard --hidden-import=pyserial.Serial ManualLevelingPythonCode.py

import serial
from serial import Serial
import keyboard

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

def keypress(keyboardEventObject):
    if keyboard.is_pressed("esc"): quit()
    elif keyboard.is_pressed("w"): command = "w"
    elif keyboard.is_pressed("s"): command = "s"
    elif keyboard.is_pressed("a"): command = "a"
    elif keyboard.is_pressed("d"): command = "d"
    else: command = "x"

    arduino.write(bytes(command, 'utf-8'))
    
keyboard.hook(keypress)

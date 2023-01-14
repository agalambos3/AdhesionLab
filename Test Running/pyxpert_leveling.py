'''
pyxpert
v1.1
(if the file in your personal directory doesn't have a version number,
it's probably v1.0)
by Henry Sottrel (sottrelh@carleton.edu)
A module for connecting python to testxpertIII and conducting simple
press-and-pull tack tests using the RetroLine tensile tester

Some functions used here are modified versions of functions from the
Simplex-Auto-Level.py program written by Lydia Fick.
'''
#imports
import serial
from serial import Serial
import numpy as np
import time
import scipy.optimize
import cv2
import random
import subprocess
import math

'''
the compression class is a class that contains the parameters for a single
probe tack test. It is designed to be used internally in the tXLink class,
so you should not need to mess with it or manually initialize compression
objects unless you are adding new features to the tXLink class.
'''
class compression:
    #Initializes the object with the chosen parameters. The non-angle parameters are saved as strings to simplify communication with testXpert
    def __init__(self, load='', holdtime='', dspeed='', uspeed='', angle=''):
        self.load = str(load)
        self.holdtime = str(holdtime)
        self.dspeed = str(dspeed / 60)
        self.uspeed = str(uspeed / 60)
        self.angle = angle
        #/60 converts from mm/min to mm/sec, which is how testXpertIII likes the
        #speeds to be expressed. The testXpert program says that it takes speeds
        #in mm/min, but I haven't gotten the speeds to work correctly without this.
    #returns a list of the test's parameters. If the parameter dictform is set to True, the output is returned as a dictionary for easier reading.
    def testInfo(self, dictform=False):
        if dictform == True:
            return {"load": self.load, "holdtime": self.holdtime, "downspeed": self.dspeed, "upspeed": self.uspeed, "angle": self.angle}
        return [self.load, self.holdtime, self.dspeed , self.uspeed, self.angle]

'''
the tXLink class allows you to create a link between a python module and the
testXpertIII file 'henry_gsi_test.zp2'. When this file is opened, it will
automatically run a script which will wait for a tXLink object to communicate
with it. having multiple tXLink objects initialized will likely cause problems.

the easiest way to use this program is to make a copy of it in another folder,
and in that folder write other python programs that import this program.

the tXLink class comes with two important methods, which are commented
individually below

tXLink has two optional parameters. If angle is set to true, tXLink will talk
to the leveling table to enable tests to be run at different angles. If leveling
is set to true, the table will automatically level itself before starting the
tests. If leveling is set to True, angle will be set to True automatically. Note
that if the leveling table is not turned on and angle is True, the program will
get stuck trying to communuicate with it and will not run tests.

Setting cmdOut to False will turn off print outputs to stop print statements from making your cmd window messy
'''
class tXLink:
    def __init__(self, leveling = False, angle = False, cmdOut = True, autoPos=False):
        self.cmdOut = cmdOut
        self.optAngle = [0,0] #if leveling is turned on, this will be changed to the new optimal angle later
        self.angle, self.leveling = angle, leveling
        if angle or leveling:
            #Initiate serial communication with the arduino
            self.arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)
            time.sleep(3) #removing this causes problems
            if leveling:
                subprocess.call('taskkill /im testXpertIII.exe') #force-quits current session of testXpertIII
                time.sleep(3) #removing this causes problems
                subprocess.Popen(['C:\\Program Files (x86)\\Zwick\\testXpert III\\testXpertIII.exe','C:\\ProgramData\\Zwick\\testXpert III\\data\\PXSimplexLeveling.zp2']) #opens the auto-level program

                if self.cmdOut:print('Initializing serial connection to Arduino and Zwick...')
                #Initiate serial communication with the tensile tester
                #Uses a virtual com: python controls COM9 which is connected to ZIMT controlled COM8
                zwick = serial.Serial(port='COM9', baudrate=9600, timeout=.1)
                time.sleep(20) # to allow serial to fully initalize, doesn't work without it
                if self.cmdOut:print('Done initializing.')

                #initiate a numpy array for drawing a visual representation of the points checked
                img = np.zeros((500, 500), dtype=np.uint8)
                scale = 200
                stepsPerDegree = 16191 #number of steps for 1 degree change

                #A function that draws the point corresponding to the angle tested
                def displayPoint(angle):
                    #Displays the most recent angle tested on the visualization img
                    #Takes parameter angle, which is a two element list

                    pixelCoordinates = (int(angle[0] * scale + img.shape[0] / 2),
                                        int(angle[1] * scale + img.shape[1] / 2))
                    try:
                        img[pixelCoordinates] = 255
                    except IndexError:
                        if self.cmdOut:print('Failed to display point because it was out of frame!')
                    cv2.imshow('Simplex Search Visualization', img)
                    cv2.waitKey(1)


                def pullOffForce(angle):
                    """
                Return a float: the minimum force (pull-off force) as reported by Zwick
                Finds the pull off force as a function of the angle.
                This is the function used for the Simplex algorithm.
                    """

                    tiltSample(angle, self.arduino)
                    displayPoint(angle) #shows where the steppers just moved to on a visualization

                    # run the test!
                    zwick.write('x'.encode()) #send start command to Zwick
                    print("sent x")
                    
                    while not zwick.in_waiting:pass #wait for Zwick to finish test and return a pull-off forces
                    force = float(zwick.read(1000).decode()) #read the pull-off force from Zwick
                    return force

                def level(targetPrecision = .01, s = .5):

                    equalateralUnitTriangle = np.array([[ 0.577,  0.000],
                                                    [-0.289,  0.500],
                                                    [-0.289, -0.500]])
                    initialSimplex = s * equalateralUnitTriangle # determine 3 initial angles (stepper positions) to test for Simplex

                    # run the scipy implementation of Simplex to determine the location of maximum pulloff
                    result = scipy.optimize.minimize(pullOffForce, x0=np.zeros(2),
                                                 method='Nelder-Mead',
                                                 options={'initial_simplex':initialSimplex,
                                                          'xatol':targetPrecision,
                                                          'fatol':1,
                                                          'disp':True})
                    optimalAngle = result.get('x')
                    tiltSample(optimalAngle, self.arduino) #move the table to the location of maximum pull-off as determined by Simplex
                    zwick.write('y'.encode()) # end the Zwick program

                    return optimalAngle
                time.sleep(30)
                self.optAngle = level() #calls the level function and uses it to set the new optimal angle
                zwick.close() #closes the zwick port
                if self.cmdOut:print(self.optAngle)

        subprocess.call('taskkill /im testXpertIII.exe /f') #force-quits current session of testXpertIII
        time.sleep(3)
        subprocess.Popen(['C:\\Program Files (x86)\\Zwick\\testXpert III\\testXpertIII.exe',
                        'C:\\ProgramData\\Zwick\\testXpert III\\data\\pyxpert_experimental.zp2']) #opens the testing file on testXpertIII
        self.testQueue = []

        #this code, which establishes the virtualcom connection to testXpert,
        #is taken from Lydia Fick, who understands it better than I do.
        port = serial.Serial(port='COM9', baudrate=9600, timeout=.1)
         #to allow serial to fully initalize, doesn't work without it
        input("Press enter once testXpert has opened")
        port.write('py'.encode())
        while not port.in_waiting:pass
        if int(port.read().decode()):
            if self.cmdOut:print("Connected Successfully.")
            self.port = port
        else:
            if self.cmdOut:print("Failed to connect to testXpertIII")


    '''
    adds a test to the end of the test queue, so tests will be run in
    the order they are added. the inputs are the parameters for the test:
    load is the applied load in N, holdtime is the time the probe is held to
    the sample in seconds, dspeed is the speed at which the probe approaches the
    sample, and uspeed is the speed at which the probe is pulled off of the sample.

    the variable self.testQueue is just a list within tXLink, so it can be
    manually edited to add, remove, or change the order of compression objects
    by using regular list methods.
    '''
    def addTest(self, load, holdtime, dspeed, uspeed, angle = ''):
        self.testQueue.append(compression(load, holdtime, dspeed, uspeed, angle))
        return
    '''
    runTests starts running the tests which have been placed in the test queue
    and keeps running them until there are no tests remaining. the test that is
    run is always the zero-index element of the self.testQueue list, and is
    removed from the list as it is run so that the next test is the new
    zero-index element. As of now it is not possible to pause the tests while
    they are running without just quitting out of the python session,
    so be sure to queue all of the tests you want to run before using runTests.
    '''
    def runTests(self, shuffle=False, testrecord = 'lasttest'):
        #Safety Check- ensure tolerances are not exceeded
        maxLoad, maxAngle = 40, 2
        for test in self.testQueue:
            params = test.testInfo()
            if float(params[0]) > maxLoad:
                print("A test's load exceeds " + str(maxLoad) + "N and may damage the equipment.\n Tests will not run.")
                return
            if not params[-1]=='':
                if math.sqrt(params[-1][0]**2 + params[-1][1]**2) > 2:
                    print("A test's absolute angle exceeds " + str(maxAngle) +"° and may damage the equipment.\n Tests will not run.")
                    return

        if shuffle:
            random.shuffle(self.testQueue) #shuffles
        self.recordfile = open(testrecord + '.csv', 'w')
        self.recordfile.write("Load, Hold Time, Down Speed, Up Speed, X angle, Y Angle\n")
        self.port.write('x'.encode()) #tells testXpert to start the test process
        while self.testQueue != []: #loop continues to run tests until there are none left in the queue
            test = self.testQueue.pop(0).testInfo() #removes the first element in testQueue and saves its parameters
            self.recordfile.write(test[0]+','+test[1]+','+test[2]+','+test[3]) #writes test info to the record
            if test[4] != '':
                self.recordfile.write(','+str(test[4][0])+','+str(test[4][1])) #writes angle to the record if one is provided
            self.recordfile.write('\n')
            for i in range(4): #this loop sends the relavent parameters for one test to testXpertIII
                while not self.port.read().decode() == str(i):pass #wait for testXpert to indicate it's ready
                self.port.write(test[i].encode()) #send a parameter as an encoded string
                if i==1 and test[4] != '':
                    tiltSample(test[4], self.arduino, optAngle = self.optAngle) #tilt the sample to the specified angle
                    if self.cmdOut:print("DONE TILTING")
        if self.angle or self.leveling:
            time.sleep(60) #Ensures the last test has time to run before re-leveling
            tiltSample([0,0], self.arduino, optAngle = self.optAngle) #tilt the sample to leveled position
        self.recordfile.close()
        self.port.write('done'.encode()) #tells testXpert to generate the output file.
        print("sent done")
        return

def tiltSample(angle, port, stepsPerDegree = 16191, optAngle = [0,0]):
    #communicates with Arduino to move the stepper motors to locations specified in angle
    #Takes parameter angle, which is a two element list

    adjustAngle = [angle[0]+optAngle[0], angle[1]+optAngle[1]]
    xAngle = int(adjustAngle[0]*stepsPerDegree)
    yAngle = int(adjustAngle[1]*stepsPerDegree)
    port.write(str(xAngle).encode('utf-8'))        # send xAngle
    #print("waiting for confirmation")
    while port.read().decode('utf-8') != 'a': pass # wait for acknoledgment
    #print("got confirmation")
    port.write(str(yAngle).encode('utf-8'))        # send yAngle
    while port.read().decode('utf-8') != 'b': pass # wait for acknoledgment
    return

if __name__ == "__main__":
    input()

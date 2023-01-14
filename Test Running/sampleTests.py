'''
This file contains a number of sample test procedures which can be used with the
pyxpert module.

You can copy a procedure to a new file or simply un-comment the one you want by
removing the triple quotes above and below each test
'''

#Runs a single probe-tack test, without leveling.
#Preload: 5 Newtons
#Hold time during preload: 10 seconds
#Probe lowering speed to apply preload: 5 mm/min
#Probe raising speed to pull off: 10 mm/min


import pyxpert_leveling as px
link = px.tXLink(leveling=True)
for n in range(5):
    link.addTest(load=7, holdtime=10, dspeed=5, uspeed=1, angle=[0,0])
link.runTests(shuffle=True, testrecord='pleasework')


'''
import pyxpert_leveling as px
link = px.tXLink(leveling=True)
for n in range(5):
    link.addTest(load=7, holdtime=10, dspeed=5, uspeed=1, angle=[0,0])
link.runTests(shuffle=True, testrecord='20220712_10_3100_cleaned_10')
'''

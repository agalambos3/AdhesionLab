'''
getminmax.py
by Henry Sottrel (sottrelh@carleton.edu)
this is a module developed to calculate the minimum and maximum force, alongside
the compliance, from testXpert excel output files. It is specifically set up
to be easy to use for data generated using the pyxpert module. running this
file from the command line should 
'''
import pandas as pd

def getMinMax(compliance = "",
            page_index = "",
            pos_index = "",
            force_index = "",
            time_index = "",):
    #get file name
    print("Enter File Name:")
    filename = input()
    xfilename = filename + ".xlsx"

    #Ask whether compliances should be calculated
    print("get compliances? (y/n)")
    if input() in ["y", "Y"]:
        getComps = True
    else:
        getComps = False

    #Set indicies
    page_index = 1
    pos_index = 0
    force_index = 1
    time_index = 2

    #load excel file as a nested list
    df = pd.read_excel(xfilename, sheet_name=page_index)
    data = df.values.tolist()[2:]

    #find the times when the probe has lifted back to the start position
    start = data[0][pos_index]
    markers = []
    contact = False
    for point in data:
        if contact == False and point[force_index] >= 0.5:
            contact = True
        elif contact == True and abs(point[pos_index] - start) <= 0.005:
            contact = False
            markers.append(point[time_index])

    #find the absolute minimum and maximum forces between the markers
    fintervals = []
    for markerindex in range(len(markers)):
        fintervals.append([])
    markerindex = 0
    currentmarker = markers[0]
    for point in data:
        if point[time_index] == currentmarker and currentmarker != markers[-1]:
            markerindex+=1
            currentmarker = markers[markerindex]
        fintervals[markerindex].append(point[force_index])

    pairs = []
    for i in range(len(fintervals)):
        if not fintervals[i] == []:
            pairs.append((max(fintervals[i]), min(fintervals[i])))

    markerindex = 0
    currentmarker = markers[0]

    slopestart = -4
    slopeend = -1


    if getComps:
        compliances = []
        for pointindex in range(len(data)):
            if data[pointindex][time_index] == currentmarker and currentmarker != markers[-1]:
                markerindex+=1
                currentmarker = markers[markerindex]
            if data[pointindex][force_index] == pairs[markerindex][0]:
                compliances.append((data[pointindex+slopeend][pos_index] - data[pointindex+slopestart][pos_index]) / (data[pointindex+slopeend][force_index] - data[pointindex+slopestart][force_index]))

    #write pairs to output file
    filenameex = "_loadvforce"
    num = 0
    while True:
        try:
            outfile = open(filename + filenameex + ".csv", "w")
        except:
            num += 1
            filenameex = filenameex + "_" + str(num)
            continue
        break
    outfile.write("Load (N), Adhesive Force (N), Compliance(m/N)\n")
    compstring = ''
    for pairindex in range(len(pairs)):
        if getComps:
            compstring = str(compliances[pairindex])
        outfile.write(str(pairs[pairindex][0])+","+str(-1 * pairs[pairindex][1])+","+compstring+"\n")
    outfile.close()

if __name__ == "__main__":
    getMinMax()

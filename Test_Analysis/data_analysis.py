import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import drive_importing as dimport

#indexing off by 4 from excel (eg. row 4 in excel is index 0 in array)


class trial():
    '''class that contains analysis information for a single trial. Also contains data points associated with trial'''
    def __init__(self,number:int,start:int) -> None:
        self.data = None
        self.loading = 0
        self.loading_region= None
        self.unloading = 0
        self.unloading_region = None
        self.pulloff = 0
        self.pulloff_region = None
        self.holding_region = None
        self.zero_region = None
        self.number = number
        self.start = start
        self.end = None
    def __str__(self) -> str:
        return "trial {}, start index: {}, end index {}".format(self.get_number(),self.get_start(),self.get_end())

    def get_number(self):
        '''get trial number'''
        return self.number
    def get_loading(self):
        '''get loading area'''
        return self.loading  
    def get_unloading(self):
        '''get unloading area'''
        return self.unloading
    def get_pulloff(self):
        '''get pulloff area'''
        return self.pulloff 
    def get_area_diff(self):
        return self.loading-self.unloading
    def get_data(self):
        return self.data
    def get_start(self):
        '''get start index of trial'''
        return self.start
    def get_zero_region(self):
        return self.zero_region
    def get_loading_region(self):
        return self.loading_region
    def get_holding_region(self):
        return self.holding_region
    def get_unloading_region(self):
        return self.unloading_region
    def get_pulloff_region(self):
        return self.pulloff_region
    def get_end(self):
        '''get end index of trial'''
        return self.end
    
    def set_data(self,npdata):
        self.data = npdata
    def set_zero_region(self,start,end):
        self.zero_region = (start,end)
    def set_loading_region(self,start,end):
        self.loading_region = (start,end)
    def set_holding_region(self,start,end):
        self.holding_region = (start,end)
    def set_unloading_region(self,start,end):
        self.unloading_region = (start,end)
    def set_pulloff_region(self,start,end):
        self.pulloff_region = (start,end)
    def set_end(self,index):
        '''set end index of trial'''
        self.end = index

    def add_loading(self,area):
        '''add to the loading area of the trial'''
        self.loading += area  
    def add_unloading(self,area):
        '''add to the unloading area of the trial'''
        self.unloading += area 
    def add_pulloff(self,area):
        '''add to the pull off area of the trial'''
        self.pulloff += area

    def plot(self):
        '''plot a trial '''
        t = self
        zs = t.get_zero_region()[0]
        ze = t.get_zero_region()[1]-zs

        ls = t.get_loading_region()[0]-zs
        le = t.get_loading_region()[1]-zs

        hs = t.get_holding_region()[0]-zs
        he = t.get_holding_region()[1]-zs

        uls = t.get_unloading_region()[0]-zs
        ule = t.get_unloading_region()[1]-zs

        ps = t.get_pulloff_region()[0]-zs
        pe = t.get_pulloff_region()[1]-zs

        x = self.get_data()[:,0]
        y = self.get_data()[:,1]
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("Trial {}".format(self.get_number()))


        ax1.scatter(x[0:ze], y[0:ze], s=2, c='b', marker="o", label='zeros')
        ax1.scatter(x[ls:le-1],y[ls:le-1], s=2, c='r', marker="o", label='loading')
        ax1.scatter(x[hs:he-1],y[hs:he-1], s=2, c='g', marker="o", label='holding')
        ax1.scatter(x[uls:ule-1],y[uls:ule-1], s=2, c='m', marker="o", label='unloading')
        ax1.scatter(x[ps-1:pe],y[ps-1:pe], s=2, c='c', marker="o", label='pulloff')
    
        print(t)
        plt.legend(loc='upper left');
        plt.savefig('trial{}'.format(self.get_number()))
        plt.show()

class analysis():
    '''class that handles data analysis of excel data generated by zwick machine '''
    
    def __init__(self,filename) -> None:
        '''initialize instance of historesis() object by giving filename to open'''
        xls = pd.ExcelFile(filename)
        df = pd.read_excel(xls,'Values Specimen 1',header=2)
        self.npdata = pd.DataFrame.to_numpy(df)
        self.trialList = []
        self.timestep = .01
    
    def get_npdata(self):
        '''get data in numpy array form'''
        return self.npdata
    
    def get_all(self):
        '''returns the list of trials'''
        return self.trialList

    def get_trial(self,number):
        '''get a specific trial from the list of trials'''
        return self.trialList[number-1]

    def get_num_trials(self):
        return len(self.trialList)

    def get_statlist(self,stat:str):
        '''returns a list of a desired statistic for each trial in the data set
        @param stat: string for what statistic to return. options are:\n
        "areadiff", "pulloff"
        '''
        sList = []
        if stat == "areadiff":
            for t in self.trialList:
                s=t.get_area_diff()
                sList.append(s)
        elif stat == "pulloff":
            for t in self.trialList:
                s=t.get_pulloff()
                sList.append(s)
        return sList

    def run_trial(self,number:int,start:int,holdtime):
        '''analyzes a single trial in the dataset. Takes the number of the trial, its holdtime, and its starting index. Returns a trial() object that contains the analysis info of the trial '''

        # np.amax(self.get_npdata()[start:,1])
        try:#TODO change summing to be trapzoidal rather than square sum. Should hopefully make sums more accurate
            #initialize trial object 
            t= trial(number,start)

            #initial index that trial starts at. Given as parameter to method
            i= start
            
            #minimum force for point to be registered in summation and as part of a region
            frcth = .01

            #corresponds to the minimum travel needed for a point to be in the loading region (assuming force and deltrvl thresholds met)
            mintrvl = .05

            #while force threshold isn't met just advance along array. this is to get through zeros and weird stuff at beginning of each trial
            force = self.get_npdata()[i,1]
            while self.npdata[i,0]<= mintrvl or force <= frcth :
                force = self.get_npdata()[i,1]
                i+=1
            i1 = i
            t.set_zero_region(start,i1)

            #while deltrvl is not zero advance along array and sum to loading
            deltrvl = self.npdata[i+1,0]-self.npdata[i,0]
            while deltrvl!= 0 or self.npdata[i,0] <=mintrvl:
                force = self.npdata[i,1]
                deltrvl = self.npdata[i+1,0]-self.npdata[i,0]

                if force >=frcth:
                    t.add_loading(force*deltrvl)
                i+=1
            i2= i
            t.set_loading_region(i1,i2)

            #advance holdtime number of seconds in the array to go through holding section
            htime = 0
            deltime = 0
            while htime < holdtime:
                deltime = self.npdata[i+1,2]-self.npdata[i,2]
                htime += deltime
                i+=1
            
            i3=i
            t.set_holding_region(i2,i3)
            
            #summing and iteration through unloading region
            force = self.get_npdata()[i,1]
            while force >-frcth:
                force = self.get_npdata()[i,1]
                nxtforce = self.get_npdata()[i+1,1]
                deltrvl = self.npdata[i+1,0]-self.npdata[i,0]
                t.add_unloading(((force+nxtforce)/2)*abs(deltrvl))
                i+=1
            i4 = i
            t.set_unloading_region(i3,i4)
            #is there a fucky wucky here?

            #summing and iteration through pulloff region
            while force < 0:
                force = self.get_npdata()[i,1]
                nxtforce = self.get_npdata()[i+1,1]
                deltrvl = self.npdata[i+1,0]-self.npdata[i,0]
                t.add_pulloff(((force+nxtforce)/2)*abs(deltrvl))
                i+=1
            i5 = i
            data=self.get_npdata()[start:i5+1]
            t.set_data(data)
            t.set_pulloff_region(i4,i5)
            t.set_end(i5)


            # print("trial ran")
            return t
        
        except IndexError:
            return None          

    def run_all(self,holdtime):
        '''runs all the trials in a data set using run_trial() method repeatley'''
        index=0
        tnum = 1
        t= 0
        while t!=None:
            t= self.run_trial(tnum,index,holdtime)
            if t != None:
                self.trialList.append(t)
                index= t.get_end()
                tnum+= 1

    def FvsDplot_trial(self,number):
        '''plot a specific trial from the dataset'''
        t = self.get_trial(number)
        zs = t.get_zero_region()[0]
        ze = t.get_zero_region()[1]

        ls = t.get_loading_region()[0]
        le = t.get_loading_region()[1]

        hs = t.get_holding_region()[0]
        he = t.get_holding_region()[1]

        uls = t.get_unloading_region()[0]
        ule = t.get_unloading_region()[1]

        ps = t.get_pulloff_region()[0]
        pe = t.get_pulloff_region()[1]

        x = self.get_npdata()[:,0]
        y = self.get_npdata()[:,1]
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("Trial {}".format(number))
        ax1.set_xlabel("Standard Travel [mm]")
        ax1.set_ylabel("Standard Force [N]")


        ax1.scatter(x[zs:ze], y[zs:ze], s=2, c='b', marker="o", label='zeros')
        ax1.scatter(x[ls:le-1],y[ls:le-1], s=2, c='r', marker="o", label='loading')
        ax1.scatter(x[hs:he-1],y[hs:he-1], s=2, c='g', marker="o", label='holding')
        ax1.scatter(x[uls:ule-1],y[uls:ule-1], s=2, c='m', marker="o", label='unloading')
        ax1.scatter(x[ps-1:pe],y[ps-1:pe], s=2, c='c', marker="o", label='pulloff')

        print(t)
        plt.legend(loc='upper left');
        plt.show()
    
    def FvsTplot_trial(self,number,vline=None):
        '''plot a specific trial from the dataset'''
        t = self.get_trial(number)
        zs = t.get_zero_region()[0]
        ze = t.get_zero_region()[1]

        ls = t.get_loading_region()[0]
        le = t.get_loading_region()[1]

        hs = t.get_holding_region()[0]
        he = t.get_holding_region()[1]

        uls = t.get_unloading_region()[0]
        ule = t.get_unloading_region()[1]

        ps = t.get_pulloff_region()[0]
        pe = t.get_pulloff_region()[1]

        x = self.get_npdata()[:,2]
        y = self.get_npdata()[:,1]
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("Trial {}".format(number))
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Standard Force [N]")


        ax1.scatter(x[zs:ze], y[zs:ze], s=2, c='b', marker="o", label='zeros')
        ax1.scatter(x[ls:le-1],y[ls:le-1], s=2, c='r', marker="o", label='loading')
        ax1.scatter(x[hs:he-1],y[hs:he-1], s=2, c='g', marker="o", label='holding')
        ax1.scatter(x[uls:ule-1],y[uls:ule-1], s=2, c='m', marker="o", label='unloading')
        ax1.scatter(x[ps-1:pe],y[ps-1:pe], s=2, c='c', marker="o", label='pulloff')
        if vline != None:
            ax1.axvline(vline)

        print(t)
        plt.legend(loc='upper left');
        plt.show()
        
def user_input():
    '''function that allows user to get analysis information they want from data set\n
    Things to implement:\n
    Have user enter name of file with raw data like with getminmax (or maybe see if file selector can be opened)\n

    Give some way for user to select analysis they want outputted (loading area, area diff, etc).
    Data should be outputted either to excel/csv file or in format where it is easy to paste into excel file\n
    
    Give user way to get the plots of each trial both in raw data form (excel) or as an image (generated through
    matplotlib plotting)\n

    If it is not too difficult make very basic GUI as it could go a long way especially when selecting multiple options\n
    
    '''
    validInput = False
    anlys = None
    while validInput == False:
        try:
            filename = input("Enter Filename:\n") + ".xlsx"
            anlys = analysis(filename)
            validInput = True
        except:
            print("Invalid file name. Please try again\n")
        
    htime = float(input("Enter the holdtime of the tests:\n"))
    
    anlys.run_all(htime)
    difflist = anlys.get_statlist("areadiff")
    outdict = {"Trial":list(range(1,len(difflist)+1)),"Area Difference":difflist}
    sdf = pd.DataFrame(outdict)
    sdf.to_excel("trial statistics.xlsx",index=False)

if __name__ == "__main__":
    file = dimport.drive_import("/Lab Computer/Probe Tack Test Data/Helen/20221102_10_30_holeOnPunch_test/clean/pyxpert_experimental_7.xlsx")
    anlys = analysis(file)
    htime = float(10)
    anlys.run_all(htime)
    # anlys.FvsDplot_trial(6)
    anlys.FvsTplot_trial(6,vline=270)



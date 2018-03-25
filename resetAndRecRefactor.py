# import modules that I'm using
import matplotlib
matplotlib.use('TKAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as pltlib
import matplotlib.ticker as plticker
from matplotlib.ticker import MultipleLocator
import Tkinter as tk
from Tkinter import *
import numpy as np
import serial
import os
import time
from datetime import datetime

#Create path for saving files
appDataPath = os.getenv('LOCALAPPDATA') + '\\shockData\\'
if not os.path.exists(appDataPath):
    os.makedirs(appDataPath)

#Give option for test data or real data
testFlag = input("Test? 1 for yes, 0 for no. ")
#These variables are set at the start to be used later on in the plotting. As long as they are 'in scope' and are set before you try to use them, it doesn't matter where you set them. Being in scope means being declared where you are using them. An example of being out of scope would be if you had a "main" function, and a separate "graph" function that is called inside main. If you declare a variable min_val inside the graph function, and try to use it in the main, it won't work because main can't see it.
min_val = 0
max_val = 1024

#Set the port number. Ultimately this will be a UI option
port = 'com6'

#This is an empty array of data that will be populated later with the values from the serial port
valList = []

#Write the data to text files
def writeToFile(valListA, valListB, valListC):
    valFiles = ["testfileA.txt", "testfileB.txt", "testfileC.txt"]
    valLists = [valListA, valListB, valListC]

    for index, file in enumerate(valFiles):
        valFile = open(file, "w")
        for val in valLists[index]:
            if not val:
                valFile.write('0 \n')
            else:
        		valFile.write(str(val))
        		#\n means the end of the line. .txt files interpret this
        		valFile.write('\n')

#Set up 3 data streams
def testData():
    fA = open('Test Results 1/testFileA.txt', 'r')
    fLinesA = fA.read().split('\n')
    valListA = []
    for aLine in fLinesA:
        if aLine.strip():
            valListA.append(int(aLine))

    fB = open('Test Results 1/testFileB.txt', 'r')
    fLinesB = fB.read().split('\n')
    valListB = []
    for bLine in fLinesB:
        if bLine.strip():
            valListB.append(int(bLine))

    fC = open('Test Results 1/testFileC.txt', 'r')
    fLinesC = fC.read().split('\n')
    valListC = []
    for cLine in fLinesC:
        if cLine.strip():
            valListC.append(int(cLine))

    return [valListA, valListB, valListC]

#Convert sample number to time for max min points
def numberTest(value, totalTime, sampleLength):
    #Check for test or not to use time values
    if testFlag == 0:
        totalTime = 2
        sampleLength = 1000

    try:
        newVal = float(value)*totalTime/sampleLength
    except:
        newVal = None
    return newVal

#Calculate peaks and troughs of data A
def peaksTroughs(valListA, totalTime):
    maxVal = max(valListA)
    maxVals = []
    for i in range(len(valListA)):
        if (valListA[i] > maxVal-5) and (valListA[i] < maxVal+5):
            maxVals.append([numberTest(i, totalTime, len(valListA)), valListA[i]])

    #Only do this if maxVals is valid
    if len(maxVals) > 1:
        for j in range(len(maxVals)-1):
            if maxVals[j+1][0] - maxVals[j][0] > 0.1:
                firstMax = maxVals[j]
                nextMax = maxVals[j+1]
                break
    try:
        firstMax
    except NameError:
        firstMax = [None, None]
    try:
        nextMax
    except NameError:
        nextMax = [None, None]

    minVal = min(valListA)
    minVals = []
    for i in range(len(valListA)):
        if (valListA[i] > minVal-5) and (valListA[i] < minVal+5):
            minVals.append([numberTest(i, totalTime, len(valListA)), valListA[i]])

    if len(minVals) > 1 and firstMax[0] != None:
        for j in range(len(minVals)):
            if minVals[j][0] > firstMax[0]:
                firstMin = minVals[j]
                break

        for k in range(len(minVals)):
            if minVals[k][0] > nextMax[0]:
                nextMin = minVals[k-1]
                break
    else:
        firstMin = [None, None]
        nextMin = [None, None]

    return [firstMax, nextMax, firstMin, nextMin]

#Save data to text file
def saveDataAsTxt(fileName, valListA, valListB, valListC, tA):
    valListASave = np.array(valListA)
    valListBSave = np.array(valListB)
    valListCSave = np.array(valListC)
    timeSave = np.array(tA)

    dataSave = np.array([valListASave, valListBSave, valListCSave,timeSave])
    dataSave = dataSave.T
    #Open a text file that is writable

    fullPath = appDataPath + fileName
    #with open(dataFilePath, 'w+') as datafile_id:
    with open(fullPath, 'w+') as datafile_id:
        np.savetxt(datafile_id, dataSave, fmt=['%s','%s','%s','%f'])

    F = open(fullPath,'a')
    F.write("DETAILS")

#Get data from serial port
def runLoop(fileName):
    if testFlag == 1:
        ser = serial.Serial(port, 230400, timeout=1)
        #Need to give 3 seconds to activate
        time.sleep(3)

    valList = []
    startTime = time.time()

    if testFlag == 1:
        startCommand = 'START$'
        #sendStart = bytes(startCommand.encode('utf-8'))
        stopCommand = 'STOP$'
        #sendStop = bytes(stopCommand.encode('utf-8'))
        ser.write(startCommand)
        print("START RECORDING")
        for i in range(7000):
            valList.append(ser.readline())
        ser.write(stopCommand)

        endTime = time.time()
        totalTime = endTime - startTime
        print("Total time is " + str(totalTime))

        #Split valList into 3 lists
        valListA = []
        valListB = []
        valListC = []

        #Split up values into three lists
        for val in valList:
            if val[0] == 'a':
                modVal = val[1:]
                try:
                    float(modVal)
                    valListA.append(int(modVal.rstrip()))
                except ValueError:
                    pass
            elif val[0] == 'b':
                modVal = val[1:]
                try:
                    float(modVal)
                    valListB.append(int(modVal.rstrip()))
                except ValueError:
                    pass
            else:
                try:
                    float(val)
                    valListC.append(int(val.rstrip()))
                except ValueError:
                    pass
    else:
        valListsToSplit = testData()
        valListA = valListsToSplit[0]
        valListB = valListsToSplit[1]
        valListC = valListsToSplit[2]
        totalTime = 2.0

    #Resize arrays to match A
    if len(valListA) <= len(valListB):
        valListB = valListB[0:len(valListA)]
        if len(valListA) <= len(valListC):
            valListC = valListC[0:len(valListA)]
        else:
            diffC = len(valListA) - len(valListC)
            for i in range(diffC):
                valListC.append(valListC[len(valListC)-1])
    else:
        diffB = len(valListA) - len(valListB)
        for i in range(diffB):
            valListB.append(valListB[len(valListB)-1])
        if len(valListA) <= len(valListC):
            valListC = valListC[0:len(valListA)]
        else:
            diffC = len(valListA) - len(valListC)
            for i in range(diffC):
                valListC.append(valListC[len(valListC)-1])

    #Write values to files for easy analysis
    writeToFile(valListA, valListB, valListC)

    #Get peaks and troughs
    maxAndMins = peaksTroughs(valListA, totalTime)
    topPeakToTrough = maxAndMins[0]
    bottomPeakToTrough = maxAndMins[1]
    topTroughToPeak = maxAndMins[2]
    bottomTroughToPeak = maxAndMins[3]

    #Increments to plot your points on are the total time divided by the amount of points
    incA = totalTime/float(len(valListA))
    tA= np.arange(0.0, totalTime, incA)

    if len(valListA) < len(tA):
        tA = tA[0:len(valListA)]

    print("LENGTH IS " + str(len(valListA)))

    values = [tA,valListA,valListB,valListC,topPeakToTrough[0],topPeakToTrough[1], bottomPeakToTrough[0], bottomPeakToTrough[1], topTroughToPeak[0], topTroughToPeak[1], bottomTroughToPeak[0], bottomTroughToPeak[1]]
    return values

#Make object for application
class App_Window(tk.Tk):

    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
    def initialize(self):
        frame = Frame(self)
        frame.pack(side="left", fill="both", expand = True)

        plotFrame = Frame(self)
        plotFrame.pack(side="right", fill="both", expand = True)

        #Left-hand-side
        self.l1 = Label(frame, text="Heading Text").grid(row=0,columnspan=2)

        self.l2 = Label(frame, text="Name").grid(row=1, sticky=W)
        self.l3 = Label(frame, text="Clicks (C)").grid(row=3, sticky=W)
        self.l4 = Label(frame, text="Clicks (R)").grid(row=5, sticky=W)
        self.l5 = Label(frame, text="Temp").grid(row=7, sticky=W)
        self.l6 = Label(frame, text="Notes").grid(row=9, sticky=W)

        defaultName = tk.StringVar(frame, value='Timestamp')

        #Put timestamp as default value and clear it when clicked
        self.e1 = Entry(frame, width=30, textvariable=defaultName)
        self.e1.bind("<Button-1>", self.clearText)
        self.e2 = Entry(frame, width=30)
        self.e3 = Entry(frame, width=30)
        self.e4 = Entry(frame, width=30)
        self.e5 = Text(frame,width=23, height=5)

        self.e1.grid(row=2, column=0,sticky=W)
        self.e2.grid(row=4, column=0,sticky=W)
        self.e3.grid(row=6, column=0,sticky=W)
        self.e4.grid(row=8, column=0,sticky=W)
        self.e5.grid(row=10, column=0,sticky=W)

        self.btn_text = tk.StringVar()
        self.saveTxt = tk.StringVar()
        self.discardTxt = tk.StringVar()

        button = tk.Button(frame,
                           textvariable=self.btn_text,
                           fg="green",
                           command=self.OnButtonClick)
        self.btn_text.set("Start")
        button.grid(row=11, column=0,stick=W)

        self.btn_text2 = tk.StringVar()
        button2 = tk.Button(frame,
                           textvariable=self.btn_text2,
                           command=self.resetGraph)
        self.btn_text2.set("Reset")
        button2.grid(row=12, column=0,stick=W)

        saveBtn = tk.Button(frame,
                           textvariable=self.saveTxt,
                           command=self.saveBtn)
        self.saveTxt.set("Save")
        saveBtn.grid(row=13, column=0,stick=W)

        discardBtn = tk.Button(frame,
                           textvariable=self.discardTxt,
                           command=self.resetGraph)
        self.discardTxt.set("Discard")
        discardBtn.grid(row=14, column=0,stick=W)

        #button = tk.Button(self,text="Start",command=self.OnButtonClick).pack(side=tk.LEFT,anchor=W)
        #button = tk.Button(plotFrame,text="Start",command=self.OnButtonClick).grid(row=11, column=0)
        #Right hand side with Graph
        Label(plotFrame, text="Graph Stuff heading").pack()

        self.f = Figure(figsize=(6,4), dpi=100)
        a = self.f.add_subplot(111)
        x = []
        y = []

        self.line1, = a.plot(x,y,'g')
        self.line2, = a.plot(x,y,'r')
        self.line3, = a.plot(x,y,'b')

        #Create dots to show peak to trough and trough to peak
        self.PtTPeak, = a.plot([],[],'mx')
        self.PtTTrough, = a.plot([],[],'mx')
        self.TtPPeak, = a.plot([],[],'mx')
        self.TtPTrough, = a.plot([],[],'mx')

        self.canvas = FigureCanvasTkAgg(self.f, plotFrame)
        self.canvas.show()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.NONE, expand=False, anchor=W)
        self.update
        toolbar = NavigationToolbar2TkAgg(self.canvas, plotFrame).pack(side=tk.TOP)
        Label(plotFrame, text="Data One").pack(anchor=W)
        Label(plotFrame, text="Data Two").pack(anchor=W)
        Label(plotFrame, text="Data Three").pack(anchor=W)

    def saveBtn(self):
        saveDataAsTxt(self.fileName, self.tA, self.valListA, self.valListB, self.valListC)

    def clearText(self, event):
        self.e1.delete(0, "end")
        return None

    def resetGraph(self):
        self.clearGraph()

    def clearGraph(self):
        print "reset"
        #valList = []
        self.line1.set_data([],[])
        self.line2.set_data([],[])
        self.line3.set_data([],[])
        self.PtTPeak.set_data([],[])
        self.PtTTrough.set_data([],[])
        self.TtPPeak.set_data([],[])
        self.TtPTrough.set_data([],[])
        ax = self.canvas.figure.axes[0]
        #ax.grid(False)

        self.canvas.draw()
        #self.refreshFigure(tA,valListA,valListB,valListC,firstIndexPtT,firstValPtT, endIndexPtT, endValPtT, firstIndexTtP, firstValTtP, endIndexTtP, endValTtP)
    	print("Finished")

    def refreshFigure(self,xA,yA,yB,yC,indexPtTPeak,valPtTPeak,indexPtTTrough,valPtTTrough,indexTtPPeak,valTtPPeak,indexTtPTrough,valTtPTrough):
        spacing = 0.1
        spacingy = 80
        minorLocator = MultipleLocator(spacing)
        minorLocatory = MultipleLocator(spacingy)

        minY = 0
        maxY = 1024

        self.line1.set_data(xA,yA)
        self.line2.set_data(xA,yB)
        self.line3.set_data(xA,yC)
        if (indexPtTPeak != None or valPtTPeak != None):
            self.PtTPeak.set_data(indexPtTPeak,valPtTPeak)
        if (indexPtTTrough != None or valPtTTrough != None):
            self.PtTTrough.set_data(indexPtTTrough,valPtTTrough)
        if (indexTtPPeak != None or valTtPPeak != None):
            self.TtPPeak.set_data(indexTtPPeak,valTtPPeak)
        if (indexTtPTrough != None or valTtPTrough != None):
            self.TtPTrough.set_data(indexTtPTrough,valTtPTrough)
        ax = self.canvas.figure.axes[0]

        ax.yaxis.set_minor_locator(minorLocatory)
        ax.xaxis.set_minor_locator(minorLocator)
        # Set grid to use minor tick locations.
        ax.grid(True, which = 'minor')

        ax.set_ylim(minY, maxY)
        ax.set_xlim(min(xA), max(xA))
        self.canvas.draw()

    def OnButtonClick(self):
        fileName = self.e1.get()

        timeStampUnsplit = str(datetime.now())[0:19].split(' ')
        timeStamp = (timeStampUnsplit[0] + 'T' + timeStampUnsplit[1] + '.txt').replace(':', '-')
        print timeStamp
        if (len(fileName) == 0 or fileName == 'Timestamp'):
            fileName = timeStamp
        else:
            fileName = fileName + '.txt'
    	values = runLoop(fileName)
        self.fileName = fileName
        self.tA = values[0]
        self.valListA = values[1]
        self.valListB = values[2]
        self.valListC = values[3]
        self.refreshFigure(values[0],values[1],values[2],values[3],values[4],values[5], values[6], values[7], values[8], values[9], values[10], values[11])


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()

if __name__ == "__main__":
    MainWindow = App_Window(None)
    MainWindow.minsize(width=800, height=600)
    MainWindow.mainloop()

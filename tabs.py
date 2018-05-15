# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/

import matplotlib
matplotlib.use('TKAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as pltlib
import matplotlib.ticker as plticker
from matplotlib.ticker import MultipleLocator
import Tkinter as tk
from Tkinter import *
import ttk
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
testFlag = raw_input("Test? 1 for yes, 0 for no. ")
#testFlag = 0
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
    fA = open('Test Results 3/testFileA.txt', 'r')
    fLinesA = fA.read().split('\n')
    valListA = []
    for aLine in fLinesA:
        if aLine.strip():
            valListA.append(int(aLine))

    fB = open('Test Results 3/testFileB.txt', 'r')
    fLinesB = fB.read().split('\n')
    valListB = []
    for bLine in fLinesB:
        if bLine.strip():
            valListB.append(int(bLine))

    fC = open('Test Results 3/testFileC.txt', 'r')
    fLinesC = fC.read().split('\n')
    valListC = []
    for cLine in fLinesC:
        if cLine.strip():
            valListC.append(int(cLine))

    return [valListA, valListB, valListC]

#Convert sample number to time for max min points
def numberTest(value, totalTime, sampleLength):
    #Check for test or not to use time values
    if testFlag == '0':
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
    print "TEST FLAG IS " + testFlag
    if testFlag == '1':
        print "REAL TEST"
        ser = serial.Serial(port, 230400, timeout=1)
        #Need to give 3 seconds to activate
        time.sleep(3)
    else:
        print "NOT REAL"

    valList = []
    startTime = time.time()

    if testFlag == '1':
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


class  App_Window(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.title('Shock Dyno')
        self.iconbitmap('icon.ico')
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, ComparePage):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        topFrame = Frame(self)
        topFrame.pack(side="top", fill="both")
        # homeBtn = tk.Button(topFrame, text="HOME", padx=20, pady=10,
        #                      command=lambda: self.show_frame(StartPage))
        homeBtn = tk.Button(topFrame, text="HOME", padx=20, pady=10, state=ACTIVE,
                             command=lambda: controller.show_frame(StartPage))
        homeBtn.config(relief=SUNKEN)
                             # frame.tkraise()
        compareBtn = tk.Button(topFrame, text="COMPARE", padx=20, pady=10,
                            command=lambda: controller.show_frame(ComparePage))
        dataBtn = tk.Button(topFrame, text="DATA", padx=20, pady=10)
        homeBtn.grid(row=0, column=1)
        compareBtn.grid(row=0, column=2)
        dataBtn.grid(row=0, column=3)

        self.initialize()


    def initialize(self):
        #Line to cut off menu
        menuSeparator = Frame(self, height=1, bg="grey").pack(side="top", fill="both")

        frame = Frame(self)
        frame.pack(side="left", fill="both", padx=10, pady=10)

        #Left-hand-side
        self.l1 = Label(frame, text="INPUT FIELDS").grid(row=0, sticky=W, columnspan=3)

        self.l2 = Label(frame, text="Name *").grid(row=1, sticky=W, columnspan=3)
        self.l3 = Label(frame, text="Clicks (C)").grid(row=3, sticky=W, columnspan=3)
        self.l4 = Label(frame, text="Clicks (R)").grid(row=5, sticky=W, columnspan=3)
        self.l5 = Label(frame, text="Temp").grid(row=7, sticky=W, columnspan=3)
        self.l6 = Label(frame, text="Notes").grid(row=9, sticky=W, columnspan=3)
        self.defaultName = tk.StringVar(frame, value='Timestamp')
        self.e2txt = tk.StringVar()
        self.e3txt = tk.StringVar()
        self.e4txt = tk.StringVar()
        self.e5txt = tk.StringVar()

        #Put timestamp as default value and clear it when clicked
        self.e1 = Entry(frame, width=30, textvariable=self.defaultName)
        self.e1.bind("<Button-1>", self.clearText)
        self.e2 = Entry(frame, width=30, textvariable=self.e2txt)
        self.e3 = Entry(frame, width=30, textvariable=self.e3txt)
        self.e4 = Entry(frame, width=30, textvariable=self.e4txt)
        self.e5 = Text(frame,width=23, height=5)

        self.e1.grid(row=2, column=0,sticky=W, columnspan=3)
        self.e2.grid(row=4, column=0,sticky=W, columnspan=3)
        self.e3.grid(row=6, column=0,sticky=W, columnspan=3)
        self.e4.grid(row=8, column=0,sticky=W, columnspan=3)
        self.e5.grid(row=10, column=0,sticky=W, columnspan=3)

        self.btn_text = tk.StringVar()
        self.saveTxt = tk.StringVar()
        self.discardTxt = tk.StringVar()

        self.startBtn = tk.Button(frame,
                           textvariable=self.btn_text,command=self.OnButtonClick, padx=15, pady=8)
        self.btn_text.set("START")
        self.startBtn.grid(row=11, column=0)

        self.btn_text2 = tk.StringVar()
        self.resetBtn = tk.Button(frame,
                           textvariable=self.btn_text2,
                           command=self.resetGraph, state=DISABLED, padx=15, pady=8)
        self.btn_text2.set("RESET")
        self.resetBtn.grid(row=11, column=1)
        frame.grid_rowconfigure(11, minsize=50)


        plotFrame = Frame(self)
        plotFrame.pack(side="right", fill="both", expand = True, padx=40, pady=10)
        self.saveBtn = tk.Button(plotFrame,
                           textvariable=self.saveTxt,
                           command=self.saveBtn, state=DISABLED, padx=20, pady=8)
        self.saveTxt.set("SAVE")
        self.saveBtn.grid(row=2, column=4, sticky=E)

        self.discardBtn = tk.Button(plotFrame,
                           textvariable=self.discardTxt,
                           command=self.resetGraph, state=DISABLED, padx=15, pady=8)
        self.discardTxt.set("DISCARD")
        self.discardBtn.grid(row=2, column=5)

        Label(plotFrame, text="GRAPH").grid(row=0, column=0, sticky=W)

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

        self.canvas._tkcanvas.grid(row=1, column=0, columnspan=6, pady=8)
        self.update
        self.data1Txt = tk.StringVar()
        self.data2Txt = tk.StringVar()
        self.data3Txt = tk.StringVar()
        self.saved = tk.StringVar()
        self.savedTxt = Label(plotFrame, textvariable=self.saved).grid(row=2, column=0, sticky=W)
        # toolbar = NavigationToolbar2TkAgg(self.canvas, plotFrame).grid(row=2, column=0, columnspan=6, sticky=W)
        self.data1 = Label(plotFrame, textvariable=self.data1Txt).grid(row=3, column=0, sticky=W)
        self.data2 = Label(plotFrame, textvariable=self.data2Txt).grid(row=4, column=0, sticky=W)
        self.data3 = Label(plotFrame, textvariable=self.data3Txt).grid(row=5, column=0, sticky=W)

    def saveBtn(self):
        self.saved.set("Saved")
        self.saveBtn.config(state='disabled')
        self.discardBtn.config(state='disabled')
        saveDataAsTxt(self.fileName, self.tA, self.valListA, self.valListB, self.valListC)

    def clearText(self, event):
        self.e1.delete(0, "end")
        return None

    def resetGraph(self):
        self.clearGraph()

    def clearGraph(self):
        self.startBtn.config(state='normal')
        self.resetBtn.config(state='disabled')
        self.saveBtn.config(state='disabled')
        self.discardBtn.config(state='disabled')
        self.data1Txt.set("")
        self.data2Txt.set("")
        self.data3Txt.set("")
        self.e2txt.set("")
        self.e3txt.set("")
        self.e4txt.set("")
        self.e5txt.set("")
        self.saved.set("")
        self.e5.delete(1.0, END)
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
        self.startBtn.config(state='disabled')
        self.resetBtn.config(state='normal')
        self.saveBtn.config(state='normal')
        self.discardBtn.config(state='normal')
        fileName = self.e1.get()
        clicks = self.e2.get()
        clicks2 = self.e3.get()
        temp = self.e4.get()
        if (len(clicks) > 0):
            self.data1Txt.set("Clicks(C): " + clicks)
        else:
            self.data1Txt.set("Clicks(C) not set")
        if (len(clicks2) > 0):
            self.data2Txt.set("Clicks(R): " + clicks2)
        else:
            self.data2Txt.set("Clicks(R) not set")
        if (len(temp) > 0):
            self.data3Txt.set("Temperature: " + temp)
        else:
            self.data3Txt.set("Temperature not set")

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


class ComparePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        #label.pack(pady=10,padx=10)
        # button1 = tk.Button(self, text="Back to Home",
        #                     command=lambda: controller.show_frame(StartPage))
        # button1.pack()
        topFrame = Frame(self)
        topFrame.pack(side="top", fill="both")
        # homeBtn = tk.Button(topFrame, text="HOME", padx=20, pady=10,
        #                      command=lambda: self.show_frame(StartPage))
        homeBtn = tk.Button(topFrame, text="HOME", padx=20, pady=10,
                             command=lambda: controller.show_frame(StartPage))
                             # frame.tkraise()
        compareBtn = tk.Button(topFrame, text="COMPARE", padx=20, pady=10,
                            command=lambda: controller.show_frame(ComparePage))
        compareBtn.config(relief=SUNKEN)
        dataBtn = tk.Button(topFrame, text="DATA", padx=20, pady=10)
        homeBtn.grid(row=0, column=1)
        compareBtn.grid(row=0, column=2)
        dataBtn.grid(row=0, column=3)
        self.initialize()

    def initialize(self):
        listFrame = Frame(self)
        listFrame.pack(side="left")

        plotFrame = Frame(self)
        plotFrame.pack(side="right", fill="both", expand = True)

        self.f = Figure(figsize=(6,4), dpi=100)
        a = self.f.add_subplot(111)

        x = []
        y = []

        self.line1, = a.plot(x,y,'r')
        self.line2, = a.plot(x,y,'g')
        self.line3, = a.plot(x,y,'b')
        self.line4, = a.plot(x,y,'y')

        self.canvas = FigureCanvasTkAgg(self.f, plotFrame)

        self.canvas.show()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.NONE, expand=False, anchor=W)
        self.update
        toolbar = NavigationToolbar2TkAgg(self.canvas, plotFrame).pack(side=tk.TOP)

        self.savedValues = os.listdir(appDataPath)
        for index, value in enumerate(self.savedValues):
            value = value.split('.')[0]
            self.savedValues[index] = IntVar()
            #checkVar = IntVar()
            self.savedValues[index].set(0)
            self.valueCheck = Checkbutton(listFrame, text=value, variable=self.savedValues[index])
            self.valueCheck.pack()

        self.compareBtn_text = tk.StringVar()
        compareBtn = tk.Button(listFrame,
                           textvariable=self.compareBtn_text,
                           command=self.compareGraphs)
        compareBtn.pack()
        self.compareBtn_text.set("Compare")

    def compareGraphs(self):

        graphNames = []
        self.savedVals2 = os.listdir(appDataPath)
        for index, value in enumerate(self.savedValues):
            if value.get() == 1:
                graphNames.append(self.savedVals2[index])

        """for index, graph in enumerate(graphNames):
            fullName = appDataPath + str(graph)
            f = open(fullName, 'r')
            lines = f.readlines()
            valListA = []
            #valListB = []
            valListC = []

            for i in range(len(lines)-1):
                valListA.append(float(lines[i].split(' ')[0]))
                #valListB.append(float(lines[i].split(' ')[1]))
                valListC.append(float(lines[i].split(' ')[2]))"""

        fullName1 = appDataPath + str(graphNames[0])
        print fullName1
        f1 = open(fullName1, 'r')
        lines1 = f1.readlines()
        valListA1 = []
        #valListB = []
        valListC1 = []

        for i in range(len(lines1)-1):
            valListA1.append(float(lines1[i].split(' ')[0]))
            #valListB.append(float(lines[i].split(' ')[1]))
            valListC1.append(float(lines1[i].split(' ')[2]))

        fullName2 = appDataPath + str(graphNames[1])
        print fullName2
        f2 = open(fullName2, 'r')
        lines2 = f2.readlines()
        valListA2 = []
        #valListB = []
        valListC2 = []

        for i in range(len(lines2)-1):
            valListA2.append(float(lines2[i].split(' ')[3]))
            #valListB.append(float(lines[i].split(' ')[1]))
            valListC2.append(float(lines2[i].split(' ')[1]))

        totalTime = 2
        incA = totalTime/float(len(valListA1))
        tA= np.arange(0.0, totalTime, incA)

        spacing = 0.1
        spacingy = 80
        minorLocator = MultipleLocator(spacing)
        minorLocatory = MultipleLocator(spacingy)

        minY = 0
        maxY = 1024

        self.line1.set_data(tA,valListA1)
        self.line2.set_data(tA,valListC1)
        self.line3.set_data(tA,valListA2)
        self.line4.set_data(tA,valListC2)
        ax = self.canvas.figure.axes[0]
        ax.yaxis.set_minor_locator(minorLocatory)
        ax.xaxis.set_minor_locator(minorLocator)
        # Set grid to use minor tick locations.
        ax.grid(True, which = 'minor')

        ax.set_ylim(minY, maxY)
        ax.set_xlim(min(tA), max(tA))
        self.canvas.draw()




app =  App_Window()
app.minsize(width=800, height=600)
app.resizable(width=False, height=False)
app.mainloop()

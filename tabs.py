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
import serial.tools.list_ports
import os
import time
from datetime import datetime

#Create path for saving files
appDataPath = os.getenv('LOCALAPPDATA') + '\\shockData\\'
configPath = os.getenv('LOCALAPPDATA') + '\\shockData\\config\\config.txt'
if not os.path.exists(appDataPath):
    os.makedirs(appDataPath)
if not os.path.exists(os.path.dirname(configPath)):
    os.makedirs(os.path.dirname(configPath))
    configFile = open(configPath, "w")
    configFile.close()

#Get initial port list that can be refreshed later
portList = list(serial.tools.list_ports.comports())
#Slice the portlist to make it more readable
slicedPortList = []
for port in portList:
    slicedPortList.append(str(port).split(' ')[0])



# with open(configPath, "w") as f:
#     f.write("FOOBAR")

#Give option for test data or real data
#testFlag = raw_input("Test? 1 for yes, 0 for no. ")
testFlag = '0'
min_val = 0
max_val = 1024

#Set the port number. Ultimately this will be a UI option
#port = 'com6'

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
def saveDataAsTxt(fileName, valListA, valListB, valListC, tA, extraVals):
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
    F.write("DETAILS \n")
    F.write("CLICKSC \n")
    if (len(extraVals[0]) > 0):
        F.write(extraVals[0])
    else:
        F.write('NA')
    F.write('\n')
    F.write("CLICKSR \n")
    if (len(extraVals[1]) > 0):
        F.write(extraVals[1])
    else:
        F.write('NA')
    F.write('\n')
    F.write("TEMP \n")
    if (len(extraVals[2]) > 0):
        F.write(extraVals[2])
    else:
        F.write('NA')
    F.write('\n')
    F.write("NOTES \n")
    if (len(extraVals[3].strip()) > 0):
        F.write(extraVals[3])
    else:
        F.write('NA')
    F.write('\n')
    F.write('PtT \n')
    if (len(extraVals[4].strip()) > 0):
        F.write(extraVals[4])
    else:
        F.write('NA')
    F.write('\n')
    F.write('TtP \n')
    if (len(extraVals[5].strip()) > 0):
        F.write(extraVals[5])
    else:
        F.write('NA')
    F.write('\n')
    F.write('END')

#Get data from serial port
def runLoop(fileName, testFlag, port):
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

        for F in (StartPage, ComparePage, DataPage):

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
        dataBtn = tk.Button(topFrame, text="DATA", padx=20, pady=10,
                            command=lambda: controller.show_frame(DataPage))
        homeBtn.grid(row=0, column=1)
        compareBtn.grid(row=0, column=2)
        dataBtn.grid(row=0, column=3)

        self.initialize()


    def initialize(self):
        #Testflag and port number intiialise
        self.testFlag = '0'
        self.portNumber = ''

        #Line to cut off menu
        menuSeparator = Frame(self, height=1, bg="grey").pack(side="top", fill="both")

        #Top row for configuration
        configRow = Frame(self)
        configRow.pack(side="top", fill="both")

        #Allow user to tick box to indicate a real test or not
        self.testTF = IntVar()
        checkBtnTxt = Label(configRow, text="Record? Check box for true").grid(row=0,column=0,padx=(10,0), sticky=W)
        checkBtn = Checkbutton(configRow, text="", variable=self.testTF, justify=LEFT)
        self.testTF.trace("w", self.testTF_callback)
        checkBtn.grid(row=0, column=1)

        #Create dropdown for port selection
        portNumText = Label(configRow, text="Select port number").grid(row=0, column=2)
        self.portNum = tk.StringVar()
        #Check if portNum is set in the config file, if so and if it's available, default it to that
        configFile = open(configPath, "r")
        lastPort = configFile.read()
        #If there is an entry in the config file, check it's listed in the current ports
        #If so, default it to this
        portExists = False
        if len(lastPort) > 0:
            for port in slicedPortList:
                if port == lastPort:
                    portExists = True
                    break
        if portExists == True:
            self.portNum.set(lastPort)

        self.portNumber = self.portNum.get()

        #Detect changes in dropdown
        self.portNum.trace("w", self.portNum_callback)

        #Because option menu needs some options, set this to blank if it's empty
        if len(slicedPortList) > 0:
            self.portNums = slicedPortList
        else:
            self.portNums = [' ']

        self.portNumPopup = OptionMenu(configRow, self.portNum, *self.portNums)
        if self.portNums == [' ']:
            self.portNumPopup.configure(state="disabled")

        self.portNumPopup.grid(row=0, column=3)
        self.portRefreshBtn = tk.Button(configRow,
                           text='Refresh Port List',command=self.refreshPorts)
        self.portRefreshBtn.grid(row=0, column=4)

        configSeparator = Frame(self, height=1, bg="grey").pack(side="top", fill="both")

        frame = Frame(self)
        frame.pack(side="left", fill="both", padx=10, pady=10)

        #Left-hand-side
        self.l1 = Label(frame, text="INPUT FIELDS").grid(row=1, sticky=W, columnspan=3)

        self.l2 = Label(frame, text="Name *").grid(row=2, sticky=W, columnspan=3)
        self.l3 = Label(frame, text="Clicks (C)").grid(row=4, sticky=W, columnspan=3)
        self.l4 = Label(frame, text="Clicks (R)").grid(row=6, sticky=W, columnspan=3)
        self.l5 = Label(frame, text="Temp").grid(row=8, sticky=W, columnspan=3)
        self.l6 = Label(frame, text="Notes").grid(row=10, sticky=W, columnspan=3)
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

        self.e1.grid(row=3, column=0,sticky=W, columnspan=3)
        self.e2.grid(row=5, column=0,sticky=W, columnspan=3)
        self.e3.grid(row=7, column=0,sticky=W, columnspan=3)
        self.e4.grid(row=9, column=0,sticky=W, columnspan=3)
        self.e5.grid(row=11, column=0,sticky=W, columnspan=3)

        self.btn_text = tk.StringVar()
        self.saveTxt = tk.StringVar()
        self.discardTxt = tk.StringVar()

        self.startBtn = tk.Button(frame,
                           textvariable=self.btn_text,command=self.OnButtonClick, padx=15, pady=8)
        self.btn_text.set("START")

        # if self.portNum.get() == '':
        #     print "PORT SET IS "
        #     print self.portNum.get()
        #     self.startBtn.configure(state='disabled')
        self.startBtn.grid(row=12, column=0)

        self.btn_text2 = tk.StringVar()
        self.resetBtn = tk.Button(frame,
                           textvariable=self.btn_text2,
                           command=self.resetGraph, state=DISABLED, padx=15, pady=8)
        self.btn_text2.set("RESET")
        self.resetBtn.grid(row=12, column=1)
        frame.grid_rowconfigure(12, minsize=50)

        #Error message for invalid port number
        self.errorMsgTxt = StringVar()
        self.errorMsg = Label(frame, textvariable=self.errorMsgTxt).grid(row=13, columnspan=3)


        plotFrame = Frame(self)
        plotFrame.pack(side="right", fill="both", expand = True, padx=40, pady=10)
        self.saveBtn = tk.Button(plotFrame,
                           textvariable=self.saveTxt,
                           command=self.saveBtn, state=DISABLED, padx=20, pady=8)
        self.saveTxt.set("SAVE")
        self.saveBtn.grid(row=3, column=4, sticky=E)

        self.discardBtn = tk.Button(plotFrame,
                           textvariable=self.discardTxt,
                           command=self.resetGraph, state=DISABLED, padx=15, pady=8)
        self.discardTxt.set("DISCARD")
        self.discardBtn.grid(row=3, column=5)

        Label(plotFrame, text="GRAPH").grid(row=1, column=0, sticky=W)

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

        self.canvas._tkcanvas.grid(row=2, column=0, columnspan=6, pady=8)
        self.update
        self.data1Txt = tk.StringVar()
        self.data2Txt = tk.StringVar()
        self.data3Txt = tk.StringVar()
        self.saved = tk.StringVar()
        self.savedTxt = Label(plotFrame, textvariable=self.saved).grid(row=3, column=0, sticky=W)
        # toolbar = NavigationToolbar2TkAgg(self.canvas, plotFrame).grid(row=2, column=0, columnspan=6, sticky=W)
        self.data1 = Label(plotFrame, textvariable=self.data1Txt).grid(row=4, column=0, sticky=W)
        self.data2 = Label(plotFrame, textvariable=self.data2Txt).grid(row=5, column=0, sticky=W)
        self.data3 = Label(plotFrame, textvariable=self.data3Txt).grid(row=6, column=0, sticky=W)

        #Display peaks and troughs info
        self.peakToTroughTxt = tk.StringVar()
        self.troughToPeakTxt = tk.StringVar()

        self.data4 = Label(plotFrame, textvariable=self.peakToTroughTxt).grid(row=4, column=1, sticky=W)
        self.data5 = Label(plotFrame, textvariable=self.troughToPeakTxt).grid(row=5, column=1, sticky=W)

    def refreshPorts(self):
        #Don't set a val, so user is forced to
        self.portNum.set('')
        portListNew = list(serial.tools.list_ports.comports())
        #Slice the portlist to make it more readable
        slicedPortListNew = []
        for port in portListNew:
            slicedPortListNew.append(str(port).split(' ')[0])

        if len(slicedPortListNew) > 0:
            self.portNumPopup.configure(state="active")
        else:
            self.startBtn.configure(state='disabled')
            self.portNumPopup.configure(state="disabled")
            slicedPortListNew = [' ']

        # Delete all old options
        self.portNumPopup.children['menu'].delete(0, 'end')

        # Insert list of new options (tk._setit hooks them up to val)
        for val in slicedPortListNew:
            self.portNumPopup.children['menu'].add_command(label=val, command=tk._setit(self.portNum, val))


    def testTF_callback(self, *args):
        if self.testTF.get() == 1:
            self.testFlag = '1'
            if self.portNum.get() == '':
                self.startBtn.configure(state='disabled')
        else:
            self.testFlag = '0'
            self.startBtn.configure(state='active')

    def portNum_callback(self, *args):
        if self.portNum.get() != '':
            self.startBtn.configure(state='active')
        self.portNumber = self.portNum.get()
        configFile = open(configPath, "w")
        configFile.write(self.portNumber)

    def saveBtn(self):
        self.saved.set("Saved")
        self.saveBtn.config(state='disabled')
        self.discardBtn.config(state='disabled')
        gete2 = self.e2txt.get()
        gete3 = self.e3txt.get()
        gete4 = self.e4txt.get()
        gete5 = self.e5.get("1.0",END)
        getTimeA = self.peakToTroughTxt.get()
        getTimeB = self.troughToPeakTxt.get()
        extraVals = [gete2, gete3, gete4, gete5, getTimeA, getTimeB]
        saveDataAsTxt(self.fileName, self.tA, self.valListA, self.valListB, self.valListC, extraVals)

    def clearText(self, event):
        self.e1.delete(0, "end")
        return None

    def resetGraph(self):
        self.clearGraph()

    def clearGraph(self):
        self.errorMsgTxt.set("")
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

        try:
            peakToTrough = indexTtPPeak - indexPtTPeak
            self.peakToTroughTxt.set("Time peak to trough: " + str(peakToTrough) + "s")
        except:
            self.peakToTroughTxt.set("Time peak to trough: INVALID")

        try:
            troughToPeak = indexPtTTrough - indexTtPTrough
            self.troughToPeakTxt.set("Time trough to peak: " + str(troughToPeak) + "s")
        except:
            self.troughToPeakTxt.set("Time trough to peak: INVALID")


        ax.yaxis.set_minor_locator(minorLocatory)
        ax.xaxis.set_minor_locator(minorLocator)
        # Set grid to use minor tick locations.
        ax.grid(True, which = 'minor')

        ax.set_ylim(minY, maxY)
        ax.set_xlim(min(xA), max(xA))
        self.canvas.draw()

    def OnButtonClick(self):
        self.errorMsgTxt.set("")
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

        #Wrap this in a try-except to catch port exceptions
        errorCode = 0
        try:
        	values = runLoop(fileName, self.testFlag, self.portNumber)
        except:
            print "ERROR"
            errorCode = 1
            self.errorMsgTxt.set("ERROR, CHECK YOUR PORTS.")
        #Only run these if there was no error
        if errorCode == 0:
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
        dataBtn = tk.Button(topFrame, text="DATA", padx=20, pady=10,
                            command=lambda: controller.show_frame(DataPage))
        homeBtn.grid(row=0, column=1)
        compareBtn.grid(row=0, column=2)
        dataBtn.grid(row=0, column=3)
        self.initialize()

    def initialize(self):
        #Grey line that separates menu
        menuSeparator = Frame(self, height=1, bg="grey", pady=20).pack(side="top", fill="both")

        #Left frame that holds comparison list
        listFrame = Frame(self)
        listFrame.pack(side="left", fill="both", padx=10, pady=10)

        #Right frame that holds plot
        plotFrame = Frame(self)
        plotFrame.pack(side="right", fill="both", expand = True, padx=40, pady=10)
        Label(plotFrame, text="COMPARE RESULTS").grid(row=0, column=0, sticky=W)
        self.f = Figure(figsize=(6,4), dpi=100)
        a = self.f.add_subplot(111)

        #Initialise x and y axes to 0
        x = []
        y = []

        #Draw null lines that can be changed later. Colours must be set here.
        self.line1, = a.plot(x,y,'r')
        self.line2, = a.plot(x,y,'g')
        self.line3, = a.plot(x,y,'b')
        self.line4, = a.plot(x,y,'y')
        self.canvas = FigureCanvasTkAgg(self.f, plotFrame)
        self.canvas.show()
        self.canvas._tkcanvas.grid(row=1, column=0, columnspan=6, pady=8)
        self.update

        #Create blank fields for data to sit in and variables to be reset
        self.g1heading = tk.StringVar()
        self.g1clicksc = tk.StringVar()
        self.g1clicksr = tk.StringVar()
        self.g1temp = tk.StringVar()
        self.g1notes = tk.StringVar()
        self.pTT1Txt = tk.StringVar()
        self.tTP1Txt = tk.StringVar()
        self.graph1Heading = Label(plotFrame, textvariable=self.g1heading).grid(row=2, column=0,sticky=W)
        self.graph1clicksC = Label(plotFrame, textvariable=self.g1clicksc).grid(row=3, column=0, sticky=W)
        self.graph1clicks4 = Label(plotFrame, textvariable=self.g1clicksr).grid(row=4, column=0, sticky=W)
        self.graph1Temp = Label(plotFrame, textvariable=self.g1temp).grid(row=5, column=0, sticky=W)
        self.graph1Notes = Label(plotFrame, textvariable=self.g1notes).grid(row=2, column=1, columnspan=2, sticky=W)
        self.pTT1 = Label(plotFrame, textvariable=self.pTT1Txt).grid(row=6, column=0, sticky=W)
        self.tTP1 = Label(plotFrame, textvariable=self.tTP1Txt).grid(row=7, column=0, sticky=W)

        self.g2heading = tk.StringVar()
        self.g2clicksc = tk.StringVar()
        self.g2clicksr = tk.StringVar()
        self.g2temp = tk.StringVar()
        self.g2notes = tk.StringVar()
        self.pTT2Txt = tk.StringVar()
        self.tTP2Txt = tk.StringVar()
        self.graph2Heading = Label(plotFrame, textvariable=self.g2heading).grid(row=2, column=3, sticky=W)
        self.graph2clicksC = Label(plotFrame, textvariable=self.g2clicksc).grid(row=3, column=3, sticky=W)
        self.graph2clicks4 = Label(plotFrame, textvariable=self.g2clicksr).grid(row=4, column=3, sticky=W)
        self.graph2Temp = Label(plotFrame, textvariable=self.g2temp).grid(row=5, column=3, sticky=W)
        self.graph2Notes = Label(plotFrame, textvariable=self.g2notes).grid(row=2, column=4, columnspan=2, sticky=W)
        self.pTT2 = Label(plotFrame, textvariable=self.pTT2Txt).grid(row=6, column=3, sticky=W)
        self.tTP2 = Label(plotFrame, textvariable=self.tTP2Txt).grid(row=7, column=3, sticky=W)

        #Get list of filenames from appdata folder
        self.savedValues = os.listdir(appDataPath)

        #New array to hold easier to read list (cut off extension)
        self.newVals = []
        for index, value in enumerate(self.savedValues):
            value = value.split('.')[0]
            self.newVals.append(value)

        #Create dynamic option variables for dropdown and monitor when they are changed
        self.option1Var = tk.StringVar()
        self.option1Var.trace("w", self.optionMenu_callback)
        self.option2Var = tk.StringVar()
        self.option2Var.trace("w", self.optionMenu_callback)

        #Create popup menus
        self.popupMenu = OptionMenu(listFrame, self.option1Var, *self.newVals)
        self.popupMenu2 = OptionMenu(listFrame, self.option2Var, *self.newVals)
        self.popupMenu.configure(width=20)
        self.popupMenu2.configure(width=20)

        #If there are more than 2 values, you can compare them, so set these to the first 2
        #If not, set them to 'NA' and disable them
        if len(self.newVals) > 2:
            self.option1Var.set(self.newVals[0])
            self.option2Var.set(self.newVals[1])
        else:
            self.popupMenu.configure(state="disabled")
            self.popupMenu2.configure(state="disabled")
            self.option1Var.set('NA')
            self.option2Var.set('NA')

        #Refresh button to check for new recordings
        self.refreshBtn = tk.Button(listFrame, text="Refresh List",
                           command=self.updateVals).grid(row=0, column=0, sticky=W)

        #Grid headings and popup menus
        Label(listFrame, text="Select first recording").grid(row=1, column=0, sticky=W, pady=10, columnspan=3)
        self.popupMenu.grid(row=2, column=0, columnspan=3)
        Label(listFrame, text="Select second recording").grid(row=3, column=0, sticky=W, pady=10, columnspan=3)
        self.popupMenu2.grid(row=4, column=0, columnspan=3)

        #Only activate compare button if there are at least 2 items to compare
        # if len(self.newVals) > 2:
        if len(self.newVals) > 2:
            self.compareBtn = tk.Button(listFrame, text="COMPARE",
                               command=self.compareGraphs, padx=15, pady=8)
        else:
            self.compareBtn = tk.Button(listFrame,
                               text="COMPARE",
                               command=self.compareGraphs, state=DISABLED, padx=15, pady=8)
            #Show message saying there are no recordings
            Label(listFrame, text="You have no saved recordings yet :-(").grid(row=6, column=0, sticky=W, pady=10, columnspan=3)

        #Reset button starts inactive and only becomes active after a comparison
        self.resetBtn = tk.Button(listFrame,
                           text="RESET",
                           command=self.resetGraphs, state=DISABLED, padx=15, pady=8)

        self.compareBtn.grid(row=5, column=0)
        self.resetBtn.grid(row=5, column=1)
        listFrame.grid_rowconfigure(5, minsize=100)

    def updateVals(self):
        oldVals = self.newVals
        newList = os.listdir(appDataPath)
        if len(self.savedValues) > 2:
            self.option1Var.set(self.newVals[0])
            self.option2Var.set(self.newVals[1])
        else:
            self.popupMenu.configure(state="disabled")
            self.popupMenu2.configure(state="disabled")
            self.option1Var.set('NA')
            self.option2Var.set('NA')

        #Work out new vals
        newVals = []
        for index, value in enumerate(newList):
            value = value.split('.')[0]
            newVals.append(value)

        # Delete all old options
        self.popupMenu.children['menu'].delete(0, 'end')
        self.popupMenu2.children['menu'].delete(0, 'end')

        # Insert list of new options (tk._setit hooks them up to val)
        for val in newVals:
            self.popupMenu.children['menu'].add_command(label=val, command=tk._setit(self.option1Var, val))
            self.popupMenu2.children['menu'].add_command(label=val, command=tk._setit(self.option2Var, val))


    def optionMenu_callback(self, *args):
        # self.savedValues = os.listdir(appDataPath)
        print "CHANGES"

    def compareGraphs(self):
        #This function extracts the data from the 2 files and displays both on the graph
        #It also deactivates the compare button and actives the reset button

        #Disable compare button and dropdowns
        self.compareBtn.configure(state="disabled")
        self.resetBtn.configure(state="active")
        self.popupMenu.configure(state="disabled")
        self.popupMenu2.configure(state="disabled")

        #Print headings
        self.g1heading.set('FIRST RECORDING')
        self.g2heading.set('SECOND RECORDING')

        #Get values from dropdown menu
        compareOne = self.option1Var.get()
        compareTwo = self.option2Var.get()

        #Assemble full names of file path and read data
        fullName1 = appDataPath + compareOne + '.txt'
        f1 = open(fullName1, 'r')
        lines1 = f1.readlines()

        fullName2 = appDataPath + compareTwo + '.txt'
        print fullName2
        f2 = open(fullName2, 'r')
        lines2 = f2.readlines()

        valListA2 = []
        #valListB = []
        valListC2 = []

        #Create empty arrays to store data
        valListA1 = []
        #valListB = []
        valListC1 = []

        #Find amount of lines before 'DETAILS' word. Note comparison graphs have to be
        #the same length. Need two counts in case they are slightly different so we can
        #use the shorter one for both, but use independent ones for details
        count1 = 0
        count2 = 0

        for i in range(len(lines1)):
            leftCol = lines1[i].split(' ')[0]
            if leftCol == 'DETAILS':
                count1 = i
                break

        for j in range(len(lines2)):
            leftCol = lines2[j].split(' ')[0]
            if leftCol == 'DETAILS':
                count2 = j
                break

        if count1 > count2:
            countToUse = count2
        else:
            countToUse = count1

        #Split up data based on column
        for i in range(countToUse):
            valListA1.append(float(lines1[i].split(' ')[1]))
            #valListB.append(float(lines[i].split(' ')[1]))
            valListC1.append(float(lines1[i].split(' ')[2]))

        for i in range(countToUse):
            valListA2.append(float(lines2[i].split(' ')[1]))
            #valListB.append(float(lines[i].split(' ')[1]))
            valListC2.append(float(lines2[i].split(' ')[2]))
            #Total time is the last value on the 4th column
            totalTime = float(lines2[i].split(' ')[0])

        #Retrieve details but if they are blank write Not Set
        clicksC1 = lines1[count1+2].strip()
        if clicksC1 == 'NA':
            clicksC1 = 'Not Set'
        self.g1clicksc.set("Clicks(C): " + clicksC1)
        clicksR1 = lines1[count1+4].strip()
        if clicksR1 == 'NA':
            clicksR1 = 'Not Set'
        self.g1clicksr.set("Clicks(R): " + clicksR1)
        temp1 = lines1[count1+6].strip()
        if temp1 == 'NA':
            temp1 = 'Not Set'
        self.g1temp.set("Temp: " + temp1)
        notes1 = lines1[count1+8].lstrip().rstrip()
        if notes1 == 'NA':
            notes1 = 'Not Set'
        self.g1notes.set("Notes: " + notes1)
        clicksC2 = lines2[count2+2].strip()
        if clicksC2 == 'NA':
            clicksC2 = 'Not Set'
        self.g2clicksc.set("Clicks(C): " + clicksC2)
        clicksR2 = lines2[count2+4].strip()
        if clicksR2 == 'NA':
            clicksR2 = 'Not Set'
        self.g2clicksr.set("Clicks(R): "+ clicksR2)
        temp2 = lines2[count2+6].strip()
        if temp2 == 'NA':
            temp2 = 'Not Set'
        self.g2temp.set("Temp: " + temp2)
        notes2 = lines2[count2+8].lstrip().rstrip()
        if notes2 == 'NA':
            notes2 = 'Not Set'
        self.g2notes.set("Notes: " + notes2)

        pTT1 = lines1[count1+10].lstrip().rstrip()
        pTT2 = lines2[count2+10].lstrip().rstrip()
        tTP1 = lines1[count1+12].lstrip().rstrip()
        tTP2 = lines2[count2+12].lstrip().rstrip()

        self.pTT1Txt.set(pTT1)
        self.pTT2Txt.set(pTT2)
        self.tTP1Txt.set(tTP1)
        self.tTP2Txt.set(tTP2)

        #Set up graph
        incA = totalTime/float(len(valListA1))
        tA= np.arange(0.0, totalTime, incA)

        spacing = 0.1
        spacingy = 80
        minorLocator = MultipleLocator(spacing)
        minorLocatory = MultipleLocator(spacingy)

        minY = 0
        maxY = 1024

        #Set values
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

    def resetGraphs(self):
        #Re-enable buttons
        self.compareBtn.configure(state="active")
        self.resetBtn.configure(state="disabled")
        self.popupMenu.configure(state="active")
        self.popupMenu2.configure(state="active")

        #Reset text fields
        self.g1heading.set("")
        self.g1clicksc.set("")
        self.g1clicksr.set("")
        self.g1temp.set("")
        self.g1notes.set("")
        self.g2heading.set("")
        self.g2clicksc.set("")
        self.g2clicksr.set("")
        self.g2temp.set("")
        self.g2notes.set("")

        #Clear graph
        self.line1.set_data([],[])
        self.line2.set_data([],[])
        self.line3.set_data([],[])
        self.line4.set_data([],[])
        ax = self.canvas.figure.axes[0]
        self.canvas.draw()

class DataPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        topFrame = Frame(self)
        topFrame.pack(side="top", fill="both")
        # homeBtn = tk.Button(topFrame, text="HOME", padx=20, pady=10,
        #                      command=lambda: self.show_frame(StartPage))
        homeBtn = tk.Button(topFrame, text="HOME", padx=20, pady=10, state=ACTIVE,
                             command=lambda: controller.show_frame(StartPage))
                             # frame.tkraise()
        compareBtn = tk.Button(topFrame, text="COMPARE", padx=20, pady=10,
                            command=lambda: controller.show_frame(ComparePage))
        dataBtn = tk.Button(topFrame, text="DATA", padx=20, pady=10)
        dataBtn.config(relief=SUNKEN)
        homeBtn.grid(row=0, column=1)
        compareBtn.grid(row=0, column=2)
        dataBtn.grid(row=0, column=3)

        self.initialize()


    def initialize(self):
        #Grey line that separates menu
        menuSeparator = Frame(self, height=1, bg="grey", pady=20).pack(side="top", fill="both")

        #Left frame that holds comparison list
        listFrame = Frame(self)
        listFrame.pack(side="left", fill="both", padx=10, pady=10)

        #Right frame that holds plot
        plotFrame = Frame(self)
        plotFrame.pack(side="right", fill="both", expand = True, padx=40, pady=10)
        Label(plotFrame, text="VIEW RESULT").grid(row=0, column=0, sticky=W)
        self.f = Figure(figsize=(6,4), dpi=100)
        a = self.f.add_subplot(111)

        #Initialise x and y axes to 0
        x = []
        y = []

        #Draw null lines that can be changed later. Colours must be set here.
        self.line1, = a.plot(x,y,'r')
        self.line2, = a.plot(x,y,'g')
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

        #Create blank fields for data to sit in and variables to be reset
        self.g1heading = tk.StringVar()
        self.g1clicksc = tk.StringVar()
        self.g1clicksr = tk.StringVar()
        self.g1temp = tk.StringVar()
        self.g1notes = tk.StringVar()
        self.graph1Heading = Label(plotFrame, textvariable=self.g1heading).grid(row=2, column=0,sticky=W)
        self.graph1clicksC = Label(plotFrame, textvariable=self.g1clicksc).grid(row=3, column=0, sticky=W)
        self.graph1clicks4 = Label(plotFrame, textvariable=self.g1clicksr).grid(row=4, column=0, sticky=W)
        self.graph1Temp = Label(plotFrame, textvariable=self.g1temp).grid(row=5, column=0, sticky=W)
        self.graph1Notes = Label(plotFrame, textvariable=self.g1notes).grid(row=2, column=1, columnspan=2, sticky=W)

        #Get list of filenames from appdata folder
        self.savedValues = os.listdir(appDataPath)

        #New array to hold easier to read list (cut off extension)
        self.newVals = []
        for index, value in enumerate(self.savedValues):
            value = value.split('.')[0]
            self.newVals.append(value)

        #Create dynamic option variables for dropdown and monitor when they are changed
        self.option1Var = tk.StringVar()
        self.option1Var.trace("w", self.optionMenu_callback)

        #Create popup menus
        self.popupMenu = OptionMenu(listFrame, self.option1Var, *self.newVals)
        self.popupMenu.configure(width=20)

        #If there are more than 2 values, you can compare them, so set these to the first 2
        #If not, set them to 'NA' and disable them
        if len(self.newVals) > 2:
            self.option1Var.set(self.newVals[0])
        else:
            self.popupMenu.configure(state="disabled")
            self.option1Var.set('NA')
        #Refresh button to check for new recordings
        self.refreshBtn = tk.Button(listFrame, text="Refresh List",
                           command=self.updateVals).grid(row=0, column=0, sticky=W)

        #Grid headings and popup menus
        Label(listFrame, text="Select recording to view").grid(row=1, column=0, sticky=W, pady=10, columnspan=3)
        self.popupMenu.grid(row=2, column=0, columnspan=3)
        #Only activate compare button if there are at least 2 items to compare
        # if len(self.newVals) > 2:
        if len(self.newVals) > 0:
            self.viewBtn = tk.Button(listFrame, text="VIEW",
                               command=self.viewGraph, padx=15, pady=8)
        else:
            self.viewBtn = tk.Button(listFrame,
                               text="VIEW",
                               command=self.self.viewGraph, state=DISABLED, padx=15, pady=8)
            #Show message saying there are no recordings
            Label(listFrame, text="You have no saved recordings yet :-(").grid(row=4, column=0, sticky=W, pady=10, columnspan=3)

        #Reset button starts inactive and only becomes active after a comparison
        self.deleteBtn = tk.Button(listFrame,
                           text="DELETE",
                           command=self.deleteGraph, state=DISABLED, padx=15, pady=8)

        self.viewBtn.grid(row=3, column=0)
        self.deleteBtn.grid(row=3, column=1)

    def optionMenu_callback(self, *args):
        pass

    def updateVals(self):
        oldVals = self.newVals
        newList = os.listdir(appDataPath)
        if len(self.savedValues) > 0:
            self.option1Var.set(self.newVals[0])
        else:
            self.popupMenu.configure(state="disabled")
            self.option1Var.set('NA')

        #Work out new vals
        newVals = []
        for index, value in enumerate(newList):
            value = value.split('.')[0]
            newVals.append(value)

        # Delete all old options
        self.popupMenu.children['menu'].delete(0, 'end')

        # Insert list of new options (tk._setit hooks them up to val)
        for val in newVals:
            self.popupMenu.children['menu'].add_command(label=val, command=tk._setit(self.option1Var, val))

    def viewGraph(self):
        #This function extracts the data from the 2 files and displays both on the graph
        #It also deactivates the compare button and actives the reset button

        #Disable compare button and dropdowns
        # self.compareBtn.configure(state="disabled")
        self.deleteBtn.configure(state="active")
        # self.popupMenu.configure(state="disabled")
        # self.popupMenu2.configure(state="disabled")

        #Print headings
        self.g1heading.set('RECORDING INFO')

        #Get values from dropdown menu
        compareOne = self.option1Var.get()

        #Assemble full names of file path and read data
        fullName1 = appDataPath + compareOne + '.txt'
        f1 = open(fullName1, 'r')
        lines1 = f1.readlines()

        valListA = []
        valListB = []
        valListC = []


        #Find amount of lines before 'DETAILS' word. Note comparison graphs have to be
        #the same length. Need two counts in case they are slightly different so we can
        #use the shorter one for both, but use independent ones for details
        count = 0

        for i in range(len(lines1)):
            leftCol = lines1[i].split(' ')[0]
            if leftCol == 'DETAILS':
                count = i
                break

        #Split up data based on column
        for i in range(count):
            valListA.append(float(lines1[i].split(' ')[1]))
            valListB.append(float(lines1[i].split(' ')[1]))
            valListC.append(float(lines1[i].split(' ')[2]))
            totalTime = float(lines1[i].split(' ')[0])

        #Get peak to trough vals
        PTs = peaksTroughs(valListA, totalTime)
        indexPtTPeak = PTs[0][0]
        valPtTPeak = PTs[0][1]
        indexPtTTrough = PTs[1][0]
        valPtTTrough = PTs[1][1]
        indexTtPPeak = PTs[2][0]
        valTtPPeak = PTs[2][1]
        indexTtPTrough = PTs[3][0]
        valTtPTrough = PTs[3][1]

        if (indexPtTPeak != None or valPtTPeak != None):
            self.PtTPeak.set_data(indexPtTPeak,valPtTPeak)
        if (indexPtTTrough != None or valPtTTrough != None):
            self.PtTTrough.set_data(indexPtTTrough,valPtTTrough)
        if (indexTtPPeak != None or valTtPPeak != None):
            self.TtPPeak.set_data(indexTtPPeak,valTtPPeak)
        if (indexTtPTrough != None or valTtPTrough != None):
            self.TtPTrough.set_data(indexTtPTrough,valTtPTrough)

        #Retrieve details but if they are blank write Not Set
        clicksC1 = lines1[count+2].strip()
        if clicksC1 == 'NA':
            clicksC1 = 'Not Set'
        self.g1clicksc.set("Clicks(C): " + clicksC1)
        clicksR1 = lines1[count+4].strip()
        if clicksR1 == 'NA':
            clicksR1 = 'Not Set'
        self.g1clicksr.set("Clicks(R): " + clicksR1)
        temp1 = lines1[count+6].strip()
        if temp1 == 'NA':
            temp1 = 'Not Set'
        self.g1temp.set("Temp: " + temp1)
        notes1 = lines1[count+8].lstrip().rstrip()
        if notes1 == 'NA':
            notes1 = 'Not Set'
        self.g1notes.set("Notes: " + notes1)

        #Set up graph
        incA = totalTime/float(len(valListA))
        tA= np.arange(0.0, totalTime, incA)

        spacing = 0.1
        spacingy = 80
        minorLocator = MultipleLocator(spacing)
        minorLocatory = MultipleLocator(spacingy)

        minY = 0
        maxY = 1024

        #Set values
        self.line1.set_data(tA,valListA)
        self.line2.set_data(tA,valListB)
        self.line3.set_data(tA,valListC)
        ax = self.canvas.figure.axes[0]
        ax.yaxis.set_minor_locator(minorLocatory)
        ax.xaxis.set_minor_locator(minorLocator)

        # Set grid to use minor tick locations.
        ax.grid(True, which = 'minor')

        ax.set_ylim(minY, maxY)
        ax.set_xlim(min(tA), max(tA))
        self.canvas.draw()

    def deleteGraph(self):
        pass




app =  App_Window()
app.minsize(width=800, height=600)
app.resizable(width=False, height=False)
app.mainloop()

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


#These variables are set at the start to be used later on in the plotting. As long as they are 'in scope' and are set before you try to use them, it doesn't matter where you set them. Being in scope means being declared where you are using them. An example of being out of scope would be if you had a "main" function, and a separate "graph" function that is called inside main. If you declare a variable min_val inside the graph function, and try to use it in the main, it won't work because main can't see it.
min_val = 0
max_val = 1024

#Prints a line to the terminal asking user to input the port number as 'COMx'. You can check the port number in device manager when the Arduino is plugged in
#port = raw_input("Enter the port number (e.g. 'COM4'): \n")
port = 'com6'

#Creates a variable called 'ser' that we will use to communicate with the serial port. Gives it the port number, the baud rate and timeout (not sure what timeout does but it fixed that 0000s problem)
ser = serial.Serial(port, 230400, timeout=1)

#Some commented out stuff experimenting with weird data
#ser = serial.Serial('COM4', 9600, timeout=1)
ser.flush()

#Sleep tells the programme to wait for x seconds. Useful in serial comms when you want to be sure something has happened
time.sleep(3)
#This is an empty array of data that will be populated later with the values from the serial port
valList = []

def runLoop(fileName):


    #TEMPORARY - Use to test data
    startTime = time.time()
    startCommand = 'START$'
    #sendStart = bytes(startCommand.encode('utf-8'))
    stopCommand = 'STOP$'
    #sendStop = bytes(stopCommand.encode('utf-8'))
    ser.write(startCommand)
    print("START RECORDING")
    for i in range(3000):
        valList.append(ser.readline())
    ser.write(stopCommand)

    endTime = time.time()
    totalTime = endTime - startTime
    #Split valList into 3 lists
    valListA = []
    valListB = []
    valListC = []

    for val in valList:
        #print(val)
        if val[0] == 'a':
            modVal = val[1:]
            try:
                float(modVal)
                #countA += 1
                valListA.append(int(modVal.rstrip()))
            except ValueError:
                pass
                #break
        elif val[0] == 'b':
            modVal = val[1:]
            try:
                float(modVal)
                #countB += 1
                valListB.append(int(modVal.rstrip()))
            except ValueError:
                pass
        else:
            try:
                float(val)
                #countC += 1
                valListC.append(int(val.rstrip()))
            except ValueError:
                pass

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

    print ("Length of Val List A is " + str(len(valListA)))
    #Open a text file that is writable
    fileA = open("testfileA.txt","w")
    for val in valListA:
    	#If number is invalid, write a 0
    	if not val:
    		fileA.write('0 \n')
    	#else write a string representation of the number to the file
    	else:
    		fileA.write(str(val))
    		#\n means the end of the line. .txt files interpret this
    		fileA.write('\n')

    #Open a text file that is writable
    fileB = open("testfileB.txt","w")
    for val in valListB:
    	#If number is invalid, write a 0
    	if not val:
    		fileB.write('0')
    	#else write a string representation of the number to the file
    	else:
    		fileB.write(str(val))
    		#\n means the end of the line. .txt files interpret this
    		fileB.write('\n')

    #Open a text file that is writable
    fileC = open("testfileC.txt","w")
    for val in valListC:
    	#If number is invalid, write a 0
    	if not val:
    		fileC.write('0')
    	#else write a string representation of the number to the file
    	else:
    		fileC.write(str(val))
    		#\n means the end of the line. .txt files interpret this
    		fileC.write('\n')


    #Calculate the time difference between peak and trough in A
    #First peak
    countStartPtT = 0
    for i in range(len(valListA) - 1):
        if countStartPtT > 20:
            firstIndexPtT = i - 20
            firstValPtT = valListA[i-20]
            break
        else:
            firstIndexPtT = None
            firstValPtT = None
        if (valListA[i+1] < valListA[i]):
            countStartPtT = countStartPtT+1
        else:
            countStartPtT = 0

    #First trough after peak
    if firstIndexPtT != None:
        for j in range(firstIndexPtT, len(valListA)-1):
            if (valListA[j] < valListA[j+1]):
                endIndexPtT = j
                endValPtT = valListA[j]
                break
            else:
                endIndexPtT = None
                endValPtT = None
    else:
        endIndexPtT = None
        endValPtT = None

    #Calculate time difference between trough to peak
    #countStartTtP = 0
    if endIndexPtT != None:
        for i in range(endIndexPtT, len(valListA) - 10):
            if (valListA[i+10] - valListA[i] > 10):
                firstIndexTtP = i;
                firstValTtP = valListA[i]
                break
            else:
                firstIndexTtP = None;
                firstValTtP = None
    else:
        firstIndexTtP = None;
        firstValTtP = None

    flatArrayVals = []

    if firstIndexTtP != None:
        for j in range(firstIndexTtP, len(valListA) - 10):
            if (valListA[j+10] - valListA[j] < 10):
                startOfFlat = j
                for k in range(20):
                    flatArrayVals.append(valListA[j+k])
                break

        for i in range(10):
            if (flatArrayVals[i+10] - flatArrayVals[i] < 3):
                endIndexTtP = startOfFlat+i
                endValTtP = valListA[endIndexTtP]
            else:
                endIndexTtP = None
                endValTtP = None
    else:
        endIndexTtP = None
        endValTtP = None

    try:
        firstIndexPtT = float(firstIndexPtT)*2/1000
    except:
        firstIndexPtT = None
    try:
        endIndexPtT = float(endIndexPtT)*2/1000
    except:
        endIndexPtT = None
    try:
        firstIndexTtP = float(firstIndexTtP)*2/1000
    except:
        firstIndexTtP = None
    try:
        endIndexTtP = float(endIndexTtP)*2/1000
    except:
        endIndexTtP = None
    #Increments to plot your points on are the total time divided by the amount of points
    #inc = totalTime/smallestLen
    totalTime = 2.0
    incA = totalTime/float(len(valListA))
    tA= np.arange(0.0, totalTime, incA)

    if len(valListA) < len(tA):
        tA = tA[0:len(valListA)]

    valListASave = np.array(valListA)
    valListBSave = np.array(valListB)
    valListCSave = np.array(valListC)
    timeSave = np.array(tA)

    print len(valListASave)
    print len(valListBSave)
    print len(valListCSave)
    print len(timeSave)

    dataSave = np.array([valListASave, valListBSave, valListCSave,timeSave])
    dataSave = dataSave.T
    #Open a text file that is writable

    dataFilePath = "\dataSave.txt"
    fullPath = appDataPath + fileName
    #with open(dataFilePath, 'w+') as datafile_id:
    with open(fullPath, 'w+') as datafile_id:
    #here you open the ascii file

        np.savetxt(datafile_id, dataSave, fmt=['%s','%s','%s','%f'])
        #here the ascii file is written."""

    #F = open(dataFilePath,'a')
    F = open(fullPath,'a')
    F.write("DETAILS")
    #x = [1,2,3,4,5,6,7,8]
    #y = [5,6,1,3,8,9,3,5]
    values = [tA,valListA,valListB,valListC,firstIndexPtT,firstValPtT, endIndexPtT, endValPtT, firstIndexTtP, firstValTtP, endIndexTtP, endValTtP]
    return values
    #App_Window.refreshFigure(App_Window.refreshFigure(),tA,valListA,valListB,valListC,firstIndexPtT,firstValPtT, endIndexPtT, endValPtT, firstIndexTtP, firstValTtP, endIndexTtP, endValTtP)


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

    def clearText(self, event):
        self.e1.delete(0, "end")
        return None

    def resetGraph(self):
        self.clearGraph()

    def clearGraph(self):
        print "reset"
        valList = []
        self.line1.set_data([],[])
        self.line2.set_data([],[])
        self.line3.set_data([],[])
        self.PtTPeak.set_data([],[])
        self.PtTTrough.set_data([],[])
        self.TtPPeak.set_data([],[])
        self.TtPTrough.set_data([],[])
        ax = self.canvas.figure.axes[0]
        ax.grid(False)

        self.canvas.draw()


        self.refreshFigure(tA,valListA,valListB,valListC,firstIndexPtT,firstValPtT, endIndexPtT, endValPtT, firstIndexTtP, firstValTtP, endIndexTtP, endValTtP)
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
        ax.grid(which = 'minor')

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
        print values
        self.refreshFigure(values[0],values[1],values[2],values[3],values[4],values[5], values[6], values[7], values[8], values[9], values[10], values[11])


if __name__ == "__main__":
    MainWindow = App_Window(None)
    MainWindow.minsize(width=800, height=600)
    MainWindow.mainloop()

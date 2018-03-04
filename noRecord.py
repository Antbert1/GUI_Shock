# import modules that I'm using
import matplotlib
matplotlib.use('TKAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as pltlib
import Tkinter as tk
from Tkinter import *
import numpy as np
import serial
import time

#Make object for application
class App_Window(tk.Tk):
    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
    def initialize(self):

        #These variables are set at the start to be used later on in the plotting. As long as they are 'in scope' and are set before you try to use them, it doesn't matter where you set them. Being in scope means being declared where you are using them. An example of being out of scope would be if you had a "main" function, and a separate "graph" function that is called inside main. If you declare a variable min_val inside the graph function, and try to use it in the main, it won't work because main can't see it.
        min_val = 0
        max_val = 1024
        print("Test")

        #Prints a line to the terminal asking user to input the port number as 'COMx'. You can check the port number in device manager when the Arduino is plugged in
        #port = raw_input("Enter the port number (e.g. 'COM4'): \n")
        port = 'com5'

        #Creates a variable called 'ser' that we will use to communicate with the serial port. Gives it the port number, the baud rate and timeout (not sure what timeout does but it fixed that 0000s problem)
        #self.ser = serial.Serial(port, 230400, timeout=1)

        #Some commented out stuff experimenting with weird data
        #ser = serial.Serial('COM4', 9600, timeout=1)
        #self.ser.flush()

        #Sleep tells the programme to wait for x seconds. Useful in serial comms when you want to be sure something has happened
        time.sleep(3)
        #This is an empty array of data that will be populated later with the values from the serial port
        self.valList = []
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

        self.e1 = Entry(frame, width=30)
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
        #b = f.add_subplot(312)
        #c = f.add_subplot(313)
        x = []
        y = []
        self.line1, = a.plot(x,y,'g')
        self.line2, = a.plot(x,y,'r')
        self.line3, = a.plot(x,y,'b')

        self.canvas = FigureCanvasTkAgg(self.f, plotFrame)
        self.canvas.show()
        #a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        #canvas = FigureCanvasTkAgg(f, plotFrame)
        #canvas.show()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.NONE, expand=False, anchor=W)
        self.update
        toolbar = NavigationToolbar2TkAgg(self.canvas, plotFrame).pack(side=tk.TOP)
        Label(plotFrame, text="Data One").pack(anchor=W)
        Label(plotFrame, text="Data Two").pack(anchor=W)
        Label(plotFrame, text="Data Three").pack(anchor=W)

    def resetGraph(self):
        self.clearGraph()

    def clearGraph(self):
        print "reset"

        self.line1.set_data([],[])
        self.line2.set_data([],[])
        self.line3.set_data([],[])
        ax = self.canvas.figure.axes[0]
        ax.grid(False)

        #ax.set_ylim(min(yA), max(yA))
        #ax.set_xlim(min(xA), max(xA))
        #ax.set_ylim(0, 1024)
        #ax.set_xlim(0, 2)
        self.canvas.draw()

    def runLoop(self):
        self.startTime = time.time()
    	startCommand = 'START$'
    	#sendStart = bytes(startCommand.encode('utf-8'))
        stopCommand = 'STOP$'
        #sendStop = bytes(stopCommand.encode('utf-8'))
    	#self.ser.write(startCommand)

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

        print len(valListA)
        print len(valListB)
        print len(valListC)
        #Increments to plot your points on are the total time divided by the amount of points
        #inc = totalTime/smallestLen
        totalTime = 2.0
        incA = totalTime/float(len(valListA))
        print totalTime/len(valListA)
        #incB = totalTime/len(valListB)
        #incC = totalTime/len(valListC)

        tA= np.arange(0.0, totalTime, incA)
        #tB= np.arange(0.0, totalTime, incB)
        #tC= np.arange(0.0, totalTime, incC)

        valListASave = np.array(valListA)
        valListBSave = np.array(valListB)
        valListCSave = np.array(valListC)
        timeSave = np.array(tA)

        dataSave = np.array([valListASave, valListBSave, valListCSave,timeSave])
        dataSave = dataSave.T
        #Open a text file that is writable

        dataFilePath = "dataSave.txt"

        with open(dataFilePath, 'w+') as datafile_id:
        #here you open the ascii file

            np.savetxt(datafile_id, dataSave, fmt=['%s','%s','%s','%f'])
            #here the ascii file is written."""

        F = open(dataFilePath,'a')
        F.write("DETAILS")

        #x = [1,2,3,4,5,6,7,8]
        #y = [5,6,1,3,8,9,3,5]
        self.refreshFigure(tA,valListA,valListB,valListC)
    	print("Finished")

    def refreshFigure(self,xA,yA,yB,yC):
        #Leave max and min at 0 and 1024
        print (min(yA))
        print (max(yA))
        #minY = min([min(yA), min(yB), min(yC)])
        #maxY = max([max(yA), max(yB), max(yC)])
        minY = 0
        maxY = 1024
        self.line1.set_data(xA,yA)
        self.line2.set_data(xA,yB)
        self.line3.set_data(xA,yC)
        ax = self.canvas.figure.axes[0]
        ax.grid(True)
        #ax.set_ylim(min(yA), max(yA))
        #ax.set_xlim(min(xA), max(xA))
        ax.set_ylim(minY, maxY)
        ax.set_xlim(min(xA), max(xA))
        self.canvas.draw()

    def OnButtonClick(self):
    	self.runLoop()


if __name__ == "__main__":
    MainWindow = App_Window(None)
    MainWindow.minsize(width=800, height=600)
    MainWindow.mainloop()

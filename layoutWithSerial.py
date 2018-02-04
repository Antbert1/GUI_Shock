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

		#Prints a line to the terminal asking user to input the port number as 'COMx'. You can check the port number in device manager when the Arduino is plugged in
		#port = raw_input("Enter the port number (e.g. 'COM4'): \n")
		port = 'com6'
		#Creates a variable called 'ser' that we will use to communicate with the serial port. Gives it the port number, the baud rate and timeout (not sure what timeout does but it fixed that 0000s problem)
		self.ser = serial.Serial(port, 230400, timeout=1)

		#Some commented out stuff experimenting with weird data
		#ser = serial.Serial('COM4', 9600, timeout=1)
		self.ser.flush()

		#Sleep tells the programme to wait for x seconds. Useful in serial comms when you want to be sure something has happened
		time.sleep(3)
		#This is an empty array of data that will be populated later with the values from the serial port
		self.valList = []
		self.startTime = time.time()
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

		#button = tk.Button(self,text="Start",command=self.OnButtonClick).pack(side=tk.LEFT,anchor=W)
		#button = tk.Button(plotFrame,text="Start",command=self.OnButtonClick).grid(row=11, column=0)
		#Right hand side with Graph
		Label(plotFrame, text="Graph Stuff heading").pack()

		f = Figure(figsize=(6,4), dpi=100)
		a = f.add_subplot(111)
		x = []
		y = []
		self.line1, = a.plot(x,y)
		self.canvas = FigureCanvasTkAgg(f, plotFrame)
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

    def runLoop(self):
    	startCommand = 'START$'
    	sendStart = bytes(startCommand.encode('utf-8'))
    	self.ser.write(startCommand)
    	print("START RECORDING")
    	for i in range(10000):
    		self.valList.append(self.ser.readline())

        endTime = time.time()
        totalTime = endTime - self.startTime
        #Split valList into 3 lists
        valListA = []
        valListB = []
        valListC = []

        for val in self.valList:
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
        #Get smallest

        if len(valListA) <= len(valListB):
        	if len(valListA) <= len(valListC):
        		smallestLen = len(valListA)
        		valListB = valListB[0:smallestLen]
        		valListC = valListC[0:smallestLen]
        	else:
        		smallestLen = len(valListC)
        		valListB = valListB[0:smallestLen]
        		valListA = valListC[0:smallestLen]
        elif len(valListB) <= len(valListC):
        	smallestLen = len(valListB)
        	valListA = valListB[0:smallestLen]
        	valListC = valListC[0:smallestLen]
        else:
        	smallestLen = len(valListC)
        	valListB = valListB[0:smallestLen]
        	valListA = valListC[0:smallestLen]

        #Increments to plot your points on are the total time divided by the amount of points
        #inc = totalTime/smallestLen

        incA = totalTime/len(valListA)
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

        """
        plt.subplot(311)
        #Print the length of the valList to see how many got
        #print(len(valList))
        plt.plot(tA, valListA,'r')
        #plt.subplot(312)
        #plt.plot(tB, valListB,'g')
        incrementY = int((max(valListA) - min(valListA))/20)
        #plt.yticks(np.arange(min(valListA), max(valListA)+1, incrementY))

        plt.subplot(312)
        #Print the length of the valList to see how many got
        #print(len(valList))
        plt.plot(tA, valListB,'g')
        #plt.subplot(312)
        #plt.plot(tB, valListB,'g')
        incrementY = int((max(valListB) - min(valListB))/20)
        #plt.yticks(np.arange(min(valListB), max(valListB)+1, incrementY))


        plt.subplot(313)
        #Print the length of the valList to see how many got
        #print(len(valList))
        plt.plot(tA, valListC,'b')
        #plt.subplot(312)
        #plt.plot(tB, valListB,'g')
        incrementY = int((max(valListC) - min(valListC))/20)
        #plt.yticks(np.arange(min(valListC), max(valListC)+1, incrementY))

        #plt.subplot(313)
        #plt.plot(tC, valListC,'b')
        #plt.ylim((1,1023))
        #Show plot
        plt.show()
        """
        #x = [1,2,3,4,5,6,7,8]
        #y = [5,6,1,3,8,9,3,5]
        self.refreshFigure(tA,valListA)
    	print("Finished")

    def refreshFigure(self,x,y):
        #x = [1,2,3,4,5,6,7,8]
        #y = [5,6,1,3,8,9,3,5]
        self.line1.set_data(x,y)
        ax = self.canvas.figure.axes[0]
        ax.set_ylim(min(y), max(y))
        ax.set_xlim(min(x), max(x))
        self.canvas.draw()

    def OnButtonClick(self):
    	self.runLoop()
    	"""if self.btn_text.get() == "Start":
    	    self.btn_text.set("Stop")
    	else:
    	    self.btn_text.set("Start")
    	    self.e1.delete(0,END)
    	    self.e2.delete(0,END)
    	    self.e3.delete(0,END)
    	    self.e4.delete(0,END)
    	    self.e5.delete('1.0',END)
    	self.refreshFigure()"""


if __name__ == "__main__":
    MainWindow = App_Window(None)
    MainWindow.minsize(width=800, height=600)
    MainWindow.mainloop()

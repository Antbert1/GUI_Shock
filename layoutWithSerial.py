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
        self.ser = serial.Serial(port, 230400, timeout=1)

        #Some commented out stuff experimenting with weird data
        #ser = serial.Serial('COM4', 9600, timeout=1)
        self.ser.flush()

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

        #button = tk.Button(self,text="Start",command=self.OnButtonClick).pack(side=tk.LEFT,anchor=W)
        #button = tk.Button(plotFrame,text="Start",command=self.OnButtonClick).grid(row=11, column=0)
        #Right hand side with Graph
        Label(plotFrame, text="Graph Stuff heading").pack()

        f = Figure(figsize=(6,4), dpi=100)
        a = f.add_subplot(111)
        #b = f.add_subplot(312)
        #c = f.add_subplot(313)
        x = []
        y = []
        self.line1, = a.plot(x,y,'g')
        self.line2, = a.plot(x,y,'r')
        self.line3, = a.plot(x,y,'b')

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
        self.startTime = time.time()
    	startCommand = 'START$'
    	#sendStart = bytes(startCommand.encode('utf-8'))
        stopCommand = 'STOP$'
        #sendStop = bytes(stopCommand.encode('utf-8'))
    	self.ser.write(startCommand)
    	print("START RECORDING")
    	for i in range(3000):
    		self.valList.append(self.ser.readline())
        self.ser.write(stopCommand)

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


        #Open a text file that is writable
        file = open("testfile.txt","w")
        for val in self.valList:
        	#If number is invalid, write a 0
        	if not val:
        		file.write('0')
        	#else write a string representation of the number to the file
        	else:
        		file.write(str(val))
        		#\n means the end of the line. .txt files interpret this
        		file.write('\n')


        #Open a text file that is writable
        fileA = open("testfileA.txt","w")
        for val in valListA:
        	#If number is invalid, write a 0
        	if not val:
        		fileA.write('0')
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
                valListC.append(valListC[len(valListC)-1])
            else:
                diffC = len(valListA) - len(valListC)
                for i in range(diffC):
                    valListC.append(valListC[len(valListC)-1])


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

        F = open(dataFilePath,'a')
        F.write("DETAILS")
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

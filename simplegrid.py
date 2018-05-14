import Tkinter as tk
from Tkinter import *
import ttk


class App_Window(tk.Tk):

    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
    def initialize(self):
        #Menu
        topFrame = Frame(self)
        topFrame.pack(side="top", fill="both")
        homeBtn = tk.Button(topFrame, text="HOME", padx=20, pady=10)
        compareBtn = tk.Button(topFrame, text="COMPARE", padx=20, pady=10)
        dataBtn = tk.Button(topFrame, text="DATA", padx=20, pady=10)
        homeBtn.grid(row=0, column=1)
        compareBtn.grid(row=0, column=2)
        dataBtn.grid(row=0, column=3)

        menuSeparator = Frame(self, height=1, bg="grey", pady=20).pack(side="top", fill="both")

        leftFrame = Frame(self, bg="red")
        leftFrame.pack(side="left", fill="both", padx=10, pady=10)

        self.l1 = Label(leftFrame, text="INPUT FIELDS").grid(row=0, sticky=W, columnspan=3)

        self.l2 = Label(leftFrame, text="Name").grid(row=1, sticky=W, columnspan=3)
        self.l3 = Label(leftFrame, text="Clicks (C)").grid(row=3, sticky=W, columnspan=3)
        self.l4 = Label(leftFrame, text="Clicks (R)").grid(row=5, sticky=W, columnspan=3)
        self.l5 = Label(leftFrame, text="Temp").grid(row=7, sticky=W, columnspan=3)
        self.l6 = Label(leftFrame, text="Notes").grid(row=9, sticky=W, columnspan=3)

        self.e1 = Entry(leftFrame, width=30)
        self.e2 = Entry(leftFrame, width=30)
        self.e3 = Entry(leftFrame, width=30)
        self.e4 = Entry(leftFrame, width=30)
        self.e5 = Text(leftFrame,width=23, height=5)

        self.e1.grid(row=2, column=0,sticky=W, columnspan=3)
        self.e2.grid(row=4, column=0,sticky=W, columnspan=3)
        self.e3.grid(row=6, column=0,sticky=W, columnspan=3)
        self.e4.grid(row=8, column=0,sticky=W, columnspan=3)
        self.e5.grid(row=10, column=0,sticky=W, columnspan=3)

        startBtn = tk.Button(leftFrame, text="START", padx=15, pady=8)
        resetBtn = tk.Button(leftFrame, text="RESET", padx=15, pady=8)
        startBtn.grid(row=11,column=0)
        resetBtn.grid(row=11,column=1)
        leftFrame.grid_rowconfigure(11, minsize=50)


        rightFrame = Frame(self, bg="blue")
        rightFrame.pack(side="right", fill="both", expand = True)
        rightBtn = tk.Button(rightFrame, text="RIGHT", padx=20, pady=10)
        rightBtn.grid(row=3, column=1)


MainWindow = App_Window(None)
MainWindow.minsize(width=1024, height=650)
MainWindow.mainloop()

from tkinter import *
from tkinter import ttk

import ZIPanal,ZIPimg,ZIPquiz



class ZIPgui:
	def __init__(self):
		self.number = 1
		self.root = Tk()

		self.root.title("Zippy")
		self.mainframe = ttk.Frame(root, padding="3 3 12 12")
		self.mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
		self.root.columnconfigure(0,weight=1)
		self.root.rowconfigure(0,weight=1)

		ttk.Label(self.mainframe, text="This is my ZIP code studying tool. I hope you enjoy! Either press a button or type the letter ").grid(column=1,row=1,sticky=N)

		self.application("Analytics", ZIPanal.gui)
		application("Image", ZIPimg.gui)
		application("Test", ZIPquiz.gui)

		for child in self.mainframe.winfo_children():
			child.grid_configure(padx=5, pady=5)
		
	
	def handle_sublaunch(self, launch_func):
		return lambda: 
			launch_func()

	def application(self, name, launch_func):
		ttk.Button(self.mainframe, text=self.number + ". " + name, command=self.handle_sublaunch(launch_func)).grid(column=3,row=1+number, sticky=W)
		if self.number >= 0 and self.number <= 9:
			root.bind(str(self.number), command=handle_sublaunch(launch_func))
		self.number += 1
	
	def show(self):
		self.root.mainloop()


if __name__=='__main__':
	ZIPgui gui = ZIPgui()
	gui.show()
'''

Cardiac cine dicom data navigation
GUI implementation using TKinter

2016-06-23
Author: Yoon-Chul Kim

'''


import dicom
import numpy as np
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import tkinter as tk
import os

from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

# from matplotlib import pyplot, cm
from skimage import data, io, filters
from PIL import Image, ImageTk
from tkinter import Tk, Button, Frame, Label, BOTH, LEFT, Scale, HORIZONTAL, RIDGE
from numpy import arange, sin, pi


class MyoCine(tk.Frame):

	def __init__(self, master=None):
		tk.Frame.__init__(self, master, background="white")
		self.dirname = []

		self.cine_series = []
		self.cine_images = []
		self.cine_imcrop_flag = False

		# self.disp_cine_ = tk.Toplevel()
		# self.disp_cine_.geometry('480x600+800+20')
		# self.disp_cine_.focus_set()
		# self.disp_cine_.title('Cine image analysis')
		#
		# self.disp_cine_slider = tk.Frame(self.disp_cine_)
		# self.disp_cine_slider.grid(row=0, column=0)
		#
		# self.disp_cine = tk.Frame(self.disp_cine_)
		# self.disp_cine.focus_set()
		# self.disp_cine.grid(row=1, column=0)

		self.frameindex = 0
		self.sliceindex = 0
		self.script_dir = os.getcwd()
		self.pack(fill=BOTH, expand=True)

		frame1 = Frame(self)
		frame1.pack(fill=BOTH, padx=5, pady=5)
		lbl1 = Label(frame1, text="Subject", relief=RIDGE, width=20)
		lbl1.pack(side=LEFT, padx=5, pady=5)
		btt1 = Button(frame1, text='File Open', command=self.choose_directory)
		btt1.pack(padx=5, pady=5)


		frame3 = Frame(self)
		frame3.pack(fill=BOTH, padx=5, pady=5)
		lbl3 = Label(frame3, text="Cine", relief=RIDGE, width=20)
		lbl3.pack(side=LEFT, padx=5, pady=5)
		btt3 = Button(frame3, text='Load data', command=self.cine_load)
		btt3.pack(side=LEFT,padx=5, pady=5)
		btt3_2 = Button(frame3, text='Display', command=self.cine_disp)
		btt3_2.pack(side=LEFT,padx=5, pady=5)


		frame9 = Frame(self)
		frame9.pack(fill=BOTH,padx=5,pady=5)
		lbl9 = Label(frame9, text="System", relief=RIDGE, width=20)
		lbl9.pack(side=LEFT, padx=5, pady=5)
		btt9 = Button(frame9, text='Quit', command=self.quit_app)
		btt9.pack(padx=5, pady=5)

		self.disp_cine_ = tk.Toplevel()
		self.disp_cine_.geometry('800x500+300+10')
		self.disp_cine_.title('Short axis CINE')

		self.disp_cine_slider = tk.Frame(self.disp_cine_); self.disp_cine_slider.grid(row=0, column=0)
		self.disp_cine_button = tk.Frame(self.disp_cine_);	self.disp_cine_button.grid(row=0, column=1)
		self.disp_cine_img = tk.Frame(self.disp_cine_);	self.disp_cine_img.grid(row=1, column=0)
		self.disp_cine_txt = tk.Frame(self.disp_cine_);	self.disp_cine_txt.grid(row=1, column=1)

		self.cine_slider1 = tk.Scale(self.disp_cine_slider,from_=0,to=14,length=200,tickinterval=1,orient=HORIZONTAL, \
		                             command=self.cine_slider_event, label='slice no.')
		self.cine_slider1.grid(row=0, column=0)
		self.cine_slider2 = tk.Scale(self.disp_cine_slider,from_=0,to=29,length=200,tickinterval=5,orient=HORIZONTAL,\
		                             command=self.cine_slider_event, label='frame no.')
		self.cine_slider2.grid(row=0, column=1)

		self.cine_lbl1 = tk.Label(self.disp_cine_txt, text='frame no. of ED:').grid(row=0,column=0)
		self.cine_info11 = tk.Entry(self.disp_cine_txt, width=10); self.cine_info11.grid(row=0,column=1)

		self.cine_lbl2 = tk.Label(self.disp_cine_txt, text='frame no. of ES:').grid(row=1,column=0)
		self.cine_info21 = tk.Entry(self.disp_cine_txt, width=10); self.cine_info21.grid(row=1,column=1)

		self.cine_lbl3 = tk.Label(self.disp_cine_txt, text='most apical slice no. of ED:').grid(row=2,column=0)
		self.cine_info31 = tk.Entry(self.disp_cine_txt, width=10); self.cine_info31.grid(row=2,column=1)

		self.cine_lbl4 = tk.Label(self.disp_cine_txt, text='most basal slice no. of ED:').grid(row=3,column=0)
		self.cine_info41 = tk.Entry(self.disp_cine_txt, width=10); self.cine_info41.grid(row=3,column=1)

		self.cine_lbl5 = tk.Label(self.disp_cine_txt, text='most apical slice no. of ES:').grid(row=4,column=0)
		self.cine_info51 = tk.Entry(self.disp_cine_txt, width=10); self.cine_info51.grid(row=4,column=1)

		self.cine_lbl6 = tk.Label(self.disp_cine_txt, text='most basal slice no. of ES:').grid(row=5,column=0)
		self.cine_info61 = tk.Entry(self.disp_cine_txt, width=10); self.cine_info61.grid(row=5,column=1)

		self.cine_lbl8 = tk.Label(self.disp_cine_txt, text='SpacingBetweenSlices(mm):').grid(row=8,column=0)
		self.cine_info81 = tk.Entry(self.disp_cine_txt, width=10); self.cine_info81.grid(row=8,column=1)

		self.cine_lbl9 = tk.Label(self.disp_cine_txt, text='PixelSpacing (mm):').grid(row=9,column=0)
		self.cine_info91 = tk.Entry(self.disp_cine_txt, width=10); self.cine_info91.grid(row=9,column=1)



		button1 = tk.Button(self.disp_cine_button, text='Update', command=self.cine_update)
		button1.grid(row=0,column=0)

		tk.Button(self.disp_cine_button, text='Area for crop', command=self.cine_draw_rectROI).grid(row=0,column=1)
		tk.Button(self.disp_cine_button, text='Crop', command=self.cine_crop).grid(row=1, column=0)

		tk.Button(self.disp_cine_button, text='Show info', font=("Helvetica", 8), command=self.cine_showinfo).grid(row=1, column=1)



	def choose_directory(self):

		self.dirname = filedialog.askdirectory(initialdir="c:/Users/YoonKim/Documents/data/", title='please select a directory')
		if len(self.dirname) > 0:
			print("You chose %s" % self.dirname)
		return self

	def get_directory(self):

		return self.dirname

	def get_images(self):

		return self.cine_images

	def get_frameindex(self):

		self.frameindex = (int(self.cine_info11.get()), int(self.cine_info21.get()))

		return self.frameindex

	def get_sliceindex(self):

		self.sliceindex = (int(self.cine_info31.get()), int(self.cine_info41.get()), int(self.cine_info51.get()), int(self.cine_info61.get()))

		return self.sliceindex

	def get_slicespacing(self):

		return float(self.cine_info81.get())

	def get_pixelspacing(self):

		return float(self.cine_info91.get())



	def cine_load(self):

		a = self.dirname + "/cine/"
		print("cine: you chose %s" % a)

		os.chdir(a)
		session_files = os.listdir()
		#self.cine_nslice = 12

		count = 0
		for f in session_files:
			if len(f) <= 3:
				#print("yk: %s" % f)
				self.cine_series.append(f)
				count = count + 1
		self.cine_nslice = count

		count1 = 0
		for j in range(0, self.cine_nslice):
			print("cine series: %s" % self.cine_series[j])
			b = a + self.cine_series[j]
			os.chdir(b)
			session_files = os.listdir()
			count2 = 0
			for f in session_files:
				ds = dicom.read_file(f)
				if count1 == 0 and count2 == 0:
					pixelDims = (int(ds.Rows), int(ds.Columns), int(30), int(self.cine_nslice))
					self.cine_images = np.zeros(pixelDims, dtype=ds.pixel_array.dtype)
					print(ds.PatientName)

					self.cine_info = ds

				self.cine_images[:, :, count2, count1] = ds.pixel_array
				count2 = count2 + 1
			count1 = count1 + 1





	def cine_disp(self):

		os.chdir(self.script_dir)

		img = self.cine_images[:, :, 0, 0]
		#print(img.shape)
		#print("image min = %f" % img.min())
		#print("image max = %f" % img.max())

		fig = Figure(figsize=(5,5))
		ax0 = fig.add_subplot(111)
		ax0.imshow(img, cmap=plt.cm.gray)

		self.canvas_cine = FigureCanvasTkAgg(fig, self.disp_cine_img)
		self.canvas_cine.show()
		self.canvas_cine.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		self.toolbar_cine = NavigationToolbar2TkAgg(self.canvas_cine, self.disp_cine_img)
		self.toolbar_cine.update()
		self.canvas_cine._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		self.cine_ax0 = ax0


	def cine_slider_event(self, event):

		#print("cine: slider has been moved...")
		if self.cine_images != []:
			img = self.cine_images[:,:,self.cine_slider2.get(),self.cine_slider1.get()]
			if self.cine_imcrop_flag == True:
				x1 = self.cine_cropbox[0]
				x2 = self.cine_cropbox[2]
				y1 = self.cine_cropbox[1]
				y2 = self.cine_cropbox[3]
				img = img[x1:x2, y1:y2]

			self.cine_ax0.clear()
			self.cine_ax0.imshow(img, cmap=plt.cm.gray)
			self.cine_ax0.axis('off')
			self.canvas_cine.draw()

			self.frameindex = self.cine_slider2.get()
			self.sliceindex = self.cine_slider1.get()


	def cine_update(self):
		img = self.cine_images[:,:,self.cine_slider2.get(), self.cine_slider1.get()]
		self.cine_ax0.clear()
		self.cine_ax0.imshow(img, cmap=plt.cm.gray)
		self.cine_ax0.axis('off')
		self.canvas_cine.draw()


	def cine_draw_rectROI(self):
		img = self.cine_images[:,:,self.cine_slider2.get(), self.cine_slider1.get()]
		self.cine_ax0.clear()
		self.cine_ax0.imshow(img, cmap=plt.cm.gray)
		#self.cine_ax0.axis('off')
		self.canvas_cine.draw()
		self.canvas_cine.get_tk_widget().bind("<Button-1>", self.cine_OnMouseDown)
		self.corners = []



	def cine_OnMouseDown(self, event):

		"""Record location of user clicks to establish cropping region"""
		self.corners.append([event.x, event.y])
		if len(self.corners) == 2:
			self.canvas_cine.rect = self.canvas_cine.get_tk_widget().create_rectangle(self.corners[0][0], self.corners[0][1], self.corners[1][0], self.corners[1][1], outline='cyan', width=2, tag='rect_tag')


	def cine_crop(self):

		self.cine_imcrop_flag = True
		img = self.cine_images[:,:,self.cine_slider2.get(), self.cine_slider1.get()]

		c_w = self.canvas_cine.get_tk_widget().winfo_width()
		c_h = self.canvas_cine.get_tk_widget().winfo_height()

		#print("(width x height) of canvas = (%d x %d)" % (c_w, c_h))
		#print("(nrow x ncol) of image = (%d x %d)" % (img.shape[0], img.shape[1]))
		#print("P1=(%d,%d), P2=(%d,%d)" % (self.corners[0][0], self.corners[0][1], self.corners[1][0], self.corners[1][1]))

		yoffset = (c_w - img.shape[1])/2
		xoffset = (c_h - img.shape[0])/2
		#print("image offset from canvas (x0, y0) = (%4.1f x %4.1f)" % (xoffset, yoffset) )

		x1 = self.corners[0][1] - xoffset
		x2 = self.corners[1][1] - xoffset

		y1 = self.corners[0][0] - yoffset
		y2 = self.corners[1][0] - yoffset

		img_crop = img[x1:x2, y1:y2]
		self.cine_cropbox = (x1, y1, x2, y2)

		self.canvas_cine.get_tk_widget().delete("rect_tag")
		self.cine_ax0.clear()
		self.cine_ax0.imshow(img_crop, cmap=plt.cm.gray)
		self.cine_ax0.axis('off')
		self.canvas_cine.draw()


	def cine_showinfo(self):

		ds2 = self.cine_info
		print(ds2.PatientName)

		# lbl11 = self.cine_info11; lbl11.delete(0, tk.END); lbl11.insert(10, ds2.PatientID)
		# lbl21 = self.cine_info21; lbl21.delete(0, tk.END); lbl21.insert(10, ds2.PatientSex)
		# lbl31 = self.cine_info31; lbl31.delete(0, tk.END); lbl31.insert(10, ds2.PatientAge)
		# lbl41 = self.cine_info41; lbl41.delete(0, tk.END); lbl41.insert(10, str(ds2.PatientSize))
		# lbl51 = self.cine_info51; lbl51.delete(0, tk.END); lbl51.insert(10, str(ds2.PatientWeight))
		# lbl61 = self.cine_info61; lbl61.delete(0, tk.END); lbl61.insert(10, ds2.StudyDate)

		lbl81 = self.cine_info81; lbl81.delete(0, tk.END); lbl81.insert(0, str(ds2.SpacingBetweenSlices))
		lbl91 = self.cine_info91; lbl91.delete(0, tk.END); lbl91.insert(0, str(ds2.PixelSpacing[0]))













	def quit_app(self):
		# if len(self.dirname) > 0:
		# 	print("YK: you chose %s" % self.dirname)
		self.quit()

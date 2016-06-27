'''

Cardiac cine dicom data navigation
GUI implementation using PyQt

2016-06-27
Author: Yoon-Chul Kim

'''


import dicom
import numpy as np
import matplotlib


''' for Anaconda '''
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

matplotlib.use("Qt4Agg")



import matplotlib.pyplot as plt
import os

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure

# from matplotlib import pyplot, cm
from skimage import data, io, filters
from PIL import Image, ImageTk
# from tkinter import Tk, Button, Frame, Label, BOTH, LEFT, Scale, HORIZONTAL, RIDGE
from numpy import arange, sin, pi


# class MyoCine(tk.Frame):

class MyoCine(QWidget):

	def __init__(self, master=None):


		super(MyoCine, self).__init__()

		self.layout = QGridLayout()
		self.btn = QPushButton("Choose Subject Directory")
		self.btn.clicked.connect(self.getdirec)

		self.layout.addWidget(self.btn, 0,0)
		self.le = QLabel("Hello")

		self.btn2 = QPushButton("Load data")
		self.btn2.clicked.connect(self.load_img)
		self.layout.addWidget(self.btn2,0,1)

		self.btn3 = QPushButton("Display")
		self.btn3.clicked.connect(self.disp_img)
		self.layout.addWidget(self.btn3,0,2)

		self.btn4 = QPushButton("Quit")
		self.btn4.clicked.connect(self.quit_app)
		self.layout.addWidget(self.btn4,0,3)

		self.fig = Figure(figsize=(5, 5), dpi=100)
		self.axes = self.fig.add_subplot(111)
		self.axes.axis((0,512,0,512))
		self.cnvs = FigureCanvas(self.fig)
		self.layout.addWidget(self.cnvs,1,0)



		self.setLayout(self.layout)
		self.setWindowTitle("Perfusion")




		self.dirname = []

		self.cine_series = []
		self.cine_images = []
		self.cine_imcrop_flag = False


		self.frameindex = 0
		self.sliceindex = 0

		self.RRinterval = np.zeros(30)

		self.script_dir = os.getcwd()



	def getdirec(self):

		self.dirname = str(QFileDialog.getExistingDirectory(self, "Select Directory", 'c:/Users/YoonKim/Documents/data/'))
		print(self.dirname)

		return self


	def load_img(self):
		a = self.dirname + "/cine/"
		print("cine: you chose %s" % a)
		os.chdir(a)
		session_files = os.listdir()

		count = 0
		for f in session_files:
			if len(f) <= 3:
				#print("yk: %s" % f)
				self.cine_series.append(f)
				count += 1

		self.cine_nslice = count
		print('perf_nslice = %d' % self.cine_nslice)

		count1 = 0
		for j in range(0, self.cine_nslice):
			print("cine series: %s" % self.cine_series[j])
			b = a + self.cine_series[j]
			os.chdir(b)
			session_files = os.listdir()
			# print(session_files)
			count2 = 0
			for f in session_files:
				ds = dicom.read_file(f)
				# print(ds.PatientName+ds.Rows+ds.Columns)
				if count1 == 0 and count2 == 0:
					pixelDims = (int(ds.Rows), int(ds.Columns), int(30), int(self.cine_nslice))
					self.cine_images = np.zeros(pixelDims, dtype=ds.pixel_array.dtype)


				self.cine_images[:, :, count2, count1] = ds.pixel_array

				if count1 == 0:
					self.RRinterval[count2] = ds.NominalInterval*(10**-3)

				count2 += 1
			count1 += 1



	def disp_img(self):
		# self.main_frame = QWidget()
		self.dpi = 100
		self.width = 5
		self.height = 5

		os.chdir(self.script_dir)
		img = self.cine_images[:, :, 0, 0]
		print(img.shape)
		print("image min = %f" % img.min())
		print("image max = %f" % img.max())

		self.fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)

		self.axes = self.fig.add_subplot(111)
		# self.axes.axis((0, 2*img.shape[1], 2*img.shape[0], 0))
		self.canvas = FigureCanvas(self.fig)
		# self.canvas.setParent(self.main_frame)

		self.background = None
		# self.background = self.canvas.copy_from_bbox(self.axes.bbox)

		self.im = self.axes.imshow(img, cmap='gray')

		self.canvas.updateGeometry()
		self.canvas.draw()

		# self.im1 = self.axes.imshow(misc.ascent(), cmap='bone', interpolation='lanczos', extent=[0,512,0,512], aspect=(1), animated=True)
		# self.im2 = self.axes.imshow(misc.face(), cmap='afmhot', interpolation='lanczos', extent=[0,265,0,256], aspect=(1), animated=True)

		# self.startButton = QtGui.QPushButton(self.tr("Keep Calculating"))
		# self.stopButton = QtGui.QPushButton(self.tr("Stop Calculation"))

		self.slider_t = QSlider(Qt.Horizontal)
		self.slider_t.setRange(0, 30)
		self.slider_t.setValue(20)
		self.slider_t.setTracking(True)
		self.slider_t.setTickPosition(QSlider.TicksBothSides)
		self.slider_t.valueChanged.connect(self.valuechange)

		self.slider_z = QSlider(Qt.Horizontal)
		self.slider_z.setRange(0, 15)
		self.slider_z.setValue(0)
		self.slider_z.setTracking(True)
		self.slider_z.setTickPosition(QSlider.TicksBothSides)
		self.slider_z.valueChanged.connect(self.valuechange)

		self.label_t = QLabel()
		self.label_z = QLabel()




		# layout = QGridLayout()
		self.layout.addWidget(self.canvas, 1, 0)
		self.layout.addWidget(self.slider_t, 2, 0)
		self.layout.addWidget(self.slider_z, 3, 0)

		self.layout.addWidget(self.label_t, 2, 1)
		self.layout.addWidget(self.label_z, 3, 1)

		# layout.addWidget(self.startButton, 2, 0)
		# layout.addWidget(self.stopButton, 3, 0)

		# self.main_frame.setLayout(layout)
		# self.setCentralWidget(self.main_frame)
		# self.setWindowTitle(self.tr("Perfusion"))


	def valuechange(self):
		# print("slider moved")
		self.frameindex = self.slider_t.value()
		self.sliceindex = self.slider_z.value()
		img = self.cine_images[:, :, self.frameindex, self.sliceindex]
		self.axes.imshow(img, cmap='gray')
		self.canvas.draw()

		self.label_t.setText(str(self.frameindex))
		self.label_z.setText(str(self.sliceindex))

	def quit_app(self):
		if len(self.dirname) > 0:
			print("YK: you chose %s" % self.dirname)
		self.close()



	def get_directory(self):

		return self.dirname

	def get_images(self):

		return self.cine_images





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


					self.cine_info = ds

				self.cine_images[:, :, count2, count1] = ds.pixel_array
				count2 = count2 + 1
			count1 = count1 + 1











def main():
	app = QApplication(sys.argv)
	ex = MyoCine()
	ex.show()
	app.exec_()


if __name__=='__main__':
	main()






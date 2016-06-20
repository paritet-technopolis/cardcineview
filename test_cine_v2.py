# image segmentation of cardiac cine
#
# Author: Yoon-Chul Kim
#
# 2016-05-18


import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import cmath

matplotlib.use("TkAgg")



# import tkinter as tk
import os
import sys

import MyoCine as myocine
from img2mask import img2mask # CYJ's code

# from tkinter import filedialog
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# from matplotlib.backend_bases import key_press_handler
# from matplotlib.figure import Figure

# from matplotlib import pyplot, cm
from skimage import data, io, filters
from PIL import Image, ImageTk
# from tkinter import Tk, Button, Frame, Label, BOTH, LEFT, Scale, HORIZONTAL, RIDGE
from numpy import arange, sin, pi


from scipy.optimize import curve_fit
from scipy.signal import medfilt


def setdiff_mask(mask1, mask2):

	nx = mask1.shape[0]
	ny = mask1.shape[1]
	mask1_ = mask1.reshape((nx*ny, 1))
	mask2_ = mask2.reshape((nx*ny, 1))
	ind1 = np.where(mask1_ == 1)
	ind2 = np.where(mask2_ == 1)

	index1 = ind1[0]
	index2 = ind2[0]
	s1 = set(index1)
	s2 = set(index2)
	s3 = s1 - s2

	mask3 = np.zeros((nx, ny))

	for j in s3:
		mask3[int(j/ny), j%ny] = 1

	return mask3


def get_index_fromMask(mask):

	nx = mask.shape[0]
	ny = mask.shape[1]
	mask_ = mask.reshape((nx*ny, 1))
	ind = np.where(mask_ == 1)
	index = ind[0]

	return index


cinedata = myocine.MyoCine()
cinedata.mainloop()

print( cinedata.get_directory() )
img1 = cinedata.get_images()

(frameno_ED, frameno_ES) = cinedata.get_frameindex()

(slno_api_ED, slno_bas_ED, slno_api_ES, slno_bas_ES) = cinedata.get_sliceindex()

slice_spacing = cinedata.get_slicespacing()
pixel_spacing = cinedata.get_pixelspacing()



print(img1.shape)

nx = img1.shape[0]
ny = img1.shape[1]
nframe = img1.shape[2]
nslice = img1.shape[3]

imgt = img1[:,:,:,slno_bas_ED]


print('frame no for ED and ES = (%3d, %3d)' % (frameno_ED, frameno_ES))
print('SpacingBetweenSlices = %5.2f' % slice_spacing)
print('PixelSpacing = %5.2f' % pixel_spacing)

imgED = img1[:,:,frameno_ED,slno_bas_ED]
imgES = img1[:,:,frameno_ES,slno_bas_ES]


fig, axes = plt.subplots(ncols=2, nrows=1, figsize=(8,4))
ax0,ax1 = axes.flat
ax0.imshow(imgED, cmap=plt.cm.gray)
ax1.imshow(imgES, cmap=plt.cm.gray)





'''
	Compute LVEDV
'''

LVEDV = 0.0
for j in range(slno_api_ED, slno_bas_ED+1):

	imgtmp = img1[:,:,frameno_ED,j]


	print('LVEDV: endocardial border detection')
	mask2 = img2mask(imgtmp)
	ind1 = get_index_fromMask(mask2)
	vol_cyl = len(ind1) * pixel_spacing * pixel_spacing * slice_spacing  # unit in mm^3

	# print('LVEDV: slice cylinder volume = %5.2f (mm^3)' % vol_cyl)

	LVEDV += vol_cyl

LVEDV = LVEDV/1000 # convert from mm^3 to mL

print('LVEDV = %5.2f (mL)' % LVEDV)


'''
	Compute LVESV
'''

LVESV = 0.0
for j in range(slno_api_ES, slno_bas_ES+1):

	imgtmp = img1[:,:,frameno_ES,j]
	print('LVESV: endocardial border detection')
	mask2 = img2mask(imgtmp)
	ind1 = get_index_fromMask(mask2)
	vol_cyl = len(ind1) * pixel_spacing * pixel_spacing * slice_spacing  # unit in mm^3

	LVESV += vol_cyl

LVESV = LVESV/1000 # convert from mm^3 to mL

print('LVESV = %5.2f (mm^3)' % LVESV)




'''
	compute LVEF
'''

LVEF = (LVEDV-LVESV)/LVEDV * 100
print('LVEF = %5.2f (percent)' % LVEF)


plt.show()




sys.exit()




print('LV cavity segmentation')
mask_LV = img2mask(img)
ind_LV = get_index_fromMask(mask_LV)

s1 = set(ind_LV)
sig_LV = np.zeros(nframe)
print(sig_LV.shape)


for t in range(0, nframe):
	for j in s1:
		sig_LV[t] = sig_LV[t] + imgt[int(j/ny), j%ny, t, ]
	sig_LV[t] = sig_LV[t]/len(s1)


fig1 = plt.figure()
plt.plot(range(0, nframe), sig_LV)
plt.title('LV blood pool signal vs. time')
plt.xlabel('frame no.')

print('epicardial border detection')
mask1 = img2mask(img)

print('endocardial border detection')
mask2 = img2mask(img)



print('locate LV center point')
fig2 = plt.figure()
plt.imshow(img)
x1 = plt.ginput(1)
print(x1)
print('clicked', x1)


print('locate RV insert')
fig3 = plt.figure()
plt.imshow(img)
x2 = plt.ginput(1)
print('clicked',x2)


mask3 = setdiff_mask(mask1, mask2)

ind_myo = get_index_fromMask(mask3)
set_myo = set(ind_myo)

fig4 = plt.figure()
plt.imshow(img)
plt.plot(x1[0][0], x1[0][1], 'ro')
plt.plot(x2[0][0], x2[0][1], 'bo')

line1 = x1+x2
print(line1)
(line1_xs, line1_ys) = zip(*line1)


fig, axes = plt.subplots(ncols=5, nrows=1, figsize=(12,6))
ax0,ax1,ax2,ax3,ax4 = axes.flat
ax0.imshow(mask_LV, cmap=plt.cm.gray)
ax1.imshow(mask1, cmap=plt.cm.gray)
ax2.imshow(mask2, cmap=plt.cm.gray)
ax3.imshow(mask3, cmap=plt.cm.gray)
ax4.imshow(img)
ax4.add_line(Line2D(line1_xs, line1_ys, linewidth=2, color='red'))

# draw six lines for myocardial segments

zLVc = complex(x1[0][0], x1[0][1])
zRVi = complex(x2[0][0], x2[0][1])


z0 = zRVi - zLVc

nseg = 6

line_list = []
line_list.append(line1)

for ind in range(1, nseg):
	z1 = z0*np.exp(-1j*2*np.pi*ind/nseg)
	zp1 = z1 + zLVc
	xp1 = [(zp1.real, zp1.imag)]
	line_list.append(x1+xp1)



print(line_list)
print(line_list[0])
print(line_list[1])



sys.exit()




mask_myoseg = np.zeros([nx, ny])
line_ref = line_list[nseg-1]
zref_pos = complex(line_ref[1][0], line_ref[1][1])
zref = zref_pos - zLVc

for j in set_myo:

	zvox_pos = complex(j%ny, int(j/ny))
	zvox = zvox_pos - zLVc
	angle = cmath.phase(zref/zvox)*180/np.pi  # in degree. I did zref/zvox to correct the segment order
	if angle < 0:
		angle += 360

	if angle > 0 and angle < 60:
		mask_myoseg[int(j/ny), j%ny] = 1.0
	elif angle > 60 and angle < 120:
		mask_myoseg[int(j/ny), j%ny] = 2.0
	elif angle > 120 and angle < 180:
		mask_myoseg[int(j/ny), j%ny] = 3.0
	elif angle > 180 and angle < 240:
		mask_myoseg[int(j/ny), j%ny] = 4.0
	elif angle > 240 and angle < 300:
		mask_myoseg[int(j/ny), j%ny] = 5.0
	else:
		mask_myoseg[int(j/ny), j%ny] = 6.0


fig5, axes = plt.subplots(ncols=3, nrows=1)
ax0,ax1,ax2 = axes.flat
ax0.imshow(img)
ax1.imshow(img, cmap=plt.cm.gray)
for ind in range(0, nseg):
	line2 = line_list[ind]
	(line2_xs, line2_ys) = zip(*line2)
	ax1.add_line(Line2D(line2_xs, line2_ys, linewidth=1, color='blue'))
ax2.imshow(mask_myoseg, cmap=plt.cm.jet)



mask_myoseg_ = mask_myoseg.reshape((nx*ny, 1))
sig_myo = np.zeros((nseg, nframe))
for ind_seg in range(0, nseg):
	ind = np.where(mask_myoseg_ == ind_seg+1)
	index = ind[0]
	s1 = set(index)
	for t in range(0, nframe):
		for j in s1:
			sig_myo[ind_seg,t] += imgt[int(j/ny), j%ny, t, ]
		sig_myo[ind_seg, t] = sig_myo[ind_seg, t]/len(s1)


print('moving average filtering of sig_myo')
sig_myo_filt = np.zeros((nseg, nframe))
for ind_seg in range(0, nseg):
	sig_myo_filt[ind_seg,:] = medfilt(sig_myo[ind_seg,:], 7)




print('Now calculate up-slope')
print('Estimate slope of LV blood')
framest_LV = int(input("Enter LV slope start frame no. : "))
frameed_LV = int(input("Enter LV slope end frame no. : "))

print('Estimate slope of myocardial signal')
framest_myo = int(input("Enter myo slope start frame no. : "))
frameed_myo = int(input("Enter myo slope end frame no. : "))

xLV = range(framest_LV, frameed_LV)
yLV = sig_LV[xLV]
print(xLV)
print(yLV)
fit = np.polyfit(xLV, yLV, 1)
fit_fn_LV = np.poly1d(fit)
slope_LV = fit[0]

xmyo = range(framest_myo, frameed_myo)
ymyo = np.zeros((nseg, len(xmyo)))
for ind_seg in range(0,nseg):
	ymyo[ind_seg,:] = sig_myo[ind_seg,xmyo]





slope_myo = np.zeros(nseg)
upslope = np.zeros(nseg)



fig6 = plt.figure()
for ind_seg in range(0,nseg):

	fit2 = np.polyfit(xmyo, ymyo[ind_seg,:], 1)
	fit2_fn_myo = np.poly1d(fit2)
	slope_myo[ind_seg] = fit2[0]
	upslope[ind_seg] = slope_myo[ind_seg]/slope_LV

	ax = fig6.add_subplot(2,3,ind_seg+1)
	ax.plot(range(0, nframe), sig_LV, c='r')
	ax.plot(xLV, fit_fn_LV(xLV), c='k')

	ax.plot(range(0, nframe), sig_myo[ind_seg, :], c='b')
	ax.plot(range(0, nframe), sig_myo_filt[ind_seg,:], c='g')
	ax.plot(xmyo, fit2_fn_myo(xmyo), c='k')

	ax.set_title('time intensity curve')
	ax.text(50, 500, 'upslope = %5.3f' % upslope[ind_seg], fontsize=10, color='green')

print(upslope)


# ax1.imshow(img, cmap=plt.cm.gray)
# for ind in range(0, nseg):
# 	line2 = line_list[ind]
# 	(line2_xs, line2_ys) = zip(*line2)
# 	ax1.add_line(Line2D(line2_xs, line2_ys, linewidth=1, color='blue'))




plt.show()



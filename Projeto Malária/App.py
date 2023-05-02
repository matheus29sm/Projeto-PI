import matplotlib.pyplot as plt
from skimage import io
from skimage import color
from skimage.filters import sobel
from skimage.draw import circle_perimeter
from skimage.morphology import *
from skimage.transform import hough_circle_peaks, hough_circle
from skimage.exposure import equalize_hist
import numpy as np
import cv2
import sys

imagem = io.imread("0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png")
red_img = imagem [:, :, 0]
green_img = imagem [:, :, 1]
blue_img = imagem [:, :, 2]

print(red_img)

print(green_img)

print(blue_img)

_,ax = plt.subplots (1,2)
ax[0].imshow (red_img,cmap='gray',vmin=0,vmax=255)
ax[1].imshow (green_img,cmap='gray',vmin=0,vmax=255)
_,ax = plt.subplots (1,2)
ax[0].imshow (green_img,cmap='gray',vmin=0,vmax=255)
ax[1].imshow (blue_img,cmap='gray',vmin=0,vmax=255)
_,ax = plt.subplots (1,2)
ax[0].imshow (red_img,cmap='gray',vmin=0,vmax=255)
ax[1].imshow (blue_img,cmap='gray',vmin=0,vmax=255)

binaria = blue_img.copy()
limiar = imagem.max() * (110 / 256)
binaria [binaria <= limiar] = 0
binaria [binaria > 0] = 1

print(binaria * 255)

binary = binary_opening (binaria)
binary = binary_closing (binaria)

print(binary)

edges = sobel(binary)
print(edges)

raios = np.arange(40, 50, 2)
hough_grade = hough_circle (edges, raios)

acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,total_num_peaks = 150)
fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(20, 8))
image = color.gray2rgb(blue_img)

for center_y, center_x, radius in zip(b, a, raio):
    circy, circx = circle_perimeter(center_y, center_x, radius, shape = image.shape)
    image[circy, circx] = (220, 20, 20)

ax.imshow(image, cmap=plt.cm.gray)
print(len(a))
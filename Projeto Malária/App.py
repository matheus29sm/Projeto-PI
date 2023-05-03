import matplotlib.pyplot as plt

from skimage import io
from skimage import color
from skimage.filters import sobel
from scipy.spatial.distance import cdist
from skimage.draw import circle_perimeter
from skimage.morphology import *
from skimage.transform import hough_circle_peaks, hough_circle
from skimage.exposure import equalize_hist
import numpy as np
import cv2
import sys


# imagem = cv2.imread(r'C:\Users\macel\Downloads\malaria\0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png')
# imagem = io.imread (r'C:\Users\mathe\Projeto-PI\Projeto Malária\malaria\images\0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png') // esse funciona
imagem = io.imread('./malaria/images/0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png')
canais = cv2.split(imagem)


red_img = canais[2]
green_img = canais [1]
blue_img = canais [0]

binaria = red_img.copy()
limiar = imagem.max() * (110 / 256)
binaria [binaria <= limiar] = 0
binaria [binaria > 0] = 1

binary = binary_opening (binaria)
binary = binary_closing (binaria)

edges = sobel(binary)

raios = np.arange(30, 45, 2)
hough_grade = hough_circle (edges, raios)

acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,total_num_peaks = 200)


fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(20, 8))
image = color.gray2rgb(red_img)

centers = []  # armazena os centros dos círculos já desenhados
min_dist = 20  # distância mínima desejada entre os centros dos círculos

for center_y, center_x, radius in zip(b, a, raio):
    # verifica se o centro atual está próximo demais de um círculo já desenhado
    is_close = False
    for c in centers:
        dist = np.sqrt((center_y - c[0])**2 + (center_x - c[1])**2)
        if dist < min_dist:
            is_close = True
            break
    if not is_close:
        circy, circx = circle_perimeter(center_y, center_x, radius, shape=image.shape)
        image[circy, circx] = (220, 20, 20)
        centers.append((center_y, center_x))

ax.imshow(image, cmap=plt.cm.gray)

num_circles = np.sum(~np.isnan(centers))
print(len(centers))

# for center_y, center_x, radius in zip(b, a, raio):
#     circy, circx = circle_perimeter(center_y, center_x, radius, shape = image.shape)
#     image[circy, circx] = (200, 20, 20)

# ax.imshow(image, cmap=plt.cm.gray)


if imagem is None:
    print('Não foi possível carregar a imagem')
else:
    cv2.imshow('Imagem', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# if imagem is None:
#     print('Não foi possível carregar a imagem')
# else:
#     cv2.imshow('Imagem', canais[1])
#     print(canais[1].shape)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

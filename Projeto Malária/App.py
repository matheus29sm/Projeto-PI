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
import os

#Descomente o diretorio que funciona com voce

#imagem = cv2.imread(r'C:\Users\macel\OneDrive\Área de Trabalho\Projetos\PI\Projeto Malaria\Projeto-PI\Projeto Malária\malaria\Example\0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png')
imagem = io.imread (r'C:\Users\macel\OneDrive\Área de Trabalho\Projetos\PI\Projeto Malaria\Projeto-PI\Projeto Malária\malaria\Example\0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png')
#imagem = io.imread('./malaria/images/0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png')
#imagem = io.imread(r'C:\Users\macel\OneDrive\Área de Trabalho\Projetos\PI\Projeto Malaria\Projeto-PI\Projeto Malária\malaria\Example\8d02117d-6c71-4e47-b50a-6cc8d5eb1d55.png')


canal = cv2.split(imagem)

blue_img = canal [0]

binaria = blue_img.copy()
limiar = imagem.max() * (110 / 256)
binaria [binaria <= limiar] = 0
binaria [binaria > 0] = 255

binary = binary_opening (binaria)
binary = binary_closing (binaria)

edges = sobel(binary)


raios = np.arange(42, 48, 2)
hough_grade = hough_circle (edges, raios)

acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 300)


fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(20, 8))
image = color.gray2rgb(blue_img)

centros = []  # armazena os centros dos círculos já desenhados
# min_dist = 30  # distância mínima desejada entre os centros dos círculos

for centro_y, centro_x, radius in zip(b, a, raio):
    # verifica se o centro atual está próximo demais de um círculo já desenhado
    is_close = False
    for c in centros:
        dist = np.sqrt((centro_y - c[0])**2 + (centro_x - c[1])**2)
        #  if dist < min_dist:
        #     is_close = True
        #     break
    if not is_close:
        circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
        image[circy, circx] = (20, 20, 220) #BGR
        centros.append((centro_y, centro_x))


num_circles = np.sum(~np.isnan(centros))
print(len(centros))

# for centro_y, centro_x, radius in zip(b, a, raio):
#     circy, circx = circle_perimeter(centro_y, centro_x, radius, shape = image.shape)
#     image[circy, circx] = (200, 20, 20)

# ax.imshow(image, cmap=plt.cm.gray)

# if imagem is None:
#     print('Não foi possível carregar a imagem')
# else:
#     fig, ax = plt.subplots(1,2, figsize=(30,20))
#     ax[0].axis("off")
#     ax[0].imshow(edges2)
#     ax[1].axis("off")
#     ax[1].imshow(edges)
#     # ax[2].axis("off")
#     # ax[2].imshow(edges2)
#     plt.show()

if imagem is None:
    print('Não foi possível carregar a imagem')
else:
    cv2.imshow('Imagem', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# if imagem is None:
#     print('Não foi possível carregar a imagem')
# else:
#     cv2.imshow('Imagem', edges2)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
    
# if imagem is None:
#     print('Não foi possível carregar a imagem')
# else:
#     cv2.imshow('Imagem', canais[1])
#     print(canais[1].shape)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
# pasta = r'Projeto-PI\Projeto Malária\malaria\images'
# def get_image_paths(pasta):
#     """
#     Retorna uma lista com os caminhos das imagens na pasta especificada.
#     """
#     image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']  # Adicione outras extensões de imagem, se necessário
#     image_paths = []
#     for filename in os.listdir(pasta):
#         if any(filename.lower().endswith(ext) for ext in image_extensions):
#             image_paths.append(os.path.join(pasta, filename))
#     return image_paths
# imagens = get_image_paths(pasta)

# for img in imagens:
#     if img is None:
#         print('Não foi possível carregar a imagem')
#     else:
#         img = io.imread(img)
#         cv2.imshow('Imagem', img)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()
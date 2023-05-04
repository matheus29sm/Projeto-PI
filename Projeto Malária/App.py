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

def pegar_caminho_imagens(pasta):
    """
    Retorna uma lista com os caminhos das imagens na pasta especificada.
    """
    tipos_imagens = ['.jpg', '.jpeg', '.png', '.bmp']  # Adicione outras extensões de imagem, se necessário
    caminho_imagens = []
    for arquivo in os.listdir(pasta):
        if any(arquivo.lower().endswith(ext) for ext in tipos_imagens):
            caminho_imagens.append(os.path.join(pasta, arquivo))
    return caminho_imagens

# descomente o de cima apenas se o de baixo não funcionar 
# para o professor testar era uma boa o de baixo.

# pasta = r'Projeto-PI\Projeto Malária\malaria\images'
# pasta = 'Projeto-PI/Projeto Malária/malaria/images' # o seu tem que analisar e dx igual 
pasta = 'Projeto Malária/malaria/images' # o meu

imagens = pegar_caminho_imagens(pasta)

for img in imagens:
    if img is None:
        print('Não foi possível carregar a imagem')
    else:
        img = io.imread(img)
        canal = cv2.split(img)

        blue_img = canal [0]

        binaria = blue_img.copy()
        limiar = img.max() * (110 / 256)
        binaria [binaria <= limiar] = 0
        binaria [binaria > 0] = 255

        binary = binary_opening (binaria)
        binary = binary_closing (binaria)

        edges = sobel(binary)


        raios = np.arange(42, 48, 2)
        hough_grade = hough_circle (edges, raios)

        acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 300)

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
        # cv2.imshow('Imagem',canal[2])
        cv2.imshow('Imagem', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # fig, ax = plt.subplots(1,2, figsize=(24,12))
        # ax[0].axis("off")
        # ax[0].imshow(img)
        # ax[1].axis("off")
        # ax[1].imshow(canal[0])
        # plt.show()


# -- Teste imagem unica --  
 
#Descomente o diretorio que funciona com voce
# Tava os errados corrigi agora 

# imagem = cv2.imread(r'C:\Users\macel\OneDrive\Área de Trabalho\Projetos\PI\Projeto Malaria\Projeto-PI\Projeto Malária\malaria\Example\0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png')
# imagem = io.imread (r'C:\Users\macel\OneDrive\Área de Trabalho\Projetos\PI\Projeto Malaria\Projeto-PI\Projeto Malária\malaria\Example\0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png')
# imagem = io.imread(r'C:\Users\mathe\Projeto-PI\Projeto Malária\malaria\Example\0ac747cd-ff32-49bf-bc1a-3e9b7702ce9c.png')

# canal = cv2.split(imagem) # analisar a de saturação 


# blue_img = canal [0]

# binaria = blue_img.copy()
# limiar = imagem.max() * (110 / 256)
# binaria [binaria <= limiar] = 0
# binaria [binaria > 0] = 255

# binary = binary_opening (binaria)
# binary = binary_closing (binaria)

# edges = sobel(binary)


# raios = np.arange(42, 48, 2)
# hough_grade = hough_circle (edges, raios)

# acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 300)


# fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(20, 8))
# image = color.gray2rgb(blue_img)

# centros = []  # armazena os centros dos círculos já desenhados
# # min_dist = 30  # distância mínima desejada entre os centros dos círculos

# for centro_y, centro_x, radius in zip(b, a, raio):
#     # verifica se o centro atual está próximo demais de um círculo já desenhado
#     is_close = False
#     for c in centros:
#         dist = np.sqrt((centro_y - c[0])**2 + (centro_x - c[1])**2)
#         #  if dist < min_dist:
#         #     is_close = True
#         #     break
#     if not is_close:
#         circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
#         image[circy, circx] = (20, 20, 220) #BGR
#         centros.append((centro_y, centro_x))


# num_circles = np.sum(~np.isnan(centros))
# print(len(centros))

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

# if imagem is None:
#     print('Não foi possível carregar a imagem')
# else:
#     cv2.imshow('Imagem', image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

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
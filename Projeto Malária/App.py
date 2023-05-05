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

# for img in imagens:
#     if img is None:
#         print('Não foi possível carregar a imagem')
#     else:
#         img = io.imread(img)
#         canal = cv2.split(img)

#         blue_img = canal[1]  # teste no canal de saturação

#         binaria = blue_img.copy()
#         limiar = img.max() * (110 / 256)
#         binaria [binaria <= limiar] = 0
#         binaria [binaria > 0] = 255

#         # binary = binary_opening (binaria)
#         # binary = binary_closing (binaria)

#         edges = sobel(binaria)

#         # edges = binary_fillholes(edges)


#         raios = np.arange(42, 60, 2)
#         hough_grade = hough_circle (edges, raios)

#         acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 100)

#         image = color.gray2rgb(edges)

#         centros = []  # armazena os centros dos círculos já desenhados
#         # min_dist = 30  # distância mínima desejada entre os centros dos círculos

#         for centro_y, centro_x, radius in zip(b, a, raio):
#             # verifica se o centro atual está próximo demais de um círculo já desenhado
#             is_close = False
#             for c in centros:
#                 dist = np.sqrt((centro_y - c[0])**2 + (centro_x - c[1])**2)
#                 #  if dist < min_dist:
#                 #     is_close = True
#                 #     break
#             if not is_close:
#                 circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
#                 image[circy, circx] = (20, 20, 220) #BGR
#                 centros.append((centro_y, centro_x))


#         # image = img
#         num_circles = np.sum(~np.isnan(centros))
#         print(len(centros))
#         # cv2.imshow('Imagem',canal[2])
#         cv2.imshow('Imagem', image)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()
#         # fig, ax = plt.subplots(1,2, figsize=(24,12))
#         # ax[0].axis("off")
#         # ax[0].imshow(img)
#         # ax[1].axis("off")
#         # ax[1].imshow(canal[0])
#         # plt.show()

new = 'Projeto Malária/malaria/new.json' # ideia e pesquisar os links no arquivo e ver se acha 

import json

# abre o arquivo JSON
with open(new) as arquivo:
    # lê todo o arquivo e converte para um objeto Python
    objeto_python = json.load(arquivo)

cont = 0
for img in imagens:
    # procurando uma string em um dicionário dentro do objeto Python
    procurar_string = img[31:]
    for item in objeto_python:
        if procurar_string in item['image']['pathname']:
            print("A string '{}' foi encontrada no arquivo JSON!".format(procurar_string),cont)
            # print(item['objects']['bounding_box']['category'] != "red blood cell") #pega os bouding box // ta errado
            break
        else:
            # print("A string '{}' não foi encontrada no arquivo JSON.".format(procurar_string))
            # print(item['image']['pathname'],cont)
            # print(procurar_string)
            cont += 1


# # define objeto_python fora do bloco with
# objeto_python = None

# # abre o arquivo JSON
# # with open(new) as arquivo:
# #     # lê cada linha do arquivo e trata como um objeto JSON
# #     for linha in arquivo:
# #         try:
# #             objeto_python = json.loads(linha)
# #             # fazer algo com o objeto Python aqui
# #         except json.JSONDecodeError:
# #             # lidar com linhas inválidas ou vazias, se necessário
# #             pass

# # abre o arquivo JSON
# with open(new) as arquivo:
#     # carrega o conteúdo do arquivo JSON em um objeto Python
#     objeto_python = json.load(arquivo)

# for img in imagens:
#     # procurando uma string em um dicionário dentro do objeto Python
#     procurar_string = img[23:]
#     if procurar_string in objeto_python["image"].values():
#         print("A string '{}' foi encontrada no arquivo JSON!".format(procurar_string))
#     else:
#         print("A string '{}' não foi encontrada no arquivo JSON!".format(procurar_string))

# 23
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
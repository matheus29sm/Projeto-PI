import matplotlib.pyplot as plt
import skimage.filters as skifil
from skimage import io
from skimage import color
from skimage.filters import sobel
from skimage.draw import circle_perimeter
from skimage.morphology import *
from skimage.transform import hough_circle_peaks, hough_circle
from skimage.exposure import equalize_hist
from skimage.measure import label, regionprops
import numpy as np
import cv2
import os
import json


def pegar_caminho_imagens(pasta):
    """
    Retorna uma lista com os caminhos das imagens na pasta especificada.
    """
    tipos_imagens = ['.jpg', '.jpeg', '.png', '.bmp']
    caminho_imagens = []
    for arquivo in os.listdir(pasta):
        if any(arquivo.lower().endswith(ext) for ext in tipos_imagens):
            caminho_imagens.append(os.path.join(pasta, arquivo))
    return caminho_imagens


pasta = 'Projeto_Malaria/malaria/images' 
arquivo_json = 'Projeto_Malaria/malaria/training.json' # ideia e pesquisar no arquivo e ver se acha 

imagens = pegar_caminho_imagens(pasta)

# abre o arquivo JSON
with open(arquivo_json) as arquivo:
    # lê todo o arquivo e converte para um objeto Python
    objeto_python = json.load(arquivo)

cont = 0
i = 0
quant_box = 0
for img in imagens:
    if img is None:
        print('Não foi possível carregar a imagem')
    else:
        # procurando uma string em um dicionário dentro do objeto Python
        procurar_img = img[31:]
        i +=1
        for item in objeto_python:
            if procurar_img in item['image']['pathname']:
                print("'{}' foi encontrada no arquivo JSON!".format(procurar_img),cont ,i)
                objetos = item['objects']
                print("objetos -> '{}'".format(len(objetos)))
                quant_box = len(objetos)
                for objeto in objetos:
                    # if "bounding_box" in objeto:
                        if "category" in objeto:
                            if objeto["category"] != "red blood cell":
                                print(objeto["category"])
                        else:
                            print("Objeto não tem categoria definida.")
                    # else:
                    #     print("Objeto não tem caixa delimitadora (bounding box) definida.")
                break
            else:
                cont += 1

        img = io.imread(img)
        canais = cv2.split(img)
        saturation = canais [1]

        thresh = skifil.threshold_otsu(saturation)
        
        binaria = saturation > thresh

        # Rotular os objetos conectados na imagem binária
        label_img = label(binaria)

        # Extrair as propriedades dos objetos, incluindo sua área
        props = regionprops(label_img)

        # Filtrar os objetos por área para manter apenas as células
        min_area = 50  # definir a área mínima para manter
        # cells = []
        # for prop in props:
        #     if prop.area >= min_area:
        #         cells.append(prop)
        mascara = np.logical_and(saturation > thresh, label_img > 0)

        edges = sobel(saturation)


        mascara = edges * mascara
        
        elem_estrut_dilat = disk(3)
        elem_estrut_eros = disk (5)

        img_dilatada = dilation(mascara, elem_estrut_dilat)
        img_erodida = erosion(img_dilatada, elem_estrut_eros)

        img_equazada = equalize_hist(img_erodida)

        img_de_sobel = sobel(img_equazada)

        img_de_sobel [img_de_sobel < 0.3] = 0
        img_de_sobel [img_de_sobel >= 0.05] = 1
        
        raios = np.arange(42, 60, 2)
        hough_grade = hough_circle (img_de_sobel, raios)

        acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 150)

        image = color.gray2rgb(saturation)

        centros = []  # armazena os centros dos círculos já desenhados

        for centro_y, centro_x, radius in zip(b, a, raio):
            # verifica se o centro atual está próximo demais de um círculo já desenhado
            is_close = False
            for c in centros:
                dist = np.sqrt((centro_y - c[0])**2 + (centro_x - c[1])**2)

            if not is_close:
                circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
                image[circy, circx] = (20, 20, 220) #BGR

            if not is_close:
               # Extrai uma região quadrada em torno do centro
                tamanho_regiao = 30
                regiao = image[centro_y - tamanho_regiao:centro_y + tamanho_regiao,
                               centro_x - tamanho_regiao:centro_x + tamanho_regiao]

                # Calcula a média dos valores de pixel da região
                media_pixel = np.mean(regiao)

                if media_pixel < 200:  # Ajuste o limite conforme necessário
                    # A região possui uma média de pixel alta, considerada como branca
                    circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
                    image[circy, circx] = (20, 220, 20)  # BGR
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
# imagem = io.imread(r'C:\Users\mathe\Projeto-PI\Projeto_Malaria\malaria\Images\0d2aba33-6920-4001-bd54-59fe0bf9f50e.png')

# canais = cv2.split(imagem) # analisar a de saturação 
# saturation = canais [1]
# thresh = skifil.threshold_otsu(saturation)

# binaria = saturation > thresh
# # Rotular os objetos conectados na imagem binária
# label_img = label(binaria)
# # Extrair as propriedades dos objetos, incluindo sua área
# props = regionprops(label_img)
# # Filtrar os objetos por área para manter apenas as células
# min_area = 50  # definir a área mínima para manter
# # cells = []
# # for prop in props:
# #     if prop.area >= min_area:
# #         cells.append(prop)
# mascara = np.logical_and(saturation > thresh, label_img > 0)
# edges = sobel(saturation)
# mascara = edges * mascara

# elem_estrut_dilat = disk(3)
# elem_estrut_eros = disk (5)
# # img_dilatada = dilation(mascara, elem_estrut_dilat)
# # img_erodida = erosion(img_dilatada, elem_estrut_eros)
# img_equazada = equalize_hist(mascara)
# img_de_sobel = sobel(mascara)
# # img_de_sobel [img_de_sobel < 0.3] = 0
# # img_de_sobel [img_de_sobel >= 0.3] = 1

# # img_de_sobel = 1 - img_de_sobel
# # img_de_sobel [img_de_sobel >= 0.95] = 0

# raios = np.arange(42, 60, 2)
# hough_grade = hough_circle (img_de_sobel, raios)
# acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 150)
# image = color.gray2rgb(saturation)
# centros = []  # armazena os centros dos círculos já desenhados


# # buee_img = canais [1]
# # binaria = blue_img.copy()
# # limiar = imagem.max() * (110 / 256)
# # binaria [binaria <= limiar] = 0
# # binaria [binaria > 0] = 255

# # binary = binary_opening (binaria)
# # binary = binary_closing (binaria)

# # edges = sobel(binary)


# # raios = np.arange(42, 48, 2)
# # hough_grade = hough_circle (edges, raios)

# # acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 300)


# # fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(20, 8))
# # image = color.gray2rgb(blue_img)

# # centros = []  # armazena os centros dos círculos já desenhados
# # # min_dist = 30  # distância mínima desejada entre os centros dos círculos

# for centro_y, centro_x, radius in zip(b, a, raio):
#     # verifica se o centro atual está próximo demais de um círculo já desenhado
#     is_close = False
#     for c in centros:
#         dist = np.sqrt((centro_y - c[0])**2 + (centro_x - c[1])**2)
#         #  if dist < min_dist:
#         #     is_close = True
#         #     break
#     if not is_close:
#            # Extrai uma região quadrada em torno do centro
#         tamanho_regiao = 30
#         regiao = image[centro_y - tamanho_regiao:centro_y + tamanho_regiao,
#                        centro_x - tamanho_regiao:centro_x + tamanho_regiao]
#         # Calcula a média dos valores de pixel da região
#         media_pixel = np.mean(regiao)
#         if media_pixel < 200:  # Ajuste o limite conforme necessário
#             # A região possui uma média de pixel alta, considerada como branca
#             circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
#             image[circy, circx] = (20, 220, 20)  # BGR
#             centros.append((centro_y, centro_x))


# num_circles = np.sum(~np.isnan(centros))
# print(len(centros))

# # for centro_y, centro_x, radius in zip(b, a, raio):
# #     circy, circx = circle_perimeter(centro_y, centro_x, radius, shape = image.shape)
# #     image[circy, circx] = (200, 20, 20)

# # ax.imshow(image, cmap=plt.cm.gray)

# if imagem is None:
#     print('Não foi possível carregar a imagem')
# else:
#     cv2.imshow('Imagem', image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# if imagem is None:
#     print('Não foi possível carregar a imagem')
# else:
#     cv2.imshow('Imagem', img_de_sobel)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# # if imagem is None:
# #     print('Não foi possível carregar a imagem')
# # else:
# #     fig, ax = plt.subplots(1,2, figsize=(30,20))
# #     ax[0].axis("off")
# #     ax[0].imshow(edges2)
# #     ax[1].axis("off")
# #     ax[1].imshow(edges)
# #     # ax[2].axis("off")
# #     # ax[2].imshow(edges2)
# #     plt.show()
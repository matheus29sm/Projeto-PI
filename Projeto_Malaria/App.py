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

imagens = pegar_caminho_imagens(pasta)

for img in imagens:
    if img is None:
        print('Não foi possível carregar a imagem')
    else:
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
        cells = []
        for prop in props:
            if prop.area >= min_area:
                cells.append(prop)
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
        img_de_sobel [img_de_sobel >= 0.3] = 1

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

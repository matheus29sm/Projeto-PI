
from matplotlib.patches import Rectangle
from skimage import io
from skimage import color
from skimage.filters import sobel
from skimage.draw import circle_perimeter
from skimage.morphology import *
from skimage.transform import hough_circle_peaks, hough_circle
from skimage.exposure import equalize_hist
from skimage.measure import label
import skimage.filters as skifil
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
import json



def pegar_caminho_imagens(pasta):
    # Retorna uma lista com os caminhos das imagens na pasta especificada.
    tipos_imagens = ['.jpg', '.jpeg', '.png', '.bmp']
    caminho_imagens = []
    for arquivo in os.listdir(pasta):
        if any(arquivo.lower().endswith(ext) for ext in tipos_imagens):
            caminho_imagens.append(os.path.join(pasta, arquivo))
    return caminho_imagens


pasta = 'Projeto_Malaria/malaria/images' 
arquivo_json = 'Projeto_Malaria/malaria/training.json'  

imagens = pegar_caminho_imagens(pasta)

# Abre o arquivo JSON
with open(arquivo_json) as arquivo:
    # Lê todo o arquivo e converte para um objeto Python
    objeto_python = json.load(arquivo)

cont = 0
i = 0
quant_box = 0
for img in imagens:
    if img is None:
        print('Não foi possível carregar a imagem')
    else:
        # Procurando uma string em um dicionário dentro do objeto Python
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

        mascara = np.logical_and(saturation > thresh, label_img > 0)
        edges = sobel(saturation)
        mascara = edges * mascara
        
        elem_estrut_dilat = disk(3)
        elem_estrut_eros = disk (5)

        img_dilatada = dilation(mascara, elem_estrut_dilat)
        img_erodida = erosion(img_dilatada, elem_estrut_eros)

        img_equalizada = equalize_hist(img_erodida)

        img_de_sobel = sobel(img_equalizada)

        img_de_sobel [img_de_sobel < 0.3] = 0
        img_de_sobel [img_de_sobel >= 0.3] = 1
        
        
        raios = np.arange(42, 60, 2)
        hough_grade = hough_circle (img_de_sobel, raios)

        acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 150)

        image = color.gray2rgb(saturation)
        image_copy = np.copy(image)

        # Armazena os centros dos círculos já desenhados
        centros = []

        bounding_boxes = []

        for centro_y, centro_x, radius in zip(b, a, raio):
            # Verifica se o centro atual está próximo de um círculo já desenhado
            is_close = False
            for c in centros:
                dist = np.sqrt((centro_y - c[0])**2 + (centro_x - c[1])**2)

            if not is_close:
                circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
                image[circy, circx] = (20, 20, 220) #BGR

            if not is_close:
               # Define as coordenadas mínimas e máximas para a região quadrada
                tamanho_regiao = 30
                min_y = max(0, centro_y - tamanho_regiao)
                max_y = min(image.shape[0], centro_y + tamanho_regiao)
                min_x = max(0, centro_x - tamanho_regiao)
                max_x = min(image.shape[1], centro_x + tamanho_regiao)

                # Extrai a região quadrada em torno do centro
                regiao = image[min_y:max_y, min_x:max_x]

                # Calcula a média dos valores de pixel da região
                media_pixel = np.mean(regiao)

                if media_pixel < 200:
                    # A região possui uma média de pixel alta, considerada como branca
                    circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
                    image[circy, circx] = (20, 220, 20)  # BGR
                    centros.append((centro_y, centro_x))

                    # Calcular as coordenadas mínimas e máximas da bounding box
                    minimum = {'r': int(max(0, centro_y - radius)), 'c': int(max(0, centro_x - radius))}
                    maximum = {'r': int(centro_y + radius), 'c': int(centro_x + radius)}
                
                    # Armazenar as coordenadas mínimas e máximas em um dicionário
                    bounding_box = {'minimum': minimum, 'maximum': maximum}
                
                    # Adicionar o dicionário à lista de bounding boxes
                    bounding_boxes.append(bounding_box)                    

                    # Desenhe as bounding boxes na imagem copiada
                    
                    # for bbox in bounding_boxes:
                    #     minimum = bbox['minimum']
                    #     maximum = bbox['maximum']
                    #     min_row, min_col = minimum['r'], minimum['c']
                    #     max_row, max_col = maximum['r'], maximum['c']

                    #     # Desenhe a bounding box na imagem copiada
                    #     cv2.rectangle(image_copy, (min_col, min_row), (max_col, max_row), (0, 255, 0), 2)

        num_circles = np.sum(~np.isnan(centros))
        print(len(centros))
        # for box in bounding_boxes:
        #     print(box)
        
        # cv2.imshow('Imagem', image)
        # cv2.imshow('Imagem',image_copy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # fig, ax = plt.subplots(1,2, figsize=(24,12))
        # ax[0].axis("off")
        # ax[0].imshow(image)
        # ax[1].axis("off")
        # ax[1].imshow(rect)
        # plt.show()


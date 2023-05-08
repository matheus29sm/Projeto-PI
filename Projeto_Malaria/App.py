from skimage import io
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

# Função para calcular a área de uma bounding-box
def bbox_area(bbox):
    # Adicionamos + 1 a cada diferença para considerar que a bbox inclui tanto as coordenadas mínimas quanto as máximas.
    return (bbox['maximum']['r'] - bbox['minimum']['r'] + 1) * (bbox['maximum']['c'] - bbox['minimum']['c'] + 1)

# Função para calcular o IoU entre as duas bounding-box
def bbox_iou(bbox1, bbox2):
    # Calcula a intersecção entre as duas bounding-box
    xA = max(bbox1['minimum']['c'], bbox2['minimum']['c'])
    yA = max(bbox1['minimum']['r'], bbox2['minimum']['r'])
    xB = min(bbox1['maximum']['c'], bbox2['maximum']['c'])
    yB = min(bbox1['maximum']['r'], bbox2['maximum']['r'])

    # Calcula a área de intersecção e união das duas bbox
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    unionArea = bbox_area(bbox1) + bbox_area(bbox2) - interArea

    # Calcula o valor de IoU
    iou = interArea / unionArea

    return iou

# Função para comparar as bounding-box e retornar a Precision, Recall e F1 score
def comparar_bounding_boxes(bboxes_obtidas, bboxes_base):
    if len(bboxes_obtidas) != 0:
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        for bbox_obtida in bboxes_obtidas:
            bbox_correpondente = False
            for bbox_base in bboxes_base:
                # # Calculando o IoU entre as bbox
                iou = bbox_iou(bbox_base, bbox_obtida)
                # Verifica se o limiar e superior a 50% 
                if iou >= 0.5:
                    # print("IoU: {:.2f}%".format(iou*100))
                    true_positives += 1
                    bbox_correpondente = True
                    break
            if not bbox_correpondente:
                false_positives += 1

        false_negatives = len(bboxes_base) - true_positives

        P = true_positives / (true_positives + false_positives)
        R = true_positives / (true_positives + false_negatives)
        F1 = 2 * (P * R) / (P + R)

        # Retornando a Precision, Recall e F1 score obtidas.
        return P, R, F1
    else:
        return 0, 0, 0


pasta = 'Projeto_Malaria/malaria/images' 
arquivo_json = 'Projeto_Malaria/malaria/training.json'  

imagens = pegar_caminho_imagens(pasta)

# Abre o arquivo JSON
with open(arquivo_json) as arquivo:
    # Lê todo o arquivo e converte para um objeto Python
    objeto_python = json.load(arquivo)

for img in imagens:
    if img is None:
        print('Não foi possível carregar a imagem')
    else:
        # Procurando uma string em um dicionário dentro do objeto Python
        procurar_img = img[31:]
        for item in objeto_python:
            if procurar_img in item['image']['pathname']:
                # print("'{}' foi encontrada no arquivo JSON!".format(procurar_img) ,i)
                objetos = item['objects']
                bboxes_base = []
                # print("objetos -> '{}'".format(len(objetos)))
                for objeto in objetos:
                    if "bounding_box" in objeto:
                        bbox = objeto['bounding_box']
                        # # Calcular as coordenadas mínimas e máximas da bounding box
                        minimum = {'r': int(bbox['minimum']['r']), 'c': int(bbox['minimum']['c'])}
                        maximum = {'r': int(bbox['maximum']['r']), 'c': int(bbox['maximum']['c'])}

                        # # Armazenar as coordenadas mínimas e máximas em um dicionário
                        bbox = {'minimum': minimum, 'maximum': maximum}

                        # # Adicionar o dicionário à lista de bounding boxes
                        bboxes_base.append(bbox)  
                    else:
                        print("Objeto não tem caixa delimitadora (bounding box) definida.")
        
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

        image = img.copy()

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
                image[circy, circx] = (220, 20, 20) #BGR

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
                    image[circy, circx] = (20, 220, 20)
                    centros.append((centro_y, centro_x))

                    # Calcular as coordenadas mínimas e máximas da bounding box
                    minimum = {'r': int(max(0, centro_y - radius)), 'c': int(max(0, centro_x - radius))}
                    maximum = {'r': int(centro_y + radius), 'c': int(centro_x + radius)}
                
                    # Armazenar as coordenadas mínimas e máximas em um dicionário
                    bounding_box = {'minimum': minimum, 'maximum': maximum}
                
                    # Adicionar o dicionário à lista de bounding boxes
                    bounding_boxes.append(bounding_box)                    

        P, R, F1 = comparar_bounding_boxes(bounding_boxes,bboxes_base)
        print("\n-------------------------")
        print("Imagem: {}".format(procurar_img))
        print("Precision: {:.2f}%".format(P*100))
        print("Recall: {:.2f}%".format(R*100))
        print("F1 score: {:.2f}%".format(F1*100))
        print("-------------------------")
        
        # Para uma melhor visualização dos circulos descomente a exibição com Opencv e comente a do plt
        # image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        # cv2.imshow('Imagem',image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Para deixar exibição dos resultados mais rapida comente a exibição do plt abaixo
        # fig, ax = plt.subplots(1,2, figsize=(24,12))
        # ax[0].axis("off")
        # ax[0].imshow(img)
        # ax[1].axis("off")
        # ax[1].imshow(image)
        # plt.show()

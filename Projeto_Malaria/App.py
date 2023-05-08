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


# Função para pegar o caminho das imagens utilizadas
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
        # verdadeiros positivos
        VP = 0 
        # falsos positivos 
        FP = 0
        # falsos negativos
        FN = 0

        for bbox_obtida in bboxes_obtidas:
            # Variavel de marcação para quando encontrar uma bounding-box correpondente
            bbox_correpondente = False
            for bbox_base in bboxes_base:
                # # Calculando o IoU entre as bbox
                iou = bbox_iou(bbox_base, bbox_obtida)
                # Verifica se o limiar e superior a 50% 
                if iou >= 0.5:
                    # print("IoU: {:.2f}%".format(iou*100))
                    VP += 1
                    bbox_correpondente = True
                    break
            if not bbox_correpondente:
                FP += 1

        FN = len(bboxes_base) - VP

        P = VP / (VP + FP)
        R = VP / (VP + FN)
        F1 = 2 * (P * R) / (P + R)

        # Retornando a Precision, Recall e F1 score obtidas.
        return P, R, F1
    else:
        # Retornando a Precision, Recall e F1 score caso não seja indentificada nenhuma bounding-box obtida com o metodo utilizado
        return 0, 0, 0

# Caminho para pegar as imagens
pasta = 'Projeto_Malaria/malaria/images' 
# Caminho para o arquivo JSON com as bounding-box base
arquivo_json = 'Projeto_Malaria/malaria/training.json'  

# Pega as imagens
imagens = pegar_caminho_imagens(pasta)

# Abertura do arquivo JSON
with open(arquivo_json) as arquivo:
    # Lê todo o arquivo e converte para um objeto Python
    objeto_python = json.load(arquivo)

# Laço para execução do processamento das imagens e exibição da Precision, Recall e F1 score
for img in imagens:
    if img is None:
        print('Não foi possível carregar a imagem')
    else:
        # Pegando apenas o nome da img e seu tipo
        procurar_img = img[31:]
        # Procurando uma string em um dicionário dentro do objeto Python
        for item in objeto_python:
            if procurar_img in item['image']['pathname']:
                objetos = item['objects']
                # Criando a lista para armazenar as bounding-box base
                bboxes_base = []
                for objeto in objetos:
                    if "bounding_box" in objeto:
                        bbox = objeto['bounding_box']
                        # Pega as coordenadas mínimas e máximas da bounding-box base
                        minimum = {'r': int(bbox['minimum']['r']), 'c': int(bbox['minimum']['c'])}
                        maximum = {'r': int(bbox['maximum']['r']), 'c': int(bbox['maximum']['c'])}

                        # Armazenar as coordenadas mínimas e máximas em um dicionário
                        bbox = {'minimum': minimum, 'maximum': maximum}

                        # Adicionar o dicionário à lista de bounding-boxes
                        bboxes_base.append(bbox)  
                    else:
                        print("Objeto não tem caixa delimitadora (bounding box) definida.")
        
        img = io.imread(img)
        # Separação dos canais da imagem 
        canais = cv2.split(img)
        # Utilização do canal de saturação
        saturation = canais [1]

        # calculo do limiar de Otsu da imagem de saturação para separa os pixels em duas classes
        thresh = skifil.threshold_otsu(saturation)
        # Cria uma imagem binária com base no limiar
        binaria = saturation > thresh
        # Rotular os objetos conectados na imagem binária
        label_img = label(binaria)
        # Cria uma máscara com base na saturação acima do limiar e nos objetos rotulados
        mascara = np.logical_and(saturation > thresh, label_img > 0)
        # Aplicação do filtro de Sobel para detectar as bordas 
        edges = sobel(saturation)
        # Aplicação da máscara nas bordas da imagem de saturação
        mascara = edges * mascara
        
        # Cria um elemento estruturante circular para a dilatação
        elem_estrut_dilat = disk(3)
        # Cria um elemento estruturante circular para a erosão
        elem_estrut_eros = disk (5)

        # Aplica a operação de dilatação na máscara
        img_dilatada = dilation(mascara, elem_estrut_dilat)
        # Aplica a operação de erosão na imagem dilatada
        img_erodida = erosion(img_dilatada, elem_estrut_eros)

        # Equaliza o histograma da imagem erodida
        img_equalizada = equalize_hist(img_erodida)
        # Reaplicar o filtro de Sobel para calcula as bordas da imagem equalizada
        img_de_sobel = sobel(img_equalizada)

        # Define uma binarização para melhorar obtenção dos circulos da imagem
        img_de_sobel [img_de_sobel < 0.3] = 0
        img_de_sobel [img_de_sobel >= 0.3] = 1
        
        # Define o tamanho para os raios utilizado no CHT
        raios = np.arange(42, 60, 2)
        # Aplica a função de Hough na imagem
        hough_grade = hough_circle (img_de_sobel, raios)

        # Função para obtenção da grade de acumuladores
        acumulador, a, b, raio = hough_circle_peaks (hough_grade, raios,50, 50,total_num_peaks = 150)

        # Copia da imagem para exibição
        image = img.copy()

        # Lista para armazenar as bounding-box obtidas com o metodo 
        bounding_boxes = []

        for centro_y, centro_x, radius in zip(b, a, raio):
            # Gera circulos em vermelho que são os falsos positivos excluidos
            circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
            image[circy, circx] = (220, 20, 20) 

            # O trecho abaixo e utilizado para pegar uma regiação do circulo e caso ela seja
            # branca o circulo e ocnsiderado falso positivo e não e utilizado na contagem final

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
                # Gera circulos em verde que são os verdadeiros positivos
                circy, circx = circle_perimeter(centro_y, centro_x, radius, shape=image.shape)
                image[circy, circx] = (20, 220, 20)
                
                # Calcular as coordenadas mínimas e máximas da bounding box obtida
                minimum = {'r': int(max(0, centro_y - radius)), 'c': int(max(0, centro_x - radius))}
                maximum = {'r': int(centro_y + radius), 'c': int(centro_x + radius)}
            
                # Armazenar as coordenadas mínimas e máximas em um dicionário
                bounding_box = {'minimum': minimum, 'maximum': maximum}
            
                # Adicionar o dicionário à lista de bounding boxes
                bounding_boxes.append(bounding_box)   

        # Executa a comparação das bouding-boxes obtidase da base e exibe no terminal os resultados                    
        P, R, F1 = comparar_bounding_boxes(bounding_boxes,bboxes_base)
        print("\n-------------------------------------------------")
        print("Imagem: {}".format(procurar_img))
        print("Precision: {:.2f}%".format(P*100))
        print("Recall: {:.2f}%".format(R*100))
        print("F1 score: {:.2f}%".format(F1*100))
        print("-------------------------------------------------")
        
        # Para uma melhor visualização dos circulos descomente a exibição com Opencv e comente a do plt
        # image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        # cv2.imshow('Imagem',image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Para deixar exibição dos resultados mais rapida comente a exibição do plt abaixo
        # fig, ax = plt.subplots(1,2, figsize=(24,12))
        # ax[0].axis("off")
        # ax[0].set_title("Imagem Original")
        # ax[0].imshow(img)
        # ax[1].axis("off")
        # ax[1].set_title("Imagem")
        # ax[1].imshow(image)
        # plt.show()

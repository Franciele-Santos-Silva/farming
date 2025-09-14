import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import time
import sys
import os

CAMINHO_VIDEO = "1751520327557.mp4"
LARGURA = 48
ALTURA = 42
FPS = 10
DURACAO_MAX = 12

CARACTERES_ASCII = " `'.,-~:;+=*!#%@█"  

def contraste_auto(img):
    hist = img.histogram()
    min_cinza = next(i for i, v in enumerate(hist) if v > 0)
    max_cinza = next(i for i in reversed(range(256)) if hist[i] > 0)
    escala = 255 / (max_cinza - min_cinza + 1e-5)
    lut = [max(0, min(255, int((i - min_cinza) * escala))) for i in range(256)]
    return img.point(lut)

def quadro_para_ascii(quadro):
    img = Image.fromarray(quadro).convert("L")
    img = contraste_auto(img)
    img = ImageEnhance.Contrast(img).enhance(2.6)
    img = ImageEnhance.Brightness(img).enhance(1.15)
    borda = img.filter(ImageFilter.FIND_EDGES)
    nitido = img.filter(ImageFilter.SHARPEN)
    img = Image.blend(nitido, borda, 0.5)

    img = img.resize((LARGURA, ALTURA))
    pixels = np.array(img)

    ascii_img = []
    for linha in pixels:
        linha_ascii = ''.join(
            CARACTERES_ASCII[int(p / 256 * len(CARACTERES_ASCII))] * 2 for p in linha
        )
        ascii_img.append(" " + linha_ascii)  
    return '\n'.join(ascii_img)

cap = cv2.VideoCapture(CAMINHO_VIDEO)
video_fps = cap.get(cv2.CAP_PROP_FPS) or 25
intervalo = max(1, int(video_fps // FPS))
total_quadros = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

max_quadros = total_quadros
if DURACAO_MAX:
    max_quadros = min(total_quadros, int(FPS * DURACAO_MAX))

quadros_ascii = []
contador = 0
while cap.isOpened() and len(quadros_ascii) < max_quadros:
    ret, quadro = cap.read()
    if not ret:
        break
    if contador % intervalo == 0:
        quadros_ascii.append(quadro_para_ascii(quadro))
    contador += 1
cap.release()

os.system('cls' if os.name == 'nt' else 'clear')
delay = 1 / FPS

try:
    while True:
        for f in quadros_ascii:
            sys.stdout.write("\033c")
            sys.stdout.write(f + "\n")
            sys.stdout.flush()
            time.sleep(delay)
except KeyboardInterrupt:
    print("\n\033[1;32m Concluído.\033[0m")

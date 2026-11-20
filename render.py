# Funcoes responsaveis por desenhar na tela

import numpy as np
import pygame as pg

from default import *
from calcs import *
# Funcao de teste para desenhar grade na tela
def desenhar_grade(tela):
    for i in range(Nx + 1):
        x = i * TAMANHO_CELULA_X
        pg.draw.line(tela, (60, 60, 60), (x, 0), (x, VERTICAL), 1)
    for j in range(Ny + 1):
        y = VERTICAL - j * TAMANHO_CELULA_Y
        pg.draw.line(tela, (60, 60, 60), (0, y), (HORIZONTAL, y), 1)

# Funcao que desenha vetores para vizualizacao
def desenhar_vetores(tela, u, v, escala=30):
    passo = 4   # subamostra para não poluir
    for i in range(0, Nx, passo):
        for j in range(0, Ny, passo):
            x0, y0 = celula_para_pixel(i, j)
            x1 = int(x0 + u[i, j] * escala)
            y1 = int(y0 - v[i, j] * escala)   # y invertido
            pg.draw.line(tela, (0, 200, 255), (x0, y0), (x1, y1), 1)
            pg.draw.circle(tela, (0, 200, 255), (x1, y1), 2)
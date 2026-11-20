# Funcoes responsaveis por desenhar na tela

import numpy as np
import pygame as pg

from default import *

# Funcao de teste para desenhar grade na tela
def desenhar_grade(tela):
    for i in range(Nx + 1):
        x = i * TAMANHO_CELULA_X
        pg.draw.line(tela, (60, 60, 60), (x, 0), (x, VERTICAL), 1)
    for j in range(Ny + 1):
        y = VERTICAL - j * TAMANHO_CELULA_Y
        pg.draw.line(tela, (60, 60, 60), (0, y), (HORIZONTAL, y), 1)
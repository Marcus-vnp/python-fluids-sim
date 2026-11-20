# FUNCOES RESPONSAVEIS POR CALCULAR TRANSFORMACOES NA SIMULACAO

import numpy as np

from default import *

def criar_grade():
    x = np.arange(Nx) * Dx
    y = np.arange(Ny) * Dy
    X, Y = np.meshgrid(x, y, indexing='ij')
    return X, Y

def celula_para_pixel(i, j):
    x = i * TAMANHO_CELULA_X
    y = VERTICAL - j * TAMANHO_CELULA_Y
    return int(x), int(y)

def pixel_para_celula(x, y):
    i = x / TAMANHO_CELULA_X
    j = (VERTICAL - y) / TAMANHO_CELULA_Y
    return int(i), int(j)

# Fazer funcao de Campo de Rotacao para demosntracao
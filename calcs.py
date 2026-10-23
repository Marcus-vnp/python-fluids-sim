# FUNCOES RESPONSAVEIS POR CALCULAR TRANSFORMACOES NA SIMULACAO

import numpy as np

from default import *

def criar_grade():
    x = np.arange(HORIZONTAL) * Dx
    y = np.arange(VERTICAL) * Dy
    X, Y = np.meshgrid(x, y, indexing='ij')
    return X, Y

# REVISAR ESSAS DUAS FUNCOES
def celula_para_pixel(Xc, Yc):
    return
def pixel_para_celula(Xp, Yp):
    return

# Fazer funcao de Campo de Rotacao para demosntracao
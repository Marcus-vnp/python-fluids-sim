# FUNCOES RESPONSAVEIS POR CALCULAR TRANSFORMACOES NA SIMULACAO

import numpy as np

from default import *

def criar_grade():
    x = np.arange(Nx) * Dx
    y = np.arange(Ny) * Dy
    X, Y = np.meshgrid(x, y, indexing='ij')
    return X, Y

def celula_para_pixel(i, j):
    return round(i * TAMANHO_CELULA_X), VERTICAL - 1 - round(j * TAMANHO_CELULA_Y)


def pixel_para_fisico(x, y):
    """Coordenadas contínuas no domínio fechado, inclusive nos pixels extremos."""
    x = min(max(x, 0), HORIZONTAL - 1)
    y = min(max(y, 0), VERTICAL - 1)
    return x * Dx / TAMANHO_CELULA_X, (VERTICAL - 1 - y) * Dy / TAMANHO_CELULA_Y


def pixel_para_celula(x, y):
    xf, yf = pixel_para_fisico(x, y)
    return round(xf / Dx), round(yf / Dy)

# Fazer funcao de Campo de Rotacao para demosntracao
def campo_horizontal(U0=1.0):
    u = np.full((Nx, Ny), U0)
    v = np.zeros((Nx, Ny))
    return u, v

def campo_rotacao(X, Y, omega=1.0):
    Xc, Yc = X.mean(), Y.mean()
    u = -omega * (Y - Yc)
    v =  omega * (X - Xc)
    return u, v

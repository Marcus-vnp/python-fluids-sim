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


def desenhar_corante(tela, grade_rgb, c):
    # surfarray também usa (x, y). Inverter y alinha a mancha com o mouse.
    valor = 2 * c[:, ::-1] / max(c.max(), 1e-6)
    claro = 255 * np.clip(valor - 1, 0, 1)
    pixels = pg.surfarray.pixels3d(grade_rgb)
    pixels[:, :, 0] = 255 * np.clip(valor, 0, 1)
    pixels[:, :, 1] = claro
    pixels[:, :, 2] = claro * 0.3
    del pixels  # destrava a superfície antes do redimensionamento
    pg.transform.smoothscale(grade_rgb, tela.get_size(), tela)


def desenhar_interacao(tela, cursor, raio, forca):
    if cursor is None:
        return
    pg.draw.circle(tela, (138, 146, 148), cursor, raio, 1)
    intensidade = np.hypot(*forca) / ACELERACAO_MAXIMA
    if intensidade == 0:
        return
    direcao = pg.Vector2(forca[0] * TAMANHO_CELULA_X / Dx,
                         -forca[1] * TAMANHO_CELULA_Y / Dy).normalize()
    ponta = pg.Vector2(cursor) + direcao * (9 + 40 * intensidade)
    cor = (220, 243, 245)
    pg.draw.line(tela, cor, cursor, ponta, 2)
    for angulo in (-28, 28):
        pg.draw.line(tela, cor, ponta, ponta - 7 * direcao.rotate(angulo), 2)

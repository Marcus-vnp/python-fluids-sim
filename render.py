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


def geometria_vetores(u, v, passo):
    """Pontos da haste e das duas asas, já projetados em pixels (N × 5 × 2)."""
    inicio = passo // 2
    amostra = np.s_[inicio::passo, inicio::passo]
    us, vs = u[amostra], v[amostra]
    i, j = np.nonzero(np.hypot(us, vs) > VELOCIDADE_MINIMA)
    origens = np.column_stack((
        (inicio + passo * i) * TAMANHO_CELULA_X,
        VERTICAL - 1 - (inicio + passo * j) * TAMANHO_CELULA_Y,
    ))
    deslocamentos = TEMPO_VISUAL * np.column_stack((
        us[i, j] * TAMANHO_CELULA_X / Dx, -vs[i, j] * TAMANHO_CELULA_Y / Dy,
    ))
    comprimentos = np.hypot(*deslocamentos.T)[:, None]
    direcoes = deslocamentos / comprimentos
    limite = min(COMPRIMENTO_MAXIMO, FRACAO_ESPACAMENTO * passo *
                 min(TAMANHO_CELULA_X, TAMANHO_CELULA_Y))
    comprimentos = np.minimum(comprimentos, limite)
    pontas = origens + direcoes * comprimentos

    profundidade = np.minimum(5.0, comprimentos * 0.42)
    base = pontas - profundidade * direcoes
    perpendicular = np.column_stack((-direcoes[:, 1], direcoes[:, 0]))
    asa = 0.55 * profundidade * perpendicular
    return np.stack((origens, pontas, base + asa, pontas, base - asa), axis=1)


def desenhar_vetores(tela, u, v, passo=4, sobre_corante=False):
    for pontos in geometria_vetores(u, v, passo).tolist():
        if sobre_corante:
            pg.draw.lines(tela, COR_CONTORNO_VETOR, False, pontos, 3)
        pg.draw.aalines(tela, COR_VETOR, False, pontos)


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

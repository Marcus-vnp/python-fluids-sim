# main.py — Semana 3

import pygame as pg
import numpy as np

from default import *
from calcs import *
from render import *
from simulacao import *

pg.init()
screen = pg.display.set_mode(RESOLUCAO)
clock = pg.time.Clock()
running = True

# Grade e campo
X, Y = criar_grade()
campo_atual = "rotacao"
u, v = campo_rotacao(X, Y, omega=1.0)

# Corante
c = np.zeros((Nx, Ny))

# Mancha inicial no centro
cx, cy = X.mean(), Y.mean()
c = np.exp(-(((X - cx)**2 + (Y - cy)**2) / (2 * 0.15**2)))

D = 0.0005                 # difusão
dt = calcular_dt(u, v, D)  # ajusta automaticamente

pausado = False


def desenhar_corante(c):
    max_c = max(c.max(), 1e-6)
    for i in range(0, Nx, 2):           # passo 2: desenha a cada 2 células
        for j in range(0, Ny, 2):
            valor = c[i, j] / max_c
            r = int(255 * min(1.0, valor * 2))
            g = int(255 * max(0.0, valor * 2 - 1))
            b = int(255 * max(0.0, valor * 2 - 1) * 0.3)
            x, y = celula_para_pixel(i, j)
            w = int(TAMANHO_CELULA_X * 2) + 1
            h = int(TAMANHO_CELULA_Y * 2) + 1
            pg.draw.rect(screen, (r, g, b), (x, y - h, w, h))


while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                pausado = not pausado
            elif event.key == pg.K_r:
                c = np.exp(-(((X - cx)**2 + (Y - cy)**2) / (2 * 0.15**2)))
            elif event.key == pg.K_1:
                campo_atual = "horizontal"
                u, v = campo_horizontal()
                dt = calcular_dt(u, v, D)
            elif event.key == pg.K_2:
                campo_atual = "rotacao"
                u, v = campo_rotacao(X, Y, omega=1.0)
                dt = calcular_dt(u, v, D)

    # --- Atualizar ---
    if not pausado:
        c = avancar(c, u, v, D, dt)

    # --- Desenhar ---
    screen.fill((10, 10, 10))
    desenhar_corante(c)

    fonte = pg.font.SysFont("consolas", 16)
    texto = f"Campo: {campo_atual} | dt: {dt:.4f} | {'PAUSADO' if pausado else 'rodando'}"
    screen.blit(fonte.render(texto, True, (230, 230, 230)), (10, 10))

    pg.display.flip()
    clock.tick(FPS)

pg.quit()
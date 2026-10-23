# Funcoes responsaveis por desenhar na tela

import numpy as np
import pygame as pg

from default import *

# Funcao de teste para desenhar grade na tela
def desenhar_grade(tela, X, Y):
    for x in X:
        pg.draw.line(tela, "white", (x[0], 0), (x[0], VERTICAL))
    for y in Y[0]:
        pg.draw.line(tela, "white", (0, y), (HORIZONTAL, y))
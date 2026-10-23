# LOOP PRINCIPAL de EXECUCAO

# bibliotcas essenciais
import pygame as pg
import numpy as np

#bibliotecas do projeto
from default import *
from calcs import *
from render import *

# Padrao do Pygame
pg.init()
screen = pg.display.set_mode(RESOLUCAO) # Resolucao da tela
clock = pg.time.Clock() # forma de rastrear o tempo
running = True # mantem o programa executando

# TESTE DA GRADE
X, Y = criar_grade()

while running: # Loop do Programa
    for event in pg.event.get(): # Configuracao do Botao de Fechar
        if event.type == pg.QUIT:
            running = False

    # Test da criacao da Grade
    desenhar_grade(screen, X, Y)

    pg.display.flip() # atualiza a tela
    clock.tick(FPS)

pg.quit() # finaliza todos os modulos do pygame
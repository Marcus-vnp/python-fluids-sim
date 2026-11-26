import numpy as np
import pygame as pg

from calcs import campo_horizontal, campo_rotacao, criar_grade
from default import DIFUSAO, ESCALA_TEMPO, FPS, INTERVALO_REAL_MAXIMO, Nx, Ny, RESOLUCAO
from interacao import Arraste, aceleracao_trajetoria, integrar_perturbacao
from render import desenhar_corante, desenhar_interacao
from simulacao import avancar_intervalo


def main():
    pg.init()
    tela = pg.display.set_mode(RESOLUCAO)
    grade_rgb = pg.Surface((Nx, Ny)).convert(tela)
    fonte = pg.font.SysFont("consolas", 16)
    relogio = pg.time.Clock()

    X, Y = criar_grade()
    campo_atual = "rotacao"
    u_base, v_base = campo_rotacao(X, Y)
    inicial = np.exp(-((X - X.mean())**2 + (Y - Y.mean())**2) / (2 * 0.15**2))
    c = inicial.copy()
    u_perturbado, v_perturbado = np.zeros_like(X), np.zeros_like(Y)
    ax, ay = np.zeros_like(X), np.zeros_like(Y)
    arraste = Arraste()
    pausado = False
    com_foco = True
    dt = 0.0

    while True:
        dt_real = relogio.tick(FPS) / 1000
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit()
                return
            if evento.type in (pg.WINDOWLEAVE, pg.WINDOWFOCUSLOST):
                arraste.cancelar()
                arraste.cursor = None
                if evento.type == pg.WINDOWFOCUSLOST:
                    com_foco = False
            elif evento.type == pg.WINDOWFOCUSGAINED:
                com_foco = True
            elif evento.type == pg.KEYDOWN:
                if evento.key == pg.K_SPACE:
                    pausado = not pausado
                    arraste.cancelar()
                elif evento.key in (pg.K_r, pg.K_1, pg.K_2):
                    if evento.key == pg.K_r:
                        c = inicial.copy()
                    elif evento.key == pg.K_1:
                        campo_atual = "horizontal"
                        u_base, v_base = campo_horizontal()
                    else:
                        campo_atual = "rotacao"
                        u_base, v_base = campo_rotacao(X, Y)
                    u_perturbado.fill(0)
                    v_perturbado.fill(0)
                    arraste.cancelar()
            elif evento.type == pg.MOUSEWHEEL and com_foco:
                arraste.ajustar_raio(evento.y)
            elif evento.type == pg.MOUSEBUTTONDOWN and evento.button == 1 and com_foco and not pausado:
                arraste.pressionar(evento.pos)
            elif evento.type == pg.MOUSEMOTION and com_foco:
                arraste.mover(evento.pos, evento.buttons[0] and not pausado)
            elif evento.type == pg.MOUSEBUTTONUP and evento.button == 1:
                if com_foco and not pausado:
                    arraste.mover(evento.pos, True)
                arraste.soltar()

        forca = (0.0, 0.0)
        if np.isfinite(dt_real) and dt_real > 0 and not pausado:
            intervalo = min(dt_real, INTERVALO_REAL_MAXIMO) * ESCALA_TEMPO
            forca = aceleracao_trajetoria(arraste.segmentos, arraste.raio, dt_real, X, Y, ax, ay)
            integrar_perturbacao(u_perturbado, v_perturbado, ax, ay, intervalo)
            u_total = u_base + u_perturbado
            v_total = v_base + v_perturbado
            c, dt = avancar_intervalo(c, u_total, v_total, DIFUSAO, intervalo)
        arraste.segmentos.clear()

        desenhar_corante(tela, grade_rgb, c)
        if arraste.anterior is None:
            forca = (0.0, 0.0)
        desenhar_interacao(tela, arraste.cursor, arraste.raio, forca)
        estado = "PAUSADO" if pausado else "rodando"
        texto = f"Campo: {campo_atual} | dt: {dt:.4f} | {estado} | Raio: {arraste.raio} px"
        tela.blit(fonte.render(texto, True, (230, 230, 230)), (10, 10))
        pg.display.flip()


if __name__ == "__main__":
    main()

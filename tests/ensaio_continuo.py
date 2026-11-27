"""Executar da raiz com python -m tests.ensaio_continuo (cinco minutos reais)."""

import os
from math import sin
from time import perf_counter
from unittest.mock import patch

os.environ.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")

import numpy as np
import pygame as pg

import main
from default import PERTURBACAO_MAXIMA


def executar():
    ler_eventos = pg.event.get
    avancar = main.avancar_intervalo
    integrar = main.integrar_perturbacao
    quadros = 0
    pico = 0
    inicio = perf_counter()

    def eventos():
        tempo = perf_counter() - inicio
        lote = ler_eventos()
        pos = round(640 + 190 * sin(4 * tempo)), round(360 + 115 * sin(6 * tempo))
        if quadros == 0:
            lote.append(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=pos))
        if tempo >= 301:
            lote.append(pg.event.Event(pg.QUIT))
        lote.append(pg.event.Event(pg.MOUSEMOTION, pos=pos, buttons=(1, 0, 0)))
        return lote

    def verificar_corante(c, u, v, D, intervalo):
        nonlocal quadros
        novo, dt = avancar(c, u, v, D, intervalo)
        assert np.isfinite(novo).all() and np.isfinite(u).all() and np.isfinite(v).all()
        assert 0 <= novo.min() <= novo.max() <= 1 and dt > 0
        quadros += 1
        return novo, dt

    def verificar_perturbacao(u, v, ax, ay, dt):
        nonlocal pico
        integrar(u, v, ax, ay, dt)
        pico = max(pico, np.hypot(u, v).max())
        assert pico <= PERTURBACAO_MAXIMA + 1e-12

    with (
        patch.object(pg.event, "get", eventos),
        patch.object(main, "avancar_intervalo", verificar_corante),
        patch.object(main, "integrar_perturbacao", verificar_perturbacao),
    ):
        main.main()
    duracao = perf_counter() - inicio
    assert duracao >= 300 and pico > 0
    print(f"{quadros} frames em {duracao:.3f} s | {quadros/duracao:.2f} FPS | "
          f"pico da perturbação {pico:.5f} m/s", flush=True)


if __name__ == "__main__":
    executar()

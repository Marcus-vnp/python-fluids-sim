import os
import unittest
from unittest.mock import patch

os.environ.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")

import numpy as np
import pygame as pg

import main
from calcs import campo_horizontal, campo_rotacao, criar_grade
from default import AMORTECIMENTO, ESCALA_TEMPO, PASSO_RAIO, RAIO_INICIAL


def clicar(pos):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=pos)


def mover(pos, esquerdo=1):
    return pg.event.Event(pg.MOUSEMOTION, pos=pos, buttons=(esquerdo, 0, 0))


def tecla(chave):
    return pg.event.Event(pg.KEYDOWN, key=chave)


def executar_frames(lotes, tempos=None):
    """Executa o loop real e observa a física e o indicador de cada frame."""
    campos, corantes, indicadores = [], [], []
    avancar = main.avancar_intervalo
    desenhar = main.desenhar_corante
    indicador = main.desenhar_interacao

    def observar_passo(c, u, v, D, intervalo):
        campos.append(np.stack((u, v)))
        return avancar(c, u, v, D, intervalo)

    def observar_corante(tela, grade, c):
        corantes.append(c.copy())
        desenhar(tela, grade, c)

    def observar_indicador(tela, cursor, raio, forca):
        indicadores.append((cursor, raio, forca))
        indicador(tela, cursor, raio, forca)

    with (
        patch.object(pg.time, "Clock") as relogio,
        patch.object(pg.event, "get", side_effect=lotes + [[pg.event.Event(pg.QUIT)]]),
        patch.object(main, "avancar_intervalo", observar_passo),
        patch.object(main, "desenhar_corante", observar_corante),
        patch.object(main, "desenhar_interacao", observar_indicador),
    ):
        relogio.return_value.tick.side_effect = (tempos or [16] * len(lotes)) + [16]
        main.main()
    return campos, corantes, indicadores


class ControlesPygame(unittest.TestCase):
    def test_primeiro_clique_soltar_e_cursor_parado(self):
        pos, fim = (600, 355), (625, 355)
        campos, _, indicadores = executar_frames([
            [], [mover(pos, 0)], [clicar(pos)], [mover(fim)], [mover(fim)], [],
            [pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=fim)], [mover((70, 70), 0)],
        ])
        base = campos[0]
        for indice in (1, 2):
            np.testing.assert_array_equal(campos[indice], base)
        pico = np.max(campos[3] - base)
        self.assertGreater(pico, 0.1)
        fator = np.exp(-AMORTECIMENTO * 0.016 * ESCALA_TEMPO)
        for i in range(4, 8):
            np.testing.assert_allclose(campos[i]-base, (campos[i-1]-base)*fator, atol=1e-14)
            self.assertEqual(indicadores[i][2], (0, 0))
        self.assertGreater(indicadores[3][2][0], 0)

    def test_gesto_completo_entre_dois_frames(self):
        pos, fim = (600, 355), (625, 355)
        campos, _, indicadores = executar_frames([
            [], [clicar(pos), pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=fim)], [],
        ])
        self.assertGreater(np.max(campos[1] - campos[0]), 0.1)
        self.assertEqual(indicadores[1][2], (0, 0))
        self.assertLess(np.max(campos[2] - campos[0]), np.max(campos[1] - campos[0]))

    def test_perda_de_foco_saida_da_janela_e_reentrada(self):
        perto, longe = (2, 3), (1200, 660)
        campos, _, indicadores = executar_frames([
            [], [clicar(perto), mover((8, 3)), pg.event.Event(pg.WINDOWFOCUSLOST)],
            [clicar(longe), mover(perto)], [pg.event.Event(pg.WINDOWFOCUSGAINED), mover(longe)],
            [clicar(perto), pg.event.Event(pg.WINDOWLEAVE)], [mover(longe)],
            [clicar(perto), mover((-1, 3)), mover(longe)], [clicar(longe), mover((1210, 660))],
        ])
        for campo in campos[1:-1]:
            np.testing.assert_array_equal(campo, campos[0])
        self.assertIsNone(indicadores[1][0])
        self.assertIsNone(indicadores[4][0])
        self.assertGreater(np.max(campos[-1] - campos[0]), 0)

    def test_pausa_scroll_reset_e_campos(self):
        pos = (650, 360)
        campos, corantes, indicadores = executar_frames([
            [], [clicar(pos), mover((685, 360))], [tecla(pg.K_SPACE), mover((900, 450))],
            [pg.event.Event(pg.MOUSEWHEEL, y=2), clicar(pos), mover((30, 20))],
            [tecla(pg.K_SPACE), mover((20, 100))],
            [tecla(pg.K_1)], [clicar(pos), mover((600, 355))],
            [tecla(pg.K_r)], [clicar(pos), mover((635, 355))], [tecla(pg.K_2)],
        ])
        np.testing.assert_array_equal(corantes[1], corantes[2])
        np.testing.assert_array_equal(corantes[2], corantes[3])
        self.assertEqual(indicadores[3][1], RAIO_INICIAL + 2*PASSO_RAIO)
        fator = np.exp(-AMORTECIMENTO * 0.016 * ESCALA_TEMPO)
        np.testing.assert_allclose(campos[2]-campos[0], (campos[1]-campos[0])*fator, atol=1e-14)
        horizontal = campo_horizontal()
        for i in (3, 5):
            np.testing.assert_array_equal(campos[i], horizontal)
        np.testing.assert_array_equal(campos[7], campo_rotacao(*criar_grade()))
        _, referencia, _ = executar_frames([[tecla(pg.K_1)]])
        np.testing.assert_array_equal(corantes[7], referencia[0])

    def test_frames_atrasados_ou_invalidos_sem_impulso_acumulado(self):
        pos = (600, 355)
        campos, _, _ = executar_frames([
            [], [clicar(pos), mover((620, 350))], [mover((640, 350))], [mover((660, 360))],
            [mover((685, 350))], [],
        ], [16, 0, float("nan"), float("inf"), 180, 16])
        self.assertEqual(len(campos), 3)
        for campo in campos[1:]:
            np.testing.assert_array_equal(campo, campos[0])


class ModosDeVisualizacao(unittest.TestCase):
    def test_mesmos_campos_e_concentracoes_em_todos_os_modos(self):
        # Repete o mesmo gesto nos três modos e observa inclusive o corante oculto.
        gesto = [[clicar((620, 350))], [mover((660, 350))], [mover((660, 310))],
                 [mover((620, 310))], [mover((620, 350))],
                 [pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=(620, 350))], []]
        referencia = None
        for modo in (pg.K_F1, pg.K_F2, pg.K_F3):
            concentracoes = []
            avancar = main.avancar_intervalo

            def observar(c, u, v, D, intervalo):
                novo, dt = avancar(c, u, v, D, intervalo)
                concentracoes.append(novo.copy())
                return novo, dt

            with (patch.object(main, "avancar_intervalo", observar),
                  patch.object(main, "desenhar_vetores", wraps=main.desenhar_vetores) as vetores):
                campos, visiveis, _ = executar_frames([[tecla(modo)]] + gesto)
            self.assertEqual(len(visiveis), 0 if modo == pg.K_F2 else len(campos))
            self.assertEqual(vetores.call_count, 0 if modo == pg.K_F1 else len(campos))
            for desenho, campo in zip(vetores.call_args_list, campos):
                np.testing.assert_array_equal(desenho.args[1:3], campo)
            if referencia is None:
                referencia = campos, concentracoes
            else:
                np.testing.assert_array_equal(campos, referencia[0])
                np.testing.assert_array_equal(concentracoes, referencia[1])

    def test_alterna_modo_e_densidade_mesmo_em_pausa(self):
        lotes = [[tecla(pg.K_SPACE), tecla(pg.K_F2)], [tecla(pg.K_g), tecla(pg.K_1)],
                 [tecla(pg.K_F3), tecla(pg.K_g)], [tecla(pg.K_F1)],
                 [tecla(pg.K_g), tecla(pg.K_F2), tecla(pg.K_r)], [tecla(pg.K_SPACE)]]
        with patch.object(main, "desenhar_vetores", wraps=main.desenhar_vetores) as vetores:
            campos, corantes, _ = executar_frames(lotes)
        self.assertEqual(len(campos), 1)
        self.assertEqual(len(corantes), 2)
        chamadas = vetores.call_args_list
        self.assertEqual([c.args[3] for c in chamadas], [4, 2, 8, 4, 4])
        self.assertEqual([c.kwargs["sobre_corante"] for c in chamadas],
                         [False, False, True, False, False])
        np.testing.assert_array_equal(chamadas[0].args[1:3], campo_rotacao(*criar_grade()))
        for chamada in chamadas[1:]:
            np.testing.assert_array_equal(chamada.args[1:3], campo_horizontal())

    def test_troca_de_modo_durante_arraste_e_decaimento(self):
        gesto = [[clicar((620, 350))], [mover((680, 350))],
                 [pg.event.Event(pg.MOUSEWHEEL, y=2), mover((680, 290))],
                 [pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=(680, 290))], []]
        referencia, corante, indicadores = executar_frames(gesto)
        teclas = [pg.K_F2, pg.K_F3, pg.K_F2, pg.K_F2, pg.K_F1]
        lotes = [[tecla(modo), *eventos] for modo, eventos in zip(teclas, gesto)]
        with patch.object(main, "desenhar_vetores", wraps=main.desenhar_vetores) as vetores:
            campos, visiveis, indicadores_observados = executar_frames(lotes)
        np.testing.assert_array_equal(campos, referencia)
        np.testing.assert_array_equal(visiveis, [corante[1], corante[-1]])
        self.assertEqual(indicadores_observados, indicadores)
        for chamada, campo in zip(vetores.call_args_list, referencia):
            np.testing.assert_array_equal(chamada.args[1:3], campo)

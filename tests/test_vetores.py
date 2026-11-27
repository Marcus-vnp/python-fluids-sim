import unittest

import numpy as np
import pygame as pg

from calcs import campo_horizontal, campo_rotacao, celula_para_pixel, criar_grade
from default import Dx, Dy, RESOLUCAO, TAMANHO_CELULA_X, TAMANHO_CELULA_Y, TEMPO_VISUAL
from render import desenhar_vetores, geometria_vetores


class GeometriaVetorial(unittest.TestCase):
    def test_horizontal_amostragem_origens_e_escala_fixa(self):
        u, v = campo_horizontal(0.25)
        for passo in (2, 4, 8):
            setas = geometria_vetores(u, v, passo)
            self.assertEqual(len(setas), u.size // passo**2)
            np.testing.assert_allclose(setas[0, 0], celula_para_pixel(passo//2, passo//2), atol=0.5)
            delta = setas[:, 1] - setas[:, 0]
            np.testing.assert_allclose(delta[:, 0], 0.25 * TAMANHO_CELULA_X / Dx * TEMPO_VISUAL)
            np.testing.assert_array_equal(delta[:, 1], 0)
            maiores = geometria_vetores(2*u, v, passo)
            np.testing.assert_allclose(maiores[:, 1] - maiores[:, 0], 2*delta, atol=1e-10)
            self.assertTrue(np.all(setas[:, 2, 0] < setas[:, 1, 0]))

    def test_rotacao_tangente_e_projecao_vertical(self):
        X, Y = criar_grade()
        u, v = campo_rotacao(X, Y)
        # Uma amostra no quadrante superior direito: seta aponta à esquerda e acima.
        seta = geometria_vetores(u, v, 8).reshape(16, 9, 5, 2)[12, 6]
        delta = seta[1] - seta[0]
        self.assertTrue(np.all(delta < 0))
        i, j = 100, 52
        fisico = delta / (TEMPO_VISUAL * np.array([TAMANHO_CELULA_X/Dx, -TAMANHO_CELULA_Y/Dy]))
        np.testing.assert_allclose(fisico, (u[i, j], v[i, j]))
        self.assertAlmostEqual(np.dot(fisico, (X[i, j]-0.5, Y[i, j]-0.5)), 0)
        for asa in seta[[2, 4]]:
            self.assertLess(np.dot(asa-seta[1], delta), 0)

    def test_oculta_nulos_limita_comprimento_e_preserva_matrizes(self):
        u, v = campo_horizontal(0.0)
        self.assertEqual(len(geometria_vetores(u, v, 4)), 0)
        u[2, 2], v[2, 2] = 8, -6
        u.setflags(write=False)
        v.setflags(write=False)
        tela = pg.Surface(RESOLUCAO)
        desenhar_vetores(tela, u, v, 4, sobre_corante=True)
        setas = geometria_vetores(u, v, 4)
        self.assertEqual(len(setas), 1)
        self.assertLess(np.linalg.norm(setas[0, 1] - setas[0, 0]), 4*TAMANHO_CELULA_X)

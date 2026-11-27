from math import cos, exp, hypot, pi, sin
import unittest

import numpy as np

from calcs import (
    campo_rotacao, celula_para_pixel, criar_grade, pixel_para_celula, pixel_para_fisico,
)
from default import (
    ACELERACAO_MAXIMA, AMORTECIMENTO, DIFUSAO, DT_MAXIMO, Dx, Dy, ESCALA_TEMPO,
    HORIZONTAL, MAX_SEGMENTOS, Nx, Ny, PERTURBACAO_MAXIMA, RAIO_INICIAL,
    RAIO_MAXIMO, RAIO_MINIMO, VERTICAL,
)
from interacao import Arraste, aceleracao_trajetoria, integrar_perturbacao, somar_gaussiana
from simulacao import avancar_intervalo, calcular_dt


class InteracaoFisica(unittest.TestCase):
    def setUp(self):
        self.X, self.Y = criar_grade()
        self.ax, self.ay = np.zeros_like(self.X), np.zeros_like(self.Y)

    def acelerar(self, segmentos, dt=1/60, raio=RAIO_INICIAL):
        return aceleracao_trajetoria(segmentos, raio, dt, self.X, self.Y, self.ax, self.ay)

    def test_coordenadas_da_grade_e_extremos_da_tela(self):
        for i, j in np.ndindex(Nx, Ny):
            pos = celula_para_pixel(i, j)
            self.assertEqual(pixel_para_celula(*pos), (i, j))
        self.assertEqual(pixel_para_fisico(0, VERTICAL - 1), (0, 0))
        np.testing.assert_allclose(pixel_para_fisico(HORIZONTAL - 1, 0), (1, 1))
        self.assertEqual(pixel_para_celula(-50, 800), (0, 0))

    def test_simetria_decaimento_e_suporte_da_gaussiana(self):
        i, j = 64, 36
        somar_gaussiana(self.ax, self.ay, self.X, self.Y,
                        (self.X[i, j], self.Y[i, j]), RAIO_INICIAL, (1, -2))
        self.assertEqual(self.ax[i, j], 1)
        np.testing.assert_allclose(self.ax[i-5:i, j], self.ax[i+5:i:-1, j])
        np.testing.assert_allclose(self.ax[i, j-5:j], self.ax[i, j+5:j:-1])
        self.assertTrue(np.all(np.diff(self.ax[i:i+15, j]) < 0))
        self.assertEqual(self.ax[i+15, j], 0)
        np.testing.assert_array_equal(self.ay, -2*self.ax)

    def test_direcao_e_velocidade_fisicas(self):
        for delta in [(3, 0), (0, -3), (3, -2), (-2, 2)]:
            inicio = (650, 320)
            fim = (650 + delta[0], 320 + delta[1])
            lento = self.acelerar([(inicio, fim)], 1/30)
            rapido = self.acelerar([(inicio, fim)], 1/60)
            np.testing.assert_allclose(rapido, np.multiply(lento, 2))
            self.assertEqual(np.sign(lento[0]), np.sign(delta[0]))
            self.assertEqual(np.sign(lento[1]), -np.sign(delta[1]))

    def test_amostragem_sem_lacunas_nem_ganho_por_evento(self):
        ini, meio, fim = (20, 360), (640, 360), (1260, 360)
        self.acelerar([(ini, fim)], raio=RAIO_MINIMO)
        unico = self.ax.copy()
        self.assertTrue(np.all(unico[2:-2, Ny//2] > 0))
        self.acelerar([(ini, meio), (meio, fim)], raio=RAIO_MINIMO)
        np.testing.assert_allclose(unico, self.ax, atol=1e-12)

    def test_bordas_sem_reaparecer_do_lado_oposto(self):
        self.acelerar([((0, 0), (4, 3))])
        self.assertGreater(self.ax[0, -1], 0)
        self.assertFalse(self.ax[-1, :].any())
        self.assertFalse(self.ax[:, 0].any())

    def test_intervalos_e_limites_vetoriais(self):
        segmento = [((0, 0), (1279, 719))]
        for dt in [0, -1, np.nan, np.inf, 2]:
            self.assertEqual(self.acelerar(segmento, dt), (0, 0))
            self.assertFalse(self.ax.any() or self.ay.any())
        seta = self.acelerar(segmento, 1e-310)
        self.assertAlmostEqual(hypot(*seta), ACELERACAO_MAXIMA)
        self.assertLessEqual(np.hypot(self.ax, self.ay).max(), ACELERACAO_MAXIMA)
        u, v = self.ax.copy(), self.ay.copy()
        self.ax.fill(40)
        self.ay.fill(20)
        for _ in range(100):
            integrar_perturbacao(u, v, self.ax, self.ay, 0.01)
        np.testing.assert_allclose(np.hypot(u, v), PERTURBACAO_MAXIMA)

    def test_amortecimento_exato_e_campo_base_preservado(self):
        base = campo_rotacao(self.X, self.Y)
        originais = [a.copy() for a in base]
        u, v = np.ones_like(self.X), -np.ones_like(self.Y)
        for _ in range(40):
            integrar_perturbacao(u, v, self.ax, self.ay, 0.01)
        for b, original, p, sinal in zip(base, originais, (u, v), (1, -1)):
            np.testing.assert_allclose(b + p, original + sinal * exp(-AMORTECIMENTO * 0.4))
            np.testing.assert_array_equal(b, original)

    def test_gesto_circular_preserva_direcoes_locais(self):
        pontos = [(640 + 180*cos(t), 360 - 130*sin(t)) for t in np.linspace(0, 2*pi, 97)]
        self.acelerar(list(zip(pontos, pontos[1:])))
        for k, componente, sinal in [(0, self.ay, 1), (24, self.ax, -1),
                                     (48, self.ay, -1), (72, self.ax, 1)]:
            self.assertGreater(sinal * componente[pixel_para_celula(*pontos[k])], 0)

    def test_raio_e_orcamento_de_eventos(self):
        a = Arraste()
        a.ajustar_raio(200)
        self.assertEqual(a.raio, RAIO_MAXIMO)
        a.ajustar_raio(-200)
        self.assertEqual(a.raio, RAIO_MINIMO)
        a.pressionar((5, 300))
        for x in range(6, 800):
            a.mover((x, 300), True)
        self.assertEqual(len(a.segmentos), MAX_SEGMENTOS)
        self.assertEqual(a.anterior, (799, 300))

    def test_cfl_bidimensional_difusao_e_passo_maximo(self):
        u = np.array([3., 0, -1])
        v = np.array([-4., 1, 0])
        self.assertAlmostEqual(calcular_dt(u, v, 0), 0.8/(3/Dx + 4/Dy))
        self.assertAlmostEqual(calcular_dt(u, v, 1), 0.8/(2*(Dx**-2 + Dy**-2)))
        self.assertEqual(calcular_dt(0, 0, 0), DT_MAXIMO)
        for invalido in [np.nan, np.inf]:
            with self.assertRaises(ValueError):
                calcular_dt(u, invalido, 0)

    def test_principio_do_maximo_e_contorno_com_velocidades_intensas(self):
        rng = np.random.default_rng(42)
        c = rng.random(self.X.shape)
        u, v = rng.uniform(-2, 2, (2, *c.shape))
        for _ in range(12):
            anterior = c.max()
            c, dt = avancar_intervalo(c, u, v, DIFUSAO, 0.01875)
            self.assertLessEqual(dt, calcular_dt(u, v, DIFUSAO))
            self.assertGreaterEqual(c.min(), 0)
            self.assertLessEqual(c.max(), anterior)
            self.assertFalse(c[[0, -1], :].any() or c[:, [0, -1]].any())

    def test_deformacao_pela_adveccao_em_diferentes_taxas(self):
        inicial = np.exp(-((self.X - 0.5)**2 + (self.Y - 0.5)**2) / (2 * 0.15**2))
        base_u, base_v = campo_rotacao(self.X, self.Y)
        resultados = []
        for fps in (30, 60, 120):
            dt = 1 / fps
            intervalo = dt * ESCALA_TEMPO
            u, v = np.zeros_like(self.X), np.zeros_like(self.Y)
            c, controle = inicial.copy(), inicial.copy()
            for i in range(fps):
                p = (450 + 440*i/fps, 365)
                q = (450 + 440*(i+1)/fps, 365)
                self.acelerar([(p, q)], dt)
                integrar_perturbacao(u, v, self.ax, self.ay, intervalo)
                c, _ = avancar_intervalo(c, base_u + u, base_v + v, DIFUSAO, intervalo)
                controle, _ = avancar_intervalo(controle, base_u, base_v, DIFUSAO, intervalo)
            self.assertGreater(np.max(np.abs(c - controle)), 0.15)
            resultados.append((c, u))
        for corante, perturbacao in resultados[:-1]:
            np.testing.assert_allclose(corante, resultados[-1][0], atol=0.025)
            np.testing.assert_allclose(perturbacao, resultados[-1][1], atol=0.012)

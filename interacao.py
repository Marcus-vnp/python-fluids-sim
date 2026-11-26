"""Trajetória do cursor e aceleração localizada sobre a grade física."""

from math import ceil, exp, expm1

import numpy as np

from calcs import pixel_para_fisico
from default import (
    ACELERACAO_MAXIMA, AMORTECIMENTO, Dx, Dy, GANHO_MOUSE, HORIZONTAL,
    INTERVALO_REAL_MAXIMO, MAX_AMOSTRAS, MAX_SEGMENTOS, PASSO_RAIO, PERTURBACAO_MAXIMA,
    RAIO_INICIAL, RAIO_MAXIMO, RAIO_MINIMO, TAMANHO_CELULA_X,
    TAMANHO_CELULA_Y, VERTICAL,
)


class Arraste:
    def __init__(self):
        self.raio = RAIO_INICIAL
        self.cursor = None
        self.anterior = None
        self.segmentos = []

    def apontar(self, pos):
        x, y = pos
        self.cursor = pos if 0 <= x < HORIZONTAL and 0 <= y < VERTICAL else None
        if self.cursor is None:
            self.soltar()

    def pressionar(self, pos):
        self.apontar(pos)
        self.anterior = self.cursor

    def mover(self, pos, pressionado):
        self.apontar(pos)
        if not pressionado:
            self.soltar()
        if self.anterior is None:
            return
        if pos != self.anterior and len(self.segmentos) < MAX_SEGMENTOS:
            self.segmentos.append((self.anterior, pos))
        self.anterior = pos

    def soltar(self):
        self.anterior = None

    def cancelar(self):
        self.soltar()
        self.segmentos.clear()

    def ajustar_raio(self, passos):
        self.raio = min(RAIO_MAXIMO, max(RAIO_MINIMO, self.raio + passos * PASSO_RAIO))


def somar_gaussiana(ax, ay, X, Y, centro, raio, forca):
    """Acumula só no retângulo que contém o disco, recortado pelo domínio."""
    x, y = centro
    rx = raio * Dx / TAMANHO_CELULA_X
    ry = raio * Dy / TAMANHO_CELULA_Y
    janela = np.s_[max(0, ceil((x-rx)/Dx)):int((x+rx)/Dx)+1,
                   max(0, ceil((y-ry)/Dy)):int((y+ry)/Dy)+1]
    q2 = ((X[janela] - x) / rx)**2 + ((Y[janela] - y) / ry)**2
    # Gaussiana de sigma = raio/3, deslocada para chegar a zero no corte.
    cauda = exp(-4.5)
    peso = np.maximum(np.exp(-4.5 * q2) - cauda, 0.0) / (1 - cauda)
    ax[janela] += forca[0] * peso
    ay[janela] += forca[1] * peso


def aceleracao_trajetoria(segmentos, raio, dt_real, X, Y, ax, ay):
    """Média espacial do gesto no frame. Retorna a última aceleração da seta."""
    ax.fill(0)
    ay.fill(0)
    if not segmentos or not 0 < dt_real <= INTERVALO_REAL_MAXIMO:
        return (0.0, 0.0)

    inicios, fins = np.asarray(segmentos, dtype=float).transpose(1, 0, 2)
    deltas = fins - inicios
    comprimentos = np.hypot(deltas[:, 0], deltas[:, 1])
    acumulado = np.cumsum(comprimentos)
    distancia = acumulado[-1]
    if not np.isfinite(distancia) or distancia <= 0:
        return (0.0, 0.0)

    # Pontos médios equidistantes no arco, sem privilegiar eventos mais densos.
    n = min(MAX_AMOSTRAS, max(1, ceil(distancia / (raio / 6))))
    arcos = (np.arange(n) + 0.5) * (distancia / n)
    indices = np.searchsorted(acumulado, arcos)
    fracao = 1 - (acumulado[indices] - arcos) / comprimentos[indices]
    pontos = inicios[indices] + fracao[:, None] * deltas[indices]

    # Velocidade média em pixels/s real, com a direção local de cada segmento.
    direcoes = deltas[indices] / comprimentos[indices, None]
    direcoes *= (Dx / TAMANHO_CELULA_X, -Dy / TAMANHO_CELULA_Y)
    impulsos = direcoes * (GANHO_MOUSE * distancia)
    # Limitar antes da divisão evita overflow mesmo para dt_real muito pequeno.
    tempo_minimo = np.hypot(impulsos[:, 0], impulsos[:, 1]) / ACELERACAO_MAXIMA
    aceleracoes = impulsos / np.maximum(dt_real, tempo_minimo)[:, None]
    for ponto, aceleracao in zip(pontos, aceleracoes):
        somar_gaussiana(ax, ay, X, Y, pixel_para_fisico(*ponto), raio, aceleracao / n)
    return tuple(aceleracoes[-1])


def integrar_perturbacao(u, v, ax, ay, dt):
    """Solução de p' = a - lambda*p para aceleração constante no frame."""
    decaimento = exp(-AMORTECIMENTO * dt)
    ganho = -expm1(-AMORTECIMENTO * dt) / AMORTECIMENTO if AMORTECIMENTO else dt
    u *= decaimento
    v *= decaimento
    u += ganho * ax
    v += ganho * ay
    divisor = np.maximum(1.0, np.hypot(u, v) / PERTURBACAO_MAXIMA)
    u /= divisor
    v /= divisor

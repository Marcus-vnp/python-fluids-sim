# simulacao.py — Advecção + difusão integradas (Semana 3)

import numpy as np
from default import Dx, Dy, DT_MAXIMO, MAX_SUBPASSOS


def calcular_dt(u, v, D, seguranca=0.8):
    """Limite para os dois operadores explícitos aplicados em sequência."""
    taxa_adv = np.max(np.abs(u) / Dx + np.abs(v) / Dy)
    taxa_dif = 2 * D * (1 / Dx**2 + 1 / Dy**2)
    if not np.isfinite([taxa_adv, taxa_dif, seguranca]).all():
        raise ValueError("Campo ou coeficientes não finitos")
    if D < 0 or not 0 < seguranca <= 1:
        raise ValueError("Difusão ou fator de segurança inválido")
    taxa = max(taxa_adv, taxa_dif)
    return min(DT_MAXIMO, seguranca / taxa) if taxa else DT_MAXIMO


def passo_adveccao(c, u, v, dt):
    c_novo = c.copy()

    # Upwind em x: usa c[i] - c[i-1] onde u > 0, c[i+1] - c[i] onde u < 0
    fluxo_x = np.where(u > 0, u * (c - np.roll(c, 1, axis=0)),
                             u * (np.roll(c, -1, axis=0) - c))
    c_novo -= dt / Dx * fluxo_x

    # Upwind em y
    fluxo_y = np.where(v > 0, v * (c - np.roll(c, 1, axis=1)),
                             v * (np.roll(c, -1, axis=1) - c))
    c_novo -= dt / Dy * fluxo_y

    return c_novo


def passo_difusao(c, D, dt):
    c_novo = c.copy()
    c_novo[1:-1, :] += D * dt / Dx**2 * (c[2:, :] - 2*c[1:-1, :] + c[:-2, :])
    c_novo[:, 1:-1] += D * dt / Dy**2 * (c[:, 2:] - 2*c[:, 1:-1] + c[:, :-2])
    return c_novo


def aplicar_contorno(c):
    c[0, :] = 0.0
    c[-1, :] = 0.0
    c[:, 0] = 0.0
    c[:, -1] = 0.0
    return c


def avancar(c, u, v, D, dt):
    c = passo_adveccao(c, u, v, dt)
    c = passo_difusao(c, D, dt)
    c = aplicar_contorno(c)
    return c


def avancar_intervalo(c, u, v, D, intervalo):
    """Divide o intervalo do frame em passos iguais que respeitam o CFL."""
    limite = calcular_dt(u, v, D)
    passos = min(MAX_SUBPASSOS, max(1, int(np.ceil(intervalo / limite))))
    dt = min(limite, intervalo / passos)
    for _ in range(passos):
        c = avancar(c, u, v, D, dt)
    return c, dt

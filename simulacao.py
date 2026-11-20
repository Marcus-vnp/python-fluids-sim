# simulacao.py — Advecção + difusão integradas (Semana 3)

import numpy as np
from default import Nx, Ny, Dx, Dy


def calcular_dt(u, v, D, seguranca=0.8):
    h = min(Dx, Dy)
    max_vel = np.max(np.abs(u)) + np.max(np.abs(v))
    dt_adv = h / max_vel if max_vel > 0 else np.inf
    dt_dif = 0.25 * h**2 / D if D > 0 else np.inf
    return seguranca * min(dt_adv, dt_dif)


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
    c = np.maximum(c, 0.0)          # evita concentrações negativas
    return c
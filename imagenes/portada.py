"""
Portada del repositorio: arte generativo.

Miles de partículas soltadas sobre un campo vectorial suave y aleatorio. Cada
una deja el rastro de su trayectoria. El campo se arma sumando ondas de
distinta frecuencia y fase.

Inspirado en la serie "Art from Code" de Danielle Navarro, escrita en R:

    Navarro, Danielle. 2024. "Art from Code I: Generative Art with R."
    https://blog.djnavarro.net/posts/2024-12-18_art-from-code-1/
    Publicado bajo licencia CC BY 4.0.

    python imagenes/portada.py          # una pieza distinta cada vez
    python imagenes/portada.py 2026     # la pieza de esa semilla
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap

FONDO = "#0E1116"

PALETAS = [
    ["#0b3954", "#087e8b", "#7fd8be", "#f3f9d2"],
    ["#231942", "#5e548e", "#be95c4", "#f2e9e4"],
    ["#1a1423", "#3d314a", "#c69f89", "#f2d0a4"],
    ["#03071e", "#37718e", "#8ee3ef", "#aff9c9"],
    ["#20232a", "#6b705c", "#a5a58d", "#ffe8d6"],
]


def campo(semilla, octavas=4):
    """Un campo de ángulos suave, hecho de ondas superpuestas."""
    rng = np.random.default_rng(semilla)
    ondas = []
    for k in range(octavas):
        frec = 0.9 * (1.85 ** k)
        ondas.append((
            frec,
            rng.uniform(0, 2 * np.pi, 3),        # fases
            rng.uniform(-1, 1, 3) / (1.5 ** k),  # amplitudes
            rng.uniform(-1, 1, 2),               # direccion
        ))

    def angulo(x, y):
        v = np.zeros_like(x)
        for frec, fase, amp, dirn in ondas:
            u = dirn[0] * x + dirn[1] * y
            v += amp[0] * np.sin(frec * (x + fase[0]))
            v += amp[1] * np.cos(frec * (y + fase[1]))
            v += amp[2] * np.sin(frec * (u + fase[2]))
        return v * np.pi
    return angulo


def pieza(semilla, n=2600, pasos=190, largo=.0042):
    rng = np.random.default_rng(semilla)
    angulo = campo(semilla)
    paleta = PALETAS[rng.integers(len(PALETAS))]
    mapa = LinearSegmentedColormap.from_list("p", paleta, N=512)

    # Punto de partida de cada particula
    x = rng.uniform(-.15, 3.15, n)
    y = rng.uniform(-.15, 1.15, n)
    tono = (x / 3 + rng.normal(0, .07, n)).clip(0, 1)
    grosor = rng.gamma(1.7, .38, n).clip(.12, 1.9)
    alfa = rng.uniform(.16, .5, n)

    trayectos = np.empty((n, pasos, 2))
    for t in range(pasos):
        trayectos[:, t, 0] = x
        trayectos[:, t, 1] = y
        a = angulo(x, y)
        x = x + np.cos(a) * largo * 3
        y = y + np.sin(a) * largo

    colores = mapa(tono)
    colores[:, 3] = alfa

    fig, ax = plt.subplots(figsize=(17, 5.8))
    fig.patch.set_facecolor(FONDO)
    ax.set_facecolor(FONDO)
    ax.add_collection(LineCollection(
        trayectos, colors=colores, linewidths=grosor,
        capstyle="round", joinstyle="round", antialiased=True))
    ax.set_xlim(.08, 2.92); ax.set_ylim(.06, .94)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig


if __name__ == "__main__":
    semilla = int(sys.argv[1]) if len(sys.argv) > 1 else \
        int(np.random.default_rng().integers(1, 1_000_000))
    fig = pieza(semilla)
    fig.savefig("imagenes/portada.png", dpi=155, facecolor=FONDO,
                bbox_inches="tight", pad_inches=0)
    print(f"imagenes/portada.png  ·  semilla {semilla}")

# =============================================================================
# Figuras de la primera parte del teórico "Las partes de un gráfico" (matplotlib)
# Valores de ozono leídos del gráfico original (media mensual, ene–abr 2024).
# Genera: partida.png, geometria.png, corregida.png en clases/clase9/imagenes
# =============================================================================
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

carpeta = Path("clases/clase9/imagenes")
carpeta.mkdir(parents=True, exist_ok=True)


def tema_minimal(ax):
    """Equivalente aproximado de theme_minimal(): sin marco, grilla suave."""
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.grid(True, color="#e5e5e5", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def guardar(fig, nombre):
    fig.savefig(carpeta / nombre, dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)


ozono_mes = pd.DataFrame({
    "mes":          [1, 2, 3, 4],
    "o3_medio_mes": [29.1, 35.5, 24.0, 25.7],
})

# --- El gráfico del que partimos (código de la clase 7, sección 4.2) ---------
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="blue", linewidth=2)
ax.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="red", s=60, zorder=3)
tema_minimal(ax)
ax.set_title("Concentración de Ozono en el ambiente, por mes, 2024", loc="left")
ax.set_xlabel("Fecha")
ax.set_ylabel("Valores")
guardar(fig, "partida.png")

# --- La geometría: dos capas separadas ---------------------------------------
fig, (ax_linea, ax_puntos) = plt.subplots(1, 2, figsize=(10, 4))

ax_linea.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="blue", linewidth=2)
tema_minimal(ax_linea)
ax_linea.set_title("Solo geom_line()", loc="left")

ax_puntos.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="red", s=60, zorder=3)
tema_minimal(ax_puntos)
ax_puntos.set_title("Solo geom_point()", loc="left")

guardar(fig, "geometria.png")

# --- Una versión corregida ---------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="blue", linewidth=2)
ax.scatter(ozono_mes["mes"], ozono_mes["o3_medio_mes"], color="red", s=60, zorder=3)
ax.set_xticks([1, 2, 3, 4], ["Ene", "Feb", "Mar", "Abr"])
ax.set_ylim(0, 40)
ax.set_yticks(range(0, 41, 5))
tema_minimal(ax)
ax.set_title("Ozono troposférico: media mensual, enero a abril de 2024", loc="left")
ax.set_xlabel("Mes (2024)")
ax.set_ylabel("Ozono (µg/m³)")
fig.text(0.99, 0.01, "Fuente: valores leídos del gráfico original.",
         ha="right", va="bottom", fontsize=8, color="gray")
guardar(fig, "corregida.png")

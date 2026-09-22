"""
CLASE 12 — Comparar curvas y análisis de cohortes
Unidad 7: datos censurados (8 h)

OBJETIVO
  Contrastar la supervivencia entre grupos y leer una tabla de cohortes,
  que es la herramienta estándar de retención en negocios.

IDEA CENTRAL
  Una cohorte es un panel mirado desde el momento de entrada de cada unidad,
  no desde el calendario.
"""
import numpy as np
import pandas as pd
from scipy import stats
from _comun import guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import clientes_supervivencia

df = clientes_supervivencia()

def kaplan_meier(dur, ev):
    t = np.sort(np.unique(dur[ev == 1]))
    S, out = 1.0, []
    for ti in t:
        n = (dur >= ti).sum()
        d = ((dur == ti) & (ev == 1)).sum()
        S *= (1 - d / n)
        out.append((ti, S))
    return pd.DataFrame(out, columns=["t", "S"])

titulo("1. Curvas por plan")
plt.figure(figsize=(8, 4.5))
for plan, g in df.groupby("plan"):
    km = kaplan_meier(g["duracion"].values, g["evento"].values)
    plt.step(np.r_[0, km["t"]], np.r_[1, km["S"]], where="post", lw=2, label=plan)
    s12 = km.loc[km["t"] <= 12, "S"]
    print(f"  {plan:<8} n={len(g):4d}  eventos={g['evento'].sum():4d}  "
          f"S(12 meses)={s12.iloc[-1] if len(s12) else 1:.3f}")
plt.legend(); plt.ylim(0, 1); plt.xlabel("meses"); plt.ylabel("activos")
plt.title("Supervivencia por plan")
guardar("clase12_km_planes.png")

titulo("2. ¿La diferencia es real? Prueba de rangos logarítmicos (log-rank)")
def log_rank(d1, e1, d2, e2):
    """Compara dos curvas comparando eventos observados contra esperados."""
    tiempos = np.sort(np.unique(np.r_[d1[e1 == 1], d2[e2 == 1]]))
    O1 = E1 = V = 0.0
    for t in tiempos:
        n1, n2 = (d1 >= t).sum(), (d2 >= t).sum()
        n = n1 + n2
        d = ((d1 == t) & (e1 == 1)).sum() + ((d2 == t) & (e2 == 1)).sum()
        if n < 2 or d == 0:
            continue
        O1 += ((d1 == t) & (e1 == 1)).sum()
        E1 += d * n1 / n
        V += d * (n1/n) * (1 - n1/n) * (n - d) / (n - 1)
    chi2 = (O1 - E1) ** 2 / V
    return chi2, 1 - stats.chi2.cdf(chi2, 1)

a = df[df["plan"] == "basico"]
b = df[df["plan"] == "premium"]
chi2, p = log_rank(a["duracion"].values, a["evento"].values,
                   b["duracion"].values, b["evento"].values)
print(f"  chi cuadrado = {chi2:.2f}   valor p = {p:.5f}")
print(">> Compara las curvas ENTERAS, no la supervivencia en un punto elegido.")

titulo("3. Tabla de cohortes: retención por mes de alta")
horizonte = 12
filas = []
for cohorte, g in df.groupby("cohorte_alta"):
    km = kaplan_meier(g["duracion"].values, g["evento"].values)
    fila = {"cohorte": cohorte, "n": len(g)}
    for m in range(3, horizonte + 1, 3):
        s = km.loc[km["t"] <= m, "S"]
        fila[f"mes_{m}"] = round(s.iloc[-1] if len(s) else 1.0, 3)
    filas.append(fila)
tabla = pd.DataFrame(filas).set_index("cohorte")
print(tabla.to_string())
print(">> Se lee en dos direcciones: hacia abajo compara cohortes,")
print(">> a lo ancho sigue la vida de una misma cohorte.")

titulo("4. Cuidado con las cohortes recientes")
print(tabla["n"].to_string())
print(">> Las cohortes tardías tienen menos seguimiento: sus celdas lejanas")
print(">> están estimadas con muy pocos datos. No compares peras con manzanas.")

cols = [c for c in tabla.columns if c.startswith("mes_")]
plt.figure(figsize=(7, 4.5))
plt.imshow(tabla[cols].values, aspect="auto", cmap="Blues_r", vmin=0, vmax=1)
plt.colorbar(label="retención")
plt.yticks(range(len(tabla)), tabla.index)
plt.xticks(range(len(cols)), cols)
plt.title("Mapa de calor de cohortes")
guardar("clase12_cohortes.png")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Dividí tu población en dos grupos con sentido de negocio y compará
   sus curvas con log-rank.
2. Construí la tabla de cohortes de tu conjunto de datos.
3. ¿Alguna cohorte se comporta distinto? Buscá qué pasó en ese período:
   una cohorte anómala casi siempre tiene una explicación operativa.
"""

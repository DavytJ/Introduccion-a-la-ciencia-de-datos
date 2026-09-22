"""
CLASE 05 — ¿Difieren estos grupos?
Unidad 3: comparación (4 h)

OBJETIVO
  Comparar grupos sin depender de supuestos distribucionales, y no engañarse
  al probar muchas hipótesis a la vez.

IDEA CENTRAL
  Si probás cien hipótesis con alfa = 0.05, cinco te van a dar significativas
  aunque no pase absolutamente nada.
"""
import numpy as np
import pandas as pd
from scipy import stats
from _comun import SEMILLA, guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import encuesta_estudiantes

rng = np.random.default_rng(SEMILLA)
df = encuesta_estudiantes()

titulo("1. Contraste clásico frente a prueba de permutación")
a = df.loc[df["carrera"] == "ADE", "p4_prefiere_seguro"]
b = df.loc[df["carrera"] == "Economia", "p4_prefiere_seguro"]
dif = a.mean() - b.mean()
t, p_t = stats.ttest_ind(a, b, equal_var=False)
print(f"Diferencia observada: {dif:+.3f}")
print(f"t de Welch: t={t:.3f}  p={p_t:.4f}")

juntos = np.concatenate([a, b])
nulos = []
for _ in range(10_000):
    rng.shuffle(juntos)
    nulos.append(juntos[:len(a)].mean() - juntos[len(a):].mean())
nulos = np.array(nulos)
p_perm = (np.abs(nulos) >= abs(dif)).mean()
print(f"Permutación (10.000): p={p_perm:.4f}")
print(">> Mismo resultado sin suponer normalidad. Es estadística por cómputo.")

plt.figure(figsize=(8, 3.5))
plt.hist(nulos, bins=60, color="lightgray")
plt.axvline(dif, color="crimson", label="diferencia observada")
plt.legend(); plt.title("Distribución nula por permutación")
guardar("clase05_permutacion.png")

titulo("2. Significación no es magnitud")
d_cohen = dif / np.sqrt(((len(a)-1)*a.var() + (len(b)-1)*b.var()) / (len(a)+len(b)-2))
print(f"d de Cohen: {d_cohen:.3f}")
print(">> Con n grande, diferencias irrelevantes salen significativas.")
print(">> Reportar SIEMPRE el tamaño del efecto junto al valor p.")

titulo("3. El problema de las pruebas múltiples")
# 60 comparaciones sobre datos donde NO hay ningún efecto real
p_falsos = [stats.ttest_ind(rng.normal(size=80), rng.normal(size=80)).pvalue
            for _ in range(60)]
p_falsos = np.array(p_falsos)
print(f"Comparaciones: 60   Efectos reales: 0")
print(f"'Significativas' con alfa=0.05: {(p_falsos < 0.05).sum()}")

titulo("4. Dos correcciones")
m = len(p_falsos)
bonf = p_falsos < 0.05 / m
orden = np.argsort(p_falsos)
umbral_bh = 0.05 * (np.arange(1, m + 1)) / m
significativos_bh = p_falsos[orden] <= umbral_bh
k = np.where(significativos_bh)[0].max() + 1 if significativos_bh.any() else 0
print(f"Bonferroni (controla el error familiar) : {bonf.sum()} significativas")
print(f"Benjamini-Hochberg (controla la tasa de falsos descubrimientos): {k}")
print(">> Bonferroni es conservador; BH es el estándar cuando hay muchas pruebas.")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Elegí dos grupos de tu conjunto de datos y compará una variable con
   permutación. Reportá diferencia, p y tamaño del efecto.
2. Contá cuántas comparaciones hiciste en total durante la exploración,
   incluidas las que descartaste. Ese es tu m real.
3. Aplicá Benjamini-Hochberg sobre todas. ¿Sobrevive tu hallazgo?
"""

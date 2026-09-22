"""
CLASE 09 — Estacionariedad y regresión espuria
Unidad 5: series temporales (12 h)

OBJETIVO
  Entender por qué dos series sin ninguna relación pueden dar una regresión
  con R² altísimo y coeficiente muy significativo.

IDEA CENTRAL
  El error más caro con series temporales no es de cómputo: es regresar
  niveles no estacionarios y creerle al resultado.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss
from _comun import SEMILLA, guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import dos_series_no_estacionarias

import warnings
warnings.filterwarnings("ignore")

df = dos_series_no_estacionarias()

titulo("1. Dos caminatas aleatorias INDEPENDIENTES por construcción")
print("Generadas con ruidos totalmente separados: la relación verdadera es CERO.")

titulo("2. Regresión en niveles")
X = sm.add_constant(df["x"])
m = sm.OLS(df["y"], X).fit()
print(f"  coeficiente = {m.params['x']:+.3f}")
print(f"  valor p     = {m.pvalues['x']:.5f}")
print(f"  R cuadrado  = {m.rsquared:.3f}")
print(f"  Durbin-Watson = {sm.stats.durbin_watson(m.resid):.2f}   (lejos de 2 = alarma)")
print(">> Todo 'significativo'. Y no hay ninguna relación.")

titulo("3. Contrastes de raíz unitaria")
for nombre in ["x", "y"]:
    p_adf = adfuller(df[nombre])[1]
    p_kpss = kpss(df[nombre], regression="c", nlags="auto")[1]
    print(f"  {nombre}: ADF p={p_adf:.3f} (H0: raíz unitaria) | "
          f"KPSS p={p_kpss:.3f} (H0: estacionaria)")
print(">> ADF no rechaza y KPSS rechaza: ambas series son no estacionarias.")
print(">> Se usan los dos contrastes porque tienen hipótesis nulas opuestas.")

titulo("4. La misma regresión en diferencias")
d = df.diff().dropna()
m2 = sm.OLS(d["y"], sm.add_constant(d["x"])).fit()
print(f"  coeficiente = {m2.params['x']:+.3f}")
print(f"  valor p     = {m2.pvalues['x']:.3f}")
print(f"  R cuadrado  = {m2.rsquared:.3f}")
print(">> Diferenciando desaparece el resultado. Era espurio.")

titulo("5. ¿Cuán frecuente es el problema?")
rng = np.random.default_rng(SEMILLA)
significativas = 0
for _ in range(500):
    a = np.cumsum(rng.normal(size=150))
    b = np.cumsum(rng.normal(size=150))
    if sm.OLS(b, sm.add_constant(a)).fit().pvalues[1] < 0.05:
        significativas += 1
print(f"De 500 pares independientes, dieron 'significativos': {significativas} ({significativas/5:.0f} %)")
print(">> Deberían ser el 5 %. Es un problema estructural, no mala suerte.")

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(df.index, df["x"], label="x"); ax[0].plot(df.index, df["y"], label="y")
ax[0].set_title("Niveles: parecen relacionadas"); ax[0].legend()
ax[1].plot(d.index, d["x"], alpha=.7); ax[1].plot(d.index, d["y"], alpha=.7)
ax[1].set_title("Diferencias: ruido puro")
guardar("clase09_espuria.png")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Aplicá ADF y KPSS a todas las series de tu conjunto de datos.
2. Si tu proyecto relaciona dos series en niveles, repetí el análisis en
   diferencias y compará. ¿Sobrevive el hallazgo?
3. Buscá en la web un gráfico de "correlaciones espurias" y explicá con lo
   visto hoy por qué la correlación es alta.
"""

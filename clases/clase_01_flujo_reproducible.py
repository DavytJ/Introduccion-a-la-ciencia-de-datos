"""
CLASE 01 — Un análisis que otro pueda repetir
Unidad 1: el dato todavía no existe (4 h)

OBJETIVO
  Que el resultado no dependa de quién lo corrió, ni de la carpeta, ni del día.

IDEA CENTRAL
  Un resultado que no se puede regenerar no es un resultado: es una anécdota.
"""
import numpy as np
import pandas as pd
from _comun import RAIZ, SALIDAS, SEMILLA, guardar, titulo
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- 1. Semillas
titulo("1. Sin semilla no hay reproducibilidad")

sin_semilla_a = np.random.default_rng().normal(size=5).round(3)
sin_semilla_b = np.random.default_rng().normal(size=5).round(3)
print("Dos corridas sin semilla:", sin_semilla_a, sin_semilla_b, sep="\n  ")

con_semilla_a = np.random.default_rng(SEMILLA).normal(size=5).round(3)
con_semilla_b = np.random.default_rng(SEMILLA).normal(size=5).round(3)
print("Dos corridas con semilla:", con_semilla_a, con_semilla_b, sep="\n  ")
print("¿Idénticas?", np.array_equal(con_semilla_a, con_semilla_b))

# ------------------------------------------------------------------ 2. Rutas
titulo("2. Rutas relativas, nunca absolutas")
# MAL:  pd.read_csv("C:/Users/diego/Escritorio/datos.csv")   -> falla en otra máquina
# BIEN: rutas construidas desde la raíz del proyecto
print("Raíz del proyecto:", RAIZ)
print("Carpeta de salidas:", SALIDAS)

# ----------------------------------------------------- 3. El análisis mínimo
titulo("3. Análisis reproducible de punta a punta")
from datos.generador import ventas_mensuales

ventas = ventas_mensuales()
resumen = ventas["ventas"].describe().round(1)
print(resumen)

ventas.to_csv(SALIDAS / "clase01_ventas.csv")
resumen.to_csv(SALIDAS / "clase01_resumen.csv")

plt.figure(figsize=(9, 3.5))
plt.plot(ventas.index, ventas["ventas"])
plt.title("Ventas mensuales")
plt.ylabel("unidades")
guardar("clase01_ventas.png")

# --------------------------------------------------- 4. Registro de la sesión
titulo("4. Dejar constancia del entorno")
import sys, platform
registro = {
    "python": sys.version.split()[0],
    "sistema": platform.system(),
    "numpy": np.__version__,
    "pandas": pd.__version__,
    "semilla": SEMILLA,
}
pd.Series(registro).to_csv(SALIDAS / "clase01_entorno.csv")
for k, v in registro.items():
    print(f"  {k}: {v}")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO (en equipo, se entrega por commit)

1. Cloná el repositorio del equipo y creá la estructura datos/ clases/ salidas/.
2. Corré este script y verificá que las tres salidas se generan.
3. Modificá SEMILLA en _comun.py, volvé a correr y explicá en la bitácora
   qué cambió y qué no. ¿Por qué el gráfico de ventas NO cambia?
4. Escribí la primera entrada de bitácora (máx. 150 palabras):
   qué intentamos, qué falló, qué decidimos.
"""

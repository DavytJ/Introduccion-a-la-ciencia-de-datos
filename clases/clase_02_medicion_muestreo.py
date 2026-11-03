"""
CLASE 02 — Medir y relevar: el dato no existe hasta que alguien lo construye
Unidad 1: el dato todavía no existe (4 h)

OBJETIVO
  Ver cómo las decisiones de muestreo determinan el resultado, comparando
  contra una población que conocemos entera.

IDEA CENTRAL
  Estadística enseña muestreo aleatorio simple. El mundo casi nunca lo es.
"""
import numpy as np
import pandas as pd
from _comun import SEMILLA, guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import poblacion_empresas

rng = np.random.default_rng(SEMILLA)
pob = poblacion_empresas()
VERDAD = pob["facturacion"].mean()

titulo("0. La verdad (que en la vida real no conocemos)")
print(f"Facturación media poblacional: {VERDAD:,.0f}")
print(pob.groupby("sector")["facturacion"].agg(["count", "mean"]).round(0))

# --------------------------------------------- 1. Muestreo aleatorio simple
titulo("1. Muestreo aleatorio simple (n = 200)")
mas = pob.sample(200, random_state=SEMILLA)
print(f"Estimación: {mas['facturacion'].mean():,.0f}   error: {mas['facturacion'].mean()-VERDAD:+,.0f}")

# ------------------------------------------------------- 2. Muestra sesgada
titulo("2. Muestra por conveniencia: solo empresas grandes responden")
prob = np.where(pob["empleados"] > pob["empleados"].median(), 0.8, 0.2)
conv = pob[rng.random(len(pob)) < prob].sample(200, random_state=SEMILLA)
print(f"Estimación: {conv['facturacion'].mean():,.0f}   error: {conv['facturacion'].mean()-VERDAD:+,.0f}")
print(">> Más datos no arreglan un marco muestral sesgado.")

# --------------------------------------------------- 3. Muestreo estratificado
titulo("3. Muestreo estratificado por sector, con ponderadores")
partes = []
for sector, grupo in pob.groupby("sector"):
    partes.append(grupo.sample(40, random_state=SEMILLA).assign(
        ponderador=len(grupo) / 40))
estr = pd.concat(partes)
sin_pond = estr["facturacion"].mean()
con_pond = np.average(estr["facturacion"], weights=estr["ponderador"])
print(f"Sin ponderar: {sin_pond:,.0f}   error: {sin_pond-VERDAD:+,.0f}")
print(f"Ponderada:    {con_pond:,.0f}   error: {con_pond-VERDAD:+,.0f}")
print(">> Ignorar el ponderador es el error más común con datos de encuesta.")

# --------------------------------------------------------- 4. Distribución
titulo("4. Repetir el muestreo 500 veces")
sim = {"aleatorio": [], "conveniencia": []}
for _ in range(500):
    sim["aleatorio"].append(pob.sample(200)["facturacion"].mean())
    sesgada = pob[rng.random(len(pob)) < prob]
    sim["conveniencia"].append(sesgada.sample(200)["facturacion"].mean())

plt.figure(figsize=(8, 4))
for k, v in sim.items():
    plt.hist(v, bins=35, alpha=0.6, label=k)
plt.axvline(VERDAD, color="black", ls="--", label="valor poblacional")
plt.legend(); plt.title("Distribución de la media según el diseño muestral")
guardar("clase02_muestreo.png")
print(">> El sesgo no se ve en la dispersión: la muestra sesgada es precisa y equivocada.")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. El equipo de encuestas: definí tu marco muestral. ¿A quién NO podés llegar?
2. Calculá el tamaño de muestra para estimar una proporción con un margen de
   error de 5 puntos y 95 % de confianza. ¿Es alcanzable en el curso?
3. Diseñá tres preguntas y anticipá qué sesgo de deseabilidad social tiene cada una.
4. Construí los ponderadores de expansión de tu diseño y documentalos.
"""

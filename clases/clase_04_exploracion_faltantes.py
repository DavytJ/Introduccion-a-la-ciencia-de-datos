"""
CLASE 04 — Exploración robusta y datos faltantes
Unidad 2: exploración y calidad (4 h)

OBJETIVO
  Describir sin dejarse engañar por colas y atípicos, y entender que la
  ausencia de un dato es información.

IDEA CENTRAL
  Los faltantes casi nunca son aleatorios, y la imputación es un supuesto,
  no una operación técnica.
"""
import numpy as np
import pandas as pd
from _comun import guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import encuesta_estudiantes

df = encuesta_estudiantes()

titulo("1. La media no describe una distribución asimétrica")
ing = df["ingreso_mensual"].dropna()
print(f"media    : {ing.mean():>10,.0f}")
print(f"mediana  : {ing.median():>10,.0f}")
print(f"desvío   : {ing.std():>10,.0f}")
print(f"MAD      : {(ing - ing.median()).abs().median():>10,.0f}   <- robusta")
print("\nCuantiles:\n", ing.quantile([.05, .25, .5, .75, .95]).round(0))

titulo("2. Winsorización: acotar sin borrar")
lim_inf, lim_sup = ing.quantile([0.01, 0.99])
wins = ing.clip(lim_inf, lim_sup)
print(f"media original    : {ing.mean():,.0f}")
print(f"media winsorizada : {wins.mean():,.0f}")
print(">> Winsorizar cambia el resultado. Es una decisión, y se declara.")

titulo("3. ¿Los faltantes son aleatorios?")
df["falta_ingreso"] = df["ingreso_mensual"].isna()
print(f"Porcentaje faltante: {df['falta_ingreso'].mean()*100:.1f} %")
print("\nComparación de quienes responden y quienes no:")
print(df.groupby("falta_ingreso")[["edad", "semestre", "p1_interes_compuesto"]].mean().round(2))
print("""
  MCAR : la ausencia no depende de nada          -> borrar no sesga
  MAR  : depende de variables observadas          -> imputación condicional
  MNAR : depende del valor ausente mismo          -> ningún método lo arregla solo
""")

titulo("4. Tres estrategias, tres respuestas distintas")
media_borrado = df["ingreso_mensual"].mean()
imp_media = df["ingreso_mensual"].fillna(df["ingreso_mensual"].mean()).mean()
imp_grupo = (df.groupby("carrera")["ingreso_mensual"]
               .transform(lambda s: s.fillna(s.mean()))).mean()
print(f"Borrado de casos    : {media_borrado:,.0f}")
print(f"Imputación por media: {imp_media:,.0f}   (no cambia la media, sí reduce la varianza)")
print(f"Imputación por grupo: {imp_grupo:,.0f}")
print(">> Ninguna recupera el dato. Elegís qué supuesto estás dispuesto a defender.")

titulo("5. Mapa de faltantes")
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].hist(ing, bins=40); ax[0].set_title("Ingreso declarado")
ax[1].imshow(df[["edad", "semestre", "ingreso_mensual"]].isna().T,
             aspect="auto", cmap="Greys", interpolation="none")
ax[1].set_yticks(range(3), ["edad", "semestre", "ingreso"])
ax[1].set_title("Mapa de faltantes (negro = ausente)")
guardar("clase04_faltantes.png")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Calculá el porcentaje de faltantes por variable de tu conjunto de datos.
2. Para la variable con más ausencias, contrastá si quienes tienen el dato
   difieren de quienes no lo tienen. ¿MCAR, MAR o MNAR? Argumentá.
3. Repetí tu estadístico principal con borrado y con imputación.
   Si el resultado cambia, esa diferencia va en el informe final.
"""

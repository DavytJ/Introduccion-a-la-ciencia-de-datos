# =============================================================================
# Clase 12. Tránsito y calidad del aire, junio de 2024 — Soluciones de los ejercicios 1 a 4
# Versión en Python (pandas + matplotlib + statsmodels)
# =============================================================================
#
# LA TABLA (transito_aire_junio2024.csv): una fila por estación y hora
#   estacion   estación de calidad de aire (tres estaciones)
#   hora       fecha y hora de la medición
#   transito   vehículos por hora cerca de la estación
#   no2        dióxido de nitrógeno, promedio de la hora (µg/m³)
#   pm25       material particulado fino, promedio de la hora (µg/m³)
#
# CÓMO SE USA ESTE ARCHIVO
#   Correr primero la PREPARACIÓN (es la misma que la de clase12_ejercicios.py)
#   y después cada solución, en orden.
#
#   El archivo está dividido en celdas con #%%. En VS Code cada celda se
#   corre con Shift + Enter, de arriba hacia abajo.
#
# Paquetes (instalar una sola vez, en la terminal):
#   pip install pandas numpy matplotlib statsmodels
# =============================================================================

#%%
# =============================================================================
# PREPARACIÓN
# =============================================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

# Para que print() muestre todas las columnas de una tabla, sin cortarla con "...".
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

RUTA = "clases/clase10/transito_aire_junio2024.csv"   # cambiar si los datos están en otra carpeta

COL_TRANSITO = "#2E86AB"
COL_NO2      = "#7B4B2A"
COL_PM25     = "#D4A373"
COL_OSCURO   = "#5C3A21"

# ---- La tabla original -------------------------------------------------------
# parse_dates le dice a pandas que la columna hora es una fecha.
aire = pd.read_csv(RUTA, parse_dates=["hora"])

# ---- Variables nuevas --------------------------------------------------------
datos = aire.copy()

# La hora del día, de 0 a 23.
datos["h"] = datos["hora"].dt.hour

# dayofweek da el día de la semana: lunes = 0, ..., sábado = 5, domingo = 6.
# np.where(condición, valor_si_se_cumple, valor_si_no)
datos["tipo_dia"] = np.where(datos["hora"].dt.dayofweek >= 5,
                             "fin de semana", "lunes a viernes")

# isin() da True cuando h es alguno de los valores de la lista.
datos["hora_pico"] = np.where(datos["h"].isin([7, 8, 9, 17, 18, 19]),
                              "hora pico", "resto")

# pd.cut() corta h en intervalos: de 0 a 5, de 6 a 11, de 12 a 17, de 18 a 23.
# El resultado es una variable categórica que guarda el orden de las franjas.
datos["franja"] = pd.cut(datos["h"], bins=[-1, 5, 11, 17, 23],
                         labels=["madrugada", "mañana", "tarde", "noche"])

# Tránsito relativo: 1 es lo habitual de la estación, 2 es el doble.
# transform("mean") pone en cada fila el promedio de su estación.
datos["transito_rel"] = datos["transito"] / datos.groupby("estacion")["transito"].transform("mean")

datos["transito_miles"] = datos["transito"] / 1000
datos["log_pm25"] = np.log(datos["pm25"])

# ---- Promedios por estación y franja (para el ejercicio 3) -------------------
# observed=True: solo las combinaciones que aparecen en los datos.
por_franja = (datos.groupby(["estacion", "franja"], observed=True)
                   [["transito", "transito_rel", "no2", "pm25"]]
                   .mean()
                   .reset_index())
print(por_franja.round(1))

ESTACIONES = sorted(datos["estacion"].unique())

# ---- Tres Cruces, solo las horas con NO2 (para los ejercicios 4 a 7) ---------
# .copy() hace una tabla nueva, a la que después se le pueden agregar columnas.
tc = datos[(datos["estacion"] == "Tres Cruces") & datos["no2"].notna()].copy()

# smf.ols("y ~ x1 + x2", data=tabla) busca la recta, como lm() en R.
# Las filas con algún faltante en esas columnas quedan afuera.
modelo_tc3 = smf.ols("no2 ~ transito_miles + pm25", data=tc).fit()
print(modelo_tc3.params)
print(modelo_tc3.rsquared)          # 0,47


#%%
# =============================================================================
# EJERCICIO 1. FALTANTES
# =============================================================================
columnas = ["transito", "no2", "pm25", "franja", "tipo_dia", "transito_rel", "log_pm25"]
faltantes = datos[columnas].isna().groupby(datos["estacion"]).sum()
print(faltantes)
# 3. Solo log_pm25 tiene faltantes, y son los mismos que los de pm25
#    (0 en Curva de Maronias, 144 en Museo Romántico, 326 en Tres Cruces).
#    Si falta pm25, no se puede calcular su logaritmo: una variable que se
#    calcula a partir de otra tiene los mismos faltantes que ella.


#%%
# =============================================================================
# EJERCICIO 2. ¿ESTÁ BIEN DEFINIDA LA HORA PICO?
# =============================================================================
# 1. Las 7, las 18 y las 19 están marcadas como hora pico, pero tienen menos
#    tránsito que las horas de 10 a 16. No hay dos picos: el tránsito es
#    alto todo el día, de 8 a 17.

# 2. Hay más de una respuesta válida. Una: las horas de 8 a 17.
datos["transito_alto"] = np.where((datos["h"] >= 8) & (datos["h"] <= 17),
                                  "tránsito alto", "resto")
print(datos["transito_alto"].value_counts())    # 900 tránsito alto y 1260 resto

# 3. El mismo código, cambiando hora_pico por transito_alto.
semana_tc = datos[(datos["estacion"] == "Tres Cruces") &
                  (datos["tipo_dia"] == "lunes a viernes")]
por_hora = semana_tc.groupby(["h", "transito_alto"])["transito"].mean().reset_index()
colores = por_hora["transito_alto"].map({"tránsito alto": COL_OSCURO, "resto": "lightgrey"})

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(por_hora["h"], por_hora["transito"], color=colores)
ax.set_title("Tránsito promedio por hora del día, Tres Cruces, lunes a viernes")
ax.set_xlabel("Hora del día (en color: tránsito alto)")
ax.set_ylabel("Vehículos por hora")
plt.show()
# Ojo: en el diccionario de map() también hay que cambiar el nombre de la
# categoría. Si queda "hora pico", ninguna barra recibe el color oscuro.


#%%
# =============================================================================
# EJERCICIO 3. PM2.5 POR FRANJA HORARIA
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
for ax, est in zip(axes, ESTACIONES):
    parte = por_franja[por_franja["estacion"] == est]
    ax.bar(parte["franja"].astype(str), parte["pm25"], color=COL_PM25)
    ax.set_title(est)
axes[0].set_ylabel("PM2.5 (µg/m³)")
fig.suptitle("PM2.5 promedio por franja horaria")
fig.tight_layout()     # acomoda los títulos para que no se pisen
plt.show()
# 3. El tránsito es máximo de tarde. El PM2.5 es máximo de noche
#    (Tres Cruces: 31,9 de noche contra 17,2 de tarde).
#    No es la misma franja: el PM2.5 de una franja no sigue al tránsito de
#    esa misma franja.


#%%
# =============================================================================
# EJERCICIO 4. AGREGAR UNA VARIABLE AL MODELO
# =============================================================================
modelo_tc4 = smf.ols("no2 ~ transito_miles + pm25 + franja", data=tc).fit()
print(modelo_tc4.params)
print(modelo_tc4.rsquared)
# 3. El R² pasa de 0,47 a 0,49: mejora poco, aunque el modelo tiene tres
#    coeficientes más.
# Cómo leer los coeficientes de la franja: la madrugada es la referencia.
#   franja[T.noche] = 6,2 quiere decir que, a igual tránsito y PM2.5, una
#   hora de la noche tiene 6,2 µg/m³ más de NO2 que una de la madrugada.
#   (En R el mismo coeficiente se llama franjanoche.)


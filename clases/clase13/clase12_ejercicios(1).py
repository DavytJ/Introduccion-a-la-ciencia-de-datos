# =============================================================================
# Clase 12. Tránsito y calidad del aire, junio de 2024 — Ejercicios
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
#   1. Correr la PREPARACIÓN. Arma las tablas y el modelo que usan los
#      ejercicios. No hay que cambiar nada ahí, salvo la ruta del archivo.
#   2. Resolver cada ejercicio en el espacio en blanco que tiene debajo.
#   3. Las soluciones de los ejercicios 1 a 4 están en clase12_soluciones.py.
#      Usarlas para comparar después de intentarlo.
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
# Este código cuenta los faltantes de la tabla aire:
#
# faltantes = aire[["transito", "no2", "pm25"]].isna().groupby(aire["estacion"]).sum()
# print(faltantes)
#
# isna() pone True donde falta el dato. sum() cuenta los True de cada estación.
#
# 1. Copiar el código y cambiarlo para contar los faltantes de la tabla datos.
# 2. Agregar a la lista las variables nuevas: franja, tipo_dia, transito_rel
#    y log_pm25.
# 3. ¿Qué variable nueva tiene faltantes? ¿De dónde salen?
# -----------------------------------------------------------------------------





#%%
# =============================================================================
# EJERCICIO 2. ¿ESTÁ BIEN DEFINIDA LA HORA PICO?
# =============================================================================
# hora_pico marca las horas 7, 8, 9, 17, 18 y 19.
# El gráfico muestra el tránsito promedio de cada hora del día en Tres Cruces,
# de lunes a viernes. Las horas pico están en color oscuro.

print(datos["hora_pico"].value_counts())

semana_tc = datos[(datos["estacion"] == "Tres Cruces") &
                  (datos["tipo_dia"] == "lunes a viernes")]
por_hora = semana_tc.groupby(["h", "hora_pico"])["transito"].mean().reset_index()

# map() cambia cada valor por el color que le toca en el diccionario.
colores = por_hora["hora_pico"].map({"hora pico": COL_OSCURO, "resto": "lightgrey"})

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(por_hora["h"], por_hora["transito"], color=colores)
ax.set_title("Tránsito promedio por hora del día, Tres Cruces, lunes a viernes")
ax.set_xlabel("Hora del día (en color: hora pico)")
ax.set_ylabel("Vehículos por hora")
plt.show()

# 1. Mirar el gráfico: ¿las barras oscuras son las más altas?
#    Anotar qué horas están mal clasificadas.
# 2. Crear en datos una variable nueva, con el nombre que elijan, que marque
#    las horas que según el gráfico tienen más tránsito.
# 3. Repetir el gráfico con la variable nueva en lugar de hora_pico.
# -----------------------------------------------------------------------------





#%%
# =============================================================================
# EJERCICIO 3. PM2.5 POR FRANJA HORARIA
# =============================================================================
# Este gráfico muestra el tránsito relativo por franja, una estación en cada
# panel. La línea punteada en 1 marca lo habitual de cada estación.

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
for ax, est in zip(axes, ESTACIONES):
    parte = por_franja[por_franja["estacion"] == est]
    ax.bar(parte["franja"].astype(str), parte["transito_rel"], color=COL_TRANSITO)
    ax.axhline(1, color="grey", linestyle="--")
    ax.set_title(est)
axes[0].set_ylabel("Tránsito relativo (1 = media de la estación)")
fig.suptitle("Tránsito por franja horaria, relativo a la media de la estación")
fig.tight_layout()     # acomoda los títulos para que no se pisen
plt.show()

# La tabla por_franja también tiene el promedio de pm25.
#
# 1. Copiar el código del gráfico y cambiarlo para graficar pm25 en lugar de
#    transito_rel. Cambiar también el título, el nombre del eje y el color
#    (COL_PM25).
# 2. La línea punteada en 1 ya no tiene sentido: sacarla.
# 3. ¿En qué franja es máximo el PM2.5? ¿Es la misma que la del tránsito?
# -----------------------------------------------------------------------------





#%%
# =============================================================================
# EJERCICIO 4. AGREGAR UNA VARIABLE AL MODELO
# =============================================================================
# El modelo modelo_tc3 explica el NO2 con el tránsito y el PM2.5:
#
# modelo_tc3 = smf.ols("no2 ~ transito_miles + pm25", data=tc).fit()
# print(modelo_tc3.params)
# print(modelo_tc3.rsquared)
#
# 1. Copiar el código y agregar la variable franja al modelo.
#    Guardarlo como modelo_tc4.
# 2. Mostrar los coeficientes y el R².
# 3. ¿Mejoró el R²? ¿Mucho o poco?
# -----------------------------------------------------------------------------





#%%
# =============================================================================
# EJERCICIO 5. UNA VARIABLE BINARIA A PARTIR DEL RESULTADO
# =============================================================================
# Para ver si cada coeficiente se distingue de cero:
#
# print(modelo_tc4.summary())
#
# De las tres franjas, solo la noche tiene un coeficiente que se distingue
# de cero.
#
# 1. Crear en tc la variable noche: vale 1 si la franja es "noche" y 0 si no.
#    Ayuda: np.where(condición, 1, 0)
# 2. Ajustar modelo_tc5 con transito_miles, pm25 y noche (sin franja).
# 3. Mostrar los coeficientes y el R². ¿Cuánto suma la noche?
# -----------------------------------------------------------------------------




#%%
# =============================================================================
# EJERCICIO 6. INTERACCIONES
# =============================================================================
# Este gráfico muestra la nube de Tres Cruces con un color por franja, y una
# recta para cada franja.

COL_FRANJA = {"madrugada": "#0072B2", "mañana": "#E69F00",
              "tarde": "#009E73", "noche": "#CC79A7"}

fig, ax = plt.subplots(figsize=(8, 5))
for f in ["madrugada", "mañana", "tarde", "noche"]:
    parte = tc[tc["franja"] == f]
    ax.scatter(parte["transito_miles"], parte["no2"], s=15, alpha=0.6,
               color=COL_FRANJA[f], label=f)
    # np.polyfit(x, y, 1) da la pendiente y la ordenada de la recta.
    pendiente, ordenada = np.polyfit(parte["transito_miles"], parte["no2"], 1)
    x = np.array([parte["transito_miles"].min(), parte["transito_miles"].max()])
    ax.plot(x, ordenada + pendiente * x, color=COL_FRANJA[f], linewidth=2)
ax.set_title("Tránsito y NO2 en Tres Cruces, por franja horaria")
ax.set_xlabel("Miles de vehículos por hora")
ax.set_ylabel("NO2 (µg/m³)")
ax.legend()
plt.show()
# Qué vemos: cada franja tiene su recta, y no son paralelas.

# Un modelo con interacción deja que la pendiente cambie según la franja.
# En la fórmula se escribe * en lugar de +:
#
# modelo_tc6 = smf.ols("no2 ~ transito_miles * franja", data=tc).fit()
#
# 1. Mirar el gráfico: ¿qué franja tiene la recta más empinada?
# 2. Crear en tc una variable binaria para esa franja: 1 si la hora es de
#    esa franja, 0 si no.
# 3. Ajustar modelo_tc7 con la interacción entre transito_miles y la
#    variable nueva. Mostrar los coeficientes y el R².
# -----------------------------------------------------------------------------




#%%
# =============================================================================
# EJERCICIO 7. ¿QUÉ PASA EN LA TARDE?
# =============================================================================
# En el gráfico del ejercicio 6 los puntos de la tarde forman dos grupos
# separados.
#
# 1. Crear la tabla tarde con las filas de tc cuya franja es "tarde".
# 2. Copiar el código del gráfico del ejercicio 6 y cambiarlo para usar la
#    tabla tarde y colorear por tipo_dia en lugar de franja.
#    Ayuda: hay que cambiar la lista que recorre el for por
#    ["lunes a viernes", "fin de semana"], y armar un diccionario de colores
#    nuevo con esas dos categorías.
# 3. ¿Qué son los dos grupos?
# -----------------------------------------------------------------------------

"""
CLASE 07 — El tiempo como estructura: descomposición y estacionalidad
Unidad 5: series temporales (12 h)

OBJETIVO
  Reconocer las componentes de una serie y manipular el eje temporal
  sin romper la información.

IDEA CENTRAL
  En econometría la autocorrelación es un problema a corregir.
  Acá es la estructura que queremos describir.
"""
import numpy as np
import pandas as pd
from _comun import guardar, titulo
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from datos.generador import ventas_mensuales

s = ventas_mensuales()["ventas"]

titulo("1. El índice temporal no es una columna cualquiera")
print(f"Frecuencia: {s.index.freqstr}   Rango: {s.index.min():%Y-%m} a {s.index.max():%Y-%m}")
print(f"¿Hay huecos? {pd.date_range(s.index.min(), s.index.max(), freq='MS').difference(s.index).empty}")

titulo("2. Remuestreo: cambiar de frecuencia es agregar, y agregar es decidir")
print("Trimestral (suma):\n", s.resample("QS").sum().head(4).round(0))
print("\nTrimestral (media):\n", s.resample("QS").mean().head(4).round(0))
print(">> Sumar o promediar no da lo mismo. Depende de si la variable es flujo o stock.")

titulo("3. Descomposición")
desc = seasonal_decompose(s, model="additive", period=12)
print("Amplitud estacional:", round(desc.seasonal.max() - desc.seasonal.min(), 1))
print("Perfil estacional promedio por mes:")
perfil = desc.seasonal.groupby(desc.seasonal.index.month).mean().round(1)
print(perfil.to_string())

fig = desc.plot()
fig.set_size_inches(9, 7)
guardar("clase07_descomposicion.png")

titulo("4. Autocorrelación: la memoria de la serie")
fig, ax = plt.subplots(2, 1, figsize=(9, 6))
plot_acf(s, lags=30, ax=ax[0], title="Autocorrelación simple")
plot_pacf(s, lags=30, ax=ax[1], title="Autocorrelación parcial")
guardar("clase07_acf.png")
print(">> El pico en el rezago 12 es la estacionalidad anual.")

titulo("5. Ventanas móviles")
tabla = pd.DataFrame({
    "ventas": s,
    "media_movil_12": s.rolling(12).mean().round(1),
    "desvio_movil_12": s.rolling(12).std().round(1),
})
print(tabla.dropna().tail(5))

plt.figure(figsize=(9, 4))
plt.plot(s.index, s, alpha=0.5, label="observado")
plt.plot(s.index, s.rolling(12).mean(), lw=2, label="media móvil 12 meses")
plt.legend(); plt.title("Serie y tendencia suavizada")
guardar("clase07_movil.png")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Cargá tu serie y verificá que el índice sea temporal y sin huecos.
2. Descomponé la serie. ¿La estacionalidad es aditiva o multiplicativa?
   Probá las dos y compará los residuos.
3. ¿Qué explica el perfil estacional en términos del negocio o del sector?
   Si no podés explicarlo, puede ser un artefacto del calendario.
"""

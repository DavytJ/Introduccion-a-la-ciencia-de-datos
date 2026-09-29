"""
CLASE 08 — Pronóstico y validación fuera de muestra
Unidad 5: series temporales (12 h)

OBJETIVO
  Producir un pronóstico y evaluarlo de la única forma que vale:
  contra datos que el modelo no vio.

IDEA CENTRAL
  Partir la muestra al azar con datos temporales es hacer trampa:
  entrenás con el futuro para predecir el pasado.
"""
import numpy as np
import pandas as pd
from _comun import guardar, titulo
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datos.generador import ventas_mensuales

s = ventas_mensuales()["ventas"]
s.index.freq = "MS"          # declarar la frecuencia evita advertencias y errores

titulo("1. Partición cronológica, nunca aleatoria")
corte = int(len(s) * 0.8)
entren, prueba = s.iloc[:corte], s.iloc[corte:]
print(f"Entrenamiento: {entren.index.min():%Y-%m} a {entren.index.max():%Y-%m}  (n={len(entren)})")
print(f"Prueba       : {prueba.index.min():%Y-%m} a {prueba.index.max():%Y-%m}  (n={len(prueba)})")

titulo("2. Modelos de referencia: sin esto no sabés si tu modelo sirve")
ingenuo = np.repeat(entren.iloc[-1], len(prueba))
estacional = np.resize(entren.iloc[-12:].values, len(prueba))  # se repite el último ciclo

titulo("3. Holt-Winters (tendencia + estacionalidad)")
hw = ExponentialSmoothing(entren, trend="add", seasonal="add",
                          seasonal_periods=12).fit()
pred_hw = hw.forecast(len(prueba))

def errores(y, yhat, nombre):
    e = np.asarray(y) - np.asarray(yhat)
    mae = np.abs(e).mean()
    rmse = np.sqrt((e ** 2).mean())
    # MASE: error relativo al modelo ingenuo estacional en entrenamiento
    escala = np.abs(entren.values[12:] - entren.values[:-12]).mean()
    print(f"  {nombre:<22} MAE={mae:8.1f}  RMSE={rmse:8.1f}  MASE={mae/escala:5.2f}")

print("Desempeño en el conjunto de prueba:")
errores(prueba, ingenuo, "Ingenuo (último valor)")
errores(prueba, estacional, "Ingenuo estacional")
errores(prueba, pred_hw, "Holt-Winters")
print(">> MASE < 1 significa que el modelo le gana al ingenuo estacional.")
print(">> MAPE se evita: explota con valores cercanos a cero y castiga asimétricamente.")

titulo("4. Validación de origen móvil (walk-forward)")
errores_wf = []
for fin in range(corte, len(s) - 1):
    m = ExponentialSmoothing(s.iloc[:fin], trend="add", seasonal="add",
                             seasonal_periods=12).fit()
    errores_wf.append(s.iloc[fin] - m.forecast(1).iloc[0])
errores_wf = np.array(errores_wf)
print(f"Origen móvil, {len(errores_wf)} pronósticos a un paso:")
print(f"  MAE={np.abs(errores_wf).mean():.1f}   sesgo medio={errores_wf.mean():+.1f}")
print(">> Un sesgo medio alejado de cero indica que el modelo sistemáticamente")
print(">> sobreestima o subestima: es más grave que un MAE alto.")

plt.figure(figsize=(10, 4))
plt.plot(entren.index, entren, label="entrenamiento")
plt.plot(prueba.index, prueba, label="real", lw=2)
plt.plot(prueba.index, pred_hw, "--", label="Holt-Winters")
plt.axvline(prueba.index[0], color="gray", ls=":")
plt.legend(); plt.title("Pronóstico fuera de muestra")
guardar("clase08_pronostico.png")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Partí tu serie cronológicamente y ajustá Holt-Winters.
2. Comparalo SIEMPRE contra el ingenuo estacional. Si no le gana, decilo.
3. Corré la validación de origen móvil y graficá los errores en el tiempo.
   ¿Se degrada el modelo en algún período? ¿Qué pasó ahí?
"""

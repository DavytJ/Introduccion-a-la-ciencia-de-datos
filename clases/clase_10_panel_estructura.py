"""
CLASE 10 — Seguir muchas unidades a la vez: el panel
Unidad 6: estructura de panel (4 h)

OBJETIVO
  Construir un panel, diagnosticar su atrito y ver cómo la estructura
  de los datos cambia la inferencia.

IDEA CENTRAL
  Un panel no es una tabla más larga: las observaciones no son independientes,
  y tratarlas como si lo fueran infla la significación.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from _comun import guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import panel_sucursales

df = panel_sucursales()

titulo("1. Anatomía del panel")
print(f"Observaciones: {len(df)}")
print(f"Unidades: {df['sucursal'].nunique()}   Períodos: {df['fecha'].nunique()}")
print(f"Panel balanceado tendría: {df['sucursal'].nunique() * df['fecha'].nunique()} filas")
print(f">> Faltan {df['sucursal'].nunique()*df['fecha'].nunique() - len(df)} filas: es DESBALANCEADO.")

titulo("2. Atrito: ¿por qué salen las unidades?")
ultimo = df.groupby("sucursal")["fecha"].max()
cierra_antes = ultimo < df["fecha"].max()
print(f"Sucursales que dejan de aparecer: {cierra_antes.sum()} de {len(ultimo)}")
media_por_suc = df.groupby("sucursal")["ventas"].mean()
print(f"Venta media de las que siguen : {media_por_suc[~cierra_antes].mean():,.0f}")
print(f"Venta media de las que salen  : {media_por_suc[cierra_antes].mean():,.0f}")
print(">> El atrito NO es aleatorio. Analizar solo a los sobrevivientes sesga todo.")
print(">> Este es el sesgo de supervivencia visto desde adentro de la estructura.")

titulo("3. Mapa de cobertura unidad x tiempo")
cobertura = df.pivot_table(index="sucursal", columns="fecha",
                           values="ventas", aggfunc="size").notna()
plt.figure(figsize=(10, 5))
plt.imshow(cobertura.values, aspect="auto", cmap="Greys", interpolation="none")
plt.xlabel("período"); plt.ylabel("sucursal")
plt.title("Cobertura del panel (negro = observado)")
guardar("clase10_panel.png")

titulo("4. Formato largo y formato ancho")
ancho = df.pivot(index="fecha", columns="sucursal", values="ventas")
print(f"Largo: {df.shape}   Ancho: {ancho.shape}")
print(">> Largo para modelar, ancho para calcular correlaciones entre unidades.")

titulo("5. La estructura cambia los errores estándar")
ols = smf.ols("ventas ~ promocion", data=df).fit()
agrup = smf.ols("ventas ~ promocion", data=df).fit(
    cov_type="cluster", cov_kwds={"groups": df["sucursal"]})
print(f"  OLS ingenuo      : coef={ols.params['promocion']:7.1f}  ee={ols.bse['promocion']:6.1f}  t={ols.tvalues['promocion']:5.2f}")
print(f"  Errores agrupados: coef={agrup.params['promocion']:7.1f}  ee={agrup.bse['promocion']:6.1f}  t={agrup.tvalues['promocion']:5.2f}")
print(">> Mismo coeficiente, error estándar distinto. El OLS ingenuo trata")
print(">> 1.800 observaciones como independientes cuando hay solo 60 sucursales.")

titulo("6. Efectos fijos como operación sobre los datos")
df["ventas_centradas"] = df["ventas"] - df.groupby("sucursal")["ventas"].transform("mean")
dentro = smf.ols("ventas_centradas ~ promocion", data=df).fit()
print(f"  Restando la media de cada sucursal: coef={dentro.params['promocion']:.1f}")
print(">> Eso es la transformación 'dentro'. La teoría del estimador es de Econometría;")
print(">> acá importa entender qué le hace a los datos.")

titulo("7. Paradoja de Simpson: agregar puede invertir el signo")
# Ejemplo construido a propósito para que se vea el efecto
simpson = pd.DataFrame({
    "sucursal": ["A"] * 20 + ["B"] * 20,
    "publicidad": list(np.linspace(1, 5, 20)) + list(np.linspace(6, 10, 20)),
})
# Dentro de cada sucursal la relación es POSITIVA...
simpson["ventas"] = (simpson["publicidad"] * 8
                     + np.where(simpson["sucursal"] == "A", 200, 100))
glob = np.corrcoef(simpson["publicidad"], simpson["ventas"])[0, 1]
print(f"  Correlación agregando todo      : {glob:+.2f}")
for suc, g in simpson.groupby("sucursal"):
    print(f"  Correlación dentro de {suc}         : "
          f"{np.corrcoef(g['publicidad'], g['ventas'])[0,1]:+.2f}")
print(">> Positiva dentro de cada sucursal, negativa al agregar.")
print(">> Siempre verificar la relación DENTRO de las unidades antes de agregar.")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Armá tu panel desde las fuentes originales. ¿Cuál es la llave (unidad, tiempo)?
2. Graficá la cobertura. ¿Hay atrito? ¿Las unidades que salen son distintas?
3. Corré una regresión con y sin errores agrupados. Reportá las dos.
4. Verificá si tu relación principal cambia al desagregar por subgrupo.
"""

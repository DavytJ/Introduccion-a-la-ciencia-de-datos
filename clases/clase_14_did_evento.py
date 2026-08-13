"""
CLASE 14 — Efecto sin aleatorización: diferencias en diferencias y estudio de evento
Unidad 8: efecto (8 h)

OBJETIVO
  Estimar el efecto de una intervención cuando no hubo experimento,
  y entender de qué supuesto depende el resultado.

IDEA CENTRAL
  Sin aleatorización, el número que obtenés vale exactamente lo que valga
  el supuesto de tendencias paralelas. Y ese supuesto no se puede probar.
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from _comun import guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import did_locales

df = did_locales()

titulo("1. La comparación ingenua está mal")
post = df[df["post"] == 1]
print(f"  Tratados después : {post[post['tratado']==1]['ventas'].mean():,.0f}")
print(f"  Control después  : {post[post['tratado']==0]['ventas'].mean():,.0f}")
print(f"  Diferencia simple: {post[post['tratado']==1]['ventas'].mean() - post[post['tratado']==0]['ventas'].mean():+,.0f}")
print(">> Mezcla el efecto con las diferencias que ya existían antes.")

titulo("2. Diferencias en diferencias, a mano")
celdas = df.groupby(["tratado", "post"])["ventas"].mean().unstack()
celdas.index = ["control", "tratado"]; celdas.columns = ["antes", "despues"]
print(celdas.round(1).to_string())
dd = ((celdas.loc["tratado", "despues"] - celdas.loc["tratado", "antes"])
      - (celdas.loc["control", "despues"] - celdas.loc["control", "antes"]))
print(f"\n  Estimador DiD: {dd:+,.1f}   (el efecto real simulado es +180)")

titulo("3. El mismo estimador por regresión, con errores agrupados")
m = smf.ols("ventas ~ tratado * post", data=df).fit(
    cov_type="cluster", cov_kwds={"groups": df["local"]})
coef = m.params["tratado:post"]
ic = m.conf_int().loc["tratado:post"]
print(f"  Interacción tratado x post: {coef:+.1f}   IC 95 % [{ic[0]:+.1f}, {ic[1]:+.1f}]")
print(">> El coeficiente de la interacción ES el efecto. Los errores se agrupan")
print(">> por local, porque las observaciones de un mismo local no son independientes.")

titulo("4. El supuesto crítico: tendencias paralelas")
medias = df.groupby(["fecha", "tratado"])["ventas"].mean().unstack()
plt.figure(figsize=(9, 4.5))
plt.plot(medias.index, medias[0], label="control", marker="o", ms=3)
plt.plot(medias.index, medias[1], label="tratado", marker="s", ms=3)
plt.axvline(df.loc[df["post"] == 1, "fecha"].min(), color="crimson", ls="--",
            label="intervención")
plt.legend(); plt.title("Trayectorias antes y después")
guardar("clase14_did.png")
print(">> Se verifica MIRANDO EL PERÍODO PREVIO. Si las series no eran paralelas")
print(">> antes, el DiD no identifica nada. No hay contraste que lo salve.")

titulo("5. Estudio de evento: el efecto período a período")
df["periodo_rel"] = (df["fecha"].dt.to_period("M").astype("int64")
                     - df.loc[df["post"] == 1, "fecha"].min().to_period("M").ordinal)
sub = df[df["periodo_rel"].between(-6, 6)].copy()
efectos = []
for k, g in sub.groupby("periodo_rel"):
    efectos.append((k, g[g["tratado"] == 1]["ventas"].mean()
                       - g[g["tratado"] == 0]["ventas"].mean()))
ev = pd.DataFrame(efectos, columns=["periodo_rel", "brecha"])
print(ev.round(1).to_string(index=False))
print(">> Las brechas ANTES del evento deberían ser planas. Si ya venían creciendo,")
print(">> lo que medís no es el efecto de la intervención.")

plt.figure(figsize=(8, 4))
plt.axhline(ev.loc[ev["periodo_rel"] < 0, "brecha"].mean(), color="gray", ls=":")
plt.axvline(-0.5, color="crimson", ls="--")
plt.plot(ev["periodo_rel"], ev["brecha"], marker="o")
plt.xlabel("períodos respecto de la intervención"); plt.ylabel("brecha tratado - control")
plt.title("Estudio de evento")
guardar("clase14_evento.png")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Identificá una intervención real en tu conjunto de datos: un cambio de
   precio, una campaña, una norma, una fecha de corte.
2. Definí grupo tratado y grupo de comparación. Defendé la elección.
3. Estimá el DiD y graficá las trayectorias previas.
4. Escribí en dos líneas qué tendría que haber pasado para que tu estimación
   esté equivocada. Si no se te ocurre nada, no pensaste lo suficiente.
"""

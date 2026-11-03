"""
CLASE 13 — ¿Qué efecto tuvo? Experimentos A/B
Unidad 8: efecto (8 h)

OBJETIVO
  Diseñar y evaluar un experimento: potencia, tamaño de muestra y las
  trampas del análisis.

IDEA CENTRAL
  La aleatorización es la única forma barata de identificar un efecto causal.
  Todo lo demás requiere supuestos que hay que defender.
"""
import numpy as np
import pandas as pd
from scipy import stats
from _comun import SEMILLA, guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import experimento_ab

rng = np.random.default_rng(SEMILLA)

titulo("1. Tamaño de muestra ANTES de correr el experimento")
def n_necesario(p0, efecto_min, alfa=0.05, potencia=0.80):
    """Tamaño por rama para detectar una diferencia de proporciones."""
    p1 = p0 + efecto_min
    p_prom = (p0 + p1) / 2
    z_a = stats.norm.ppf(1 - alfa / 2)
    z_b = stats.norm.ppf(potencia)
    num = (z_a * np.sqrt(2 * p_prom * (1 - p_prom))
           + z_b * np.sqrt(p0 * (1 - p0) + p1 * (1 - p1))) ** 2
    return int(np.ceil(num / efecto_min ** 2))

for efecto in [0.005, 0.010, 0.020, 0.050]:
    print(f"  Para detectar {efecto:.1%} sobre una base de 8,5 %: "
          f"{n_necesario(0.085, efecto):>7,} por rama")
print(">> Detectar efectos chicos es carísimo. Si no tenés el n, no corras el test.")

titulo("2. El experimento")
df = experimento_ab()
res = df.groupby("grupo")["convirtio"].agg(["count", "sum", "mean"])
res.columns = ["n", "conversiones", "tasa"]
print(res.round(4).to_string())

c = df[df["grupo"] == "control"]["convirtio"]
t = df[df["grupo"] == "tratamiento"]["convirtio"]
dif = t.mean() - c.mean()
ee = np.sqrt(c.var(ddof=1)/len(c) + t.var(ddof=1)/len(t))
z = dif / ee
p = 2 * (1 - stats.norm.cdf(abs(z)))
print(f"\n  Diferencia: {dif:+.4f} ({dif/c.mean():+.1%} relativo)")
print(f"  IC 95 %   : [{dif-1.96*ee:+.4f}, {dif+1.96*ee:+.4f}]")
print(f"  valor p   : {p:.4f}")
print(">> El intervalo dice más que el valor p: muestra qué efectos son compatibles.")

titulo("3. Verificar el balance ANTES de mirar el resultado")
print(df.groupby("grupo")["ticket"].mean().round(1).to_string())
print(">> Si las covariables no están balanceadas, la aleatorización falló.")

titulo("4. Trampa 1: mirar el resultado todos los días")
falsos = 0
for _ in range(300):
    a = rng.binomial(1, 0.085, 3000)
    b = rng.binomial(1, 0.085, 3000)          # sin efecto real
    for corte in range(200, 3001, 200):       # 15 miradas
        _, pv = stats.ttest_ind(a[:corte], b[:corte])
        if pv < 0.05:
            falsos += 1
            break
print(f"  Experimentos SIN efecto declarados significativos: {falsos/3:.0f} %")
print(">> Debería ser 5 %. Espiar el resultado infla el error de tipo I.")
print(">> Solución: fijar el n de antemano, o usar pruebas secuenciales.")

titulo("5. Trampa 2: buscar el subgrupo que funcionó")
df["segmento"] = rng.choice(list("ABCDEFGH"), len(df))
hallazgos = []
for seg, g in df.groupby("segmento"):
    gc = g[g["grupo"] == "control"]["convirtio"]
    gt = g[g["grupo"] == "tratamiento"]["convirtio"]
    if len(gc) > 30 and len(gt) > 30:
        pv = stats.ttest_ind(gt, gc).pvalue
        hallazgos.append((seg, gt.mean()-gc.mean(), pv))
h = pd.DataFrame(hallazgos, columns=["segmento", "efecto", "p"]).sort_values("p")
print(h.round(4).to_string(index=False))
print(f">> Subgrupos con p < 0,05: {(h['p'] < 0.05).sum()} de {len(h)}.")
print(">> Cambiá la semilla y volvé a correr: con suficientes subgrupos,")
print(">> tarde o temprano aparece uno 'significativo' sin que exista efecto.")
print(">> Los subgrupos se declaran ANTES, o se corrigen por pruebas múltiples.")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Diseñá un experimento posible para tu proyecto: unidad de aleatorización,
   métrica principal (una sola), efecto mínimo que valdría la pena detectar.
2. Calculá el n necesario. ¿Es viable?
3. Si no podés aleatorizar, escribí por qué. Eso te lleva a la clase 14.
"""

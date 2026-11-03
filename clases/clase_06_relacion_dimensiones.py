"""
CLASE 06 — ¿Qué se mueve con qué? ¿Cuántas dimensiones hay?
Unidad 4: relación y estructura latente (4 h)

OBJETIVO
  Usar correlación y componentes principales para describir estructura,
  sin confundirlas con explicación causal.

IDEA CENTRAL
  PCA y análisis factorial no son lo mismo, y ninguno de los dos descubre causas.
"""
import numpy as np
import pandas as pd
from scipy import stats
from _comun import guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import rendimientos_sectoriales, encuesta_estudiantes

titulo("1. Pearson mide lineal; Spearman mide monótono")
x = np.linspace(1, 10, 120)
y = np.exp(x / 3)
print(f"Relación exponencial perfecta:")
print(f"  Pearson : {stats.pearsonr(x, y)[0]:.3f}")
print(f"  Spearman: {stats.spearmanr(x, y)[0]:.3f}")

titulo("2. Matriz de correlación de sectores productivos")
R = rendimientos_sectoriales()
C = R.corr()
print(C.round(2))

titulo("3. PCA: ¿cuántas fuentes comunes hay detrás?")
Z = (R - R.mean()) / R.std()               # estandarizar es obligatorio
autoval, autovec = np.linalg.eigh(Z.corr())
orden = np.argsort(autoval)[::-1]
autoval, autovec = autoval[orden], autovec[:, orden]
varianza = autoval / autoval.sum()

print("Varianza explicada por componente:")
for i, v in enumerate(varianza[:5], 1):
    print(f"  CP{i}: {v:6.1%}   acumulada: {varianza[:i].sum():6.1%}")

cargas = pd.DataFrame(autovec[:, :2] * np.sqrt(autoval[:2]),
                      index=R.columns, columns=["CP1", "CP2"])
print("\nCargas (correlación de cada sector con el componente):")
print(cargas.round(2))
print("""
  Interpretación: CP1 con cargas parejas y del mismo signo = factor común
  ('país'). CP2 separa sectores primarios de servicios = factor de commodities.
  El nombre lo ponemos nosotros; el método solo entrega números.
""")

titulo("4. ¿Cuántos componentes retener? Análisis paralelo")
rng = np.random.default_rng(1)
simulados = np.array([np.sort(np.linalg.eigvalsh(np.corrcoef(
    rng.normal(size=(len(R), R.shape[1])), rowvar=False)))[::-1]
    for _ in range(500)])
umbral = simulados.mean(axis=0)
retener = (autoval > umbral).sum()
print(f"Autovalores reales   : {autoval[:4].round(2)}")
print(f"Umbral por simulación: {umbral[:4].round(2)}")
print(f">> Retener {retener} componentes (los que superan al ruido puro).")

plt.figure(figsize=(7, 4))
plt.plot(range(1, len(autoval) + 1), autoval, "o-", label="datos")
plt.plot(range(1, len(autoval) + 1), umbral, "s--", label="ruido simulado")
plt.axhline(1, color="gray", lw=0.8)
plt.xlabel("componente"); plt.ylabel("autovalor"); plt.legend()
plt.title("Gráfico de sedimentación con análisis paralelo")
guardar("clase06_pca.png")

titulo("5. Análisis factorial: validar un cuestionario")
enc = encuesta_estudiantes()
items = ["p1_interes_compuesto", "p2_inflacion", "p3_diversificacion",
         "p4_prefiere_seguro", "p5_evita_perdidas", "p6_ahorro_precaucion"]
Ci = enc[items].corr()
av, ave = np.linalg.eigh(Ci)
o = np.argsort(av)[::-1]
cargas_items = pd.DataFrame(ave[:, o][:, :2] * np.sqrt(av[o][:2]),
                            index=items, columns=["F1", "F2"])
print(cargas_items.round(2))
print(">> Los ítems se agrupan en dos bloques: el cuestionario mide dos cosas,")
print(">> no una. Si el equipo de encuestas quería un solo índice, está en problemas.")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO

1. Construí la matriz de correlación de tu conjunto de datos con Pearson y
   con Spearman. ¿Dónde difieren y por qué?
2. Aplicá PCA. ¿Cuántos componentes retiene el análisis paralelo?
3. Intentá nombrar los dos primeros componentes. Si no podés, decilo:
   un componente sin interpretación es un resultado válido.
4. Equipo de encuestas: verificá si tus ítems miden un constructo o varios.
"""

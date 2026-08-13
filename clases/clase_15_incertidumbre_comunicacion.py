"""
CLASE 15 — ¿Cuánto de esto me creo? Bootstrap, límites y comunicación
Unidad 9: incertidumbre y responsabilidad (4 h)

OBJETIVO
  Poner un intervalo alrededor de cualquier estadístico, y cerrar el curso
  con el catálogo de errores demostrado en código.

IDEA CENTRAL
  Un número sin incertidumbre no es un resultado, es una opinión con decimales.
"""
import numpy as np
import pandas as pd
from _comun import SEMILLA, guardar, titulo
import matplotlib.pyplot as plt
from datos.generador import encuesta_estudiantes, panel_sucursales

rng = np.random.default_rng(SEMILLA)

titulo("1. Bootstrap: inferencia sin fórmulas asintóticas")
def bootstrap(datos, estadistico, B=5000, alfa=0.05):
    datos = np.asarray(datos)
    reps = np.array([estadistico(rng.choice(datos, len(datos), replace=True))
                     for _ in range(B)])
    return reps, np.quantile(reps, [alfa/2, 1-alfa/2])

ing = encuesta_estudiantes()["ingreso_mensual"].dropna().values
for nombre, f in [("media", np.mean), ("mediana", np.median),
                  ("percentil 90", lambda x: np.quantile(x, .9)),
                  ("coef. de variación", lambda x: x.std()/x.mean())]:
    reps, ic = bootstrap(ing, f)
    print(f"  {nombre:<20} {f(ing):>10,.2f}   IC 95 % [{ic[0]:,.2f}, {ic[1]:,.2f}]")
print(">> Funciona para CUALQUIER estadístico, incluso los que no tienen fórmula.")

titulo("2. Lo que el bootstrap NO arregla")
print("""  - No arregla un sesgo de selección: remuestrea la muestra que tenés.
  - No arregla dependencia temporal: para series hay que usar bootstrap
    por bloques, no remuestreo simple.
  - No convierte una muestra chica en una grande.""")

titulo("3. Bootstrap por bloques para datos dependientes")
panel = panel_sucursales()
media_por_suc = panel.groupby("sucursal")["ventas"].mean()
# MAL: remuestrear observaciones sueltas ignorando la agrupación
reps_mal, ic_mal = bootstrap(panel["ventas"].values, np.mean, B=1000)
# BIEN: remuestrear unidades enteras
reps_bien = np.array([media_por_suc.sample(len(media_por_suc), replace=True).mean()
                      for _ in range(1000)])
ic_bien = np.quantile(reps_bien, [.025, .975])
print(f"  Remuestreando observaciones: IC [{ic_mal[0]:,.0f}, {ic_mal[1]:,.0f}]  ancho={ic_mal[1]-ic_mal[0]:,.0f}")
print(f"  Remuestreando sucursales   : IC [{ic_bien[0]:,.0f}, {ic_bien[1]:,.0f}]  ancho={ic_bien[1]-ic_bien[0]:,.0f}")
print(">> El primero es falsamente preciso: es el mismo error que los errores")
print(">> estándar sin agrupar de la clase 10.")

plt.figure(figsize=(8, 4))
plt.hist(reps_mal, bins=50, alpha=.6, label="por observación (mal)")
plt.hist(reps_bien, bins=50, alpha=.6, label="por unidad (bien)")
plt.legend(); plt.title("Distribución bootstrap de la media")
guardar("clase15_bootstrap.png")

titulo("4. Catálogo de errores del curso")
print("""
   1. Sesgo de anticipación .... usar información que aún no estaba disponible
   2. Sesgo de supervivencia ... analizar solo a los que quedaron  (clase 10)
   3. Marco muestral sesgado ... más datos no lo arreglan          (clase 02)
   4. Ignorar ponderadores ..... la muestra no es la población     (clase 02)
   5. Faltantes no aleatorios .. la ausencia es información        (clase 04)
   6. Pruebas múltiples ........ probar mucho y reportar lo lindo  (clase 05)
   7. Regresión espuria ........ niveles no estacionarios          (clase 09)
   8. Independencia falsa ...... datos agrupados sin agrupar       (clase 10)
   9. Falacia ecológica ........ agregar invierte relaciones       (clase 10)
  10. Descartar censurados ..... sesga toda estimación de duración (clase 11)
  11. Espiar el experimento .... mirar hasta que dé significativo  (clase 13)
  12. Tendencias no paralelas .. el DiD deja de identificar        (clase 14)
""")

titulo("5. Lista de control antes de entregar")
print("""
  [ ] ¿Alguien más puede regenerar todos mis resultados desde el repositorio?
  [ ] ¿Declaré todas las decisiones de limpieza y sus alternativas?
  [ ] ¿Reporté incertidumbre junto a cada número principal?
  [ ] ¿Cuántas hipótesis probé en total, incluidas las descartadas?
  [ ] ¿Mi conclusión es causal? ¿Con qué derecho?
  [ ] ¿Qué tendría que ser cierto para que esté equivocado?
  [ ] ¿Declaré dónde usé asistentes de IA y cómo verifiqué la salida?
""")

# ------------------------------------------------------------------ EJERCICIO
"""
EJERCICIO FINAL

1. Calculá un intervalo bootstrap para el estadístico principal de tu proyecto.
   Si tus datos son agrupados o temporales, usá el remuestreo correcto.
2. Recorré el catálogo de errores y marcá cuáles aplican a tu trabajo.
   Para cada uno que aplique, explicá qué hiciste al respecto.
3. Completá la lista de control antes de la defensa.
"""

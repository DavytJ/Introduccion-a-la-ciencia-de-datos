# Clase 3 — Práctico: crear un dataset y volver a cargarlo

Continuación de la clase 2 (Generación de datos / DGP). Ocho ejercicios sobre
construir un dataset, escribirlo en un archivo y volver a leerlo.

## Archivos

| Archivo | Uso |
|---|---|
| `generar_archivos.py` | Se ejecuta **una sola vez** antes del práctico. Crea `datos/`. |
| `ejercicios.py` | Script con consignas y esqueletos. Para trabajar en VS Code. |
| `ejercicios.ipynb` | Mismo contenido en notebook, una celda por ejercicio. |
| `ejercicios.qmd` | Mismo contenido en revealjs, para proyectar en clase. |
| `soluciones.py` | Soluciones con la discusión conceptual de cada ejercicio. |
| `soluciones.ipynb` | Soluciones en notebook. |

Las consignas de los tres formatos se generan desde una fuente única, así que
no pueden desincronizarse.

## Puesta en marcha

```
pip install pandas numpy pyarrow
py generar_archivos.py          # Windows
python3 generar_archivos.py     # Mac / Linux
```

`pyarrow` solo hace falta para el ejercicio 4 (comparación CSV / parquet).

## Recorrido

| # | Ejercicio | Qué falla |
|---|---|---|
| 1 | Del diccionario al DataFrame | El tipo por defecto pierde el orden de las categorías |
| 2 | Restricciones del DGP como código | Los supuestos de medición no están escritos en ningún lado |
| 3 | Diccionario de variables | El dato viaja sin su instrumento |
| 4 | Viaje de ida y vuelta | El CSV no conserva tipos; aparece `Unnamed: 0` |
| 5 | El CSV que armó Excel | `UnicodeDecodeError`; y el decimal que no falla pero corrompe |
| 6 | Dónde está el archivo | La ruta absoluta con el nombre de usuario de otra persona |
| 7 | El `-99` que se lleva la media | Faltante disfrazado de número válido: 85,3 g → 48,5 g |
| 8 | El archivo del equipo vecino | Separador de miles leído como decimal: 1.471,50 → 169,28 |

Los cuatro últimos son los que producen errores silenciosos. Conviene reservarles
tiempo de discusión.

## Notas para la cátedra

- **`ejercicios.py` se detiene en el ejercicio 5.** Es deliberado: la línea
  `pd.read_csv(RUTA)` lanza `UnicodeDecodeError` y ahí empieza la consigna. En
  el notebook esto no interrumpe el resto porque cada ejercicio es una celda.
- Los archivos de `datos/` se generan con semilla fija: son idénticos en todas
  las máquinas, así que los resultados numéricos de las soluciones se pueden
  corregir contra un valor exacto.
- Todas las soluciones fueron ejecutadas encadenadas, en el orden de los
  ejercicios, sobre pandas 3.0.
- El desafío final asigna a cada uno de los siete equipos el punto de quiebre
  esperado de su estructura de datos.

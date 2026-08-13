# Introducción a la Ciencia de Datos

Universidad de Montevideo — Facultad de Ciencias Empresariales y Economía
Curso semestral · 60 horas · 6 créditos

Repositorio de código del curso: un script por clase, ejecutable sin descargar
nada. Todos los conjuntos de datos son sintéticos, generados con semilla fija,
de modo que cualquier persona obtiene exactamente los mismos resultados.

---

## Instalación

```bash
git clone <url-del-repositorio>
cd curso-intro-ciencia-datos
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Cómo correr una clase

```bash
cd clases
python clase_01_flujo_reproducible.py
```

Las figuras y tablas se escriben en `salidas/`, que está ignorada por Git:
los resultados se regeneran, no se versionan.

---

## Estructura

```
.
├── clases/          un script por clase, autocontenido y comentado
├── datos/           generador de los conjuntos sintéticos
├── salidas/         figuras y tablas (se regenera, no se versiona)
└── requirements.txt
```

---

## Mapa de clases

| # | Clase | Unidad | Problema |
|---|-------|--------|----------|
| 01 | Un análisis que otro pueda repetir | 1 | El dato todavía no existe |
| 02 | Medir y relevar | 1 | El dato todavía no existe |
| 03 | Estructura y calidad del dato | 2 | ¿Cómo es esto? |
| 04 | Exploración robusta y faltantes | 2 | ¿Cómo es esto? |
| 05 | Comparar grupos y pruebas múltiples | 3 | ¿Difieren estos grupos? |
| 06 | Correlación, PCA y análisis factorial | 4 | ¿Qué se mueve con qué? |
| 07 | Descomposición y estacionalidad | 5 | ¿Qué pasó en el tiempo? |
| 08 | Pronóstico y validación fuera de muestra | 5 | ¿Qué va a pasar? |
| 09 | Estacionariedad y regresión espuria | 5 | ¿Qué pasó en el tiempo? |
| 10 | Panel: estructura, atrito y agrupamiento | 6 | ¿Y si sigo muchas unidades? |
| 11 | Censura y Kaplan-Meier | 7 | ¿Cuándo ocurre el evento? |
| 12 | Comparación de curvas y cohortes | 7 | ¿Cuándo ocurre el evento? |
| 13 | Experimentos A/B | 8 | ¿Qué efecto tuvo? |
| 14 | Diferencias en diferencias y estudio de evento | 8 | ¿Qué efecto tuvo? |
| 15 | Bootstrap, límites y comunicación | 9 | ¿Cuánto de esto me creo? |

---

## Data lab: trabajo de los equipos

Cada equipo mantiene su propio repositorio con esta estructura y, además:

- **`bitacora.md`** — una entrada por semana, máximo 150 palabras, con tres
  campos: *qué intentamos*, *qué falló*, *qué decidimos*. El segundo campo es
  obligatorio: una semana sin nada que haya fallado es una semana sin trabajo.
- **`decisiones.md`** — cada decisión de limpieza o de método, con la
  alternativa que se descartó y por qué.
- **`datos/`** — script de obtención. Los datos crudos no se versionan; el
  código que los obtiene, sí.

El historial de *commits* es parte de la evaluación: debe mostrar trabajo
distribuido en el tiempo y entre los integrantes.

## Uso de asistentes de IA

Está permitido y es contenido del curso. Se exige declarar dónde se usó y
verificar de forma independiente toda salida. Cada integrante responde por
cada línea que entrega, sin importar de dónde salió.

## Requisitos

Python 3.10 o superior. Sin `scikit-learn`: el aprendizaje automático
corresponde a otra materia, y todo lo de aquí se resuelve con NumPy, pandas,
SciPy y statsmodels.

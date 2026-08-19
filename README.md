<p align='center'>
  <img src='imagenes/portada.png' alt='Arte generativo: trayectorias sobre un campo vectorial aleatorio' width='100%'>
</p>
<p align='center'>
  <sub>
    Portada generada con código · <a href='imagenes/portada.py'><code>imagenes/portada.py</code></a> · semilla 314<br>
    Inspirada en la serie <a href='https://blog.djnavarro.net/posts/2024-12-18_art-from-code-1/'><em>Art from Code</em></a>
    de Danielle Navarro (2024), publicada bajo
    <a href='https://creativecommons.org/licenses/by/4.0/'>CC BY 4.0</a>.
  </sub>
</p>
---
 
# Introducción a la Ciencia de Datos
 
**Universidad de Montevideo · Facultad de Ciencias Empresariales y Economía**
Curso semestral · 30 sesiones · Agosto a noviembre de 2026
 
Repositorio público del curso: guiones de clase, desafíos, plantillas y el programa.
 
📄 **[Leer el programa](PROGRAMA_ESTUDIANTES.html)** · [ver el fuente](PROGRAMA_ESTUDIANTES.qmd)
 
---

# Introduccion-a-la-ciencia-de-datos
Curso de introducción a la ciencia de datos para negocios y finanzas

La ciencia de datos combina la investigación científica, el conocimiento estadístico y la programación informática, y se ocupa de obtener información útil a partir de datos. Las empresas los emplean para planificar, evaluar, innovar y responder con rapidez a los cambios del mercado; los gobiernos, para orientar sus decisiones y evaluar políticas públicas; y otras organizaciones, desde asociaciones civiles hasta universidades, recurren cada vez más a ellos para fundamentar lo que hacen.

Este curso ofrece una primera introducción a ese campo, organizada alrededor de la metodología de trabajo con datos: los flujos de proceso que van de la pregunta al resultado y las herramientas básicas con que se recorren. Se conocen los distintos tipos de datos, las formas en que se generan y los modos en que se almacenan y se recuperan, con el apoyo de los elementos teóricos que les dan sustento: nociones de probabilidad, inferencia y regresión, y un panorama de los métodos de inferencia causal y de aprendizaje automático

---

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/DavytJ/Introduccion-a-la-ciencia-de-datos.git
cd Introduccion-a-la-ciencia-de-datos
```

Crear y activar un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

(Se recomienda Python 3.11; las versiones 3.10+ deberían ser compatibles.)

---

## Cómo correr una clase

Ejemplos — la organización puede cambiar según la versión del repositorio:

```bash
# ejecutar un guion en la raíz de 'clases'
cd clases
python clase_01_flujo_reproducible.py

# o, para los guiones organizados por carpeta (ejemplo del nuevo formato)
cd clases/clase01
python clase01.py
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

Python 3.11 o superior (3.10+ compatible). Sin `scikit-learn`: el aprendizaje automático
corresponde a otra materia, y todo lo de aquí se resuelve con NumPy, pandas,
SciPy y statsmodels.


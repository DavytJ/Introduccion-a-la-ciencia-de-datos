# =============================================================================
# Carga y transformación
# Ejemplo: medioambiente y aire (ozono, PM2.5, conteo vehicular) — Montevideo
# Versión R  — código extraído de carga_y_transformacion.qmd
# =============================================================================


# -----------------------------------------------------------------------------
# Paquetes
# -----------------------------------------------------------------------------
paquetes <- c("ggplot2", "tidyverse", "DescTools", "readxl", "xlsx", "here",
              "vtable", "modelsummary", "haven", "lubridate", "patchwork",
              "stringr", "sf", "leaflet", "leaflet.minicharts", "webshot2")

# 1. Detectar cuáles NO están instalados e instalarlos
paquetes_faltantes <- paquetes[!(paquetes %in% installed.packages()[, "Package"])]
if (length(paquetes_faltantes) > 0) {
  install.packages(paquetes_faltantes)
}

# 2. Cargarlos todos silenciosamente
invisible(lapply(paquetes, function(pkg) {
  suppressPackageStartupMessages(suppressWarnings(library(pkg, character.only = TRUE)))
}))


# =============================================================================
# 1. Carga de datos: ejemplo medioambiente y aire
# =============================================================================

## Ozono — datos minutales de concentración de O3 en aire ambiente
ozono <- read_csv(here::here("clases/clase7/o3_01_2024_04_2024.csv"),
                  locale = locale(encoding = "latin1"))

## Material particulado menor de 2,5 micras, estaciones automáticas
pm <- read_csv(here::here("clases/clase7/pm_2_5_01_2024_04_2024.csv"),
               locale = locale(encoding = "latin1"))

## Conteo vehicular en las principales avenidas de Montevideo
# El sistema del Centro de Gestión de Movilidad (CGM) usa analíticas de video
# para medir volúmenes vehiculares. Los detectores miden el total de vehículos
# y su clasificación por largo, por sentido de circulación, y pueden
# discriminarse por carril dentro de cada sentido.
auto <- read_csv(here::here("clases/clase7/autoscope_04_2024_volumen.csv"),
                 locale = locale(encoding = "latin1"))


# =============================================================================
# 2. Data profiling: id, nulos y duplicados
# =============================================================================

## 2.1 Información básica del dataset
str(ozono)

## 2.2 Identificador
# Los datos se toman por estación (que tiene una ubicación geográfica, es decir,
# es una característica de la estación) y por fecha.
# El identificador podría ser la fecha: sirve para unir con otros datos.
# También podría ser la combinación de fecha y estación.

# 1- Tenemos problemas con los valores de las estaciones
ozono[1:10, 3]

unique(ozono$estacion)

# Creamos el diccionario de traducción (Busca = Reemplaza)
pauta_limpieza <- c(
  "Ã³" = "o",
  "Ã±" = "ni",
  "Ã¡" = "á",
  "Ã©" = "é",
  "Ã­" = "í",
  "Ãº" = "ú",
  "Ã“" = "Ó",
  "Ã‘" = "NI",
  "Ã"  = "í"   # a veces la 'í' sola se rompe así; dejarla al final de la lista
)

# Aplicamos la limpieza a la columna
ozono_limpio <- ozono %>%
  mutate(
    estacion = str_replace_all(estacion, pauta_limpieza)
  )

## 2.3 Valores faltantes
colSums(is.na(ozono))

# La única variable con valores faltantes es la medición, por lo tanto se pueden
# eliminar, ya que no eliminamos identificador (podría discutirse si hay que
# eliminar fechas sin registro).

# Quito los NA de todo el dataset (si hubiera más columnas con NA también quita
# esa fila):
ozono_sinna <- ozono_limpio %>%
  na.omit()

# Quito los NA de columnas específicas:
ozono_sinna <- ozono_limpio %>%
  filter(is.na(o3) != TRUE)

## 2.4 Duplicados
# Número total de filas repetidas en todo el dataset
ozono_sinna %>%
  duplicated() %>%
  sum()

# Mostrar TODAS las filas involucradas en un duplicado (la primera y sus copias)
ozono_repetidas <- ozono_sinna %>%
  filter(duplicated(.) | duplicated(., fromLast = TRUE))

## 2.5 Eliminar duplicados
# Conserva solo la primera aparición de cada fila única
dataset_sindup <- ozono_sinna %>%
  distinct()

# Duplicados según una sola columna, conservando el resto del primer registro
dataset_sindup_columna <- ozono_sinna %>%
  distinct(estacion, .keep_all = TRUE)


# =============================================================================
# 3. Tipos de datos y transformación de datos
# =============================================================================

## 3.1 Fechas
# "POSIXct" "POSIXt" es el formato estándar para fechas y horas exactas
# (Timestamp o Datetime).
class(ozono$fecha)

# 1. POSIXct (la clase real): ct = calendar time. Internamente R lo guarda como
#    la cantidad de segundos desde el 1 de enero de 1970. Al ser un número por
#    dentro, es muy rápido y eficiente para cálculos (restar dos fechas para
#    saber cuántas horas o días pasaron).
# 2. POSIXt (la clase heredada): una "superclase" virtual. Solo sirve para que R
#    sepa que la variable es un formato de tiempo y pueda usar con ella
#    funciones de fechas (sumarle días, extraer el mes, etc.).

## 3.2 Crear variables
ozono_new <- ozono_sinna %>%
  mutate(
    anio = lubridate::year(fecha),
    mes  = lubridate::month(fecha),
    hora = lubridate::hour(fecha)
  )


# =============================================================================
# 4. Generación de información
# =============================================================================

## 4.1 Agregación mensual
ozono_mes <- ozono_new %>%
  group_by(mes) %>%
  summarise(
    o3_medio_mes = mean(o3),
    n_registros_mes = n())

## 4.2 Visualización
ozono_mes %>%
  ggplot(aes(x = mes, y = o3_medio_mes)) +
  geom_line(color = "blue", linewidth = 1) +  # Une los puntos con una línea
  geom_point(color = "red", size = 3) +       # Dibuja los puntos individuales
  theme_minimal() +                           # Aplica un diseño limpio
  labs(
    title = "Concentración de Ozono en el ambiente, por mes, 2024",
    x = "Fecha",
    y = "Valores"
  )

# Partes básicas de un gráfico:
#   - dataset
#   - variable eje x
#   - variable eje y
#   - tipo de gráfico
#   - títulos: del gráfico y nombres de los ejes
# Información completa en el cheatsheet: https://ggplot2.tidyverse.org/


# =============================================================================
# 5. Análisis profundo: agregación temporal minutal -> horario -> diario
# =============================================================================
# Pregunta central: al agregar, ¿qué estadístico representa el fenómeno?
#   - media: nivel típico
#   - máximo: episodios puntuales (sensible a errores del sensor)
#   - percentil 95: episodios altos pero robusto a picos aislados
#   - n: cuántos minutos respaldan el valor agregado (cobertura)

## 5.1 Horario
ozono_hora <- ozono_sinna %>%
  mutate(fecha_hora = floor_date(fecha, unit = "hour")) %>%
  group_by(estacion, fecha_hora) %>%
  summarise(
    media  = mean(o3),
    maximo = max(o3),
    p95    = quantile(o3, 0.95),
    n_min  = n(),               # de un máximo de 60
    .groups = "drop"
  )

ozono_hora %>%
  ggplot(aes(x = fecha_hora, y = media)) +
  geom_line(color = "blue", linewidth = 1) +
  geom_point(color = "red", size = 1) +
  theme_minimal() +
  labs(
    title = "Concentración de Ozono en el ambiente, por hora, 2024",
    x = "Fecha",
    y = "Valores"
  )


# =============================================================================
# 6. Teoría estadística
# =============================================================================
# Los paneles pA...pE se construyen en un script aparte.
source(here::here("clases/clase7/estadistica_basica.R"))

print(pA)
print(pB)

# Densidad:  h_i = f_i / a_i
print(pC)
print(pD)

# Qué pasa si hay algunos datos outliers o espurios
print(pE)


# =============================================================================
# 7. Diario
# =============================================================================
ozono_dia <- ozono_sinna %>%
  mutate(dia = as_date(fecha)) %>%
  group_by(estacion, dia) %>%
  summarise(
    media  = mean(o3),
    maximo = max(o3),
    p95    = quantile(o3, 0.95),
    n_min  = n(),               # de un máximo de 1440
    .groups = "drop"
  )

ozono_dia %>%
  ggplot(aes(x = dia, y = media)) +
  geom_line(color = "blue", linewidth = 1) +
  geom_point(color = "red", size = 1) +
  theme_minimal() +
  labs(
    title = "Concentración de Ozono en el ambiente, por hora, 2024",
    x = "Fecha",
    y = "Valores"
  )

# Las tres curvas cuentan historias distintas sobre el mismo día
ozono_dia %>%
  pivot_longer(c(media, p95, maximo), names_to = "estadistico", values_to = "o3") %>%
  ggplot(aes(x = dia, y = o3, color = estadistico)) +
  geom_line() +
  facet_wrap(~ estacion, ncol = 1, scales = "free_y") +
  theme_minimal() +
  labs(title = "Agregación diaria: media, p95 y máximo por estación",
       x = NULL, y = "O3 (µg/m³)")


# =============================================================================
# 8. El estadístico normativo: máximo diario de la media móvil de 8 horas
# =============================================================================
# Las guías OMS (2021) para O3 usan el máximo diario de la media móvil de 8 h.
# Una media móvil requiere una grilla horaria COMPLETA: si faltan horas, la
# ventana de 8 posiciones deja de ser una ventana de 8 horas.

grilla_horaria <- seq(min(ozono_hora$fecha_hora), max(ozono_hora$fecha_hora),
                      by = "hour")

ozono_8h <- ozono_hora %>%
  select(estacion, fecha_hora, media) %>%
  complete(estacion, fecha_hora = grilla_horaria) %>%   # inserta NA en horas ausentes
  arrange(estacion, fecha_hora) %>%
  group_by(estacion) %>%
  mutate(
    # stats::filter, no dplyr::filter (mismo nombre, función distinta)
    media_8h = as.numeric(stats::filter(media, rep(1 / 8, 8), sides = 1))
  ) %>%
  ungroup()

max_8h_dia <- ozono_8h %>%
  mutate(dia = as_date(fecha_hora)) %>%
  group_by(estacion, dia) %>%
  summarise(
    max_8h  = if (all(is.na(media_8h))) NA_real_ else max(media_8h, na.rm = TRUE),
    horas_validas = sum(!is.na(media_8h)),
    .groups = "drop"
  )

ggplot(max_8h_dia, aes(x = dia, y = max_8h, color = estacion)) +
  geom_line() +
  geom_hline(yintercept = 100, linetype = "dashed") +   # guía OMS 2021: 100 µg/m³
  theme_minimal() +
  labs(title = "Máximo diario de la media móvil de 8 h",
       x = NULL, y = "O3 (µg/m³)")


# =============================================================================
# 9. Mapa
# =============================================================================
source(here::here("clases/clase7/mapa.R"))

mapa


# =============================================================================
# 10. Patrones de faltantes
# =============================================================================
# Tres tipos de faltante en una serie de sensor:
#   a) explícito: la fila existe, o3 es NA
#   b) en rachas: muchos NA consecutivos -> sensor caído o en mantenimiento
#   c) implícito: la fila no existe (el minuto no está en el archivo)
# Eliminar NA sin mirar esto borra evidencia sobre el proceso de medición.

## 10.1 Faltantes explícitos por estación
ozono_limpio %>%
  group_by(estacion) %>%
  summarise(
    n_filas  = n(),
    n_na     = sum(is.na(o3)),
    prop_na  = mean(is.na(o3)),
    .groups = "drop"
  )

## 10.2 ¿Cuándo faltan? Proporción de NA por día
na_dia <- ozono_limpio %>%
  mutate(dia = as_date(fecha)) %>%
  group_by(estacion, dia) %>%
  summarise(prop_na = mean(is.na(o3)), .groups = "drop")

ggplot(na_dia, aes(x = dia, y = prop_na)) +
  geom_col(fill = "grey40") +
  facet_wrap(~ estacion, ncol = 1) +
  theme_minimal() +
  labs(title = "Proporción de minutos sin dato, por día y estación",
       x = NULL, y = "Proporción de NA")

## 10.3 Rachas de NA consecutivos (rle = run length encoding)
rachas <- ozono_limpio %>%
  arrange(estacion, fecha) %>%
  group_by(estacion) %>%
  reframe({
    r <- rle(is.na(o3))
    tibble(faltante = r$values, largo = r$lengths)
  })

rachas %>%
  filter(faltante) %>%
  mutate(tipo = cut(largo, breaks = c(0, 1, 10, 60, 1440, Inf),
                    labels = c("1 min", "2-10 min", "11 min-1 h",
                               "1 h-1 día", "> 1 día"))) %>%
  count(estacion, tipo, name = "n_rachas")

## 10.4 Faltantes implícitos: minutos que no están en el archivo
ozono_limpio %>%
  group_by(estacion) %>%
  summarise(
    primero   = min(fecha),
    ultimo    = max(fecha),
    esperados = as.numeric(difftime(max(fecha), min(fecha), units = "mins")) + 1,
    presentes = n_distinct(fecha),
    .groups = "drop"
  ) %>%
  mutate(implicitos = esperados - presentes,
         prop_implicitos = implicitos / esperados)

## 10.5 Cobertura contra la grilla del período pedido
INICIO <- as.POSIXct("2024-01-01 00:00:00", tz = tz(ozono_limpio$fecha))
FIN    <- as.POSIXct("2024-04-30 23:59:00", tz = tz(ozono_limpio$fecha))
ESPERADOS <- as.numeric(difftime(FIN, INICIO, units = "mins")) + 1

cobertura <- ozono_limpio %>%
  group_by(estacion) %>%
  summarise(presentes = n_distinct(fecha),
            validos   = sum(!is.na(o3)),
            .groups = "drop") %>%
  mutate(esperados         = ESPERADOS,
         sin_fila          = esperados - presentes,
         fila_sin_medicion = presentes - validos,
         cobertura         = 100 * round(validos / esperados, 3))
cobertura

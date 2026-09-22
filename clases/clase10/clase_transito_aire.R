# =============================================================================
# ¿Se ve el tránsito en la calidad del aire?
# Tres Cruces, junio de 2024: conteo vehicular, NO2 y PM2.5
# Versión en R (tidyverse + ggplot2), equivalente a clase_transito_aire.py
# =============================================================================
#
# Cómo está organizado este script
# --------------------------------
# Paso 0   Carga de los tres archivos y preparación de series por hora.
# Paso 1   Mapa: dónde se cuenta el tránsito y dónde se mide el aire.
# Paso 2   Elección de la estación: qué mide cada una y cuánto tránsito tiene cerca.
# Paso 3   Una semana de las tres series.
# Paso 4   Perfil horario (el "día típico"), con las series normalizadas.
# Paso 5   Correlación "cruda" entre tránsito y contaminante.
# Paso 6   Desvíos: sacar lo habitual de cada hora.
# Paso 7   Correlación con rezagos (tránsito de k horas antes).
# Paso 8   Comparación con el azar (corriendo el tránsito días enteros).
# Paso 9   Rezagos de hasta 24 horas.
# Paso 10  Modelo de regresión: lo habitual + lo que agrega el tránsito.
# Paso 11  La misma pregunta en la otra estación que mide NO2.
#
# Cada paso termina con dos comentarios: "Qué vemos" y "Qué no sabemos
# todavía", que es la pregunta que motiva el paso siguiente.
#
# Paquetes necesarios (instalar una sola vez):
#   install.packages(c("dplyr", "tidyr", "readr", "lubridate",
#                      "stringr", "ggplot2"))
# =============================================================================

library(dplyr)      # manipular tablas: filter, mutate, group_by, summarise...
library(tidyr)      # cambiar la forma de las tablas: pivot_longer, complete...
library(readr)      # leer archivos csv
library(lubridate)  # trabajar con fechas y horas
library(stringr)    # trabajar con texto
library(ggplot2)    # gráficos


# -----------------------------------------------------------------------------
# Parámetros: lo único que habría que cambiar para usar otros archivos
# -----------------------------------------------------------------------------
CARPETA   <- "clases/clase10"                    # carpeta con los tres archivos
ARCH_AUTO <- "autoscope_06_2024_volumen.csv"     # conteo vehicular, junio 2024
ARCH_NO2  <- "no2_05_2024_08_2024.csv"           # NO2, mayo a agosto 2024
ARCH_PM   <- "pm_2_5_05_2024_08_2024.csv"     # PM2.5, mayo a agosto 2024
RADIO_KM  <- 1.5                                 # "cerca" de una estación

# Colores fijos para cada serie, iguales en todos los gráficos
COL_TRANSITO <- "#2E86AB"   # celeste
COL_NO2      <- "#7B4B2A"   # marrón
COL_PM25     <- "#D4A373"   # arena
COL_OSCURO   <- "#5C3A21"   # marrón oscuro (líneas de referencia)

# Tema común para todos los gráficos: fondo blanco y grilla suave
theme_set(theme_minimal(base_size = 12))


# =============================================================================
# PASO 0. Carga y preparación
# =============================================================================

# ---- 0.1 Arreglar los caracteres mal codificados -----------------------------
# Los archivos vienen con los acentos "rotos" (por ejemplo "MaroÃ±as" en lugar
# de "Maroñas"). Este vector dice qué buscar (nombre) y por qué reemplazarlo
# (valor). El orden importa: la regla "Ã" sola tiene que ir al final.
pauta_limpieza <- c("Ã³" = "o", "Ã±" = "ni", "Ã¡" = "á", "Ã©" = "é",
                    "Ã­" = "í", "Ãº" = "ú", "Ã“" = "Ó", "Ã‘" = "NI",
                    "Ã" = "í")

limpiar <- function(texto) {
  # Recorre la pauta en orden y aplica cada reemplazo como texto literal
  # (fixed = sin expresiones regulares)
  for (i in seq_along(pauta_limpieza)) {
    texto <- str_replace_all(texto, fixed(names(pauta_limpieza)[i]),
                             pauta_limpieza[i])
  }
  texto
}

# ---- 0.2 Datos de aire: de minutos a horas -----------------------------------
# Los archivos de aire tienen una fila por minuto y estación.
# Para comparar con el tránsito, los llevamos a una fila por hora y estación:
# el promedio de los minutos de esa hora.
cargar_aire <- function(archivo, columna) {
  datos <- read_csv(file.path(CARPETA, archivo),
                    locale = locale(encoding = "latin1"),
                    show_col_types = FALSE) |>
    distinct() |>                                   # saca filas repetidas
    mutate(estacion = limpiar(estacion))

  # Coordenadas de cada estación (son fijas: tomamos la primera fila)
  coords <- datos |>
    group_by(estacion) |>
    summarise(latitud = first(latitud), longitud = first(longitud))

  # floor_date(fecha, "hour") lleva 08:37 a 08:00: agrupa los minutos por hora
  por_hora <- datos |>
    mutate(hora = floor_date(fecha, "hour")) |>
    group_by(estacion, hora) |>
    summarise(valor = mean(.data[[columna]], na.rm = TRUE), .groups = "drop") |>
    mutate(valor = ifelse(is.nan(valor), NA, valor))  # hora sin ningún dato -> NA

  list(por_hora = por_hora, coords = coords)
}

no2_datos <- cargar_aire(ARCH_NO2, "no2")
pm_datos  <- cargar_aire(ARCH_PM, "pm2_5")

# Todas las estaciones con sus coordenadas (NO2 y PM2.5 juntas, sin repetir)
coords_todas <- bind_rows(no2_datos$coords, pm_datos$coords) |>
  distinct(estacion, .keep_all = TRUE)

# ---- 0.3 Conteo vehicular ----------------------------------------------------
# Una fila por detector, carril y cada 5 minutos. "fecha" y "hora" vienen en
# columnas separadas: las unimos en un solo momento (fecha_hora).
auto <- read_csv(file.path(CARPETA, ARCH_AUTO),
                 locale = locale(encoding = "latin1"),
                 show_col_types = FALSE) |>
  distinct() |>
  mutate(fecha_hora = as.POSIXct(paste(as.Date(fecha), hora),
                                 format = "%Y-%m-%d %H:%M:%OS", tz = "UTC"))

# Un "punto de conteo" es una ubicación (latitud, longitud); puede tener
# varios carriles y detectores.
puntos <- auto |>
  count(latitud, longitud, name = "registros")

# ---- 0.4 Distancia entre dos puntos del mapa, en km --------------------------
# Fórmula de haversine: distancia sobre la superficie de la Tierra
# (radio de 6371 km). Las coordenadas se pasan a radianes.
dist_km <- function(lat1, lon1, lat2, lon2) {
  a_rad <- pi / 180
  lat1 <- lat1 * a_rad; lon1 <- lon1 * a_rad
  lat2 <- lat2 * a_rad; lon2 <- lon2 * a_rad
  a <- sin((lat2 - lat1) / 2)^2 +
       cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2)^2
  2 * 6371 * asin(sqrt(a))
}

# ---- 0.5 Armar la serie de una estación --------------------------------------
# Devuelve una tabla con una fila por hora de junio y tres columnas:
#   transito : vehículos por hora, sumando los puntos cercanos a la estación
#   no2      : NO2 promedio de esa hora en la estación
#   pm25     : PM2.5 promedio de esa hora en la estación
# y además la lista de puntos cercanos.
HORAS_JUNIO <- tibble(hora = seq(as.POSIXct("2024-06-01 00:00", tz = "UTC"),
                                 as.POSIXct("2024-06-30 23:00", tz = "UTC"),
                                 by = "hour"))

serie_estacion <- function(est) {
  c_est <- coords_todas |> filter(estacion == est)

  cerca <- puntos |>
    mutate(dist = dist_km(latitud, longitud, c_est$latitud, c_est$longitud)) |>
    filter(dist < RADIO_KM)

  # Suma de vehículos de los puntos cercanos, por hora.
  # Si en una hora no hay ningún registro, queda NA (no 0).
  transito <- auto |>
    semi_join(cerca, by = c("latitud", "longitud")) |>
    mutate(hora = floor_date(fecha_hora, "hour")) |>
    group_by(hora) |>
    summarise(transito = sum(volume), .groups = "drop")

  aire <- function(d) d$por_hora |> filter(estacion == est) |> select(hora, valor)

  serie <- HORAS_JUNIO |>                       # la grilla completa de horas
    left_join(transito, by = "hora") |>
    left_join(aire(no2_datos) |> rename(no2 = valor), by = "hora") |>
    left_join(aire(pm_datos)  |> rename(pm25 = valor), by = "hora")

  list(serie = serie, cerca = cerca)
}


# =============================================================================
# PASO 1. ¿Dónde medimos?
# =============================================================================
g1 <- ggplot() +
  geom_point(data = puntos, aes(longitud, latitud),
             color = COL_TRANSITO, size = 1) +
  geom_point(data = coords_todas, aes(longitud, latitud),
             color = COL_OSCURO, shape = 8, size = 5, stroke = 1.2) +
  geom_text(data = coords_todas, aes(longitud, latitud, label = estacion),
            hjust = -0.15, vjust = -0.6, size = 3.5) +
  coord_quickmap() +             # respeta la proporción entre latitud y longitud
  labs(title = "Dónde se cuenta el tránsito y dónde se mide el aire",
       x = "Longitud", y = "Latitud")
print(g1)
# Cómo leer: eje x = longitud (oeste a este), eje y = latitud (sur a norte).
#   Puntos: conteo vehicular. Estrellas: estaciones de aire.
# Qué vemos: los puntos de conteo están repartidos de forma muy desigual.
# Qué no sabemos: en cuál estación conviene buscar la huella del tránsito.


# =============================================================================
# PASO 2. ¿Qué estación elegimos?
# =============================================================================
# Armamos la serie de cada estación y resumimos:
#   cuántos puntos de conteo tiene cerca y cuántas horas con dato de cada contaminante.
estaciones <- coords_todas$estacion
series <- lapply(estaciones, serie_estacion)
names(series) <- estaciones

resumen <- tibble(
  estacion      = estaciones,
  puntos_cerca  = sapply(series, function(s) nrow(s$cerca)),
  horas_no2     = sapply(series, function(s) sum(!is.na(s$serie$no2))),
  horas_pm25    = sapply(series, function(s) sum(!is.na(s$serie$pm25)))
)
print(resumen)

# Gráfico A: puntos de conteo cerca de cada estación
g2a <- ggplot(resumen, aes(puntos_cerca, estacion)) +
  geom_col(fill = COL_TRANSITO) +
  labs(title = paste("Puntos de conteo a menos de", RADIO_KM, "km"),
       x = "Cantidad", y = NULL)
print(g2a)

# Gráfico B: qué días de junio tiene dato cada estación (al menos 12 horas)
dias_con_dato <- bind_rows(lapply(estaciones, function(est) {
  series[[est]]$serie |>
    mutate(dia = as.Date(hora)) |>
    group_by(dia) |>
    summarise(NO2 = sum(!is.na(no2)), PM2.5 = sum(!is.na(pm25)), .groups = "drop") |>
    pivot_longer(c(NO2, PM2.5), names_to = "contaminante", values_to = "horas") |>
    filter(horas >= 12) |>
    mutate(estacion = est)
}))

g2b <- ggplot(dias_con_dato, aes(dia, estacion, color = contaminante)) +
  geom_point(shape = 15, size = 3, position = position_dodge(width = 0.4)) +
  scale_color_manual(values = c(NO2 = COL_NO2, PM2.5 = COL_PM25)) +
  labs(title = "Días de junio con dato (al menos 12 horas)", x = NULL, y = NULL)
print(g2b)
# Qué vemos: el NO2 se mide solo en dos estaciones. Una tiene muchos puntos
#   de conteo cerca; la otra, muy pocos. La que tiene más tránsito medido
#   tiene NO2 solo la primera mitad de junio.
# Decisión: empezamos por la estación con más tránsito medido alrededor,
#   aceptando que tiene menos días. Al final (paso 11) volvemos a la otra.
ESTACION <- resumen |>
  filter(horas_no2 > 0) |>
  slice_max(puntos_cerca, n = 1) |>
  pull(estacion)
cat("Estación elegida:", ESTACION, "\n")

df <- series[[ESTACION]]$serie      # la tabla con la que trabajamos desde acá


# =============================================================================
# PASO 3. Mirar las series: una semana
# =============================================================================
# pivot_longer pasa de tres columnas (transito, no2, pm25) a dos
# (variable, valor): así ggplot puede dibujar un panel por variable.
semana <- df |>
  filter(hora >= as.POSIXct("2024-06-04", tz = "UTC"),
         hora <  as.POSIXct("2024-06-11", tz = "UTC")) |>
  pivot_longer(c(transito, no2, pm25), names_to = "variable", values_to = "valor") |>
  mutate(variable = factor(variable, levels = c("transito", "no2", "pm25"),
                           labels = c("Vehículos por hora", "NO2 (µg/m³)", "PM2.5 (µg/m³)")))

g3 <- ggplot(semana, aes(hora, valor, color = variable)) +
  geom_line() +                                   # los NA cortan la línea
  facet_wrap(~ variable, ncol = 1, scales = "free_y") +   # cada panel, su escala
  scale_color_manual(values = c(COL_TRANSITO, COL_NO2, COL_PM25), guide = "none") +
  scale_x_datetime(date_labels = "%a %d", date_breaks = "1 day") +
  labs(title = paste("Una semana en", ESTACION), x = NULL, y = NULL)
print(g3)
# Qué vemos: el tránsito sube de día y baja de noche, y baja el fin de semana.
#   El NO2 parece tener un ritmo diario parecido. El PM2.5 tiene episodios.
# Qué no sabemos: "parece" no alcanza; hay que mirar muchos días juntos.


# =============================================================================
# PASO 4. El día típico: perfil horario
# =============================================================================
# Para cada hora del día (0 a 23) y tipo de día, promediamos todos los días.
# Después dividimos cada serie por su promedio: así las tres quedan en la
# misma escala (1 = promedio, 2 = el doble, 0,5 = la mitad).
perfil <- df |>
  mutate(tipo_dia = ifelse(wday(hora, week_start = 1) >= 6,
                           "fin de semana", "lunes a viernes"),
         h = hour(hora)) |>
  group_by(tipo_dia, h) |>
  summarise(across(c(transito, no2, pm25), \(x) mean(x, na.rm = TRUE)), .groups = "drop") |>
  group_by(tipo_dia) |>
  mutate(across(c(transito, no2, pm25), \(x) x / mean(x, na.rm = TRUE))) |>  # normalizar
  ungroup() |>
  pivot_longer(c(transito, no2, pm25), names_to = "serie", values_to = "relativo") |>
  mutate(tipo_dia = factor(tipo_dia, levels = c("lunes a viernes", "fin de semana")))  # orden de los paneles

g4 <- ggplot(perfil, aes(h, relativo, color = serie)) +
  geom_line() + geom_point(size = 1) +
  facet_wrap(~ tipo_dia) +
  scale_color_manual(values = c(transito = COL_TRANSITO, no2 = COL_NO2, pm25 = COL_PM25),
                     labels = c(transito = "Tránsito", no2 = "NO2", pm25 = "PM2.5")) +
  labs(title = "El día típico (cada serie dividida por su media)",
       x = "Hora del día", y = "Relativo a su media", color = NULL)
print(g4)
# Qué vemos: el NO2 tiene picos en las mismas horas que el tránsito. Los
#   picos llegan en orden: tránsito, NO2, PM2.5.
# Ojo: el fin de semana se apoya en pocos días (el NO2 tiene ~12 días de dato).
# Qué no sabemos: dos cosas con ritmo diario se parecen aunque no tengan
#   relación entre sí.


# =============================================================================
# PASO 5. La correlación "cruda"
# =============================================================================
# cor(..., use = "complete.obs") usa solo las horas donde las dos variables
# tienen dato.
r_no2  <- cor(df$transito, df$no2,  use = "complete.obs")
r_pm25 <- cor(df$transito, df$pm25, use = "complete.obs")
cat(sprintf("Correlación cruda: NO2 r = %.2f | PM2.5 r = %.2f\n", r_no2, r_pm25))

cruda <- df |>
  pivot_longer(c(no2, pm25), names_to = "contaminante", values_to = "valor") |>
  mutate(contaminante = ifelse(contaminante == "no2",
                               sprintf("NO2: r = %.2f", r_no2),
                               sprintf("PM2.5: r = %.2f", r_pm25)))

g5 <- ggplot(cruda, aes(transito, valor)) +
  geom_point(alpha = 0.4, size = 1, color = COL_TRANSITO) +
  facet_wrap(~ contaminante, scales = "free_y") +
  labs(title = "Tránsito contra contaminante, hora a hora",
       x = "Vehículos por hora", y = "Contaminante (µg/m³)")
print(g5)
# Cómo leer: cada punto es una hora.
# Qué vemos: el NO2 sube con el tránsito; el PM2.5 no.
# Qué no sabemos: parte de esa r viene solo de que los dos tienen ciclo diario.


# =============================================================================
# PASO 6. Sacar el ciclo diario: desvíos respecto de lo habitual
# =============================================================================
# A cada hora le restamos el promedio de esa hora del día y ese tipo de día
# (semana o fin de semana). Lo que queda responde a: ¿esta hora estuvo por
# encima o por debajo de lo habitual?
res <- df |>
  mutate(finde = wday(hora, week_start = 1) >= 6, h = hour(hora)) |>
  group_by(finde, h) |>
  mutate(across(c(transito, no2, pm25), \(x) x - mean(x, na.rm = TRUE))) |>
  ungroup() |>
  arrange(hora)                     # importante: las filas en orden de tiempo

r_no2_d  <- cor(res$transito, res$no2,  use = "complete.obs")
r_pm25_d <- cor(res$transito, res$pm25, use = "complete.obs")
cat(sprintf("Correlación de desvíos: NO2 r = %.2f | PM2.5 r = %.2f\n", r_no2_d, r_pm25_d))

desvios <- res |>
  pivot_longer(c(no2, pm25), names_to = "contaminante", values_to = "valor") |>
  mutate(contaminante = ifelse(contaminante == "no2",
                               sprintf("NO2: r = %.2f", r_no2_d),
                               sprintf("PM2.5: r = %.2f", r_pm25_d)))

g6 <- ggplot(desvios, aes(transito, valor)) +
  geom_hline(yintercept = 0, color = "grey60") +
  geom_vline(xintercept = 0, color = "grey60") +
  geom_point(alpha = 0.4, size = 1, color = COL_TRANSITO) +
  facet_wrap(~ contaminante, scales = "free_y") +
  labs(title = "Sin el ciclo diario",
       x = "Tránsito: diferencia con lo habitual",
       y = "Contaminante: diferencia con lo habitual")
print(g6)
# Cómo leer: el cruce de las líneas grises es una hora "normal".
# Qué vemos: la r del NO2 baja bastante (casi todo era el ciclo), pero no
#   llega a cero. La del PM2.5 sigue en cero.
# Qué no sabemos: el aire tarda en reaccionar. ¿Y si responde al tránsito
#   de un rato antes?


# =============================================================================
# PASO 7. ¿Con qué demora? Correlación con el tránsito de k horas antes
# =============================================================================
# desplazar(x, k) devuelve la serie x corrida k lugares:
#   k > 0: en cada fila queda el valor de k horas ANTES (lag)
#   k < 0: en cada fila queda el valor de k horas DESPUÉS (lead)
desplazar <- function(x, k) {
  if (k > 0) dplyr::lag(x, k) else if (k < 0) dplyr::lead(x, -k) else x
}

# Para cada k, la correlación entre el contaminante de ahora y el tránsito
# de k horas antes
cor_rezagos <- function(datos, col, rezagos) {
  tibble(k = rezagos,
         r = sapply(rezagos, function(k)
           cor(datos[[col]], desplazar(datos$transito, k), use = "complete.obs")))
}

rezagos_7 <- bind_rows(
  cor_rezagos(res, "no2",  -3:8) |> mutate(contaminante = "NO2"),
  cor_rezagos(res, "pm25", -3:8) |> mutate(contaminante = "PM2.5"))

g7 <- ggplot(rezagos_7, aes(k, r, color = contaminante)) +
  geom_hline(yintercept = 0, color = "grey60") +
  geom_vline(xintercept = 0, color = "grey60", linetype = "dashed") +
  geom_line() + geom_point() +
  scale_color_manual(values = c(NO2 = COL_NO2, PM2.5 = COL_PM25)) +
  labs(title = "Contaminante ahora vs tránsito de k horas antes (desvíos)",
       x = "k (horas; k > 0 es tránsito del pasado)", y = "Correlación", color = NULL)
print(g7)
# Cómo leer: cada punto es una correlación como la del paso 6, con el
#   tránsito corrido k horas.
# Qué vemos: el NO2 responde en 1-2 horas y se apaga en unas 5. El PM2.5 no
#   reacciona en las primeras horas y empieza a subir donde termina el gráfico.
# Qué no sabemos: buscamos el mejor rezago entre varios; ¿un número así
#   podría salir por casualidad?


# =============================================================================
# PASO 8. ¿Casualidad? Corremos el tránsito días enteros
# =============================================================================
# Si movemos toda la serie de tránsito varios días (lo que sale por el final
# entra por el principio), rompemos cualquier relación real con el aire,
# pero el tránsito conserva su forma. Si la correlación real queda por encima
# de todas las corridas, no es fácil explicarla por casualidad.
rotar <- function(x, n) {
  # Mueve x n lugares hacia adelante, en círculo
  largo <- length(x)
  n <- n %% largo
  if (n == 0) return(x)
  c(x[(largo - n + 1):largo], x[1:(largo - n)])
}

REZAGOS_BUSQUEDA <- 0:3
r_max <- function(y, transito) {
  # La mejor correlación entre los rezagos 0 a 3 horas
  max(sapply(REZAGOS_BUSQUEDA, function(k)
    cor(y, desplazar(transito, k), use = "complete.obs")), na.rm = TRUE)
}

dias <- nrow(res) %/% 24
azar <- bind_rows(lapply(c("no2", "pm25"), function(col) {
  obs <- r_max(res[[col]], res$transito)
  corridas <- sapply(3:(dias - 3), function(d) r_max(res[[col]], rotar(res$transito, 24 * d)))
  cat(sprintf("%s: corridas con r igual o mayor que la real: %.0f%%\n",
              col, 100 * mean(corridas >= obs)))
  tibble(contaminante = ifelse(col == "no2", "NO2", "PM2.5"), r = corridas, real = obs)
}))

g8 <- ggplot(azar, aes(r)) +
  geom_histogram(bins = 10, fill = "grey80", color = "grey50") +
  geom_vline(aes(xintercept = real), color = COL_OSCURO, linewidth = 1) +
  facet_wrap(~ contaminante) +
  labs(title = "¿La relación supera a la casualidad?",
       subtitle = "Barras: tránsito corrido al azar. Línea: la correlación real.",
       x = "Mejor correlación (rezagos 0 a 3 h)", y = "Cantidad de corridas")
print(g8)
# Qué vemos: el NO2 queda por encima de todas las corridas; el PM2.5 (con
#   rezagos cortos) queda en el medio.
# Qué no sabemos: en el paso 7 la curva del PM2.5 subía justo donde se cortaba.


# =============================================================================
# PASO 9. Dos contaminantes, dos ritmos: rezagos de hasta 24 horas
# =============================================================================
rezagos_9 <- bind_rows(
  cor_rezagos(res, "no2",  0:24) |> mutate(contaminante = "NO2"),
  cor_rezagos(res, "pm25", 0:24) |> mutate(contaminante = "PM2.5"))

g9 <- ggplot(rezagos_9, aes(k, r, color = contaminante)) +
  geom_hline(yintercept = 0, color = "grey60") +
  geom_line() + geom_point(size = 1.5) +
  scale_color_manual(values = c(NO2 = COL_NO2, PM2.5 = COL_PM25)) +
  labs(title = "Contaminante ahora vs tránsito de k horas antes, hasta 24 horas",
       x = "k (horas; tránsito del pasado)", y = "Correlación", color = NULL)
print(g9)
# Qué vemos: el NO2 responde enseguida al tránsito (1-2 horas) y se apaga.
#   El PM2.5 empieza a subir a las 5-6 horas y llega a su máximo cerca de
#   las 12-13: no sale del caño y se va, se junta.
# Por eso en el paso 4 el PM2.5 tenía su pico de noche: el tránsito de la
#   mañana (8 h) + 13 h = 21 h.


# =============================================================================
# PASO 10. Un modelo
# =============================================================================
# La idea, en palabras:
#   lo que medimos = lo habitual de esa hora + lo que agrega el tránsito + lo que no sabemos
#
# En símbolos, para cada hora t:
#   y(t) = h(t) + a + b · x(t - k) + error
#     h(t)      lo habitual: el promedio de esa hora del día (y tipo de día)  -> pasos 4 y 6
#     x(t - k)  el desvío del tránsito de k horas antes                       -> pasos 6 y 9
#     a, b      la recta que mejor une el desvío del tránsito con el del
#               contaminante (mínimos cuadrados, función lm).
#               b es cuánto sube el contaminante por cada vehículo por hora de más.
#     error     lo que el modelo no sabe (viento, lluvia, otras fuentes)
#
# El rezago k sale del paso 9: el NO2 responde en ~1 hora, el PM2.5 en ~13.
REZAGO <- c(no2 = 1, pm25 = 13)

ajustar_modelo <- function(col) {
  d <- tibble(hora            = df$hora,
              medido          = df[[col]],                          # lo medido
              desvio          = res[[col]],                         # su desvío
              transito_desvio = desplazar(res$transito, REZAGO[[col]])) |>
    filter(!is.na(medido), !is.na(desvio), !is.na(transito_desvio))

  # 1. Lo habitual de cada hora: lo medido menos su desvío
  d <- d |> mutate(habitual = medido - desvio)

  # 2. La recta entre los dos desvíos: desvio = a + b * transito_desvio
  recta <- lm(desvio ~ transito_desvio, data = d)
  a <- coef(recta)[[1]]
  b <- coef(recta)[[2]]

  # 3. La predicción: lo habitual más lo que agrega el tránsito
  d <- d |> mutate(modelo = habitual + a + b * transito_desvio)
  list(datos = d, a = a, b = b)
}

# R²: qué parte de la variación de lo medido reproduce una predicción
r2 <- function(medido, predicho) {
  1 - sum((medido - predicho)^2) / sum((medido - mean(medido))^2)
}

modelos <- list(no2 = ajustar_modelo("no2"), pm25 = ajustar_modelo("pm25"))

tabla <- bind_rows(lapply(names(modelos), function(col) {
  m <- modelos[[col]]
  tibble(contaminante            = ifelse(col == "no2", "NO2", "PM2.5"),
         rezago_k_h              = REZAGO[[col]],
         b_por_1000_veh_h        = round(1000 * m$b, 2),
         R2_solo_lo_habitual     = round(r2(m$datos$medido, m$datos$habitual), 2),
         R2_habitual_mas_transito = round(r2(m$datos$medido, m$datos$modelo), 2),
         horas_usadas            = nrow(m$datos))
}))
print(tabla)

# ---- 10a. La pieza nueva del modelo: la recta entre los desvíos -------------
puntos_recta <- bind_rows(lapply(names(modelos), function(col) {
  modelos[[col]]$datos |>
    mutate(contaminante = sprintf("%s: tránsito de %d h antes",
                                  ifelse(col == "no2", "NO2", "PM2.5"), REZAGO[[col]]),
           a = modelos[[col]]$a, b = modelos[[col]]$b)
}))

g10a <- ggplot(puntos_recta, aes(transito_desvio, desvio)) +
  geom_hline(yintercept = 0, color = "grey60") +
  geom_vline(xintercept = 0, color = "grey60") +
  geom_point(alpha = 0.4, size = 1, color = COL_TRANSITO) +
  geom_abline(aes(intercept = a, slope = b), color = COL_OSCURO, linewidth = 1) +
  facet_wrap(~ contaminante, scales = "free") +
  labs(title = "Cuánto agrega el tránsito: la recta entre los desvíos",
       x = "Tránsito: diferencia con lo habitual (veh/h)",
       y = "Contaminante: diferencia con lo habitual")
print(g10a)

# ---- 10b. El modelo completo contra lo medido, una semana --------------------
# right_join con la grilla de horas: las horas sin dato quedan NA y cortan la línea
semana_modelo <- bind_rows(lapply(names(modelos), function(col) {
  modelos[[col]]$datos |>
    right_join(HORAS_JUNIO, by = "hora") |>
    filter(hora >= as.POSIXct("2024-06-04", tz = "UTC"),
           hora <  as.POSIXct("2024-06-11", tz = "UTC")) |>
    select(hora, medido, habitual, modelo) |>
    pivot_longer(c(medido, habitual, modelo), names_to = "serie", values_to = "valor") |>
    mutate(contaminante = ifelse(col == "no2", "NO2", "PM2.5"))
}))

g10b <- ggplot(semana_modelo |> arrange(hora), aes(hora, valor, color = serie, linetype = serie)) +
  geom_line() +
  facet_wrap(~ contaminante, ncol = 1, scales = "free_y") +
  scale_color_manual(values = c(medido = "black", habitual = "grey55", modelo = COL_TRANSITO),
                     labels = c(medido = "Medido", habitual = "Solo lo habitual de la hora",
                                modelo = "Habitual + tránsito")) +
  scale_linetype_manual(values = c(medido = "solid", habitual = "dashed", modelo = "solid"),
                        labels = c(medido = "Medido", habitual = "Solo lo habitual de la hora",
                                   modelo = "Habitual + tránsito")) +
  scale_x_datetime(date_labels = "%a %d", date_breaks = "1 day") +
  labs(title = "El modelo contra lo medido, una semana",
       x = NULL, y = "µg/m³", color = NULL, linetype = NULL)
print(g10b)
# Qué vemos: sin ninguna otra variable (ni viento, ni lluvia, ni temperatura),
#   lo habitual de la hora explica la mitad del NO2 y una quinta parte del
#   PM2.5. Sumar el tránsito, cada uno con su demora, mejora a los dos.
# Conclusión: el tránsito se ve en los dos contaminantes, con ritmos
#   distintos: el NO2 enseguida, el PM2.5 medio día después.
# ¿Dónde se equivoca el modelo? En los episodios y en algunas noches:
#   ahí está lo que no pusimos (el tiempo, otras fuentes).


# =============================================================================
# PASO 11. ¿Y en la otra estación? Lo mismo en todas las que miden NO2
# =============================================================================
estaciones_no2 <- resumen |> filter(horas_no2 > 0) |> pull(estacion)

# Desvíos de una estación (lo mismo que el paso 6, en forma de función)
desvios_de <- function(serie) {
  serie |>
    mutate(finde = wday(hora, week_start = 1) >= 6, h = hour(hora)) |>
    group_by(finde, h) |>
    mutate(across(c(transito, no2, pm25), \(x) x - mean(x, na.rm = TRUE))) |>
    ungroup() |>
    arrange(hora)
}

curvas <- list(); barras <- list()
for (est in estaciones_no2) {
  r_est <- desvios_de(series[[est]]$serie)
  n_cerca <- nrow(series[[est]]$cerca)
  etiqueta <- sprintf("%s (%d puntos cerca)", est, n_cerca)

  curvas[[est]] <- cor_rezagos(r_est, "no2", -3:8) |> mutate(estacion = etiqueta)

  obs <- r_max(r_est$no2, r_est$transito)
  dias_e <- nrow(r_est) %/% 24
  corr <- sapply(3:(dias_e - 3), function(d) r_max(r_est$no2, rotar(r_est$transito, 24 * d)))
  cat(sprintf("%s: %d puntos cerca, mejor r = %.2f, corridas >= real: %.0f%%\n",
              est, n_cerca, obs, 100 * mean(corr >= obs)))
  barras[[est]] <- tibble(estacion = est, real = obs, r_azar = corr)
}

g11a <- ggplot(bind_rows(curvas), aes(k, r, color = estacion)) +
  geom_hline(yintercept = 0, color = "grey60") +
  geom_vline(xintercept = 0, color = "grey60", linetype = "dashed") +
  geom_line() + geom_point() +
  scale_color_manual(values = c(COL_TRANSITO, COL_NO2)) +
  labs(title = "NO2 vs tránsito de k horas antes (desvíos)",
       x = "k (horas)", y = "Correlación", color = NULL)
print(g11a)

barras_df <- bind_rows(barras)
g11b <- ggplot(barras_df, aes(estacion)) +
  geom_col(data = distinct(barras_df, estacion, real), aes(y = real),
           fill = COL_NO2, alpha = 0.8) +
  geom_point(aes(y = r_azar), color = "grey40", size = 1.5) +
  labs(title = "Barra: r real (0 a 3 h). Puntos: corridas al azar",
       x = NULL, y = "Correlación")
print(g11b)
# Qué vemos: donde hay mucho tránsito medido cerca, la relación aparece y
#   supera al azar; donde hay pocos puntos de conteo, no se distingue del azar.
# Ojo: eso NO prueba que allí el tránsito no importe. No encontrar algo
#   también depende de qué tan bien lo medimos.

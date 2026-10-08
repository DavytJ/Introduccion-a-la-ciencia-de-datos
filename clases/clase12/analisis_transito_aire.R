# =============================================================================
# Tránsito y calidad del aire, junio de 2024: análisis de la tabla horaria
# Una variable, grupos, dos variables y un modelo lineal
# Versión en R (dplyr + ggplot2)
# =============================================================================
#
# La tabla (transito_aire_junio2024.csv) tiene una fila por estación y hora:
#   estacion   estación de calidad de aire (tres estaciones)
#   hora       fecha y hora de la medición (hora local de Montevideo; el
#              archivo la rotula como UTC, pero no hay que convertirla)
#   transito   vehículos por hora, sumando los puntos de conteo a menos de
#              1,5 km de la estación
#   no2        dióxido de nitrógeno, promedio de la hora (µg/m³)
#   pm25       material particulado fino, promedio de la hora (µg/m³)
#
# Cómo está organizado
#   Parte 0   Carga e inspección
#   Parte 1   Faltantes
#   Parte 2   Variables nuevas
#   Parte 3   Una variable
#   Parte 4   Comparar grupos
#   Parte 5   Dos variables
#   Parte 6   Modelo lineal
#
# En este script no se usa la tabla como serie de tiempo: la hora entra solo
# como categoría (franja, tipo de día), no como eje.
#
# Paquetes (instalar una sola vez):
#   install.packages(c("dplyr", "readr", "lubridate", "ggplot2"))
# =============================================================================

library(dplyr)      # filter, mutate, group_by, summarise
library(readr)      # read_csv
library(lubridate)  # hour, wday, as_date
library(ggplot2)    # gráficos

RUTA <- "clases/clase10/transito_aire_junio2024.csv"

COL_TRANSITO <- "#2E86AB"
COL_NO2      <- "#7B4B2A"
COL_PM25     <- "#D4A373"
COL_OSCURO   <- "#5C3A21"

theme_set(theme_minimal(base_size = 12))


# =============================================================================
# PARTE 0. Carga e inspección
# =============================================================================
aire <- read_csv(here::here(RUTA))

glimpse(aire)            # nombre y tipo de cada columna
head(aire)               # primeras filas
count(aire, estacion)    # cuántas filas tiene cada estación
# Qué vemos: 2160 filas y 5 columnas. Cada estación tiene 720 filas:
#   30 días por 24 horas. El identificador es la pareja (estacion, hora).


# =============================================================================
# PARTE 1. Faltantes
# =============================================================================
# is.na(x) da TRUE donde falta el dato; sum() cuenta los TRUE.
faltantes <- aire |>
  group_by(estacion) |>
  summarise(filas        = n(),
            sin_transito = sum(is.na(transito)),
            sin_no2      = sum(is.na(no2)),
            sin_pm25     = sum(is.na(pm25)))
print(faltantes)
# Qué vemos: el tránsito está completo. Museo Romántico no tiene ningún dato
#   de NO2 (720 faltantes). Tres Cruces tiene NO2 en 291 horas y PM2.5 en 394.
#   Curva de Maronias es la más completa: 655 horas de NO2 y 720 de PM2.5.
# Consecuencia: todo lo que use NO2 se hace con dos estaciones, y en Tres
#   Cruces con menos de la mitad del mes.


# =============================================================================
# PARTE 2. Variables nuevas
# =============================================================================

# ---- 2.1 A partir de la hora -------------------------------------------------
# hour() devuelve la hora del día (0 a 23).
# wday(..., week_start = 1) devuelve el día de la semana con lunes = 1,
#   así que sábado y domingo son 6 y 7.
# case_when() asigna un valor según la primera condición que se cumple.
datos <- aire |>
  mutate(h         = hour(hora),
         dia       = as_date(hora),
         tipo_dia  = ifelse(wday(hora, week_start = 1) >= 6,
                            "fin de semana", "lunes a viernes"),
         franja    = case_when(h <= 5  ~ "madrugada",
                               h <= 11 ~ "mañana",
                               h <= 17 ~ "tarde",
                               TRUE    ~ "noche"),
         hora_pico = ifelse(h %in% c(7, 8, 9, 17, 18, 19), "hora pico", "resto"))

# Las franjas tienen un orden. Si no se lo decimos, R las ordena
# alfabéticamente (madrugada, mañana, noche, tarde).
datos <- datos |>
  mutate(franja = factor(franja,
                         levels = c("madrugada", "mañana", "tarde", "noche")))

count(datos, franja)      # 540 filas por franja: 6 horas x 30 días x 3 estaciones
count(datos, tipo_dia)

# ---- 2.2 A partir del tránsito -----------------------------------------------
# El tránsito de cada estación suma una cantidad distinta de puntos de conteo:
# Tres Cruces da 33 veces más que Curva de Maronias, y eso no significa que
# pasen 33 veces más autos. Para comparar estaciones usamos el tránsito
# relativo: 1 = lo habitual de esa estación, 2 = el doble.
#
# group_by() + mutate() calcula dentro de cada grupo sin reducir filas:
# mean(transito) es el promedio de la estación de esa fila.
# ntile(x, 3) parte los valores en tres grupos del mismo tamaño (terciles).
datos <- datos |>
  group_by(estacion) |>
  mutate(transito_rel   = transito / mean(transito),
         nivel_transito = ntile(transito, 3)) |>
  ungroup() |>
  mutate(nivel_transito = factor(nivel_transito, levels = 1:3,
                                 labels = c("bajo", "medio", "alto")),
         transito_miles = transito / 1000)

# ---- 2.3 A partir del PM2.5 --------------------------------------------------
# El logaritmo comprime los valores grandes: sirve para variables con cola larga.
datos <- datos |>
  mutate(log_pm25 = log(pm25))

glimpse(datos)

# ---- 2.4 Subconjuntos que usamos varias veces --------------------------------
con_no2     <- datos |> filter(!is.na(no2))                 # dos estaciones
tres_cruces <- datos |> filter(estacion == "Tres Cruces")
maronias    <- datos |> filter(estacion == "Curva de Maronias")


# =============================================================================
# PARTE 3. Una variable
# =============================================================================

# ---- 3.1 Resumen numérico ----------------------------------------------------
resumen_pm25 <- datos |>
  group_by(estacion) |>
  summarise(horas   = sum(!is.na(pm25)),
            minimo  = min(pm25, na.rm = TRUE),
            mediana = median(pm25, na.rm = TRUE),
            media   = mean(pm25, na.rm = TRUE),
            maximo  = max(pm25, na.rm = TRUE))
print(resumen_pm25)
# Qué vemos: en las tres estaciones la media es bastante mayor que la mediana
#   (Curva de Maronias: 20,1 contra 11,9). El máximo es 243,8.
#   El mínimo es exactamente 3,0 en las tres.

# ---- 3.2 Histograma de PM2.5 -------------------------------------------------
# Un histograma parte el eje x en intervalos (binwidth = ancho del intervalo)
# y cuenta cuántas observaciones caen en cada uno.
g1 <- ggplot(datos, aes(pm25)) +
  geom_histogram(binwidth = 5, boundary = 0, fill = COL_PM25, color = "white") +
  facet_wrap(~ estacion, ncol = 1, scales = "free_y") +
  labs(title = "PM2.5 por hora, junio de 2024",
       x = "PM2.5 (µg/m³)", y = "Cantidad de horas")
print(g1)
# Cómo leer: cada barra es un intervalo de 5 µg/m³; su altura, cuántas horas.
# Aviso de R: "Removed 470 rows containing non-finite values". No es un error:
#   son las 470 filas sin dato de PM2.5, que no entran en el histograma.
# Qué vemos: la mayoría de las horas tiene valores bajos y hay una cola larga
#   hacia la derecha (pocas horas con valores muy altos).

# ---- 3.3 Media y mediana sobre el histograma ---------------------------------
g2 <- ggplot(maronias, aes(pm25)) +
  geom_histogram(binwidth = 5, boundary = 0, fill = COL_PM25, color = "white") +
  geom_vline(xintercept = median(maronias$pm25, na.rm = TRUE),
             color = COL_OSCURO, linewidth = 1) +
  geom_vline(xintercept = mean(maronias$pm25, na.rm = TRUE),
             color = COL_OSCURO, linewidth = 1, linetype = "dashed") +
  labs(title = "PM2.5 en Curva de Maronias",
       subtitle = "Línea llena: mediana (11,9). Línea punteada: media (20,1).",
       x = "PM2.5 (µg/m³)", y = "Cantidad de horas")
print(g2)
# Qué vemos: la media queda corrida hacia la cola. Unas pocas horas con
#   valores muy altos la arrastran; la mediana no se mueve por ellas.

# ---- 3.4 El piso del instrumento ---------------------------------------------
# Mirando solo los valores bajos, con intervalos más finos:
g3 <- ggplot(filter(datos, pm25 < 30), aes(pm25)) +
  geom_histogram(binwidth = 0.5, boundary = 0, fill = COL_PM25, color = "white") +
  facet_wrap(~ estacion, ncol = 1, scales = "free_y") +
  labs(title = "PM2.5 por debajo de 30 µg/m³",
       x = "PM2.5 (µg/m³)", y = "Cantidad de horas")
print(g3)

datos |>
  group_by(estacion) |>
  summarise(horas_en_3 = sum(pm25 == 3, na.rm = TRUE))
# Qué vemos: no hay ningún valor por debajo de 3 y hay una barra alta
#   justo en 3 (128 horas en Museo Romántico, 40 en Curva de Maronias, 5 en
#   Tres Cruces). El instrumento no informa valores menores: 3 quiere decir
#   "3 o menos".

# ---- 3.5 El mismo histograma en logaritmo ------------------------------------
g4 <- ggplot(datos, aes(log_pm25)) +
  geom_histogram(bins = 30, fill = COL_PM25, color = "white") +
  facet_wrap(~ estacion, ncol = 1, scales = "free_y") +
  labs(title = "Logaritmo de PM2.5",
       x = "log(PM2.5)", y = "Cantidad de horas")
print(g4)
# Qué vemos: en logaritmo la cola larga desaparece y la forma es mucho más
#   simétrica. El piso en 3 sigue visible (log(3) = 1,1).

# ---- 3.6 Dos variables simétricas, para comparar -----------------------------
g5 <- ggplot(tres_cruces, aes(no2)) +
  geom_histogram(binwidth = 5, boundary = 0, fill = COL_NO2, color = "white") +
  labs(title = "NO2 en Tres Cruces", x = "NO2 (µg/m³)", y = "Cantidad de horas")
print(g5)

g6 <- ggplot(tres_cruces, aes(transito)) +
  geom_histogram(binwidth = 2500, boundary = 0, fill = COL_TRANSITO, color = "white") +
  labs(title = "Tránsito en Tres Cruces", x = "Vehículos por hora",
       y = "Cantidad de horas")
print(g6)

tres_cruces |>
  summarise(media_no2 = mean(no2, na.rm = TRUE), mediana_no2 = median(no2, na.rm = TRUE),
            media_transito = mean(transito), mediana_transito = median(transito))
# Qué vemos: el NO2 de Tres Cruces no tiene cola larga; media y mediana
#   coinciden (38,2). El tránsito tiene dos grupos de valores: horas de poco
#   tránsito (la madrugada) y horas de mucho tránsito (el día).

# ---- 3.7 Diagrama de caja por estación ---------------------------------------
# La caja va del primer al tercer cuartil; la línea del medio es la mediana.
# Los puntos sueltos son valores alejados del resto.
g7 <- ggplot(datos, aes(estacion, pm25)) +
  geom_boxplot(fill = COL_PM25, outlier.size = 0.8) +
  labs(title = "PM2.5 por estación", x = NULL, y = "PM2.5 (µg/m³)")
print(g7)

g8 <- ggplot(con_no2, aes(estacion, no2)) +
  geom_boxplot(fill = COL_NO2, outlier.size = 0.8) +
  labs(title = "NO2 por estación (las dos que lo miden)", x = NULL, y = "NO2 (µg/m³)")
print(g8)
# Qué vemos: Museo Romántico tiene el PM2.5 más bajo. En las tres hay muchos
#   puntos sueltos hacia arriba: es la cola larga del histograma, vista de otra
#   forma. El NO2 tiene medianas parecidas en las dos estaciones (30 y 38),
#   con más dispersión en Curva de Maronias.


# =============================================================================
# PARTE 4. Comparar grupos
# =============================================================================

# ---- 4.1 Promedios por franja horaria ----------------------------------------
por_franja <- datos |>
  group_by(estacion, franja) |>
  summarise(transito     = mean(transito),
            transito_rel = mean(transito_rel),
            no2          = mean(no2, na.rm = TRUE),
            pm25         = mean(pm25, na.rm = TRUE),
            .groups = "drop")
print(por_franja)

g9 <- ggplot(por_franja, aes(franja, transito_rel)) +
  geom_col(fill = COL_TRANSITO) +
  geom_hline(yintercept = 1, color = "grey40", linetype = "dashed") +
  facet_wrap(~ estacion) +
  labs(title = "Tránsito por franja horaria, relativo a la media de la estación",
       x = NULL, y = "Tránsito relativo (1 = media de la estación)")
print(g9)

g10 <- ggplot(por_franja, aes(franja, pm25)) +
  geom_col(fill = COL_PM25) +
  facet_wrap(~ estacion) +
  labs(title = "PM2.5 promedio por franja horaria", x = NULL, y = "PM2.5 (µg/m³)")
print(g10)
# Qué vemos: el tránsito es máximo de tarde y mínimo de madrugada, en las
#   tres estaciones. El PM2.5 es máximo de noche (Tres Cruces: 31,9 de noche
#   contra 17,2 de tarde): no sigue al tránsito de la misma franja.
# Por qué se usa transito_rel: con el tránsito en vehículos, las barras de
#   Tres Cruces aplastarían a las otras dos.

# ---- 4.2 Entre semana y fin de semana ----------------------------------------
por_tipo_dia <- datos |>
  group_by(estacion, tipo_dia) |>
  summarise(transito     = mean(transito),
            transito_rel = mean(transito_rel),
            no2          = mean(no2, na.rm = TRUE),
            pm25         = mean(pm25, na.rm = TRUE),
            .groups = "drop")
print(por_tipo_dia)

g11 <- ggplot(por_tipo_dia, aes(estacion, transito_rel, fill = tipo_dia)) +
  geom_col(position = "dodge") +
  scale_fill_manual(values = c("fin de semana" = COL_PM25,
                               "lunes a viernes" = COL_TRANSITO)) +
  labs(title = "Tránsito relativo según el tipo de día",
       x = NULL, y = "Tránsito relativo", fill = NULL)
print(g11)
# Qué vemos: el fin de semana el tránsito baja en las tres, pero no igual:
#   0,67 en Museo Romántico, 0,78 en Tres Cruces y 0,90 en Curva de Maronias.
#   El PM2.5 casi no cambia entre semana y fin de semana.

# ---- 4.3 NO2 según el nivel de tránsito --------------------------------------
no2_por_nivel <- con_no2 |>
  group_by(estacion, nivel_transito) |>
  summarise(no2 = mean(no2), horas = n(), .groups = "drop")
print(no2_por_nivel)

g12 <- ggplot(no2_por_nivel, aes(nivel_transito, no2)) +
  geom_col(fill = COL_NO2) +
  facet_wrap(~ estacion) +
  labs(title = "NO2 promedio según el nivel de tránsito de la hora",
       x = "Nivel de tránsito (terciles de cada estación)", y = "NO2 (µg/m³)")
print(g12)
# Qué vemos: en Tres Cruces el NO2 sube en cada escalón de tránsito. En Curva
#   de Maronias sube del nivel bajo al medio y después no cambia.

# ---- 4.4 Hora pico contra el resto -------------------------------------------
con_no2 |>
  group_by(estacion, hora_pico) |>
  summarise(no2 = mean(no2), horas = n(), .groups = "drop")
# Qué vemos: en las dos estaciones el NO2 es más alto en hora pico
#   (Tres Cruces: 46,7 contra 35,4).

# ---- 4.5 Otra tabla: una fila por estación y día -----------------------------
# Cambia la unidad de análisis: de la hora al día. La guía de la OMS (2021)
# para el promedio de 24 horas es 15 µg/m³ de PM2.5 y 25 µg/m³ de NO2.
# Un promedio diario hecho con pocas horas no representa al día: nos quedamos
# con los días que tienen al menos 18 horas de dato.
diario <- datos |>
  group_by(estacion, dia) |>
  summarise(horas_pm25 = sum(!is.na(pm25)),
            pm25_dia   = mean(pm25, na.rm = TRUE),
            horas_no2  = sum(!is.na(no2)),
            no2_dia    = mean(no2, na.rm = TRUE),
            .groups = "drop")

dias_pm25 <- diario |>
  filter(horas_pm25 >= 18) |>
  mutate(supera = ifelse(pm25_dia > 15, "supera la guía", "no supera"))

count(dias_pm25, estacion, supera)

g13 <- ggplot(dias_pm25, aes(estacion, fill = supera)) +
  geom_bar() +
  scale_fill_manual(values = c("supera la guía" = COL_OSCURO, "no supera" = "grey75")) +
  labs(title = "Días con PM2.5 promedio por encima de 15 µg/m³",
       subtitle = "Solo días con al menos 18 horas de dato",
       x = NULL, y = "Cantidad de días", fill = NULL)
print(g13)

diario |>
  filter(horas_no2 >= 18) |>
  mutate(supera = no2_dia > 25) |>
  count(estacion, supera)
# Qué vemos: en Tres Cruces 14 de 16 días superan la guía de PM2.5; en Curva
#   de Maronias, 15 de 30; en Museo Romántico, 5 de 23.
#   En NO2: 10 de 10 días en Tres Cruces y 20 de 27 en Curva de Maronias.
# Ojo: las barras no tienen la misma altura porque cada estación tiene una
#   cantidad distinta de días con dato suficiente.


# =============================================================================
# PARTE 5. Dos variables
# =============================================================================

# ---- 5.1 Diagramas de dispersión ---------------------------------------------
g14 <- ggplot(con_no2, aes(transito, no2)) +
  geom_point(alpha = 0.4, size = 1, color = COL_NO2) +
  facet_wrap(~ estacion, scales = "free_x") +
  labs(title = "Tránsito y NO2, hora a hora",
       x = "Vehículos por hora", y = "NO2 (µg/m³)")
print(g14)

g15 <- ggplot(datos, aes(transito, pm25)) +
  geom_point(alpha = 0.4, size = 1, color = COL_PM25) +
  facet_wrap(~ estacion, scales = "free_x") +
  labs(title = "Tránsito y PM2.5, hora a hora",
       x = "Vehículos por hora", y = "PM2.5 (µg/m³)")
print(g15)

g16 <- ggplot(con_no2, aes(pm25, no2)) +
  geom_point(alpha = 0.4, size = 1, color = COL_OSCURO) +
  facet_wrap(~ estacion) +
  labs(title = "PM2.5 y NO2, hora a hora",
       x = "PM2.5 (µg/m³)", y = "NO2 (µg/m³)")
print(g16)
# Cómo leer: cada punto es una hora. scales = "free_x" deja que cada panel
#   tenga su propio eje x, porque el tránsito de las estaciones no es comparable.
# Qué vemos: en Tres Cruces la nube tránsito-NO2 sube hacia la derecha. En
#   Curva de Maronias casi no tiene forma. Tránsito y PM2.5: sin forma en
#   ninguna de las tres.

# ---- 5.2 Coeficiente de correlación por estación -----------------------------
# cor() da un número entre -1 y 1: cerca de 1, las dos variables suben juntas
# siguiendo una recta; cerca de 0, no hay relación lineal.
# use = "complete.obs" usa solo las filas donde las dos variables tienen dato.
correlaciones_no2 <- con_no2 |>
  group_by(estacion) |>
  summarise(transito_no2 = cor(transito, no2, use = "complete.obs"),
            no2_pm25     = cor(no2, pm25,     use = "complete.obs"))
print(correlaciones_no2)

correlaciones_pm25 <- datos |>
  group_by(estacion) |>
  summarise(transito_pm25 = cor(transito, pm25, use = "complete.obs"))
print(correlaciones_pm25)
# Qué vemos:
#                       transito-NO2   transito-PM2.5   NO2-PM2.5
#   Curva de Maronias       0,15          -0,15           0,55
#   Tres Cruces             0,59          -0,02           0,40
#   Museo Romántico          --           -0,10            --
# La misma pareja de variables da 0,59 en una estación y 0,15 en la otra.
# Ojo: una correlación no dice cuál variable influye sobre cuál, y dos
#   variables con ritmo diario se parecen aunque no tengan relación entre sí.

# ---- 5.3 La dispersión con una tercera variable: el color --------------------
g17 <- ggplot(filter(tres_cruces, !is.na(no2)), aes(transito, no2, color = franja)) +
  geom_point(size = 1.5, alpha = 0.7) +
  scale_color_manual(values = c("madrugada" = "grey60", "mañana" = COL_PM25,
                                "tarde" = COL_TRANSITO, "noche" = COL_OSCURO)) +
  labs(title = "Tránsito y NO2 en Tres Cruces, por franja horaria",
       x = "Vehículos por hora", y = "NO2 (µg/m³)", color = NULL)
print(g17)
# Qué vemos: la madrugada queda abajo a la izquierda (poco tránsito, poco
#   NO2) y la tarde arriba a la derecha. La noche tiene NO2 alto para el
#   tránsito que tiene: queda por encima del resto.


# =============================================================================
# PARTE 6. Modelo lineal
# =============================================================================
# La idea: resumir la nube de puntos con una recta.
#   no2 = a + b · transito_miles + error
#     a      el NO2 que la recta le asigna a una hora sin tránsito
#     b      cuánto sube el NO2 por cada mil vehículos por hora de más
#     error  lo que la recta no explica
# lm() busca la recta que hace mínima la suma de los errores al cuadrado.
# Usamos el tránsito en miles para que b tenga un tamaño cómodo de leer.

# ---- 6.1 La recta en Tres Cruces ---------------------------------------------
tc <- tres_cruces |> filter(!is.na(no2))       # las 291 horas con NO2

modelo_tc <- lm(no2 ~ transito_miles, data = tc)
coef(modelo_tc)                    # a y b
summary(modelo_tc)$r.squared       # R²: parte de la variación que explica la recta
# Qué vemos: a = 18,3 y b = 0,79. Una hora con 30 mil vehículos tiene, según
#   la recta, 18,3 + 0,79 · 30 = 42 µg/m³ de NO2. R² = 0,35: la recta explica
#   un tercio de la variación del NO2.

g18 <- ggplot(tc, aes(transito_miles, no2)) +
  geom_point(alpha = 0.4, size = 1, color = COL_NO2) +
  geom_abline(intercept = coef(modelo_tc)[1], slope = coef(modelo_tc)[2],
              color = COL_OSCURO, linewidth = 1) +
  labs(title = "Tres Cruces: NO2 = 18,3 + 0,79 · tránsito (en miles)",
       x = "Miles de vehículos por hora", y = "NO2 (µg/m³)")
print(g18)

# ---- 6.2 La misma recta en Curva de Maronias ---------------------------------
cm <- maronias |> filter(!is.na(no2))

modelo_cm <- lm(no2 ~ transito_miles, data = cm)
coef(modelo_cm)
summary(modelo_cm)$r.squared
# Qué vemos: R² = 0,02. La recta casi no explica nada. Curva de Maronias
#   tiene muy pocos puntos de conteo cerca: el tránsito medido ahí representa
#   mal al tránsito que rodea a la estación.
# Ojo: eso no prueba que allí el tránsito no importe.

# ---- 6.3 Agregar una variable categórica: la franja --------------------------
# Con una variable categórica, lm() elige una categoría de referencia
# (la primera: madrugada) y estima cuánto suma cada una de las otras.
modelo_tc2 <- lm(no2 ~ transito_miles + franja, data = tc)
coef(modelo_tc2)
summary(modelo_tc2)$r.squared
# Qué vemos: a igual tránsito, la noche tiene 9,2 µg/m³ más de NO2 que la
#   madrugada. Es lo que se veía en el gráfico por colores. R² sube a 0,39.

# ---- 6.4 Agregar otra variable numérica: el PM2.5 ----------------------------
modelo_tc3 <- lm(no2 ~ transito_miles + pm25, data = tc)
coef(modelo_tc3)
summary(modelo_tc3)$r.squared
# Qué vemos: R² = 0,47. El PM2.5 no es una causa del NO2: las horas en que el
#   aire no se renueva tienen los dos contaminantes altos. El PM2.5 funciona
#   como indicador de esas condiciones, que no están en la tabla (viento, lluvia).

# ---- 6.5 Los errores del modelo (residuos) -----------------------------------
# residuo = valor medido - valor que da la recta
tc <- tc |>
  mutate(predicho = fitted(modelo_tc),
         residuo  = resid(modelo_tc))

g19 <- ggplot(tc, aes(predicho, residuo)) +
  geom_hline(yintercept = 0, color = "grey50") +
  geom_point(alpha = 0.4, size = 1, color = COL_NO2) +
  labs(title = "Residuos del modelo de Tres Cruces",
       x = "NO2 que da la recta (µg/m³)", y = "Residuo (µg/m³)")
print(g19)

sd(tc$residuo)                                 # tamaño típico del error
cor(tc$residuo[-1], tc$residuo[-nrow(tc)])     # residuo de una hora contra el de la anterior
# Qué vemos: los residuos se reparten a los dos lados del cero, con un error
#   típico de 14 µg/m³. Pero el residuo de una hora se parece mucho al de la
#   hora anterior (r = 0,80): si el modelo se queda corto a las 20, también se
#   queda corto a las 21.
# Consecuencia: las horas no son observaciones independientes. La recta y el
#   R² sirven para describir; los errores estándar y p-valores que muestra
#   summary(modelo_tc) suponen independencia y acá no son válidos.

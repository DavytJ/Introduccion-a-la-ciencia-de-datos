# =============================================================================
# Tránsito y calidad del aire, junio de 2024 — Soluciones
# Describir una tabla: una variable, grupos, dos variables y una recta
# =============================================================================
#
# LA TABLA (transito_aire_junio2024.csv): una fila por estación y hora
#   estacion   estación de calidad de aire (tres estaciones)
#   hora       fecha y hora de la medición
#   transito   vehículos por hora cerca de la estación
#   no2        dióxido de nitrógeno, promedio de la hora (µg/m³)
#   pm25       material particulado fino, promedio de la hora (µg/m³)
#
# Paquetes (instalar una sola vez):
#   install.packages(c("dplyr", "readr", "lubridate", "ggplot2"))
# =============================================================================

library(dplyr)
library(readr)
library(lubridate)
library(ggplot2)

RUTA <- "clases/clase10/transito_aire_junio2024.csv"
theme_set(theme_minimal(base_size = 12))


# ---- Ejercicio 1 (COMPLETAR 1 a 2) ------------------------------
datos <- read_csv(RUTA)

glimpse(datos)
count(datos, estacion)

# Modelo: is.na(x) da TRUE donde falta el dato; sum() cuenta los TRUE.
datos |>
  group_by(estacion) |>
  summarise(sin_transito = sum(is.na(transito)))

datos |>
  group_by(estacion) |>
  summarise(sin_no2  = sum(is.na(no2)),
            sin_pm25 = sum(is.na(pm25)))


# ---- Ejercicio 2 (COMPLETAR 3 a 4) ------------------------------
datos <- datos |>
  mutate(h = hour(hora))

# Ayuda:
#   wday(hora, week_start = 1) da el día de la semana con lunes = 1;
#     sábado y domingo son 6 y 7.
#   ifelse(condición, valor_si_se_cumple, valor_si_no)
#   h %in% c(7, 8, 9) es TRUE cuando h es alguno de esos valores.

datos <- datos |>
  mutate(tipo_dia  = ifelse(wday(hora, week_start = 1) >= 6,
                            "fin de semana", "lunes a viernes"),
         hora_pico = ifelse(h %in% c(7, 8, 9, 17, 18, 19), "hora pico", "resto"))
count(datos, tipo_dia)
count(datos, hora_pico)


# ---- Ejercicio 3 (COMPLETAR 5) ------------------------------

datos <- datos |>
  mutate(franja = case_when(h <= 5  ~ "madrugada",
                            h <= 11 ~ "mañana",
                            h <= 17 ~ "tarde",
                            TRUE    ~ "noche"))

datos <- datos |>
  mutate(franja = factor(franja,
                         levels = c("madrugada", "mañana", "tarde", "noche")))
count(datos, franja)


# ---- Ejercicio 4 (COMPLETAR 6 a 8) ------------------------------
maronias <- datos |> filter(estacion == "Curva de Maronias")

# Ayuda:
#   mean(x, na.rm = TRUE) y median(x, na.rm = TRUE) ignoran los faltantes.
#   ggplot(tabla, aes(variable)) + geom_histogram(binwidth = ancho)
#   geom_vline(xintercept = valor) dibuja una línea vertical.

maronias |>
  summarise(media = mean(pm25, na.rm = TRUE), mediana = median(pm25, na.rm = TRUE))

ggplot(maronias, aes(pm25)) +
  geom_histogram(binwidth = 5, boundary = 0, fill = "#D4A373", color = "white") +
  geom_vline(xintercept = median(maronias$pm25, na.rm = TRUE)) +
  geom_vline(xintercept = mean(maronias$pm25, na.rm = TRUE), linetype = "dashed") +
  labs(x = "PM2.5 (µg/m³)", y = "Cantidad de horas")


# ---- Ejercicio 5 (COMPLETAR 9 a 11) ------------------------------
tres_cruces <- datos |> filter(estacion == "Tres Cruces")

# Ayuda:
#   tabla |> group_by(grupo) |> summarise(nombre = mean(variable, na.rm = TRUE))
#   ggplot(tabla, aes(grupo, valor)) + geom_col()

por_franja <- tres_cruces |>
  group_by(franja) |>
  summarise(transito = mean(transito),
            pm25     = mean(pm25, na.rm = TRUE))
print(por_franja)

ggplot(por_franja, aes(franja, transito)) +
  geom_col(fill = "#2E86AB") +
  labs(x = NULL, y = "Vehículos por hora (promedio)")

ggplot(por_franja, aes(franja, pm25)) +
  geom_col(fill = "#D4A373") +
  labs(x = NULL, y = "PM2.5 (µg/m³, promedio)")


# ---- Ejercicio 6 (COMPLETAR 12 a 13) ------------------------------
datos |>
  group_by(estacion) |>
  summarise(transito_medio = mean(transito))

# group_by() + mutate() calcula dentro de cada grupo sin reducir filas:
# acá mean(transito) es el promedio de la estación de esa fila.
# transito_rel = 1 es lo habitual de esa estación; 2 es el doble.
datos <- datos |>
  group_by(estacion) |>
  mutate(transito_rel = transito / mean(transito)) |>
  ungroup()

# Ayuda:
#   group_by(grupo1, grupo2) agrupa por dos columnas a la vez.
#   aes(x, y, fill = grupo) + geom_col(position = "dodge") pone las barras
#     de cada grupo una al lado de la otra.

por_tipo_dia <- datos |>
  group_by(estacion, tipo_dia) |>
  summarise(transito_rel = mean(transito_rel), .groups = "drop")
print(por_tipo_dia)

ggplot(por_tipo_dia, aes(estacion, transito_rel, fill = tipo_dia)) +
  geom_col(position = "dodge") +
  labs(x = NULL, y = "Tránsito relativo", fill = NULL)


# ---- Ejercicio 7 (COMPLETAR 14 a 16) ------------------------------
con_no2 <- datos |> filter(!is.na(no2))
count(con_no2, estacion)

# Ayuda:
#   ggplot(tabla, aes(x, y)) + geom_point(alpha = 0.4)
#   facet_wrap(~ grupo, scales = "free_x") hace un panel por grupo, cada uno
#     con su propio eje x.
#   cor(x, y, use = "complete.obs") usa solo las filas con los dos datos.

ggplot(con_no2, aes(transito, no2)) +
  geom_point(alpha = 0.4, size = 1, color = "#7B4B2A") +
  facet_wrap(~ estacion, scales = "free_x") +
  labs(x = "Vehículos por hora", y = "NO2 (µg/m³)")

con_no2 |>
  group_by(estacion) |>
  summarise(transito_no2 = cor(transito, no2, use = "complete.obs"),
            no2_pm25     = cor(no2, pm25,     use = "complete.obs"))


# ---- Ejercicio 8 (COMPLETAR 17 a 19) ------------------------------
tc <- datos |>
  filter(estacion == "Tres Cruces", !is.na(no2)) |>
  mutate(transito_miles = transito / 1000)

# Ayuda:
#   lm(y ~ x, data = tabla) busca la recta y = a + b·x más cercana a los puntos.
#   coef(modelo)[1] es a (ordenada) y coef(modelo)[2] es b (pendiente).
#   geom_abline(intercept = a, slope = b) dibuja la recta.

modelo <- lm(no2 ~ transito_miles, data = tc)
coef(modelo)
summary(modelo)$r.squared

ggplot(tc, aes(transito_miles, no2)) +
  geom_point(alpha = 0.4, size = 1, color = "#7B4B2A") +
  geom_abline(intercept = coef(modelo)[1], slope = coef(modelo)[2], linewidth = 1) +
  labs(x = "Miles de vehículos por hora", y = "NO2 (µg/m³)")

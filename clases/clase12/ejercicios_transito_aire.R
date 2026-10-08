# =============================================================================
# Tránsito y calidad del aire, junio de 2024 — Ejercicios
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
# CÓMO SE LEE ESTE ARCHIVO
#   Cada ejercicio tiene un encabezado con cinco rótulos:
#     Qué se busca      el propósito del ejercicio
#     Ya está escrito   el código que viene hecho; no hay que tocarlo
#     Se pide           lo único que hay que escribir, numerado
#     Se verifica       los resultados que tienen que dar
#     En la bitácora    la pregunta que se responde por escrito
#   Los lugares donde hay que escribir están marcados así:
#     # --- COMPLETAR 1 ---
#   La numeración de «Se pide» y la de los COMPLETAR es la misma.
#
#   El archivo se corre de arriba hacia abajo, línea por línea (Ctrl + Enter).
#   Los ejercicios se apoyan en los anteriores: las columnas que se crean en
#   el 2 y el 3 se usan después.
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


# =============================================================================
# EJERCICIO 1. FALTANTES
# =============================================================================
# En la Parte 1 se contaron los faltantes de la tabla aire:
#
# faltantes <- aire |>
#   group_by(estacion) |>
#   summarise(filas        = n(),
#             sin_transito = sum(is.na(transito)),
#             sin_no2      = sum(is.na(no2)),
#             sin_pm25     = sum(is.na(pm25)))
#
# Contar los faltantes de la tabla datos, agregando las variables nuevas:
# franja, tipo_dia, transito_rel y log_pm25.
# -----------------------------------------------------------------------------


# =============================================================================
# EJERCICIO 2. ¿ESTÁ BIEN DEFINIDA LA HORA PICO?
# =============================================================================
# En la Parte 2 se creó hora_pico: las horas 7, 8, 9, 17, 18 y 19.
# El gráfico muestra el tránsito promedio de cada hora del día en Tres Cruces,
# de lunes a viernes, con las horas pico en color.

por_hora <- datos |>
  filter(estacion == "Tres Cruces", tipo_dia == "lunes a viernes") |>
  group_by(h, hora_pico) |>
  summarise(transito = mean(transito), .groups = "drop")

ggplot(por_hora, aes(h, transito, fill = hora_pico)) +
  geom_col() +
  scale_fill_manual(values = c("hora pico" = "#5C3A21", "resto" = "grey75")) +
  labs(title = "Tránsito promedio por hora del día, Tres Cruces, lunes a viernes",
       x = "Hora del día", y = "Vehículos por hora", fill = NULL)

# 1. Mirar el gráfico: ¿las horas en color son las de más tránsito?
#    Anotar qué horas están mal clasificadas.
# 2. Crear en datos una variable nueva, con el nombre que elijan, que marque
#    las horas que según el gráfico tienen más tránsito.
# 3. Repetir el gráfico usando la variable nueva en lugar de hora_pico.
# -----------------------------------------------------------------------------

# =============================================================================
# EJERCICIO 3. PM2.5 POR FRANJA HORARIA
# =============================================================================
# El gráfico g9 muestra el tránsito relativo por franja horaria.
# La tabla por_franja también tiene el promedio de pm25.
#
# 1. Copiar el código de g9 y cambiarlo para graficar pm25 en lugar de
#    transito_rel. Cambiar también el título, el nombre del eje y el color
#    (COL_PM25).
# 2. La línea punteada en 1 ya no tiene sentido: sacarla.
# 3. ¿En qué franja es máximo el PM2.5? ¿Coincide con la del tránsito?
# -----------------------------------------------------------------------------


# =============================================================================
# EJERCICIO 4. AGREGAR UNA VARIABLE AL MODELO
# =============================================================================
# El modelo modelo_tc3 explica el NO2 con el tránsito y el PM2.5:
#
# modelo_tc3 <- lm(no2 ~ transito_miles + pm25, data = tc)
# coef(modelo_tc3)
# summary(modelo_tc3)$r.squared
#
# 1. Copiar el código y agregar la variable franja al modelo.
#    Guardarlo como modelo_tc4.
# 2. Mostrar los coeficientes y el R².
# 3. ¿Mejoró el R²? ¿Mucho o poco?
# -----------------------------------------------------------------------------


# =============================================================================
# EJERCICIO 5. UNA VARIABLE BINARIA A PARTIR DEL RESULTADO
# =============================================================================
# En summary(modelo_tc4), de las tres franjas solo la noche tiene un
# coeficiente que se distingue de cero.
#
# 1. Crear en tc la variable noche: vale 1 si la franja es "noche" y 0 si no.
# 2. Ajustar modelo_tc5 con transito_miles, pm25 y noche (sin franja).
# 3. Mostrar los coeficientes y el R². ¿Cuánto suma la noche?
# -----------------------------------------------------------------------------


# =============================================================================
# EJERCICIO 6. Interacciones
# =============================================================================

COL_FRANJA <- c("madrugada" = "#0072B2", "mañana" = "#E69F00",
                "tarde" = "#009E73", "noche" = "#CC79A7")

g17 <- ggplot(tc, aes(transito_miles, no2, color = franja)) +
  geom_point(size = 2.5, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 1.2) +
  scale_color_manual(values = COL_FRANJA) +
  labs(title = "Tránsito y NO2 en Tres Cruces, por franja horaria",
       x = "Miles de vehículos por hora", y = "NO2 (µg/m³)", color = NULL)
print(g17)
# Qué vemos: cada franja tiene su recta, y no son paralelas. En la madrugada
#   el NO2 sube mucho más rápido con el tránsito que en el resto del día.

# En el gráfico g17 una de las cuatro rectas tiene una pendiente distinta
# de las demás. El modelo con interacción se escribió así:
#
# modelo_tc6 <- lm(no2 ~ transito_miles * franja, data = tc)
#
# 1. Mirar el gráfico: ¿qué franja tiene la recta más empinada?
# 2. Crear en tc una variable binaria para esa franja (1 si la hora
#    pertenece a esa franja, 0 si no).
# 3. Ajustar modelo_tc7 con la interacción entre transito_miles y la
#    variable nueva. Mostrar los coeficientes y el R²

# =============================================================================
# EJERCICIO 7. ¿QUÉ PASA EN LA TARDE?
# =============================================================================
# En el gráfico g17 los puntos de la tarde forman dos grupos separados.
#
# 1. Crear la tabla tarde con las filas de tc cuya franja es "tarde".
# 2. Copiar el código de g17 y cambiarlo para usar la tabla tarde y
#    colorear por tipo_dia en lugar de franja.
# 3. ¿Qué son los dos grupos?
# -----------------------------------------------------------------------------

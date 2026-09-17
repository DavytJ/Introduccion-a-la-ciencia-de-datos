# =============================================================================
# Clase 9 — Unión de fuentes y gráficos por grupo
# Ejemplo: ozono (O3) y material particulado (PM2.5) — Montevideo, ene–abr 2024
# Fuente: Catálogo de Datos Abiertos (catalogodatos.gub.uy), Intendencia de Montevideo
# Versión R / ggplot2 — continúa carga_y_transformacion.R (clase 7)
# =============================================================================
# Lo que ya sabemos hacer (clase 7) y acá se repite sin explicación:
#   cargar, limpiar nombres de estación, quitar NA, agrupar por hora/día, un gráfico.
# Lo nuevo de hoy:
#   1. una función que hace lo mismo con cualquiera de los dos archivos
#   2. unir dos fuentes con inner_join y ver qué se pierde al unir
#   3. un color por grupo: aes(color = ...) y la leyenda sale sola
#   4. dos geometrías nuevas: geom_boxplot y geom_point sobre dos variables
#   5. facet_wrap: la misma pregunta en varios paneles
# =============================================================================

# -----------------------------------------------------------------------------
# Paquetes
# -----------------------------------------------------------------------------
paquetes <- c("tidyverse", "lubridate", "here", "patchwork")
faltantes <- paquetes[!(paquetes %in% installed.packages()[, "Package"])]
if (length(faltantes) > 0) install.packages(faltantes)
invisible(lapply(paquetes, function(p) suppressPackageStartupMessages(library(p, character.only = TRUE))))

# Carpeta donde el script guarda las figuras (las usa el teórico)
dir.create(here::here("clases/clase9/imagenes"), showWarnings = FALSE, recursive = TRUE)
guardar <- function(p, nombre, ancho = 8, alto = 5) {
  ggsave(here::here("clases/clase9/imagenes", nombre), p,
         width = ancho, height = alto, dpi = 300, bg = "white")
}


# =============================================================================
# 1. Carga y limpieza: lo de la clase 7, ahora dentro de una función
# =============================================================================
# En la clase 7 limpiamos la columna estación del ozono con un diccionario.
# Hoy tenemos dos archivos con el mismo problema. En vez de copiar el bloque
# dos veces, lo convertimos en función: se escribe una vez y se llama dos.

pauta_limpieza <- c(
  "Ã³" = "o", "Ã±" = "ni", "Ã¡" = "á", "Ã©" = "é", "Ã­" = "í",
  "Ãº" = "ú", "Ã“" = "Ó", "Ã‘" = "NI", "Ã" = "í"
)

cargar_aire <- function(archivo, columna_valor) {
  # archivo:        nombre del archivo dentro de clases/clase7
  # columna_valor:  nombre de la columna con la medición ("o3", "pm2_5", ...)
  # Devuelve fecha, estacion y la columna de valor, sin filas sin medición.
  read_csv(here::here("clases/clase7", archivo),
           locale = locale(encoding = "latin1"), show_col_types = FALSE) %>%
    mutate(estacion = str_replace_all(estacion, pauta_limpieza)) %>%
    filter(!is.na(.data[[columna_valor]])) %>%
    select(fecha, estacion, all_of(columna_valor))
}

ozono <- cargar_aire("o3_01_2024_04_2024.csv", "o3")
pm    <- cargar_aire("pm_2_5_01_2024_04_2024.csv", "pm2_5")

head(ozono)
head(pm)

# ¿Las dos redes miden en las mismas estaciones? Esto decide qué se puede unir.
unique(ozono$estacion)
unique(pm$estacion)


# =============================================================================
# 2. Lo simple primero: unir directo, minuto a minuto
# =============================================================================
# Para poner O3 y PM2.5 en la misma fila hay que decir CON QUÉ se aparean:
# misma estación y misma fecha. Esa es la clave de la unión.
# inner_join: se quedan solo las filas que existen en ambos lados.
aire_min <- inner_join(ozono, pm, by = c("fecha", "estacion"))

nrow(ozono); nrow(pm); nrow(aire_min)      # ¿cuánto quedó?
count(aire_min, estacion)                  # ¿qué estaciones quedaron?

# Lo que no está en aire_min no desapareció: sigue en ozono y en pm.
# Se puede graficar; lo que no se puede es comparar.


# =============================================================================
# 3. Agregación horaria: también en una función
# =============================================================================
agregar_hora <- function(datos, columna_valor) {
  datos %>%
    mutate(fecha_hora = floor_date(fecha, unit = "hour")) %>%
    group_by(estacion, fecha_hora) %>%
    summarise(
      media  = mean(.data[[columna_valor]]),
      maximo = max(.data[[columna_valor]]),
      n_min  = n(),
      .groups = "drop"
    )
}

o3_h <- agregar_hora(ozono, "o3")
pm_h <- agregar_hora(pm, "pm2_5")

# Unión horaria: una fila por estación y hora, con las dos medias
aire <- inner_join(
  o3_h %>% select(estacion, fecha_hora, o3    = media),
  pm_h %>% select(estacion, fecha_hora, pm2_5 = media),
  by = c("estacion", "fecha_hora")
)

nrow(o3_h); nrow(pm_h); nrow(aire)
count(aire, estacion)


# =============================================================================
# 4. Un color por grupo: las dos series en el tiempo
# =============================================================================
# En ggplot un atributo pasa a ser informativo cuando va DENTRO de aes():
#   geom_line(color = "blue")        -> fijo, decisión de legibilidad
#   aes(color = estacion)            -> mapeado, un color por estación y leyenda
# No hace falta un bucle: ggplot parte los datos por la variable mapeada.
#
# Cada serie se grafica desde su propia tabla (o3_h, pm_h), con todas sus
# estaciones. aire se usa recién para comparar.

p_o3 <- ggplot(o3_h, aes(x = fecha_hora, y = media, color = estacion)) +
  geom_line(linewidth = 0.3) +
  theme_minimal() +
  labs(title = "Ozono y PM2.5 por hora, enero a abril de 2024",
       x = NULL, y = "O3 (µg/m³)", color = "Estación")

p_pm <- ggplot(pm_h, aes(x = fecha_hora, y = media, color = estacion)) +
  geom_line(linewidth = 0.3) +
  theme_minimal() +
  labs(x = "Fecha", y = "PM2.5 (µg/m³)", color = "Estación")

# patchwork: "/" apila, "|" pone lado a lado. Apilados porque las unidades y
# los rangos son distintos: en el mismo eje el PM2.5 quedaría aplastado.
p_series <- p_o3 / p_pm
p_series
guardar(p_series, "series_o3_pm25.png", ancho = 11, alto = 7)


# =============================================================================
# 5. Perfil horario: ¿a qué hora del día hay más ozono? ¿y más PM2.5?
# =============================================================================
# Agrupamos por la HORA DEL DÍA (0 a 23), no por cada hora del calendario.
# Es una pregunta distinta a la de la serie: no "cuándo" sino "a qué hora".
# Para tener los dos contaminantes en paneles, apilamos las tablas con una
# columna que diga cuál es cuál (bind_rows) y usamos facet_wrap.

perfil <- bind_rows(
  o3_h %>% mutate(contaminante = "O3 (µg/m³)"),
  pm_h %>% mutate(contaminante = "PM2.5 (µg/m³)")
) %>%
  mutate(hora_del_dia = hour(fecha_hora)) %>%
  group_by(contaminante, estacion, hora_del_dia) %>%
  summarise(media = mean(media), .groups = "drop")

p_perfil <- ggplot(perfil, aes(x = hora_del_dia, y = media, color = estacion)) +
  geom_line() +
  geom_point(size = 1) +
  facet_wrap(~ contaminante, scales = "free_y") +   # escala propia en y
  scale_x_continuous(breaks = seq(0, 21, 3)) +
  theme_minimal() +
  labs(title = "Los dos contaminantes tienen ciclos diarios distintos",
       x = "Hora del día", y = NULL, color = "Estación")
p_perfil
guardar(p_perfil, "perfil_horario.png", ancho = 11, alto = 4.5)

# Nota: cada punto del perfil es la media de ~120 días; si una estación estuvo
# caída varios días, ese promedio se apoya en menos datos que los demás.


# =============================================================================
# 6. Boxplot: la distribución completa, no solo la media
# =============================================================================
# Un boxplot por mes muestra mediana, cuartiles y valores extremos. Con la
# media diaria de cada estación como dato: cada caja resume ~30 días × estaciones.

o3_dia <- ozono %>%
  mutate(dia = as_date(fecha)) %>%
  group_by(estacion, dia) %>%
  summarise(media = mean(o3), .groups = "drop") %>%
  mutate(mes = month(dia, label = TRUE))      # factor ordenado: ene, feb, ...

p_box <- ggplot(o3_dia, aes(x = mes, y = media)) +
  geom_boxplot() +
  theme_minimal() +
  labs(title = "Ozono: distribución de la media diaria, por mes",
       x = "Mes (2024)", y = "O3 (µg/m³)")
p_box
guardar(p_box, "boxplot_mes.png", ancho = 7, alto = 5)


# =============================================================================
# 7. Dispersión: ¿los días con más ozono son los días con más PM2.5?
# =============================================================================
# Solo se puede en la estación en común (la que quedó en aire).
r_global <- cor(aire$o3, aire$pm2_5)
r_global

p_disp <- ggplot(aire, aes(x = pm2_5, y = o3)) +
  geom_point(size = 0.8, alpha = 0.3) +
  theme_minimal() +
  labs(title = sprintf("Ozono vs PM2.5, medias horarias, %s (r = %.2f)",
                       unique(aire$estacion)[1], r_global),
       x = "PM2.5 (µg/m³)", y = "O3 (µg/m³)")
p_disp
guardar(p_disp, "dispersion_o3_pm25.png", ancho = 8, alto = 6)

# Lo que se ve:
#   - una pared vertical en PM2.5 ≈ 3: el piso del sensor, no atmósfera
#   - las dos variables asimétricas a la derecha
#   - un triángulo, no una recta: cuando una es alta, la otra no


# =============================================================================
# 8. Color por hora: ¿es el reloj?
# =============================================================================
# El ozono se forma con sol (tarde); el PM2.5 se acumula con aire quieto
# (noche, madrugada). Si los extremos son de horas distintas, se ve con color.

## 8.1 Color continuo: la hora como número
p_hora <- ggplot(aire, aes(x = pm2_5, y = o3, color = hour(fecha_hora))) +
  geom_point(size = 0.8, alpha = 0.5) +
  scale_x_log10(breaks = c(3, 5, 10, 20, 30, 50)) +    # separa lo chico
  scale_color_viridis_c() +
  theme_minimal() +
  labs(title = "Ozono vs PM2.5, medias horarias, Curva de Maroñas",
       x = "PM2.5 (µg/m³)", y = "O3 (µg/m³)", color = "Hora del día")
p_hora
guardar(p_hora, "dispersion_color_hora.png", ancho = 8, alto = 6)

## 8.2 Color discreto: la hora cortada en cuatro franjas
# Los cortes son una decisión. En enero el sol se pone después de las 20:
# la franja "noche" contiene tardes. Cambiar breaks cambia lo que se ve.
aire <- aire %>%
  mutate(franja = cut(hour(fecha_hora),
                      breaks = c(-1, 5, 11, 17, 23),
                      labels = c("madrugada (0–5)", "mañana (6–11)",
                                 "tarde (12–17)", "noche (18–23)")))

p_franjas <- ggplot(aire, aes(x = pm2_5, y = o3, color = franja)) +
  geom_point(size = 0.8, alpha = 0.5) +
  scale_x_log10(breaks = c(3, 5, 10, 20, 30, 50)) +
  theme_minimal() +
  labs(title = "Ozono vs PM2.5, medias horarias, Curva de Maroñas",
       x = "PM2.5 (µg/m³)", y = "O3 (µg/m³)", color = "Franja horaria")
p_franjas
guardar(p_franjas, "dispersion_franjas.png", ancho = 8, alto = 6)


# =============================================================================
# 9. Paneles: la misma pregunta dentro de cada franja
# =============================================================================
# Comparar horas parecidas entre sí. Si dentro de cada franja la relación
# sigue, no era solo el reloj. El r de cada panel va en su etiqueta.

r_franja <- aire %>%
  group_by(franja) %>%
  summarise(r = cor(o3, pm2_5), n = n(), .groups = "drop") %>%
  mutate(panel = sprintf("%s   r = %.2f   n = %d", franja, r, n))
r_franja

p_paneles <- aire %>%
  left_join(r_franja, by = "franja") %>%
  ggplot(aes(x = pm2_5, y = o3)) +
  geom_point(size = 0.8, alpha = 0.4) +
  facet_wrap(~ panel) +                          # mismas escalas en los cuatro
  scale_x_log10(breaks = c(3, 5, 10, 20, 30, 50)) +
  theme_minimal() +
  labs(title = "Ozono vs PM2.5 dentro de cada franja horaria, Curva de Maroñas",
       x = "PM2.5 (µg/m³)", y = "O3 (µg/m³)")
p_paneles
guardar(p_paneles, "paneles_franjas.png", ancho = 10, alto = 8)

# Lectura: el r global compara todas las horas con todas; el r dentro de una
# franja compara horas parecidas. Si el segundo es más fuerte, la hora
# mezclaba, no explicaba. r mide asociación, no causa: los dos dependen del
# viento, la temperatura y el tráfico del día (unidad 5).


# =============================================================================
# 10. Guardar la tabla unida
# =============================================================================
write_csv(aire, here::here("clases/clase9/aire_horario_o3_pm25.csv"))

# =============================================================================
# En la bitácora
# =============================================================================
# 1. ¿Qué estaciones quedaron fuera de la unión y por qué? (secciones 1 a 3)
# 2. Repetir la sección 3 con left_join en lugar de inner_join: ¿cuántas filas
#    quedan? ¿qué hay en la columna pm2_5 de las que no aparearon?
# 3. Cambiar los cortes de la sección 8.2 a c(-1, 6, 12, 19, 23) y rehacer
#    los paneles: ¿qué cambia?
# 4. Con los datos del equipo: identificar dos tablas que se puedan unir y
#    escribir cuál es la clave de la unión.

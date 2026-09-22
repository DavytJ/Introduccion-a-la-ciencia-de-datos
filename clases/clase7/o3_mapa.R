# =============================================================================
# Mapa de Montevideo con barras de O3 por estación y mes
# Versión R (sf + ggplot2)
# =============================================================================
# Requiere: sf, ggplot2, dplyr, readr, stringr, lubridate
#
# Capa base: límites de barrios de Montevideo (INE) en WGS84, disponible como
# GeoJSON en https://github.com/vierja/geojson_montevideo (archivo barrios.geojson).
# Fuente oficial equivalente (shapefile, UTM 21S): Servicio de Geomática, IM,
# "Barrios de Montevideo según INE", geoweb.montevideo.gub.uy.
# =============================================================================
suppressPackageStartupMessages({
  library(sf)
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(stringr)
  library(lubridate)
})

# --- Configuración -------------------------------------------------------------
ARCHIVO_O3      <- "clases/clase7/o3_01_2024_04_2024.csv"
ARCHIVO_BARRIOS <- "clases/clase7/barrios.geojson"
URL_BARRIOS     <- "https://raw.githubusercontent.com/vierja/geojson_montevideo/master/barrios.geojson"

# Nombres de las columnas de coordenadas en el archivo de ozono.
# Si las coordenadas están en un archivo aparte de estaciones, ver el bloque 2.
COL_LAT <- "latitud"
COL_LON <- "longitud"


# -----------------------------------------------------------------------------
# 1. Capa base: barrios
# -----------------------------------------------------------------------------
if (!file.exists(ARCHIVO_BARRIOS)) {
  download.file(URL_BARRIOS, ARCHIVO_BARRIOS, mode = "wb")
}
barrios <- st_read(ARCHIVO_BARRIOS, quiet = TRUE) %>%
  st_transform(4326)
# Nota: el GeoJSON del repositorio está codificado en latin1, así que la columna
# `nombre` puede leerse con caracteres mal codificados. No se usa en el mapa;
# si hiciera falta: barrios$nombre <- iconv(barrios$nombre, "latin1", "UTF-8").


# -----------------------------------------------------------------------------
# 2. Datos de ozono: media mensual por estación + coordenadas
# -----------------------------------------------------------------------------
ozono <- read_csv(ARCHIVO_O3, locale = locale(encoding = "latin1"), show_col_types = FALSE)

pauta_limpieza <- c("Ã³" = "o", "Ã±" = "ni", "Ã¡" = "á", "Ã©" = "é",
                    "Ã­" = "í", "Ãº" = "ú", "Ã“" = "Ó", "Ã‘" = "NI", "Ã" = "í")

ozono <- ozono %>%
  mutate(estacion = str_replace_all(estacion, pauta_limpieza)) %>%
  filter(!is.na(o3))

# Una fila por estación con sus coordenadas
estaciones <- ozono %>%
  distinct(estacion, lat = .data[[COL_LAT]], lon = .data[[COL_LON]])

# Si las coordenadas vinieran en UTM 21S (valores del orden de 10^5 - 10^6),
# convertir a lat/lon:
if (max(abs(estaciones$lon)) > 1000) {
  estaciones <- estaciones %>%
    st_as_sf(coords = c("lon", "lat"), crs = 32721) %>%
    st_transform(4326) %>%
    mutate(lon = st_coordinates(.)[, 1], lat = st_coordinates(.)[, 2]) %>%
    st_drop_geometry()
}

# Media mensual por estación
o3_mes <- ozono %>%
  mutate(mes = month(fecha)) %>%
  group_by(estacion, mes) %>%
  summarise(o3_medio = mean(o3), .groups = "drop") %>%
  left_join(estaciones, by = "estacion")


# -----------------------------------------------------------------------------
# 3. Geometría de las barras (en grados, sobre el mapa)
# -----------------------------------------------------------------------------
# Cada estación tiene un grupo de barras (una por mes) centrado en su longitud,
# con base en su latitud. La altura se escala: ESCALA grados por µg/m³.
ANCHO_BARRA <- 0.0065           # grados de longitud
ESCALA      <- 0.0009           # grados de latitud por µg/m³ (50 µg/m³ = 0.045°)
meses       <- sort(unique(o3_mes$mes))
n_meses     <- length(meses)
nombres_mes <- c("ene", "feb", "mar", "abr", "may", "jun",
                 "jul", "ago", "sep", "oct", "nov", "dic")   # sin depender del locale

barras <- o3_mes %>%
  mutate(
    pos  = match(mes, meses) - (n_meses + 1) / 2,     # -1.5, -0.5, 0.5, 1.5 para 4 meses
    xmin = lon + pos * ANCHO_BARRA - ANCHO_BARRA / 2,
    xmax = lon + pos * ANCHO_BARRA + ANCHO_BARRA / 2,
    ymin = lat,
    ymax = lat + o3_medio * ESCALA,
    mes_lbl = factor(nombres_mes[mes], levels = nombres_mes[meses])
  )

# Barra de referencia (esquina inferior izquierda del mapa)
bb <- st_bbox(barrios)
ref <- tibble(x = bb["xmin"] + 0.02, y = bb["ymin"] + 0.03, valor = 50)


# -----------------------------------------------------------------------------
# 4. Mapa
# -----------------------------------------------------------------------------
paleta_meses <- c("#fde725", "#5ec962", "#21918c", "#3b528b")   # viridis, 4 valores

mapa <- ggplot() +
  geom_sf(data = barrios, fill = "#e9e5dc", colour = "white", linewidth = 0.35) +
  # sombra de las barras para que se despeguen del fondo
  geom_rect(data = barras,
            aes(xmin = xmin + 0.001, xmax = xmax + 0.001, ymin = ymin - 0.001, ymax = ymax - 0.001),
            fill = "black", alpha = 0.15) +
  geom_rect(data = barras,
            aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax, fill = mes_lbl),
            colour = "white", linewidth = 0.2) +
  geom_point(data = estaciones, aes(lon, lat), shape = 21, fill = "black", colour = "white", size = 2.2) +
  geom_label(data = estaciones, aes(lon, lat - 0.012, label = estacion),
             size = 2.8, label.size = 0, fill = alpha("white", 0.8), fontface = "bold") +
  # barra de referencia
  geom_rect(data = ref, aes(xmin = x, xmax = x + ANCHO_BARRA, ymin = y, ymax = y + valor * ESCALA),
            fill = "grey30") +
  geom_text(data = ref, aes(x + ANCHO_BARRA * 1.6, y + valor * ESCALA / 2, label = "50 µg/m³"),
            hjust = 0, size = 2.8, colour = "grey30") +
  scale_fill_manual(values = paleta_meses, name = "Media mensual de O3") +
  coord_sf(xlim = c(bb["xmin"], bb["xmax"]), ylim = c(bb["ymin"], bb["ymax"]), expand = FALSE) +
  labs(
    title = "Ozono en Montevideo, enero–abril 2024",
    subtitle = "Concentración media mensual (µg/m³) por estación de monitoreo",
    caption = "Fuentes: Intendencia de Montevideo (calidad del aire); límites de barrios INE"
  ) +
  theme_void(base_size = 11) +
  theme(
    panel.background = element_rect(fill = "#cfe3ee", colour = NA),   # Río de la Plata
    plot.background  = element_rect(fill = "white", colour = NA),
    legend.position  = c(0.02, 0.98), legend.justification = c(0, 1),
    legend.background = element_rect(fill = alpha("white", 0.85), colour = NA),
    legend.title = element_text(size = 9, face = "bold"),
    legend.text  = element_text(size = 9),
    plot.title   = element_text(face = "bold", size = 14),
    plot.subtitle = element_text(colour = "grey30"),
    plot.caption = element_text(colour = "grey50", size = 8),
    plot.margin  = margin(10, 10, 10, 10)
  )

ggsave("mapa_o3_montevideo.png", mapa, width = 10, height = 8, dpi = 200, bg = "white")
ggsave("mapa_o3_montevideo.pdf", mapa, width = 10, height = 8, device = cairo_pdf)
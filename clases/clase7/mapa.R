# =============================================================================
# Mapa interactivo de Montevideo con barras de O3 por estación y mes
# Versión R (leaflet + leaflet.minicharts)
# =============================================================================
# Requiere: leaflet, leaflet.minicharts, htmlwidgets, dplyr, tidyr, readr,
#           stringr, lubridate, sf (solo si las coordenadas vienen en UTM)
#
# leaflet trae el mapa base como teselas de OpenStreetMap / CartoDB, así que no
# hace falta ningún shapefile. leaflet.minicharts agrega gráficos de barras (o
# torta, o polar) anclados a coordenadas. El resultado es un HTML autocontenido
# que se abre en cualquier navegador y se puede incrustar en Quarto (html).
# =============================================================================
suppressPackageStartupMessages({
  library(leaflet)
  library(leaflet.minicharts)
  library(htmlwidgets)
  library(dplyr)
  library(tidyr)
  library(readr)
  library(stringr)
  library(lubridate)
})

# --- Configuración -------------------------------------------------------------
ARCHIVO_O3 <- "clases/clase7/o3_01_2024_04_2024.csv"
COL_LAT    <- "latitud"
COL_LON    <- "longitud"


# -----------------------------------------------------------------------------
# 1. Datos: media mensual por estación, en formato ancho (una columna por mes)
# -----------------------------------------------------------------------------
ozono <- read_csv(here::here(ARCHIVO_O3), locale = locale(encoding = "latin1"), show_col_types = FALSE)

pauta_limpieza <- c("Ã³" = "o", "Ã±" = "ni", "Ã¡" = "á", "Ã©" = "é",
                    "Ã­" = "í", "Ãº" = "ú", "Ã“" = "Ó", "Ã‘" = "NI", "Ã" = "í")

ozono <- ozono %>%
  mutate(estacion = str_replace_all(estacion, pauta_limpieza)) %>%
  filter(!is.na(o3))

estaciones <- ozono %>%
  distinct(estacion, lat = .data[[COL_LAT]], lon = .data[[COL_LON]])

# Coordenadas en UTM 21S -> lat/lon (solo si hace falta)
if (max(abs(estaciones$lon)) > 1000) {
  library(sf)
  estaciones <- estaciones %>%
    st_as_sf(coords = c("lon", "lat"), crs = 32721) %>%
    st_transform(4326) %>%
    mutate(lon = st_coordinates(.)[, 1], lat = st_coordinates(.)[, 2]) %>%
    st_drop_geometry()
}

nombres_mes <- c("ene", "feb", "mar", "abr", "may", "jun",
                 "jul", "ago", "sep", "oct", "nov", "dic")

o3_ancho <- ozono %>%
  mutate(mes = nombres_mes[month(fecha)]) %>%
  group_by(estacion, mes) %>%
  summarise(o3_medio = round(mean(o3), 1), .groups = "drop") %>%
  pivot_wider(names_from = mes, values_from = o3_medio) %>%
  left_join(estaciones, by = "estacion")

columnas_mes <- intersect(nombres_mes, names(o3_ancho))   # respeta el orden calendario
o3_ancho

# Texto del popup: una tabla por estación
popups <- o3_ancho %>%
  rowwise() %>%
  mutate(popup = paste0(
    "<b>", estacion, "</b><br>",
    paste0(columnas_mes, ": ", c_across(all_of(columnas_mes)), " µg/m³", collapse = "<br>")
  )) %>%
  ungroup() %>%
  pull(popup)


# -----------------------------------------------------------------------------
# 2. Mapa
# -----------------------------------------------------------------------------
paleta_meses <- c("#fde725", "#5ec962", "#21918c", "#3b528b")[seq_along(columnas_mes)]

mapa <- leaflet(o3_ancho) %>%
  # mapa base: OpenStreetMap no requiere clave. Los de CartoDB (Positron, gris
  # claro, ideal para datos) requieren API key desde 2025; otra opción sin
  # clave es providers$Esri.WorldGrayCanvas.
  addTiles() %>%
  setView(lng = -56.17, lat = -34.86, zoom = 12) %>%
  addMinicharts(
    lng = o3_ancho$lon, lat = o3_ancho$lat,
    type = "bar",
    chartdata = o3_ancho[, columnas_mes],
    colorPalette = paleta_meses,
    width = 60, height = 60,
    showLabels = TRUE,                    # valor sobre cada barra
    labelMinSize = 8,
    popup = popupArgs(html = popups),
    legend = TRUE, legendPosition = "topright",
    layerId = o3_ancho$estacion
  ) %>%
  addLabelOnlyMarkers(
    lng = ~lon, lat = ~lat, label = ~estacion,
    labelOptions = labelOptions(noHide = TRUE, direction = "bottom", offset = c(0, 32),
                                textsize = "12px", style = list("font-weight" = "bold"))
  ) %>%
  addControl(
    html = "<b>Ozono en Montevideo, ene–abr 2024</b><br>Media mensual (µg/m³) por estación",
    position = "topleft"
  )

mapa      # en RStudio se abre en el visor

# HTML autocontenido (incluye el JS de leaflet; las teselas se cargan desde internet)
saveWidget(mapa, "mapa_o3_montevideo_leaflet.html", selfcontained = TRUE)


# -----------------------------------------------------------------------------
# 3. Variante: la misma información con un deslizador temporal
# -----------------------------------------------------------------------------
# addMinicharts acepta un argumento `time`: si los datos están en formato largo
# (una fila por estación y mes), dibuja una barra por estación y agrega un
# control para recorrer los meses. Útil para mostrar la estacionalidad.
o3_largo <- ozono %>%
  mutate(mes = month(fecha)) %>%
  group_by(estacion, mes) %>%
  summarise(o3_medio = round(mean(o3), 1), .groups = "drop") %>%
  left_join(estaciones, by = "estacion") %>%
  arrange(mes, estacion)

mapa_tiempo <- leaflet() %>%
  addTiles() %>%
  setView(lng = -56.17, lat = -34.86, zoom = 12) %>%
  addMinicharts(
    lng = o3_largo$lon, lat = o3_largo$lat,
    chartdata = o3_largo$o3_medio,
    time = nombres_mes[o3_largo$mes],
    type = "bar",
    fillColor = "#21918c",
    width = 30, height = 80,
    showLabels = TRUE,
    layerId = o3_largo$estacion
  )

saveWidget(mapa_tiempo, "mapa_o3_montevideo_leaflet_tiempo.html", selfcontained = TRUE)

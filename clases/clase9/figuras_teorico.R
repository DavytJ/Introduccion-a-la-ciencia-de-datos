# =============================================================================
# Figuras de la primera parte del teórico "Las partes de un gráfico" (ggplot2)
# Valores de ozono leídos del gráfico original (media mensual, ene–abr 2024).
# Genera: partida.png, geometria.png, corregida.png en clases/clase9/imagenes
# =============================================================================
library(tidyverse)
library(patchwork)

dir.create(here::here("clases/clase9/imagenes"), showWarnings = FALSE, recursive = TRUE)
guardar <- function(p, nombre, ancho = 8, alto = 5) {
  ggsave(here::here("clases/clase9/imagenes", nombre), p,
         width = ancho, height = alto, dpi = 300, bg = "white")
}

ozono_mes <- tibble(
  mes          = 1:4,
  o3_medio_mes = c(29.1, 35.5, 24.0, 25.7)
)

# --- El gráfico del que partimos (código de la clase 7, sección 4.2) ---------
p_partida <- ozono_mes %>%
  ggplot(aes(x = mes, y = o3_medio_mes)) +
  geom_line(color = "blue", linewidth = 1) +
  geom_point(color = "red", size = 3) +
  theme_minimal() +
  labs(title = "Concentración de Ozono en el ambiente, por mes, 2024",
       x = "Fecha", y = "Valores")
guardar(p_partida, "partida.png")

# --- La geometría: dos capas separadas ---------------------------------------
p_linea <- ggplot(ozono_mes, aes(x = mes, y = o3_medio_mes)) +
  geom_line(color = "blue", linewidth = 1) +
  theme_minimal() + labs(title = "Solo geom_line()", x = NULL, y = NULL)
p_puntos <- ggplot(ozono_mes, aes(x = mes, y = o3_medio_mes)) +
  geom_point(color = "red", size = 3) +
  theme_minimal() + labs(title = "Solo geom_point()", x = NULL, y = NULL)
guardar(p_linea | p_puntos, "geometria.png", ancho = 10, alto = 4)

# --- Una versión corregida ---------------------------------------------------
p_corregida <- ozono_mes %>%
  ggplot(aes(x = mes, y = o3_medio_mes)) +
  geom_line(color = "blue", linewidth = 1) +
  geom_point(color = "red", size = 3) +
  scale_x_continuous(breaks = 1:4, labels = c("Ene", "Feb", "Mar", "Abr")) +
  scale_y_continuous(limits = c(0, 40), breaks = seq(0, 40, 5)) +
  theme_minimal() +
  theme(panel.grid.minor = element_blank()) +
  labs(title = "Ozono troposférico: media mensual, enero a abril de 2024",
       x = "Mes (2024)", y = "Ozono (µg/m³)",
       caption = "Fuente: valores leídos del gráfico original.")
guardar(p_corregida, "corregida.png")

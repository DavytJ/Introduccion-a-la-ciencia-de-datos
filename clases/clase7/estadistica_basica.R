# =============================================================================
# Figuras didácticas: de la tabla de frecuencias a la media y el percentil 95
# Genera  media_p95_frecuencias.png/.pdf   (paneles A y B)
#         media_p95.png/.pdf               (paneles C, D y E)
# Versión R (ggplot2 + patchwork)
# =============================================================================
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(patchwork)
})

set.seed(2024)

# --- Datos simulados: un día de mediciones minutales (n = 1440) ----------------
# Distribución gamma: asimétrica a la derecha, como una concentración.
k <- 4; theta <- 8                       # forma y escala
n <- 1440
x <- rgamma(n, shape = k, scale = theta)

mu      <- k * theta                                 # media poblacional  E[X]
q95_pob <- qgamma(0.95, shape = k, scale = theta)    # p95 poblacional   F^{-1}(0.95)

media <- mean(x)                                     # media muestral
p95   <- unname(quantile(x, 0.95))                   # p95 muestral (type = 7)

# --- Panel E: los mismos datos con 10 picos espurios ---------------------------
x_con_picos <- c(x, rep(500, 10))
media_c <- mean(x_con_picos)
p95_c   <- unname(quantile(x_con_picos, 0.95))

datos <- tibble(x = x)
azul <- "#1f77b4"; rojo <- "#d62728"; gris <- "#7f7f7f"

tema <- theme_minimal(base_size = 11) +
  theme(legend.position = c(0.98, 0.98), legend.justification = c(1, 1),
        legend.background = element_rect(fill = "white", colour = gris, linewidth = 0.3),
        legend.text = element_text(size = 8), legend.title = element_blank(),
        legend.key.height = unit(0.4, "cm"),
        plot.title = element_text(size = 11))


# =============================================================================
# TABLA DE FRECUENCIAS
# =============================================================================
# Todo lo que sigue se puede leer de esta tabla:
#   m_i : marca de clase (punto medio del intervalo)
#   n_i : frecuencia absoluta            f_i = n_i / n  frecuencia relativa
#   N_i : frecuencia absoluta acumulada  F_i = N_i / n  frecuencia rel. acumulada
ANCHO_CLASE <- 10
cortes <- seq(0, (floor(max(x) / ANCHO_CLASE) + 1) * ANCHO_CLASE, by = ANCHO_CLASE)

# right = FALSE para que los intervalos sean [a, b) como dicen las etiquetas.
# Por defecto hist() usa (a, b], la convención opuesta: es un error fácil de
# cometer y de no notar, porque solo cambia el conteo en los valores de corte.
h      <- hist(x, breaks = cortes, right = FALSE, plot = FALSE)
tabla  <- tibble(
  clase = sprintf("[%g, %g)", cortes[-length(cortes)], cortes[-1]),
  m_i   = h$mids,
  n_i   = h$counts,
  f_i   = n_i / n,
  N_i   = cumsum(n_i),
  F_i   = cumsum(n_i) / n
)
print(as.data.frame(tabla), digits = 3)

# La media también se puede calcular DESDE la tabla, como promedio ponderado de
# las marcas de clase. Es una aproximación: se pierde la posición exacta de cada
# dato dentro de su intervalo.
media_agrupada <- sum(tabla$m_i * tabla$n_i) / sum(tabla$n_i)

# La primera clase con F_i >= 0.95 es la que contiene al p95.
i_p95 <- which(tabla$F_i >= 0.95)[1]

cat(sprintf("\nmedia exacta = %.4f   media agrupada = %.4f   (diferencia %+.4f)\n",
            media, media_agrupada, media_agrupada - media))
cat(sprintf("clase que contiene el p95: %s   p95 = %.2f\n", tabla$clase[i_p95], p95))


# =============================================================================
# FIGURA 1 — Paneles A y B: la tabla y su histograma
# =============================================================================

# --- A. Tabla de frecuencias --------------------------------------------------
# La tabla se dibuja con geom_text sobre un lienzo 0-1: sin dependencias extra
# (nada de gridExtra ni gt) y con control total del resaltado.
COLS_X  <- c(0.02, 0.33, 0.48, 0.63, 0.78, 0.94)
COLS_HJ <- c(0, 0.5, 0.5, 0.5, 0.5, 1)          # 0 izq, 0.5 centro, 1 der
Y0 <- 0.98; DY <- 0.050

textos <- list(tabla$clase,
               sprintf("%g",   tabla$m_i),
               sprintf("%d",   tabla$n_i),
               sprintf("%.3f", tabla$f_i),
               sprintf("%d",   tabla$N_i),
               sprintf("%.3f", tabla$F_i))

celdas <- bind_rows(lapply(seq_along(textos), function(j) {
  tibble(x = COLS_X[j], hj = COLS_HJ[j],
         y = Y0 - DY * seq_len(nrow(tabla)),
         texto = textos[[j]],
         cara = ifelse(seq_len(nrow(tabla)) == i_p95, "bold", "plain"))
}))

encabezados <- tibble(x = COLS_X, hj = COLS_HJ, y = Y0,
                      etiqueta = c("'clase'", "m[i]", "n[i]", "f[i]", "N[i]", "F[i]"))

y_tot <- Y0 - DY * (nrow(tabla) + 1)
totales <- tibble(x = COLS_X[c(1, 3, 4)], hj = COLS_HJ[c(1, 3, 4)], y = y_tot,
                  texto = c("total", format(n), "1.000"))

y_pie <- y_tot - DY * 1.6
pA <- ggplot() +
  # fila resaltada: la que contiene al p95
  annotate("rect", xmin = 0, xmax = 1,
           ymin = Y0 - DY * i_p95 - DY * 0.42, ymax = Y0 - DY * i_p95 + DY * 0.42,
           fill = rojo, alpha = 0.15) +
  geom_text(data = encabezados, aes(x, y, label = etiqueta, hjust = hj),
            parse = TRUE, size = 3.5, fontface = "bold") +
  annotate("segment", x = 0, xend = 1, y = Y0 - DY * 0.5, yend = Y0 - DY * 0.5) +
  geom_text(data = celdas, aes(x, y, label = texto, hjust = hj, fontface = cara),
            size = 3.3) +
  annotate("segment", x = 0, xend = 1, y = y_tot + DY * 0.5, yend = y_tot + DY * 0.5) +
  geom_text(data = totales, aes(x, y, label = texto, hjust = hj),
            size = 3.3, fontface = "bold") +
  # pie: definiciones y las dos lecturas de la tabla
  annotate("text", x = 0, y = y_pie, hjust = 0, size = 3.3, parse = TRUE,
           label = "f[i] == n[i]/n ~~~~ N[i] == sum(n[j], j <= i, ) ~~~~ F[i] == N[i]/n") +
  annotate("text", x = 0, y = y_pie - DY * 1.6, hjust = 0, size = 3.3,
           label = "La media es el promedio ponderado de las marcas de clase:") +
  annotate("text", x = 0.04, y = y_pie - DY * 2.9, hjust = 0, size = 3.3, parse = TRUE,
           label = sprintf("bar(x) %%~~%% frac(1, n) * sum(m[i] * n[i], i, ) ~~ '=' ~~ '%.2f' ~~~ '(exacta: %.2f)'",
                           media_agrupada, media)) +
  annotate("text", x = 0, y = y_pie - DY * 4.3, hjust = 0, size = 3.3, parse = TRUE,
           label = sprintf("'El ' * p[95] * ' está en la primera clase con ' * F[i] >= 0.95 * ' :  %s'",
                           tabla$clase[i_p95])) +
  coord_cartesian(xlim = c(0, 1), ylim = c(0, 1)) +
  labs(title = "A. Tabla de frecuencias (clases de 10 µg/m³)") +
  theme_void(base_size = 11) +
  theme(plot.title = element_text(size = 11, hjust = 0))

# --- B. Histograma de frecuencias ---------------------------------------------
etiqueta_banda <- sprintf("clase del p95: %s", tabla$clase[i_p95])
banda <- tibble(xmin = cortes[i_p95], xmax = cortes[i_p95 + 1], etq = etiqueta_banda)

pB <- ggplot(tabla, aes(m_i, n_i)) +
  geom_rect(data = banda, inherit.aes = FALSE,
            aes(xmin = xmin, xmax = xmax, ymin = 0, ymax = Inf, fill = etq), alpha = 0.15) +
  geom_col(width = ANCHO_CLASE * 0.92, fill = gris, alpha = 0.55,
           colour = "white", linewidth = 0.4) +
  # polígono de frecuencias: une las marcas de clase
  geom_line(aes(linetype = "polígono de frecuencias"), linewidth = 0.5) +
  geom_point(size = 1.2) +
  geom_label(aes(y = n_i, label = n_i), nudge_y = 22, size = 3,
             label.size = NA, label.padding = unit(0.08, "lines"), fill = "white") +
  scale_fill_manual(values = setNames(rojo, etiqueta_banda), name = NULL) +
  scale_linetype_manual(values = c("polígono de frecuencias" = "solid"), name = NULL) +
  scale_x_continuous(breaks = cortes[seq(1, length(cortes), 2)]) +
  scale_y_continuous(
    name = expression(n[i] ~ ~"(frecuencia absoluta)"),
    sec.axis = sec_axis(~ . / n, name = expression(f[i] ~ ~"(frecuencia relativa)"))
  ) +
  labs(title = "B. El mismo contenido, en un histograma", x = "O3 (µg/m³)") +
  theme_minimal(base_size = 11) +
  theme(plot.title = element_text(size = 11),
        legend.position = c(0.98, 0.98), legend.justification = c(1, 1),
        legend.background = element_rect(fill = "white", colour = gris, linewidth = 0.3),
        legend.text = element_text(size = 8), legend.spacing.y = unit(0, "cm"),
        legend.key.height = unit(0.4, "cm"))

figura1 <- (pA | pB) +
  plot_layout(widths = c(1, 1.15)) +
  plot_annotation(
    title = "De los datos a la tabla de frecuencias: n = 1440 mediciones simuladas",
    theme = theme(plot.title = element_text(hjust = 0.5, size = 13)))

ggsave("media_p95_frecuencias.png", figura1, width = 14, height = 7, dpi = 200, bg = "white")
ggsave("media_p95_frecuencias.pdf", figura1, width = 14, height = 7, device = cairo_pdf)


# =============================================================================
# FIGURA 2 — Paneles C, D y E: media, p95 y robustez
# =============================================================================

# --- C. Distribución, media y p95 ---------------------------------------------
grid <- tibble(x = seq(0, 165, length.out = 400),
               f = dgamma(x, shape = k, scale = theta))
lineasC <- tibble(valor = c(media, p95), que = c("media", "p95"))

pC <- ggplot(datos, aes(x)) +
  geom_histogram(aes(y = after_stat(density)), breaks = cortes,
                 fill = gris, alpha = 0.45) +
  geom_area(data = filter(grid, x >= p95), aes(x, f), fill = rojo, alpha = 0.25) +
  geom_line(data = grid, aes(x, f), colour = "black") +
  geom_vline(data = lineasC, aes(xintercept = valor, colour = que), linewidth = 1) +
  scale_colour_manual(values = c(media = azul, p95 = rojo),
                      labels = c(media = sprintf("media = %.1f", media),
                                 p95 = sprintf("p95 = %.1f", p95))) +
  annotate("text", x = 47, y = 0.0245, label = "densidad poblacional f(x)",
           hjust = 0, size = 3, colour = "black") +
  annotate("text", x = 80, y = 0.0035, label = "5 % superior", hjust = 0, size = 3, colour = rojo) +
  annotate("text", x = 82, y = 0.0300, label = sprintf("datos simulados (n = %d)", n),
           hjust = 0, size = 3, colour = gris) +
  annotate("text", x = 163, y = c(0.0165, 0.0125, 0.0105, 0.0080), hjust = 1, size = 3,
           parse = TRUE,
           label = c("bar(x) == frac(1, n) * sum(x[i], i == 1, n)",
                     "sum(x[i] - bar(x), i == 1, n) == 0",
                     "'(punto de equilibrio)'",
                     sprintf("'poblacional: ' * mu == E*'[X]' ~ '=' ~ %.0f", mu))) +
  annotate("rect", xmin = 108, xmax = 165, ymin = 0.0065, ymax = 0.0185,
           fill = NA, colour = gris, linewidth = 0.3) +
  coord_cartesian(xlim = c(0, 165)) +
  labs(title = "C. ¿Dónde están la media y el p95?", x = "O3 (µg/m³)", y = "densidad") +
  tema + theme(legend.position = c(0.98, 0.80))

# --- D. Definición del p95 vía la función de distribución empírica -------------
pD <- ggplot(datos, aes(x)) +
  stat_function(fun = pgamma, args = list(shape = k, scale = theta),
                aes(linetype = "pob"), colour = gris, n = 400) +
  stat_ecdf(aes(linetype = "emp"), colour = "black", geom = "step") +
  geom_hline(yintercept = 0.95, colour = rojo, linetype = "dashed", linewidth = 0.4) +
  geom_vline(xintercept = media, colour = azul, linewidth = 1, alpha = 0.6) +
  geom_vline(xintercept = p95, colour = rojo, linewidth = 1) +
  # los puntos (extremo de clase, F_i) de la tabla del panel A caen sobre F_n
  geom_point(data = tabla, aes(cortes[-1], F_i), shape = 21, colour = rojo, size = 1.8) +
  annotate("point", x = p95, y = 0.95, colour = rojo, size = 2) +
  annotate("text", x = 118, y = 0.975, label = "0.95", colour = rojo, size = 3, hjust = 1) +
  scale_linetype_manual(values = c(emp = "solid", pob = "dotted"),
                        labels = c(emp = expression(F[n](x) ~ "empírica"),
                                   pob = expression(F(x) ~ "poblacional"))) +
  annotate("text", x = 122, y = c(0.44, 0.33, 0.25, 0.195, 0.11), hjust = 1, size = 3,
           parse = TRUE,
           label = c("F[n](x) == frac(1, n) * sum(bold('1') * group('{', x[i] <= x, '}'), i == 1, n)",
                     "p[95] == min * group('{', x * ':' ~ F[n](x) >= 0.95, '}')",
                     "'con datos ordenados ' * x[(1)] <= group('', cdots <= x[(n)], '') * ':'",
                     sprintf("p[95] == x[(group(lceil, 0.95 * n, rceil))] ~ '=' ~ x[(%d)]", ceiling(0.95 * n)),
                     sprintf("'poblacional: ' * F^{-1} * (0.95) == %.1f", q95_pob))) +
  annotate("rect", xmin = 48, xmax = 126, ymin = 0.08, ymax = 0.48,
           fill = NA, colour = gris, linewidth = 0.3) +
  scale_y_continuous(limits = c(0, 1.02)) +
  labs(title = "D. El p95 como inversa de la distribución",
       x = "O3 (µg/m³)", y = "proporción de observaciones ≤ x") +
  tema + theme(legend.position = c(0.02, 0.98), legend.justification = c(0, 1))

# --- E. Robustez: 10 picos espurios -------------------------------------------
cortes_E <- seq(0, 510, length.out = 81)
conteo <- function(v) {
  hh <- hist(v, breaks = cortes_E, plot = FALSE)
  tibble(centro = hh$mids, n = hh$counts) %>% filter(n > 0)
}
hist_orig  <- conteo(x)
hist_picos <- conteo(x_con_picos)
ancho <- diff(cortes_E)[1]

lineasE <- tibble(
  valor = c(media, media_c, p95, p95_c),
  que   = factor(c("media antes", "media después", "p95 antes", "p95 después"),
                 levels = c("media antes", "media después", "p95 antes", "p95 después"))
)

pE <- ggplot() +
  geom_col(data = hist_orig, aes(centro, n, fill = "orig"), width = ancho, alpha = 0.45) +
  geom_col(data = hist_picos, aes(centro, n, colour = "picos"), width = ancho,
           fill = NA, linewidth = 0.3) +
  geom_vline(data = lineasE, aes(xintercept = valor, colour = que, linetype = que), linewidth = 1) +
  scale_fill_manual(values = c(orig = gris), labels = c(orig = "datos originales")) +
  scale_colour_manual(
    values = c(picos = "black", "media antes" = azul, "media después" = azul,
               "p95 antes" = rojo, "p95 después" = rojo),
    labels = c(picos = "+ 10 picos de 500 µg/m³",
               "media antes"   = sprintf("media antes = %.1f", media),
               "media después" = sprintf("media después = %.1f", media_c),
               "p95 antes"     = sprintf("p95 antes = %.1f", p95),
               "p95 después"   = sprintf("p95 después = %.1f", p95_c))) +
  scale_linetype_manual(
    values = c(picos = "solid", "media antes" = "dashed", "media después" = "solid",
               "p95 antes" = "dashed", "p95 después" = "solid"),
    guide = "none") +
  annotate("label", x = 300, y = 3.5, size = 3, colour = "black",
           label = paste0(
             sprintf("la media se mueve %+.1f\nel p95 se mueve %+.1f\n\n", media_c - media, p95_c - p95),
             "en la media cada dato pesa por su valor:\n",
             "10 picos de 5000 la moverían 10 veces más\n\n",
             "en el p95 cada dato pesa por su rango:\n",
             sprintf("10 de %d es %.1f %% < 5 %%, el valor de los\npicos no importa",
                     length(x_con_picos), 100 * 10 / length(x_con_picos)))) +
  scale_y_log10() +
  guides(colour = guide_legend(override.aes = list(
    linetype = c("solid", "dashed", "solid", "dashed", "solid"), fill = NA))) +
  labs(title = "E. 10 picos espurios entre 1450 datos",
       x = "O3 (µg/m³)", y = "frecuencia (escala log)") +
  tema + theme(legend.spacing.y = unit(0.05, "cm"))

figura2 <- (pC | pD | pE) +
  plot_annotation(
    title = "Media y percentil 95: dos formas de resumir la misma distribución",
    theme = theme(plot.title = element_text(hjust = 0.5, size = 13)))

ggsave("media_p95.png", figura2, width = 15, height = 5, dpi = 200, bg = "white")
ggsave("media_p95.pdf", figura2, width = 15, height = 5, device = cairo_pdf)

cat(sprintf("\nmedia=%.2f  p95=%.2f  |  con picos: media=%.2f  p95=%.2f\n",
            media, p95, media_c, p95_c))
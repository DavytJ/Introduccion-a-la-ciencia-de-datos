"""
EJEMPLO — Un conjunto de datos famoso: los pingüinos de Palmer
Diez filas reales del dataset "penguins" (Horst, Hill y Gorman, 2020),
escritas a mano para no depender de la red.
"""
import pandas as pd

pinguinos = pd.DataFrame({
    "especie":          ["Adelia", "Adelia", "Adelia", "Adelia", "Barbijo",
                         "Barbijo", "Barbijo", "Juanito", "Juanito", "Juanito"],
    "isla":             ["Torgersen", "Torgersen", "Biscoe", "Dream", "Dream",
                         "Dream", "Dream", "Biscoe", "Biscoe", "Biscoe"],
    "largo_pico_mm":    [39.1, 39.5, 37.8, 39.5, 46.5, 50.0, 51.3, 46.1, 50.0, 48.7],
    "alto_pico_mm":     [18.7, 17.4, 18.3, 16.7, 17.9, 19.5, 19.2, 13.2, 16.3, 14.1],
    "largo_aleta_mm":   [181, 186, 174, 178, 192, 196, 193, 211, 230, 210],
    "masa_corporal_g":  [3750, 3800, 3400, 3250, 3500, 3900, 3650, 4500, 5700, 4450],
})

print(pinguinos.to_string(index=False))

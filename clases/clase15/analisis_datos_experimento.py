# -*- coding: utf-8 -*-
"""
Análisis datos experimento — versión Python (script).
Equivalente al Rmd analisis_datos_experimento.Rmd.
Ejecutar con:  python analisis_datos_experimento.py
Requiere:      pip install pandas numpy scipy statsmodels
"""


# ======================================================================
# Paquetes
# ======================================================================

# Instalar una sola vez (desde la terminal o descomentando la línea):
# pip install pandas numpy scipy statsmodels

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gammaln
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from itertools import combinations


# ======================================================================
# Funciones auxiliares
# ======================================================================
#
# En R muchas de estas cosas vienen en effectsize y gtsummary. En Python las definimos acá
# para que quede explícito qué se calcula. No hace falta modificarlas.

# ---------- Formato de p-valores (estilo gtsummary) ----------
def formato_p(p):
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "<0.001"
    if p > 0.9:
        return ">0.9"
    if p >= 0.1:
        return f"{p:.1f}"
    if p >= 0.01:
        return f"{p:.2f}"
    return f"{p:.3f}"


# ---------- Fisher exacto r×c por Monte Carlo (como fisher.test(..., simulate.p.value = TRUE)) ----------
def fisher_rxc_mc(tab, B=10_000, seed=123):
    """p-valor de Fisher para tablas r×c simulando tablas con los mismos márgenes."""
    tab = np.asarray(tab)
    filas = np.repeat(np.arange(tab.shape[0]), tab.sum(axis=1))
    cols = np.concatenate([np.repeat(np.arange(tab.shape[1]), tab[i, :]) for i in range(tab.shape[0])])
    # log-probabilidad hipergeométrica de una tabla (los márgenes son constantes)
    logp = lambda t: -gammaln(t + 1).sum()
    obs = logp(tab)
    rng = np.random.default_rng(seed)
    cuenta = 0
    for _ in range(B):
        t = np.zeros_like(tab)
        np.add.at(t, (filas, rng.permutation(cols)), 1)
        if logp(t) <= obs + 1e-7:
            cuenta += 1
    return (cuenta + 1) / (B + 1)


def test_categorico(x, y):
    """Chi-cuadrado, o Fisher si alguna frecuencia esperada es < 5 (criterio de gtsummary)."""
    tab = pd.crosstab(x, y)
    _, p, _, esperados = stats.chi2_contingency(tab)
    if (esperados < 5).any():
        if tab.shape == (2, 2):
            return stats.fisher_exact(tab).pvalue, "Fisher exacto"
        return fisher_rxc_mc(tab), "Fisher (Monte Carlo)"
    return p, "Chi-cuadrado de Pearson"


# ---------- Tamaños de efecto (equivalentes a effectsize) ----------
def phi(tab):
    tab = np.asarray(tab)
    chi2 = stats.chi2_contingency(tab, correction=False)[0]
    return np.sqrt(chi2 / tab.sum())


def cramers_v(tab, ajustado=True):
    """V de Cramér; ajustado=True aplica la corrección de sesgo (default de effectsize)."""
    tab = np.asarray(tab)
    n = tab.sum()
    r, k = tab.shape
    chi2 = stats.chi2_contingency(tab, correction=False)[0]
    phi2 = chi2 / n
    if not ajustado:
        return np.sqrt(phi2 / min(r - 1, k - 1))
    phi2c = max(0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rc, kc = r - (r - 1) ** 2 / (n - 1), k - (k - 1) ** 2 / (n - 1)
    return np.sqrt(phi2c / min(rc - 1, kc - 1))


def cohens_d(x, y):
    nx, ny = len(x), len(y)
    sp = np.sqrt(((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1)) / (nx + ny - 2))
    return (np.mean(x) - np.mean(y)) / sp


def hedges_g(x, y):
    n = len(x) + len(y)
    return cohens_d(x, y) * (1 - 3 / (4 * n - 9))


def rank_biserial(x, y):
    U = stats.mannwhitneyu(x, y).statistic
    return 2 * U / (len(x) * len(y)) - 1


def eta_omega_squared(modelo):
    """η² y ω² a partir de un modelo ols con un solo factor."""
    tabla = sm.stats.anova_lm(modelo, typ=2)
    ss_ef, ss_res = tabla["sum_sq"].iloc[0], tabla["sum_sq"].iloc[-1]
    df_ef = tabla["df"].iloc[0]
    ms_res = ss_res / tabla["df"].iloc[-1]
    ss_tot = ss_ef + ss_res
    eta2 = ss_ef / ss_tot
    omega2 = (ss_ef - df_ef * ms_res) / (ss_tot + ms_res)
    return eta2, omega2


def rank_epsilon_squared(*grupos):
    n = sum(len(g) for g in grupos)
    H = stats.kruskal(*grupos).statistic
    return H / ((n**2 - 1) / (n + 1))


# ---------- ANOVA de Welch (oneway.test) ----------
def welch_anova(*grupos):
    k = len(grupos)
    n = np.array([len(g) for g in grupos])
    m = np.array([np.mean(g) for g in grupos])
    v = np.array([np.var(g, ddof=1) for g in grupos])
    w = n / v
    mw = np.sum(w * m) / np.sum(w)
    A = np.sum(w * (m - mw) ** 2) / (k - 1)
    tmp = np.sum((1 - w / np.sum(w)) ** 2 / (n - 1)) / (k**2 - 1)
    F = A / (1 + 2 * (k - 2) * tmp)
    df1, df2 = k - 1, 1 / (3 * tmp)
    return F, df1, df2, stats.f.sf(F, df1, df2)


# ---------- Post-hoc (pairwise.t.test y pairwise.wilcox.test) ----------
def pairwise_t_test(y, g, p_adjust="holm"):
    """Como pairwise.t.test de R: t con DE combinada de TODOS los grupos."""
    niveles = list(pd.Categorical(g).categories)
    datos = {lv: y[g == lv] for lv in niveles}
    gl = sum(len(d) - 1 for d in datos.values())
    s2 = sum((len(d) - 1) * np.var(d, ddof=1) for d in datos.values()) / gl
    pares, ps = [], []
    for a, b in combinations(niveles, 2):
        se = np.sqrt(s2 * (1 / len(datos[a]) + 1 / len(datos[b])))
        t = (np.mean(datos[a]) - np.mean(datos[b])) / se
        pares.append((a, b)); ps.append(2 * stats.t.sf(abs(t), gl))
    return _tabla_pares(pares, ps, p_adjust)


def pairwise_wilcox_test(y, g, p_adjust="holm"):
    niveles = list(pd.Categorical(g).categories)
    pares, ps = [], []
    for a, b in combinations(niveles, 2):
        pares.append((a, b)); ps.append(stats.mannwhitneyu(y[g == a], y[g == b]).pvalue)
    return _tabla_pares(pares, ps, p_adjust)


def _tabla_pares(pares, ps, metodo):
    p_aj = multipletests(ps, method=metodo)[1]
    return pd.DataFrame({"grupo_1": [a for a, _ in pares], "grupo_2": [b for _, b in pares],
                         "p": [f"{v:.4g}" for v in ps],
                         f"p_{metodo}": [f"{v:.4g}" for v in p_aj]})

# ---------- Tabla descriptiva con tests (equivalente a tbl_summary + add_p) ----------
def tabla_descriptiva(df, by, labels=None, continuas=None, dicotomicas=None, decimales=None):
    """
    df          : DataFrame
    by          : columna de agrupación
    labels      : dict {columna: etiqueta}
    continuas   : dict {columna: "media" | "mediana"}
                  "media"   -> media (DE);         test t de Welch (2 grupos) o ANOVA de Welch (>2)
                  "mediana" -> mediana (Q1, Q3);   Wilcoxon / Mann-Whitney (2) o Kruskal-Wallis (>2)
    dicotomicas : dict {columna: nivel a mostrar}, ej. {"fumador": "Sí"}
    decimales   : dict {columna: nº de decimales}
    """
    labels = labels or {}
    continuas = continuas or {}
    dicotomicas = dicotomicas or {}
    decimales = decimales or {}

    grupos = list(pd.Categorical(df[by]).categories)
    cols = [f"Overall (N = {len(df)})"] + [f"{g} (N = {(df[by] == g).sum()})" for g in grupos]
    subsets = [df] + [df[df[by] == g] for g in grupos]
    filas, tests_usados = [], []

    def agregar_test(nombre):
        if nombre not in tests_usados:
            tests_usados.append(nombre)

    for var in [c for c in df.columns if c != by]:
        etiqueta = labels.get(var, var)
        n_var = df[var].notna().sum()

        if var in continuas:
            d = decimales.get(var, 0)
            if continuas[var] == "media":
                celdas = [f"{s[var].mean():,.{d}f} ({s[var].std():,.{d}f})" for s in subsets]
            else:
                celdas = [f"{s[var].median():,.{d}f} ({s[var].quantile(.25):,.{d}f}, {s[var].quantile(.75):,.{d}f})"
                          for s in subsets]
            muestras = [df.loc[df[by] == g, var].dropna() for g in grupos]
            if continuas[var] == "media":
                if len(grupos) == 2:
                    p, t = stats.ttest_ind(*muestras, equal_var=False).pvalue, "t de Welch"
                else:
                    p, t = welch_anova(*muestras)[3], "ANOVA de Welch"
            else:
                if len(grupos) == 2:
                    p, t = stats.mannwhitneyu(*muestras).pvalue, "Wilcoxon (Mann-Whitney)"
                else:
                    p, t = stats.kruskal(*muestras).pvalue, "Kruskal-Wallis"
            agregar_test(t)
            filas.append([etiqueta, n_var, *celdas, formato_p(p)])

        else:  # categórica o dicotómica
            p, t = test_categorico(df[var], df[by])
            agregar_test(t)
            pct = lambda s, nivel: f"{(s[var] == nivel).sum()} ({100 * (s[var] == nivel).mean():.0f}%)"
            if var in dicotomicas:
                nivel = dicotomicas[var]
                filas.append([etiqueta, n_var, *[pct(s, nivel) for s in subsets], formato_p(p)])
            else:
                filas.append([etiqueta, n_var, *[""] * len(subsets), formato_p(p)])
                for nivel in pd.Categorical(df[var]).categories:
                    filas.append([f"    {nivel}", "", *[pct(s, nivel) for s in subsets], ""])

    tabla = pd.DataFrame(filas, columns=["Característica", "N", *cols, "p-valor"])
    nota = ("Celdas: n (%); media (DE); mediana (Q1, Q3).\n"
            "Tests usados: " + "; ".join(tests_usados) + ".")
    return tabla, nota


def resaltar_p(tabla, alfa=0.05):
    """Pone en negrita los p-valores < alfa (como bold_p)."""
    def estilo(v):
        try:
            num = 0.0 if str(v).startswith("<") else float(v)
            return "font-weight: bold" if num < alfa else ""
        except ValueError:
            return ""
    return (tabla.style.hide(axis="index")
            .map(estilo, subset=["p-valor"])
            .set_properties(subset=["Característica"], **{"text-align": "left", "white-space": "pre"}))


# ======================================================================
# Dato ejemplo (aquí levantar sus datos)
# ======================================================================

# Para usar datos propios, por ejemplo:
# df = pd.read_csv("mis_datos.csv")
# df = pd.read_excel("mis_datos.xlsx")
# y convertir las variables categóricas con pd.Categorical(...)

rng = np.random.default_rng(123)
n = 20

fumador = rng.choice(["No", "Sí"], n, p=[0.6, 0.4])
nivel_educ = rng.choice(["Primaria", "Secundaria", "Terciaria"], n)

df = pd.DataFrame({
    # binarias
    "sexo":       pd.Categorical(rng.choice(["Femenino", "Masculino"], n)),
    "fumador":    pd.Categorical(fumador, categories=["No", "Sí"]),
    # categóricas
    "nivel_educ": pd.Categorical(nivel_educ, categories=["Primaria", "Secundaria", "Terciaria"]),
    "region":     pd.Categorical(rng.choice(["Norte", "Centro", "Sur"], n),
                                 categories=["Norte", "Centro", "Sur"]),
})

# numéricas (con algo de asociación inducida para que los tests "muestren" algo)
df["edad"] = np.round(rng.normal(40, 10, n) + np.where(df["fumador"] == "Sí", 8, 0))
df["ingreso"] = np.round(rng.lognormal(np.log(30000), 0.4, n) *
                         (df["nivel_educ"].cat.codes + 1))   # asimétrica, crece con educación

print(df)


# ======================================================================
# TABLA DESCRIPTIVA
# ======================================================================

# --- Tabla descriptiva con tests, comparando por sexo ---
tabla, nota = tabla_descriptiva(
    df,
    by="sexo",
    dicotomicas={"fumador": "Sí"},
    continuas={"edad": "media",       # aprox. normal -> media (DE)
               "ingreso": "mediana"}, # asimétrica    -> mediana (Q1, Q3)
    labels={"edad": "Edad (años)", "ingreso": "Ingreso mensual", "fumador": "Fumador",
            "nivel_educ": "Nivel educativo", "region": "Región"},
)

print(tabla.to_string(index=False))
print(nota)


# Cómo leer la tabla. Cada fila es una variable y las columnas muestran su resumen en toda la muestra
# y por separado en cada grupo (acá, por sexo). La última columna dice si hay evidencia de que la variable
# difiere entre los grupos.
#
# Columnas
#
# - Característica: el nombre de la variable. Las categóricas tienen sus niveles indentados debajo.
# - N: cuántas observaciones no faltantes tiene esa variable.
# - Overall: el resumen en la muestra completa.
# - Una columna por grupo (Femenino / Masculino): el mismo resumen dentro de cada grupo.
# - p-valor: el resultado del test que compara los grupos para esa variable (en negrita si es < 0,05).
#
# Cómo leer cada celda
#
# - Fumador: n (%) de personas que fuman. Al ser dicotómica, solo se muestra el nivel "Sí".
# - Nivel educativo y Región: n (%) por nivel. Los porcentajes son dentro de la columna.
# - Edad: media (DE).
# - Ingreso mensual: mediana (Q1, Q3), porque es asimétrica.
#
# Qué test se usó (ver la nota debajo de la tabla)
#
# - Categóricas: chi-cuadrado, o Fisher si alguna frecuencia esperada es menor que 5
#   (con n = 20 casi siempre pasa). En tablas mayores que 2×2, Fisher se calcula por Monte Carlo.
# - Edad: t de Welch, que compara medias sin asumir varianzas iguales.
# - Ingreso: Wilcoxon (Mann-Whitney), que compara distribuciones por rangos sin asumir normalidad.
#
# Ojo: en el df de mentira el sexo se generó al azar, así que lo esperable es que no haya diferencias.
# Las asociaciones inducidas son fumador–edad y educación–ingreso. Para verlas, cambiá by="sexo" por
# by="fumador" o by="nivel_educ".
#
# *Nota: el generador aleatorio de Python no es el de R, así que los números no coinciden con los de la versión en R.*


# ======================================================================
# AUMENTACIÓN DE DATOS
# ======================================================================
#
# Bootstrap + ruido gaussiano: se remuestrean filas completas (preserva la estructura conjunta) y se
# agrega ruido N(0, (noise · DE)²) a cada variable numérica.
#
# Advertencia: la aumentación no agrega información. Las filas nuevas son copias perturbadas de las
# originales, así que los p-valores calculados sobre df_boot salen artificialmente chicos. Sirve para
# probar código, no para inferencia.

def augment_boot(data, n_new, noise=0.1, seed=123):
    rng = np.random.default_rng(seed)
    out = data.sample(n=n_new, replace=True, random_state=seed).reset_index(drop=True)
    for v in out.select_dtypes("number").columns:
        out[v] = out[v] + rng.normal(0, noise * data[v].std(), n_new)
    return out

df_boot = augment_boot(df, n_new=200, noise=0.1)
df_boot["edad"] = df_boot["edad"].round()
df_boot["ingreso"] = df_boot["ingreso"].round().clip(lower=0)

print(df_boot.head())


# ======================================================================
# ASOCIACIÓN
# ======================================================================

# Elegí el conjunto de datos:
datos = df_boot   # aumentado (n = 200) -> p-valores inflados, solo para probar
# datos = df      # original  (n = 20)  -> el que vale para inferencia


# ======================================================================
# Categórica × categórica (vale para binaria)
# ======================================================================

# 2x2: sexo × fumador
tab = pd.crosstab(datos["sexo"], datos["fumador"])
print(tab)

chi2, p, gl, esperados = stats.chi2_contingency(tab)          # con corrección de Yates en 2x2, como R
print(f"Chi-cuadrado = {chi2:.3f}, gl = {gl}, p = {p:.4g}")
print("Esperados (chequear >= 5):")
print(pd.DataFrame(esperados, index=tab.index, columns=tab.columns).round(2))

# Fisher exacto + OR condicional con IC (lo mismo que reporta fisher.test en R)
print(f"Fisher exacto: p = {stats.fisher_exact(tab).pvalue:.4g}")
or_cond = stats.contingency.odds_ratio(tab)
print(f"OR (condicional) = {or_cond.statistic:.3f}, IC95% = {np.round(or_cond.confidence_interval(), 3)}")

# Tamaños de efecto
print(f"Phi = {phi(tab):.3f}")
t22 = sm.stats.Table2x2(tab.values)
print(f"OR (muestral) = {t22.oddsratio:.3f}, IC95% = {np.round(t22.oddsratio_confint(), 3)}")

# r × c: nivel educativo × región
tab2 = pd.crosstab(datos["nivel_educ"], datos["region"])
print(tab2)

chi2, p, gl, _ = stats.chi2_contingency(tab2)
print(f"Chi-cuadrado = {chi2:.3f}, gl = {gl}, p = {p:.4g}")
print("Fisher r×c (Monte Carlo, B = 10000): p =", round(fisher_rxc_mc(tab2), 4))
print(f"V de Cramér (ajustada) = {cramers_v(tab2):.3f}")


# ======================================================================
# Binaria × continua: edad según fumador
# ======================================================================

x = datos.loc[datos["fumador"] == "No", "edad"]
y = datos.loc[datos["fumador"] == "Sí", "edad"]

# t de Welch
res = stats.ttest_ind(x, y, equal_var=False)
ic = res.confidence_interval()
print(f"Welch t = {res.statistic:.3f}, gl = {res.df:.1f}, p = {res.pvalue:.4g}, "
      f"IC95% dif. medias = [{ic.low:.2f}, {ic.high:.2f}]")
print(f"d de Cohen = {cohens_d(x, y):.3f}  |  g de Hedges = {hedges_g(x, y):.3f}")

# Correlación punto-biserial
r = stats.pointbiserialr((datos["fumador"] == "Sí").astype(int), datos["edad"])
print(f"r punto-biserial = {r.statistic:.3f}, p = {r.pvalue:.4g}")

# Wilcoxon / Mann-Whitney
res = stats.mannwhitneyu(x, y)
print(f"Wilcoxon W = {res.statistic:.1f}, p = {res.pvalue:.4g}")
print(f"Correlación rank-biserial = {rank_biserial(x, y):.3f}")


# ======================================================================
# Categórica × continua: ingreso según nivel educativo
# ======================================================================

grupos = [datos.loc[datos["nivel_educ"] == lv, "ingreso"] for lv in datos["nivel_educ"].cat.categories]

# ANOVA de Welch (oneway.test)
F, df1, df2, p = welch_anova(*grupos)
print(f"ANOVA de Welch: F = {F:.3f}, gl = ({df1}, {df2:.1f}), p = {p:.4g}")

# ANOVA clásico (aov) + tamaños de efecto
m = smf.ols("ingreso ~ C(nivel_educ)", data=datos).fit()
print(sm.stats.anova_lm(m, typ=2))
eta2, omega2 = eta_omega_squared(m)
print(f"η² = {eta2:.3f}  |  ω² = {omega2:.3f}")

# Kruskal-Wallis
res = stats.kruskal(*grupos)
print(f"Kruskal-Wallis H = {res.statistic:.3f}, p = {res.pvalue:.4g}")
print(f"ε² (rangos) = {rank_epsilon_squared(*grupos):.3f}")

# Post-hoc con corrección de Holm
print("pairwise.t.test (DE combinada):")
print(pairwise_t_test(datos["ingreso"], datos["nivel_educ"], p_adjust="holm"))

print("pairwise.wilcox.test:")
print(pairwise_wilcox_test(datos["ingreso"], datos["nivel_educ"], p_adjust="holm"))

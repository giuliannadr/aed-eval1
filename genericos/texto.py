"""Busqueda de patrones: fuerza bruta vs KMP (Modulo 6). Devuelven (posiciones, comparaciones)."""


def fuerza_bruta(texto, patron):
    n, m = len(texto), len(patron)
    pos, comp = [], 0
    if m == 0:
        return list(range(n + 1)), 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comp += 1
            if texto[i + j] != patron[j]:
                break
            j += 1
        if j == m:
            pos.append(i)
    return pos, comp


def tabla_lps(patron):
    """lps[i]: largo del mayor prefijo propio de patron[:i+1] que tambien es sufijo."""
    lps = [0] * len(patron)
    k = 0
    for i in range(1, len(patron)):
        while k > 0 and patron[i] != patron[k]:
            k = lps[k - 1]
        if patron[i] == patron[k]:
            k += 1
        lps[i] = k
    return lps


def kmp(texto, patron):
    n, m = len(texto), len(patron)
    if m == 0:
        return list(range(n + 1)), 0
    lps = tabla_lps(patron)
    pos, comp, j = [], 0, 0
    for i in range(n):  # i nunca retrocede
        while j > 0:
            comp += 1
            if texto[i] == patron[j]:
                break
            j = lps[j - 1]
        else:
            comp += 1
        if texto[i] == patron[j]:
            j += 1
        if j == m:
            pos.append(i - m + 1)
            j = lps[j - 1]
    return pos, comp
"""Mochila 0/1 con programacion dinamica (Modulo 6). O(n*W) tiempo y espacio."""


def mochila_01(pesos, valores, capacidad):
    if len(pesos) != len(valores):
        raise ValueError("pesos y valores deben tener igual largo")
    n = len(pesos)
    dp = [[0] * (capacidad + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        p, v = pesos[i - 1], valores[i - 1]
        for w in range(capacidad + 1):
            dp[i][w] = dp[i - 1][w]                      # no tomar el item i
            if p <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - p] + v)  # tomarlo
    elegidos, w = [], capacidad
    for i in range(n, 0, -1):                            # reconstruccion
        if dp[i][w] != dp[i - 1][w]:
            elegidos.append(i - 1)
            w -= pesos[i - 1]
    elegidos.reverse()
    return dp[n][capacidad], elegidos


def mochila_fuerza_bruta(pesos, valores, capacidad):
    """Referencia O(2^n) solo para validar en los tests."""
    n, mejor = len(pesos), 0
    for mask in range(1 << n):
        p = sum(pesos[i] for i in range(n) if mask >> i & 1)
        if p <= capacidad:
            mejor = max(mejor, sum(valores[i] for i in range(n) if mask >> i & 1))
    return mejor
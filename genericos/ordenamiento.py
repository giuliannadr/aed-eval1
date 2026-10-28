"""Algoritmos de ordenamiento genéricos (M3 4).

Todos reciben una función key (como sorted) y devuelven una lista NUEVA,
sin modificar la original: si ordenaran en el lugar, al medir con timeit
las repeticiones trabajarían sobre una lista ya ordenada y los tiempos
saldrían falsamente bajos.
"""


def _identidad(x):
    return x


def insercion(lista, key=_identidad):
    """Ordenamiento por inserción (M3 4.2). Estable.

    O(n²) en el peor caso (lista invertida) y en el promedio; O(n) en el
    mejor caso (lista ya ordenada), porque cada elemento se compara una
    sola vez con el anterior.
    """
    resultado = list(lista)
    for i in range(1, len(resultado)):
        actual = resultado[i]
        clave = key(actual)
        j = i - 1
        # > estricto (no >=): los iguales no se adelantan, así es estable
        while j >= 0 and key(resultado[j]) > clave:
            resultado[j + 1] = resultado[j]   # desplaza a la derecha
            j -= 1
        resultado[j + 1] = actual
    return resultado


def mergesort(lista, key=_identidad):
    """Mergesort (M3 4.5): divide y conquista. Estable.

    O(n log n) en todos los casos. Usa O(n) de memoria extra para las
    sublistas: es el trade-off tiempo vs memoria frente a inserción.
    La recursión tiene profundidad log n, así que no hay riesgo de
    superar el límite de recursión de Python.
    """
    if len(lista) <= 1:
        return list(lista)
    medio = len(lista) // 2
    izquierda = mergesort(lista[:medio], key)
    derecha = mergesort(lista[medio:], key)
    return _fusionar(izquierda, derecha, key)


def _fusionar(izquierda, derecha, key):
    """Fusiona dos listas ordenadas en una sola con dos punteros (M3 5.3). O(n)."""
    resultado = []
    i = j = 0
    while i < len(izquierda) and j < len(derecha):
        # <= (no <): ante empate gana el de la izquierda, que venía
        # antes en la lista original. Eso hace estable al algoritmo.
        if key(izquierda[i]) <= key(derecha[j]):
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1
    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado
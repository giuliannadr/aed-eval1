"""Algoritmos de búsqueda genéricos sobre listas de claves.

Las funciones trabajan con listas de valores comparables (por ejemplo,
timestamps). Para buscar eventos se usan listas alineadas: una lista de
claves ordenadas y otra de eventos en el mismo orden; el índice que
devuelven estas funciones sirve para obtener el evento de la segunda.
"""

from bisect import bisect_left, bisect_right


def busqueda_secuencial(lista, objetivo):
    """Busca objetivo recorriendo la lista elemento por elemento.

    No requiere que la lista esté ordenada. O(n) en el peor caso
    (cuando el objetivo no está o está al final).

    Returns:
        int: índice de la primera aparición, o -1 si no está.
    """
    for i, valor in enumerate(lista):   # enumerate da (índice, valor)
        if valor == objetivo:
            return i
    return -1


def busqueda_binaria(lista, objetivo):
    """Busca objetivo descartando la mitad del espacio en cada paso (M3 1.2).

    Precondición: la lista debe estar ordenada de menor a mayor. Si no lo
    está, no da error pero el resultado puede ser incorrecto.
    O(log n). Con valores repetidos devuelve la posición de alguno, no
    necesariamente el primero (para eso, usar busqueda_bisect).

    Returns:
        int: índice de una aparición del objetivo, o -1 si no está.
    """
    bajo = 0
    alto = len(lista) - 1
    # <= y no <: con < se perdería el caso en que bajo y alto coinciden
    while bajo <= alto:
        medio = (bajo + alto) // 2
        if lista[medio] == objetivo:
            return medio
        if lista[medio] < objetivo:
            bajo = medio + 1   # el objetivo está a la derecha del medio
        else:
            alto = medio - 1   # el objetivo está a la izquierda del medio
    return -1


def busqueda_bisect(lista, objetivo):
    """Busca objetivo con bisect_left (consulta indexada, M3 1.3).

    Precondición: lista ordenada. O(log n). A diferencia de
    busqueda_binaria, con repetidos devuelve siempre la primera aparición.

    Returns:
        int: índice de la primera aparición, o -1 si no está.
    """
    i = bisect_left(lista, objetivo)
    # i puede valer len(lista) si objetivo es mayor que todos: por eso se
    # chequea i < len(lista) antes de acceder a lista[i]
    if i < len(lista) and lista[i] == objetivo:
        return i
    return -1


def rango_bisect(lista, desde, hasta):
    """Posiciones de los valores entre desde y hasta (inclusive). O(log n).

    Precondición: lista ordenada. Devuelve índices (inicio, fin) para
    cortar con lista[inicio:fin], o una lista alineada con la misma
    operación. Es la misma consulta por rango que resuelve el BST.

    Raises:
        ValueError: si desde es mayor que hasta.
    """
    if desde > hasta:
        raise ValueError("desde no puede ser mayor que hasta")
    inicio = bisect_left(lista, desde)
    fin = bisect_right(lista, hasta)   # right: después del último igual a hasta
    return inicio, fin  
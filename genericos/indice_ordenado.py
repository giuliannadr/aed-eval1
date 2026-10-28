"""Índice ordenado con listas alineadas y búsqueda por rango con bisect."""

from bisect import bisect_right

from genericos.busqueda import rango_bisect


class IndiceOrdenado:
    """Mantiene dos listas alineadas: claves ordenadas y sus valores.

    Las búsquedas usan bisect sobre la lista de claves, y los índices que
    devuelve sirven para cortar la lista de valores. Como las dos listas
    son privadas y solo se modifican juntas en agregar, no pueden
    desalinearse.

    Costo de agregar: O(n) en general (insertar en el medio desplaza
    elementos, M2 3.5), pero O(1) amortizado si las claves llegan en
    orden creciente, porque la inserción es al final. Es el caso real
    de los incidentes, que llegan en orden de tiempo, y justo el peor
    caso del BST.
    """

    def __init__(self):
        self._claves = []
        self._valores = []

    def agregar(self, clave, valor):
        """Inserta manteniendo el orden. Con claves repetidas, el nuevo va
        después de los iguales (bisect_right), así se conserva el orden
        de llegada."""
        i = bisect_right(self._claves, clave)
        self._claves.insert(i, clave)
        self._valores.insert(i, valor)

    def buscar_rango(self, desde, hasta):
        """Valores con clave entre desde y hasta (inclusive), ordenados por
        clave. O(log n + k). El corte con [:] devuelve una lista nueva.

        Raises:
            ValueError: si desde es mayor que hasta.
        """
        inicio, fin = rango_bisect(self._claves, desde, hasta)
        return self._valores[inicio:fin]

    def __len__(self):
        """Cantidad de valores almacenados."""
        return len(self._claves)
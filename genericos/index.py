class Index:
    """Índice secundario por una clave que puede repetirse.

    Internamente es un dict {clave: [valores]}: varios valores pueden
    compartir la misma clave, por eso cada clave guarda una lista.

    Args:
        key (callable): función que recibe un valor y devuelve la clave
            por la que se indexa.
    """

    def __init__(self, key):
        self._key = key
        self._datos = {}

    def agregar(self, valor):
        """Agrega un valor al índice. O(1) promedio."""
        clave = self._key(valor)
        if clave not in self._datos:
            self._datos[clave] = []
        self._datos[clave].append(valor)

    def buscar(self, clave):
        """Devuelve los valores con esa clave, en orden de inserción.

        Devuelve una copia, así modificarla desde afuera no altera el
        índice (cuesta O(k), con k = cantidad de valores de esa clave).
        Si la clave no existe, devuelve una lista vacía.
        """
        return self._datos.get(clave, []).copy()
class Index:
    """Índice secundario por una clave que puede repetirse.

    Internamente es un dict {clave: [eventos]}: varios eventos pueden
    compartir la misma clave (por ejemplo, la misma categoría), por eso
    el valor es una lista y no un evento suelto.

    Se usa para claves repetidas (category, origin). El índice por id,
    que es único, lo maneja EventStore con un dict simple.

    Args:
        key (callable): función que recibe un Event y devuelve la clave
            por la que se indexa. Ej: lambda e: e.category
    """

    def __init__(self, key):
        self._key = key
        self._datos = {}

    def agregar(self, evento):
        """Agrega un evento al índice. O(1) promedio."""
        clave = self._key(evento)
        if clave not in self._datos:
            self._datos[clave] = []
        self._datos[clave].append(evento)

    def buscar(self, clave):
        """Devuelve los eventos con esa clave.

        Devuelve una copia, así modificarla desde afuera no altera el
        índice (cuesta O(k), con k = cantidad de eventos de esa clave).
        Si la clave no existe, devuelve una lista vacía.
        """
        return self._datos.get(clave, []).copy()
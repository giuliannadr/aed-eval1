from dominio.event import Event
from dominio.index import Index


class EventStore:
    """Almacén central de eventos: la única puerta de entrada al sistema.

    Mantiene la colección completa y sus índices sincronizados:
    - un dict {id: evento} (clave primaria): búsqueda por id y
      verificación de unicidad en O(1) promedio;
    - índices secundarios por category y origin (ver Index).

    No permite eliminar eventos: son registros históricos inmutables,
    y así no hay que mantener la consistencia de los índices al borrar
    (lo que costaría O(k) por cada índice).
    """

    def __init__(self):
        self._eventos = []
        self._por_id = {}
        self._por_categoria = Index(key=lambda e: e.category)
        self._por_origen = Index(key=lambda e: e.origin)

    def agregar(self, evento):
        """Agrega un evento y actualiza todos los índices. O(1) promedio.

        Raises:
            TypeError: si evento no es un Event.
            ValueError: si ya existe un evento con ese id.
        """
        # Primero se valida todo y después se modifica: si el id está
        # repetido, ningún índice llega a actualizarse.
        if not isinstance(evento, Event):
            raise TypeError("evento debe ser un Event")
        if evento.id in self._por_id:
            raise ValueError(f"ya existe un evento con id {evento.id}")
        self._eventos.append(evento)
        self._por_id[evento.id] = evento
        self._por_categoria.agregar(evento)
        self._por_origen.agregar(evento)

    def buscar_por_id(self, id_evento):
        """Devuelve el evento con ese id, o None si no existe. O(1) promedio."""
        return self._por_id.get(id_evento)

    def buscar_por_categoria(self, categoria):
        """Devuelve una copia de los eventos de esa categoría ([] si no hay)."""
        return self._por_categoria.buscar(categoria)

    def buscar_por_origen(self, origen):
        """Devuelve una copia de los eventos con ese origen ([] si no hay)."""
        return self._por_origen.buscar(origen)

    def todos(self):
        """Devuelve una copia de todos los eventos en orden de llegada. O(n)."""
        return list(self._eventos)

    def __len__(self):
        """Cantidad de eventos almacenados (permite usar len(store))."""
        return len(self._eventos)
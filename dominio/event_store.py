from dominio.event import Event
from genericos.bst import BST
from genericos.index import Index


class EventStore:
    """Almacén central de eventos: la única puerta de entrada al sistema.

    Mantiene la colección completa y sus índices sincronizados:
    - una lista en orden de llegada (recorrido directo de todos los eventos);
    - un dict {id: evento} (clave primaria): búsqueda por id y
      verificación de unicidad en O(1) promedio;
    - índices secundarios por category y origin (ver Index);
    - un BST por timestamp para consultas por rango.

    La lista y el dict por id guardan los mismos eventos: es una
    redundancia consciente (la lista conserva el orden de llegada).
    Todas las estructuras guardan referencias al mismo objeto, no
    copias, lo cual es seguro porque los eventos son inmutables.

    No permite eliminar eventos: son registros históricos inmutables,
    y así no hay que mantener la consistencia de los índices al borrar
    (lo que costaría O(k) por cada índice).
    """

    def __init__(self):
        self._eventos = []
        self._por_id = {}
        self._por_categoria = Index(key=lambda e: e.category)
        self._por_origen = Index(key=lambda e: e.origin)
        self._por_timestamp = BST()

    def agregar(self, evento):
        """Agrega un evento y actualiza todos los índices.

        Costo: O(1) promedio para la lista y los dicts, más O(h) para el
        BST (h = altura). Si los eventos llegan ordenados por timestamp,
        el BST se degenera y h = n (peor caso).

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
        self._por_timestamp.insertar(evento.timestamp, evento)

    def buscar_por_id(self, id_evento):
        """Devuelve el evento con ese id, o None si no existe. O(1) promedio."""
        return self._por_id.get(id_evento)

    def buscar_por_categoria(self, categoria):
        """Devuelve una copia de los eventos de esa categoría ([] si no hay)."""
        return self._por_categoria.buscar(categoria)

    def buscar_por_origen(self, origen):
        """Devuelve una copia de los eventos con ese origen ([] si no hay)."""
        return self._por_origen.buscar(origen)

    def buscar_por_rango(self, desde, hasta):
        """Devuelve los eventos con timestamp entre desde y hasta (inclusive).

        Usa el BST por timestamp: O(h + k). El orden no está garantizado.

        Raises:
            ValueError: si desde es mayor que hasta.
        """
        return self._por_timestamp.buscar_rango(desde, hasta)

    def todos(self):
        """Devuelve una copia de todos los eventos en orden de llegada. O(n)."""
        return list(self._eventos)

    def __len__(self):
        """Cantidad de eventos almacenados (permite usar len(store))."""
        return len(self._eventos)
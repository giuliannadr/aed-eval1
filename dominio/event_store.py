from dominio.event import Event
from genericos.avl import AVL
from genericos.bst import BST
from genericos.index import Index
from genericos.indice_ordenado import IndiceOrdenado


class EventStore:
    """Almacén central de eventos: la única puerta de entrada al sistema.

    Mantiene la colección completa y sus índices sincronizados:
    - una lista en orden de llegada (recorrido directo de todos los eventos);
    - un dict {id: evento} (clave primaria): búsqueda por id y
      verificación de unicidad en O(1) promedio;
    - índices secundarios por category y origin (ver Index);
    - un BST por timestamp para consultas por rango;
    - una lista ordenada por timestamp (IndiceOrdenado) que resuelve la
      misma consulta con bisect;
    - un AVL por timestamp (Parte 2): resuelve la misma consulta que el
      BST, pero con altura O(log n) garantizada aunque los timestamps
      lleguen ordenados (el peor caso del BST).

    El BST, el índice ordenado y el AVL resuelven la misma consulta:
    son redundancias conscientes para comparar las tres estructuras
    sobre los mismos datos. Todas guardan referencias al mismo objeto,
    no copias, lo cual es seguro porque los eventos son inmutables.

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
        self._por_timestamp_ordenado = IndiceOrdenado()
        self._por_timestamp_avl = AVL()

    def agregar(self, evento):
        """Agrega un evento y actualiza todos los índices.

        Costo: O(1) promedio para la lista y los dicts, O(h) para el BST
        (h = n si los timestamps llegan ordenados), O(log n) para el AVL
        y O(n) en general para el índice ordenado (O(1) amortizado si
        llegan en orden).

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
        self._por_timestamp_ordenado.agregar(evento.timestamp, evento)
        self._por_timestamp_avl.insertar(evento.timestamp, evento)

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

    def buscar_por_rango_ordenado(self, desde, hasta):
        """Igual que buscar_por_rango, pero con lista ordenada + bisect.

        O(log n + k) y el resultado sale ordenado por timestamp.

        Raises:
            ValueError: si desde es mayor que hasta.
        """
        return self._por_timestamp_ordenado.buscar_rango(desde, hasta)

    def buscar_por_rango_avl(self, desde, hasta):
        """Igual que buscar_por_rango, pero con el AVL (Parte 2).

        O(log n + k) en el peor caso (el BST es O(n + k) con datos
        ordenados) y el resultado sale ordenado por timestamp.

        Raises:
            ValueError: si desde es mayor que hasta.
        """
        return self._por_timestamp_avl.buscar_rango(desde, hasta)

    def altura_avl(self):
        """Altura del AVL por timestamp. Se mantiene en O(log n) aunque los
        timestamps lleguen ordenados (el peor caso del BST)."""
        return self._por_timestamp_avl.altura()

    def todos(self):
        """Devuelve una copia de todos los eventos en orden de llegada. O(n)."""
        return list(self._eventos)

    def __len__(self):
        """Cantidad de eventos almacenados (permite usar len(store))."""
        return len(self._eventos)
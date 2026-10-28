"""Red de rutas entre nodos, construida a partir de los incidentes."""

from genericos.estructuras import Cola


class Router:
    """Grafo dirigido de rutas: cada evento aporta una arista origin -> destination.

    Representación: lista de adyacencia con un dict {nodo: set(vecinos)}
    (M2 7.4.1). Se usa set porque muchos eventos repiten la misma ruta y
    la arista debe aparecer una sola vez. Es dirigido porque una ruta
    tiene sentido de origen a destino.

    Los recorridos BFS y DFS cuestan O(V + E) (M2 7.10).
    """

    def __init__(self, eventos=()):
        self._grafo = {}
        for evento in eventos:
            self.agregar_ruta(evento.origin, evento.destination)

    def agregar_ruta(self, origen, destino):
        """Agrega la arista origen -> destino. O(1) promedio."""
        self._grafo.setdefault(origen, set()).add(destino)
        self._grafo.setdefault(destino, set())  # el destino también es nodo

    def vecinos(self, nodo):
        """Vecinos de un nodo, ordenados para que los recorridos sean
        reproducibles (un set no garantiza orden)."""
        return sorted(self._grafo.get(nodo, ()))

    def distancias_bfs(self, inicio):
        """Distancia mínima en cantidad de saltos desde inicio a cada nodo
        alcanzable (M2 7.7). Usa la Cola FIFO del proyecto.

        Raises:
            ValueError: si inicio no es un nodo del grafo.
        """
        if inicio not in self._grafo:
            raise ValueError(f"el nodo {inicio} no existe")
        distancias = {inicio: 0}   # también funciona como conjunto de visitados
        cola = Cola()
        cola.encolar(inicio)
        while len(cola):
            nodo = cola.desencolar()
            for vecino in self.vecinos(nodo):
                if vecino not in distancias:
                    distancias[vecino] = distancias[nodo] + 1
                    cola.encolar(vecino)
        return distancias

    def recorrido_dfs(self, inicio):
        """Orden de visita en profundidad desde inicio (M2 7.8.2).

        Iterativo con una lista como pila (append/pop, LIFO), para no
        depender del límite de recursión.

        Raises:
            ValueError: si inicio no es un nodo del grafo.
        """
        if inicio not in self._grafo:
            raise ValueError(f"el nodo {inicio} no existe")
        visitados = set()
        orden = []
        pila = [inicio]
        while pila:
            nodo = pila.pop()
            if nodo in visitados:
                continue
            visitados.add(nodo)
            orden.append(nodo)
            # Se apilan al revés para visitar primero el vecino menor
            for vecino in reversed(self.vecinos(nodo)):
                if vecino not in visitados:
                    pila.append(vecino)
        return orden
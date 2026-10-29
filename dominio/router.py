"""Red de rutas entre nodos, construida a partir de los incidentes."""

from genericos.estructuras import Cola
from genericos.grafo import Grafo
from genericos.unionfind import UnionFind


class Router:
    """Grafo dirigido de rutas: cada evento aporta una arista origin -> destination.

    Representación: lista de adyacencia con un dict {nodo: set(vecinos)}
    (M2 7.4.1). Se usa set porque muchos eventos repiten la misma ruta y
    la arista debe aparecer una sola vez. Es dirigido porque una ruta
    tiene sentido de origen a destino.

    Parte 2: además se cuenta cuántos incidentes usan cada ruta y ese
    conteo es su peso (cuanto más incidentes, más costosa/riesgosa).
    Con esos pesos se calculan caminos mínimos (Dijkstra), la red mínima
    que conecta todos los nodos (Kruskal) y las zonas conectadas
    (Union-Find), usando las estructuras de genericos/.

    Los recorridos BFS y DFS cuestan O(V + E) (M2 7.10).
    """

    def __init__(self, eventos=()):
        self._grafo = {}
        self._pesos = {}   # {(origen, destino): cantidad de incidentes}
        for evento in eventos:
            self.agregar_ruta(evento.origin, evento.destination)

    def agregar_ruta(self, origen, destino):
        """Agrega la arista origen -> destino y suma 1 a su peso. O(1) promedio."""
        self._grafo.setdefault(origen, set()).add(destino)
        self._grafo.setdefault(destino, set())  # el destino también es nodo
        self._pesos[(origen, destino)] = self._pesos.get((origen, destino), 0) + 1

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

    # ------------------------------------------------------------ Parte 2
    def peso_ruta(self, origen, destino):
        """Cantidad de incidentes que usaron la ruta origen -> destino (0 si ninguno)."""
        return self._pesos.get((origen, destino), 0)

    def _grafo_ponderado(self, dirigido=True):
        """Construye un Grafo (genericos) con los pesos. O(V + E).

        En la versión no dirigida, A->B y B->A se fusionan sumando sus
        pesos y se ignoran los lazos (origen == destino), que no aportan
        a la conectividad.
        """
        g = Grafo(dirigido=dirigido)
        for nodo in self._grafo:
            g.agregar_nodo(nodo)
        if dirigido:
            for (o, d), p in self._pesos.items():
                g.agregar_arista(o, d, p)
        else:
            fusion = {}
            for (o, d), p in self._pesos.items():
                if o != d:
                    clave = tuple(sorted((o, d)))
                    fusion[clave] = fusion.get(clave, 0) + p
            for (u, v), p in fusion.items():
                g.agregar_arista(u, v, p)
        return g

    def camino_minimo(self, origen, destino):
        """Ruta de menor costo acumulado de origen a destino (Dijkstra).

        Devuelve (costo, [nodos]) o None si destino es inalcanzable.
        Costo: O((V + E) log V).

        Raises:
            ValueError: si origen o destino no son nodos del grafo.
        """
        for nodo in (origen, destino):
            if nodo not in self._grafo:
                raise ValueError(f"el nodo {nodo} no existe")
        dist, prev = self._grafo_ponderado().dijkstra(origen)
        if dist[destino] == float("inf"):
            return None
        return dist[destino], Grafo.camino(prev, origen, destino)

    def red_minima(self):
        """Árbol (o bosque) de expansión mínima sobre la red no dirigida (Kruskal).

        Devuelve (aristas, costo_total): el conjunto de rutas más barato
        que mantiene conectados a todos los centros alcanzables entre sí.
        Costo: O(E log E).
        """
        return self._grafo_ponderado(dirigido=False).kruskal()

    def zonas_conectadas(self):
        """Grupos de nodos conectados entre sí, ignorando la dirección
        (Union-Find con compresión y unión por rango). Devuelve una lista
        de listas ordenadas. Costo: O(E α(V))."""
        uf = UnionFind(self._grafo.keys())
        for origen, destino in self._pesos:
            uf.union(origen, destino)
        grupos = {}
        for nodo in self._grafo:
            grupos.setdefault(uf.find(nodo), []).append(nodo)
        return sorted((sorted(g) for g in grupos.values()), key=lambda g: g[0])
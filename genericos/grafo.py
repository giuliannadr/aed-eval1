"""Grafo ponderado con lista de adyacencia {u: {v: peso}} (Modulo 5)."""
import heapq
from collections import deque
from genericos.unionfind import UnionFind


class Grafo:
    def __init__(self, dirigido=True):
        self.dirigido = dirigido
        self.adj = {}

    def agregar_nodo(self, u):
        self.adj.setdefault(u, {})

    def agregar_arista(self, u, v, peso=1):
        if peso < 0:
            raise ValueError("Dijkstra requiere pesos no negativos")
        self.agregar_nodo(u)
        self.agregar_nodo(v)
        self.adj[u][v] = peso
        if not self.dirigido:
            self.adj[v][u] = peso

    def nodos(self):
        return list(self.adj)

    def aristas(self):
        """Lista (u, v, w); en no dirigido cada arista aparece una vez."""
        vistas, out = set(), []
        for u, vec in self.adj.items():
            for v, w in vec.items():
                if not self.dirigido:
                    clave = frozenset((u, v))
                    if clave in vistas:
                        continue
                    vistas.add(clave)
                out.append((u, v, w))
        return out

    def _chequear(self, x):
        if x not in self.adj:
            raise KeyError(f"nodo inexistente: {x}")

    # BFS: O(V+E). Distancia en cantidad de saltos.
    def bfs(self, origen):
        self._chequear(origen)
        dist = {origen: 0}
        orden = []
        cola = deque([origen])
        while cola:
            u = cola.popleft()
            orden.append(u)
            for v in self.adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    cola.append(v)
        return orden, dist

    # DFS iterativo (evita limite de recursion): O(V+E)
    def dfs(self, origen):
        self._chequear(origen)
        visitados, orden, pila = set(), [], [origen]
        while pila:
            u = pila.pop()
            if u in visitados:
                continue
            visitados.add(u)
            orden.append(u)
            for v in reversed(list(self.adj[u])):
                if v not in visitados:
                    pila.append(v)
        return orden

    # Dijkstra con heapq: O((V+E) log V), pesos >= 0
    def dijkstra(self, origen):
        self._chequear(origen)
        dist = {n: float("inf") for n in self.adj}
        prev = {origen: None}
        dist[origen] = 0
        heap = [(0, origen)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue  # entrada obsoleta
            for v, w in self.adj[u].items():
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        return dist, prev

    @staticmethod
    def camino(prev, origen, destino):
        if destino not in prev:
            return None
        ruta = []
        n = destino
        while n is not None:
            ruta.append(n)
            n = prev[n]
        ruta.reverse()
        return ruta if ruta[0] == origen else None

    # Kruskal: O(E log E). Devuelve bosque minimo (MSF) si no es conexo.
    def kruskal(self):
        uf = UnionFind(self.adj.keys())
        elegidas, costo = [], 0
        for u, v, w in sorted(self.aristas(), key=lambda a: a[2]):
            if uf.union(u, v):
                elegidas.append((u, v, w))
                costo += w
        return elegidas, costo

    # Prim con heapq: O(E log V). Reinicia en cada componente.
    def prim(self):
        visitados, elegidas, costo = set(), [], 0
        for inicio in self.adj:
            if inicio in visitados:
                continue
            visitados.add(inicio)
            heap = [(w, inicio, v) for v, w in self.adj[inicio].items()]
            heapq.heapify(heap)
            while heap:
                w, u, v = heapq.heappop(heap)
                if v in visitados:
                    continue
                visitados.add(v)
                elegidas.append((u, v, w))
                costo += w
                for x, wx in self.adj[v].items():
                    if x not in visitados:
                        heapq.heappush(heap, (wx, v, x))
        return elegidas, costo

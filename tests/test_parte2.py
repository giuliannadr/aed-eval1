import random
import unittest
from genericos.avl import AVL, BST
from genericos.unionfind import UnionFind
from genericos.grafo import Grafo
from genericos.texto import fuerza_bruta, kmp, tabla_lps
from genericos.dp import mochila_01, mochila_fuerza_bruta


class TestAVL(unittest.TestCase):
    def test_rotaciones_simples_y_dobles(self):
        for claves in ([3, 2, 1], [1, 2, 3], [3, 1, 2], [1, 3, 2]):
            a = AVL()
            for c in claves:
                a.insertar(c, c)
            self.assertEqual(a.altura(), 2)
            self.assertEqual(a.raiz.clave, 2)
            self.assertTrue(a.es_valido())

    def test_ordenado_mantiene_log(self):
        a = AVL()
        for i in range(4000):
            a.insertar(i, i)
        self.assertLessEqual(a.altura(), 17)  # 1.44*log2(4000) ~ 17
        self.assertTrue(a.es_valido())

    def test_bst_se_degenera(self):
        b = BST()
        for i in range(500):
            b.insertar(i, i)
        self.assertEqual(b.altura(), 500)

    def test_aleatorio_buscar_rango_repetidos(self):
        rng = random.Random(1)
        datos = [rng.randint(0, 200) for _ in range(1000)]
        a = AVL()
        for i, d in enumerate(datos):
            a.insertar(d, i)
        self.assertTrue(a.es_valido())
        self.assertEqual(sorted(a.buscar(50)), [i for i, d in enumerate(datos) if d == 50])
        esperado = sorted(i for i, d in enumerate(datos) if 20 <= d <= 80)
        self.assertEqual(sorted(a.rango(20, 80)), esperado)
        self.assertEqual(a.buscar(9999), [])
        with self.assertRaises(ValueError):
            a.rango(5, 1)

    def test_vacio(self):
        a = AVL()
        self.assertEqual(a.buscar(1), [])
        self.assertEqual(a.rango(0, 10), [])


class TestUF(unittest.TestCase):
    def test_basico(self):
        uf = UnionFind(range(6))
        self.assertTrue(uf.union(0, 1))
        self.assertTrue(uf.union(1, 2))
        self.assertFalse(uf.union(0, 2))
        self.assertEqual(uf.find(0), uf.find(2))
        self.assertNotEqual(uf.find(0), uf.find(5))


def grafo_demo(dirigido):
    g = Grafo(dirigido)
    for u, v, w in [("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5), ("C", "D", 8)]:
        g.agregar_arista(u, v, w)
    return g


class TestGrafo(unittest.TestCase):
    def test_bfs_dfs(self):
        g = grafo_demo(True)
        orden, dist = g.bfs("A")
        self.assertEqual(dist, {"A": 0, "B": 1, "C": 1, "D": 2})
        self.assertEqual(sorted(g.dfs("A")), ["A", "B", "C", "D"])
        self.assertEqual(g.bfs("D")[0], ["D"])

    def test_dijkstra(self):
        g = grafo_demo(True)
        dist, prev = g.dijkstra("A")
        self.assertEqual(dist["B"], 3)
        self.assertEqual(dist["D"], 8)
        self.assertEqual(g.camino(prev, "A", "D"), ["A", "C", "B", "D"])

    def test_inalcanzable_y_errores(self):
        g = Grafo(True)
        g.agregar_arista("A", "B", 1)
        g.agregar_nodo("Z")
        dist, prev = g.dijkstra("A")
        self.assertEqual(dist["Z"], float("inf"))
        self.assertIsNone(g.camino(prev, "A", "Z"))
        with self.assertRaises(KeyError):
            g.bfs("X")
        with self.assertRaises(ValueError):
            g.agregar_arista("A", "B", -1)

    def test_mst_kruskal_prim_coinciden(self):
        g = grafo_demo(False)
        ak, ck = g.kruskal()
        ap, cp = g.prim()
        self.assertEqual(ck, 8)  # A-C 1, C-B 2, B-D 5
        self.assertEqual(ck, cp)
        self.assertEqual(len(ak), 3)
        self.assertEqual(len(ap), 3)

    def test_mst_no_conexo_es_bosque(self):
        g = grafo_demo(False)
        g.agregar_arista("X", "Y", 7)
        self.assertEqual(g.kruskal()[1], 15)
        self.assertEqual(g.prim()[1], 15)

    def test_aleatorio_dijkstra_vs_bellman_ford(self):
        rng = random.Random(7)
        g = Grafo(True)
        for i in range(30):
            g.agregar_nodo(i)
        for _ in range(120):
            g.agregar_arista(rng.randrange(30), rng.randrange(30), rng.randint(1, 20))
        dist, _ = g.dijkstra(0)
        bf = {n: float("inf") for n in g.adj}
        bf[0] = 0
        for _ in range(29):
            for u, v, w in g.aristas():
                if bf[u] + w < bf[v]:
                    bf[v] = bf[u] + w
        self.assertEqual(dist, bf)


class TestTexto(unittest.TestCase):
    def test_lps(self):
        self.assertEqual(tabla_lps("ababaca"), [0, 0, 1, 2, 3, 0, 1])

    def test_casos(self):
        for t, p in [("abracadabra", "abra"), ("aaaaa", "aa"), ("abc", "d"),
                     ("abc", "abcd"), ("", "a"), ("abc", "")]:
            self.assertEqual(kmp(t, p)[0], fuerza_bruta(t, p)[0], (t, p))
        self.assertEqual(kmp("abracadabra", "abra")[0], [0, 7])
        self.assertEqual(kmp("aaaaa", "aa")[0], [0, 1, 2, 3])  # solapadas

    def test_aleatorio(self):
        rng = random.Random(3)
        for _ in range(300):
            t = "".join(rng.choice("ab") for _ in range(rng.randint(0, 40)))
            p = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
            self.assertEqual(kmp(t, p)[0], fuerza_bruta(t, p)[0])


class TestDP(unittest.TestCase):
    def test_clasico(self):
        v, items = mochila_01([1, 3, 4, 5], [1, 4, 5, 7], 7)
        self.assertEqual(v, 9)
        self.assertEqual(items, [1, 2])

    def test_bordes(self):
        self.assertEqual(mochila_01([], [], 10), (0, []))
        self.assertEqual(mochila_01([5], [10], 4), (0, []))
        with self.assertRaises(ValueError):
            mochila_01([1], [1, 2], 3)

    def test_vs_fuerza_bruta(self):
        rng = random.Random(5)
        for _ in range(100):
            n = rng.randint(0, 9)
            p = [rng.randint(1, 10) for _ in range(n)]
            val = [rng.randint(1, 20) for _ in range(n)]
            W = rng.randint(0, 30)
            v, items = mochila_01(p, val, W)
            self.assertEqual(v, mochila_fuerza_bruta(p, val, W))
            self.assertLessEqual(sum(p[i] for i in items), W)
            self.assertEqual(sum(val[i] for i in items), v)


if __name__ == "__main__":
    unittest.main()

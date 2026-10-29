"""Pruebas de la integración de la Parte 2 en el dominio:
EventStore + AVL, Router + grafo ponderado y TextAnalyzer + KMP."""

import random
import unittest

from dominio.event import Event
from dominio.event_store import EventStore
from dominio.router import Router
from dominio.text_analyzer import TextAnalyzer


def evento(id_, ts=0, origen="A", destino="B", texto="todo normal", cat="red", prio=3):
    return Event(id_, ts, cat, prio, texto, origen, destino)


class TestEventStoreAVL(unittest.TestCase):
    def test_avl_coincide_con_bst_y_bisect(self):
        rng = random.Random(42)
        store = EventStore()
        for i in range(300):
            store.agregar(evento(i, ts=rng.randint(0, 100)))
        for desde, hasta in [(0, 100), (10, 20), (50, 50), (101, 200)]:
            avl = store.buscar_por_rango_avl(desde, hasta)
            self.assertEqual(sorted(e.id for e in avl),
                             sorted(e.id for e in store.buscar_por_rango(desde, hasta)))
            self.assertEqual([e.timestamp for e in avl],
                             [e.timestamp for e in store.buscar_por_rango_ordenado(desde, hasta)])

    def test_rango_invertido(self):
        store = EventStore()
        with self.assertRaises(ValueError):
            store.buscar_por_rango_avl(5, 1)
    
    def test_ordenado_el_avl_se_mantiene_balanceado(self):
        store = EventStore()
        for i in range(1000):          # timestamps ordenados: peor caso del BST
            store.agregar(evento(i, ts=i))
        self.assertLessEqual(store.altura_avl(), 14)

    def test_id_repetido_no_toca_el_avl(self):
        store = EventStore()
        store.agregar(evento(1, ts=5))
        with self.assertRaises(ValueError):
            store.agregar(evento(1, ts=9))
        self.assertEqual(len(store.buscar_por_rango_avl(0, 100)), 1)


class TestRouterPonderado(unittest.TestCase):
    def setUp(self):
        # A->B x3, B->C x1, A->C x5, C->D x2, X->Y x1 (zona aparte)
        evs, i = [], 0
        for o, d, n in [("A", "B", 3), ("B", "C", 1), ("A", "C", 5), ("C", "D", 2), ("X", "Y", 1)]:
            for _ in range(n):
                evs.append(evento(i, origen=o, destino=d))
                i += 1
        self.router = Router(evs)

    def test_peso_ruta(self):
        self.assertEqual(self.router.peso_ruta("A", "B"), 3)
        self.assertEqual(self.router.peso_ruta("B", "A"), 0)

    def test_camino_minimo(self):
        costo, ruta = self.router.camino_minimo("A", "D")
        self.assertEqual((costo, ruta), (6, ["A", "B", "C", "D"]))  # 3+1+2 < 5+2

    def test_inalcanzable_y_errores(self):
        self.assertIsNone(self.router.camino_minimo("D", "A"))
        with self.assertRaises(ValueError):
            self.router.camino_minimo("A", "Z")

    def test_red_minima_es_bosque(self):
        aristas, costo = self.router.red_minima()
        self.assertEqual(costo, 1 + 2 + 3 + 1)   # B-C, C-D, A-B, X-Y
        self.assertEqual(len(aristas), 4)

    def test_zonas_conectadas(self):
        self.assertEqual(self.router.zonas_conectadas(), [["A", "B", "C", "D"], ["X", "Y"]])

    def test_lazo_y_vacio(self):
        r = Router([evento(1, origen="A", destino="A")])
        self.assertEqual(r.red_minima(), ([], 0))
        self.assertEqual(Router().zonas_conectadas(), [])

    def test_bfs_y_dfs_de_la_parte_1_siguen_igual(self):
        self.assertEqual(self.router.distancias_bfs("A"), {"A": 0, "B": 1, "C": 1, "D": 2})
        self.assertEqual(self.router.recorrido_dfs("A"), ["A", "B", "C", "D"])


class TestTextAnalyzerKMP(unittest.TestCase):
    def setUp(self):
        self.ta = TextAnalyzer()

    def test_detecta_alerta_pegada_a_puntuacion(self):
        self.assertFalse(self.ta.es_alerta("hubo una falla, se reinicia"))
        self.assertTrue(self.ta.es_alerta_kmp("hubo una falla, se reinicia"))

    def test_mayusculas_y_sin_alerta(self):
        self.assertTrue(self.ta.es_alerta_kmp("URGENTE revisar"))
        self.assertFalse(self.ta.es_alerta_kmp("todo funciona bien"))
        self.assertFalse(self.ta.es_alerta_kmp(""))

    def test_falso_positivo_documentado(self):
        self.assertTrue(self.ta.es_alerta_kmp("las fallas fueron menores"))

    def test_filtrar_coincide_con_palabras_completas_sin_puntuacion(self):
        textos = ["caída del servidor", "todo ok", "intrusión detectada", "mantenimiento"]
        evs = [evento(i, texto=t) for i, t in enumerate(textos)]
        self.assertEqual(self.ta.filtrar_alertas_kmp(evs), self.ta.filtrar_alertas(evs))


if __name__ == "__main__":
    unittest.main()
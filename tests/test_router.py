import unittest

from dominio.event import Event
from dominio.router import Router


class TestRouter(unittest.TestCase):

    def setUp(self):
        # A -> B -> C  y  A -> D -> C
        self.router = Router()
        for origen, destino in (("A", "B"), ("B", "C"), ("A", "D"), ("D", "C")):
            self.router.agregar_ruta(origen, destino)

    def test_bfs_distancias(self):
        self.assertEqual(self.router.distancias_bfs("A"),
                         {"A": 0, "B": 1, "D": 1, "C": 2})

    def test_dirigido(self):
        # Desde C no sale ninguna ruta
        self.assertEqual(self.router.distancias_bfs("C"), {"C": 0})

    def test_dfs_orden(self):
        self.assertEqual(self.router.recorrido_dfs("A"), ["A", "B", "C", "D"])

    def test_nodo_inexistente(self):
        with self.assertRaises(ValueError):
            self.router.distancias_bfs("Z")

    def test_construido_desde_eventos_sin_aristas_repetidas(self):
        eventos = [Event(1, 10, "red", 3, "x", "A", "B"),
                   Event(2, 20, "red", 3, "x", "A", "B")]
        self.assertEqual(Router(eventos).vecinos("A"), ["B"])

    def test_ciclo_no_entra_en_bucle(self):
        self.router.agregar_ruta("C", "A")   # cierra el ciclo A -> B -> C -> A
        self.assertEqual(len(self.router.distancias_bfs("A")), 4)
        self.assertEqual(len(self.router.recorrido_dfs("A")), 4)


if __name__ == "__main__":
    unittest.main()
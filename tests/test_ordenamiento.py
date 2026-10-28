import random
import unittest

from datos.generador import generar_eventos
from dominio.event import Event
from genericos.ordenamiento import insercion, mergesort

ALGORITMOS = (insercion, mergesort)


class TestOrdenamiento(unittest.TestCase):

    def test_contra_sorted_numeros(self):
        rng = random.Random(0)
        for _ in range(100):
            lista = [rng.randint(0, 50) for _ in range(rng.randint(0, 40))]
            for ordenar in ALGORITMOS:
                with self.subTest(algoritmo=ordenar.__name__):
                    self.assertEqual(ordenar(lista), sorted(lista))

    def test_contra_sorted_eventos_por_timestamp(self):
        eventos = generar_eventos(200)
        esperado = sorted(eventos, key=lambda e: e.timestamp)
        for ordenar in ALGORITMOS:
            with self.subTest(algoritmo=ordenar.__name__):
                self.assertEqual(ordenar(eventos, key=lambda e: e.timestamp), esperado)

    def test_estable(self):
        # Mismo timestamp: tienen que conservar el orden de entrada
        a = Event(1, 100, "red", 3, "x", "A", "B")
        b = Event(2, 100, "red", 3, "x", "A", "B")
        c = Event(3, 50, "red", 3, "x", "A", "B")
        for ordenar in ALGORITMOS:
            with self.subTest(algoritmo=ordenar.__name__):
                self.assertEqual(ordenar([a, b, c], key=lambda e: e.timestamp), [c, a, b])

    def test_no_modifica_la_original(self):
        lista = [3, 1, 2]
        for ordenar in ALGORITMOS:
            with self.subTest(algoritmo=ordenar.__name__):
                ordenar(lista)
                self.assertEqual(lista, [3, 1, 2])

    def test_vacia_y_un_elemento(self):
        for ordenar in ALGORITMOS:
            with self.subTest(algoritmo=ordenar.__name__):
                self.assertEqual(ordenar([]), [])
                self.assertEqual(ordenar([7]), [7])

    def test_ordenada_invertida_y_todos_iguales(self):
        for lista in ([1, 2, 3, 4], [4, 3, 2, 1], [5, 5, 5, 5]):
            for ordenar in ALGORITMOS:
                with self.subTest(algoritmo=ordenar.__name__, lista=lista):
                    self.assertEqual(ordenar(lista), sorted(lista))


if __name__ == "__main__":
    unittest.main()
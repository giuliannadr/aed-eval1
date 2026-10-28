import random
import unittest

from genericos.busqueda import (
    busqueda_binaria,
    busqueda_bisect,
    busqueda_secuencial,
    rango_bisect,
)

LISTA = [10, 20, 20, 20, 35, 50]
BUSQUEDAS = (busqueda_secuencial, busqueda_binaria, busqueda_bisect)


class TestBusquedaBordes(unittest.TestCase):

    def test_al_principio_medio_y_final(self):
        for buscar in BUSQUEDAS:
            with self.subTest(funcion=buscar.__name__):
                self.assertEqual(buscar(LISTA, 10), 0)
                self.assertEqual(buscar(LISTA, 35), 4)
                self.assertEqual(buscar(LISTA, 50), 5)

    def test_ausente_menor_mayor_y_entre(self):
        for buscar in BUSQUEDAS:
            with self.subTest(funcion=buscar.__name__):
                self.assertIsNone(buscar(LISTA, 5))
                self.assertIsNone(buscar(LISTA, 99))
                self.assertIsNone(buscar(LISTA, 25))

    def test_lista_vacia(self):
        for buscar in BUSQUEDAS:
            with self.subTest(funcion=buscar.__name__):
                self.assertIsNone(buscar([], 10))

    def test_un_elemento(self):
        for buscar in BUSQUEDAS:
            with self.subTest(funcion=buscar.__name__):
                self.assertEqual(buscar([7], 7), 0)
                self.assertIsNone(buscar([7], 3))

    def test_bisect_devuelve_primer_repetido(self):
        self.assertEqual(busqueda_bisect(LISTA, 20), 1)

    def test_binaria_con_repetidos_devuelve_alguno(self):
        # Solo se garantiza que sea una posición donde hay un 20
        i = busqueda_binaria(LISTA, 20)
        self.assertEqual(LISTA[i], 20)


class TestRangoBisect(unittest.TestCase):

    def _corte(self, desde, hasta):
        inicio, fin = rango_bisect(LISTA, desde, hasta)
        return LISTA[inicio:fin]

    def test_rango_normal(self):
        self.assertEqual(self._corte(20, 35), [20, 20, 20, 35])

    def test_hasta_incluye_todos_los_repetidos(self):
        # Si se usara bisect_left para hasta, se perderían los 20
        self.assertEqual(self._corte(10, 20), [10, 20, 20, 20])

    def test_desde_igual_hasta(self):
        self.assertEqual(self._corte(20, 20), [20, 20, 20])

    def test_rango_excede_la_lista(self):
        self.assertEqual(self._corte(0, 100), LISTA)

    def test_rango_vacio(self):
        self.assertEqual(self._corte(36, 49), [])

    def test_rango_invertido_error(self):
        with self.assertRaises(ValueError):
            rango_bisect(LISTA, 50, 10)


class TestContraReferencia(unittest.TestCase):
    """Compara contra implementaciones simples en muchas listas al azar."""

    def test_busquedas_aleatorio(self):
        rng = random.Random(0)
        for _ in range(200):
            lista = sorted(rng.randint(0, 50) for _ in range(rng.randint(0, 30)))
            objetivo = rng.randint(-5, 55)
            esperado = busqueda_secuencial(lista, objetivo)
            # bisect y secuencial devuelven la PRIMERA aparición: deben coincidir
            self.assertEqual(busqueda_bisect(lista, objetivo), esperado)
            # la binaria puede dar otra aparición, pero si da un índice,
            # ahí tiene que estar el objetivo
            i = busqueda_binaria(lista, objetivo)
            if esperado is None:
                self.assertIsNone(i)
            else:
                self.assertEqual(lista[i], objetivo)

    def test_rango_aleatorio(self):
        rng = random.Random(1)
        for _ in range(200):
            lista = sorted(rng.randint(0, 50) for _ in range(rng.randint(0, 30)))
            desde = rng.randint(-5, 55)
            hasta = rng.randint(desde, 60)
            inicio, fin = rango_bisect(lista, desde, hasta)
            esperado = [x for x in lista if desde <= x <= hasta]
            self.assertEqual(lista[inicio:fin], esperado)


if __name__ == "__main__":
    unittest.main()
import random
import unittest

from genericos.busqueda import (
    busqueda_binaria,
    busqueda_bisect,
    busqueda_secuencial,
    rango_bisect,
)

LISTA = [10, 20, 20, 20, 35, 50]


class TestBusquedaBordes(unittest.TestCase):

    def test_al_principio_medio_y_final(self):
        for buscar in (busqueda_secuencial, busqueda_binaria, busqueda_bisect):
            self.assertEqual(buscar(LISTA, 10), 0)
            self.assertEqual(buscar(LISTA, 35), 4)
            self.assertEqual(buscar(LISTA, 50), 5)

    def test_ausente_menor_mayor_y_entre(self):
        for buscar in (busqueda_secuencial, busqueda_binaria, busqueda_bisect):
            self.assertEqual(buscar(LISTA, 5), -1)
            self.assertEqual(buscar(LISTA, 99), -1)
            self.assertEqual(buscar(LISTA, 25), -1)

    def test_lista_vacia(self):
        for buscar in (busqueda_secuencial, busqueda_binaria, busqueda_bisect):
            self.assertEqual(buscar([], 10), -1)

    def test_un_elemento(self):
        for buscar in (busqueda_secuencial, busqueda_binaria, busqueda_bisect):
            self.assertEqual(buscar([7], 7), 0)
            self.assertEqual(buscar([7], 3), -1)

    def test_bisect_devuelve_primer_repetido(self):
        self.assertEqual(busqueda_bisect(LISTA, 20), 1)

    def test_binaria_con_repetidos_devuelve_alguno(self):
        # Solo se garantiza que sea una posición donde hay un 20
        i = busqueda_binaria(LISTA, 20)
        self.assertEqual(LISTA[i], 20)


class TestRangoBisect(unittest.TestCase):

    def test_rango_normal(self):
        inicio, fin = rango_bisect(LISTA, 20, 35)
        self.assertEqual(LISTA[inicio:fin], [20, 20, 20, 35])

    def test_rango_vacio(self):
        inicio, fin = rango_bisect(LISTA, 36, 49)
        self.assertEqual(LISTA[inicio:fin], [])

    def test_rango_invertido_error(self):
        with self.assertRaises(ValueError):
            rango_bisect(LISTA, 50, 10)


class TestContraReferencia(unittest.TestCase):
    """Compara contra la secuencial en muchas listas al azar."""

    def test_aleatorio(self):
        rng = random.Random(0)
        for _ in range(200):
            lista = sorted(rng.randint(0, 50) for _ in range(rng.randint(0, 30)))
            objetivo = rng.randint(-5, 55)
            esperado = busqueda_secuencial(lista, objetivo)
            # bisect y secuencial devuelven la PRIMERA aparición: deben coincidir
            self.assertEqual(busqueda_bisect(lista, objetivo), esperado)
            # la binaria puede dar otra aparición: alcanza con que esté (o no) igual
            self.assertEqual(busqueda_binaria(lista, objetivo) == -1, esperado == -1)


if __name__ == "__main__":
    unittest.main()
import unittest

from dominio.event import Event, clave_atencion
from genericos.estructuras import Cola, ColaPrioridad


class _Cosa:
    """Objeto sin comparación (<): si la cola llegara a comparar
    dos valores, el test explotaría con TypeError."""

    def __init__(self, prioridad):
        self.prioridad = prioridad


class TestCola(unittest.TestCase):

    def test_fifo(self):
        cola = Cola()
        for valor in ("A", "B", "C"):
            cola.encolar(valor)
        self.assertEqual(
            [cola.desencolar(), cola.desencolar(), cola.desencolar()],
            ["A", "B", "C"],
        )

    def test_ver_siguiente_no_saca(self):
        cola = Cola()
        cola.encolar("A")
        cola.encolar("B")
        self.assertEqual(cola.ver_siguiente(), "A")
        self.assertEqual(len(cola), 2)

    def test_len(self):
        cola = Cola()
        for valor in ("A", "B", "C"):
            cola.encolar(valor)
        cola.desencolar()
        self.assertEqual(len(cola), 2)

    def test_desencolar_vacia_error(self):
        with self.assertRaises(IndexError):
            Cola().desencolar()

    def test_ver_siguiente_vacia_error(self):
        with self.assertRaises(IndexError):
            Cola().ver_siguiente()


class TestColaPrioridad(unittest.TestCase):

    def setUp(self):
        self.cp = ColaPrioridad(key=clave_atencion)

    def test_sale_primero_el_mas_grave(self):
        leve = Event(1, 100, "red", 1, "x", "A", "B")
        grave = Event(2, 200, "red", 5, "x", "A", "B")
        self.cp.encolar(leve)
        self.cp.encolar(grave)
        self.assertEqual(self.cp.desencolar(), grave)

    def test_misma_prioridad_sale_el_mas_antiguo(self):
        nuevo = Event(1, 500, "red", 3, "x", "A", "B")
        viejo = Event(2, 100, "red", 3, "x", "A", "B")
        self.cp.encolar(nuevo)
        self.cp.encolar(viejo)
        self.assertEqual(self.cp.desencolar(), viejo)

    def test_igual_prioridad_y_timestamp_desempata_por_id(self):
        id_mayor = Event(2, 100, "red", 3, "x", "A", "B")
        id_menor = Event(1, 100, "red", 3, "x", "A", "B")
        # Se encola primero el de id mayor: si saliera por orden de
        # llegada, saldría ese. Tiene que salir el de id menor.
        self.cp.encolar(id_mayor)
        self.cp.encolar(id_menor)
        self.assertEqual(self.cp.desencolar(), id_menor)

    def test_contador_desempata_sin_comparar_valores(self):
        # Clave que se repite: el desempate lo tiene que hacer el contador.
        cp = ColaPrioridad(key=lambda x: x.prioridad)
        primera = _Cosa(1)
        segunda = _Cosa(1)
        cp.encolar(primera)
        cp.encolar(segunda)
        # No explota, y a igual clave sale el que entró primero.
        self.assertIs(cp.desencolar(), primera)
        self.assertIs(cp.desencolar(), segunda)

    def test_ver_siguiente_no_saca(self):
        e = Event(1, 100, "red", 3, "x", "A", "B")
        self.cp.encolar(e)
        self.assertEqual(self.cp.ver_siguiente(), e)
        self.assertEqual(len(self.cp), 1)

    def test_len(self):
        for i in range(3):
            self.cp.encolar(Event(i, 100, "red", 3, "x", "A", "B"))
        self.cp.desencolar()
        self.assertEqual(len(self.cp), 2)

    def test_desencolar_vacia_error(self):
        with self.assertRaises(IndexError):
            self.cp.desencolar()

    def test_ver_siguiente_vacia_error(self):
        with self.assertRaises(IndexError):
            self.cp.ver_siguiente()


if __name__ == "__main__":
    unittest.main()
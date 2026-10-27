import unittest

from dominio.event import Event
from dominio.event_store import EventStore


class TestEventStore(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada test: store nuevo con 3 eventos conocidos."""
        self.store = EventStore()
        self.e1 = Event(1, 100, "red", 3, "caída", "A", "B")
        self.e2 = Event(2, 200, "red", 5, "falla", "B", "C")
        self.e3 = Event(3, 300, "hardware", 1, "", "A", "C")
        for e in (self.e1, self.e2, self.e3):
            self.store.agregar(e)

    def test_buscar_por_categoria(self):
        self.assertEqual(self.store.buscar_por_categoria("red"), [self.e1, self.e2])

    def test_categoria_inexistente_lista_vacia(self):
        self.assertEqual(self.store.buscar_por_categoria("energia"), [])

    def test_buscar_por_id(self):
        self.assertEqual(self.store.buscar_por_id(2), self.e2)

    def test_buscar_por_rango(self):
        resultado = self.store.buscar_por_rango(150, 300)
        self.assertEqual(sorted(resultado, key=lambda e: e.id), [self.e2, self.e3])

    def test_rechazo_no_modifica_indices(self):
        repetido = Event(1, 999, "seguridad", 2, "x", "D", "E")
        with self.assertRaises(ValueError):
            self.store.agregar(repetido)
        # Ningún índice tiene que haber cambiado:
        self.assertEqual(len(self.store), 3)
        self.assertEqual(self.store.buscar_por_id(1), self.e1)
        self.assertEqual(self.store.buscar_por_categoria("seguridad"), [])
        self.assertEqual(self.store.buscar_por_origen("D"), [])
        self.assertEqual(self.store.buscar_por_rango(999, 999), [])

    def test_id_inexistente_none(self):
        self.assertIsNone(self.store.buscar_por_id(999))

    def test_buscar_por_origen(self):
        self.assertEqual(self.store.buscar_por_origen("A"), [self.e1, self.e3])

    def test_modificar_copia_no_altera_indice(self):
        copia = self.store.buscar_por_categoria("red")
        copia.append(Event(4, 400, "red", 2, "x", "D", "E"))
        self.assertEqual(len(self.store.buscar_por_categoria("red")), 2)

    def test_agregar_algo_que_no_es_event(self):
        with self.assertRaises(TypeError):
            self.store.agregar("no es un evento")


if __name__ == "__main__":
    unittest.main()
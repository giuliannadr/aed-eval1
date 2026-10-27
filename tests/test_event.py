import unittest
from dataclasses import FrozenInstanceError

from dominio.event import Event


class TestEvent(unittest.TestCase):

    # --- Casos válidos ---

    def test_evento_valido(self):
        e = Event(1, 100, "red", 3, "caída", "A", "B")
        self.assertEqual(e.priority, 3)
        self.assertEqual(e.category, "red")

    def test_text_vacio_permitido(self):
        e = Event(1, 100, "red", 3, "", "A", "B")
        self.assertEqual(e.text, "")

    # Bordes: los errores más comunes están en los límites (< vs <=)
    def test_priority_minima_valida(self):
        e = Event(1, 100, "red", 1, "x", "A", "B")
        self.assertEqual(e.priority, 1)

    def test_priority_maxima_valida(self):
        e = Event(1, 100, "red", 5, "x", "A", "B")
        self.assertEqual(e.priority, 5)

    def test_timestamp_cero_valido(self):
        e = Event(1, 0, "red", 3, "x", "A", "B")
        self.assertEqual(e.timestamp, 0)

    # --- Inmutabilidad ---

    def test_inmutable(self):
        e = Event(1, 100, "red", 3, "caída", "A", "B")
        with self.assertRaises(FrozenInstanceError):
            e.priority = 5

    # --- Casos inválidos ---

    def test_id_none(self):
        with self.assertRaises(TypeError):
            Event(None, 100, "red", 3, "x", "A", "B")

    def test_timestamp_negativo(self):
        with self.assertRaises(ValueError):
            Event(1, -1, "red", 3, "x", "A", "B")

    def test_timestamp_no_es_int(self):
        with self.assertRaises(TypeError):
            Event(1, "100", "red", 3, "x", "A", "B")

    def test_priority_decimal(self):
        with self.assertRaises(TypeError):
            Event(1, 100, "red", 3.5, "x", "A", "B")

    def test_priority_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            Event(1, 100, "red", 6, "x", "A", "B")

    def test_category_vacia(self):
        with self.assertRaises(ValueError):
            Event(1, 100, "", 3, "x", "A", "B")

    def test_category_solo_espacios(self):
        with self.assertRaises(ValueError):
            Event(1, 100, "   ", 3, "x", "A", "B")

    def test_category_con_espacios_al_costado(self):
        with self.assertRaises(ValueError):
            Event(1, 100, "red ", 3, "x", "A", "B")

    def test_origin_vacio(self):
        with self.assertRaises(ValueError):
            Event(1, 100, "red", 3, "x", "", "B")

    def test_destination_vacio(self):
        with self.assertRaises(ValueError):
            Event(1, 100, "red", 3, "x", "A", "")

    def test_text_none(self):
        with self.assertRaises(TypeError):
            Event(1, 100, "red", 3, None, "A", "B")


if __name__ == "__main__":
    unittest.main()
import unittest

from dominio.event import Event
from dominio.text_analyzer import TextAnalyzer


class TestTextAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analizador = TextAnalyzer()

    def test_detecta_alerta(self):
        self.assertTrue(self.analizador.es_alerta("caída en el servicio"))

    def test_sin_alerta(self):
        self.assertFalse(self.analizador.es_alerta("consulta de rutina"))

    def test_texto_vacio(self):
        self.assertFalse(self.analizador.es_alerta(""))

    def test_mayusculas(self):
        self.assertTrue(self.analizador.es_alerta("Falla general"))

    def test_filtrar_alertas(self):
        alerta = Event(1, 10, "red", 3, "urgente revisar", "A", "B")
        normal = Event(2, 20, "red", 3, "reporte de uso", "A", "B")
        self.assertEqual(self.analizador.filtrar_alertas([alerta, normal]), [alerta])

    def test_contar_palabras(self):
        eventos = [Event(1, 10, "red", 3, "falla de red", "A", "B"),
                   Event(2, 20, "red", 3, "falla", "A", "B")]
        self.assertEqual(self.analizador.contar_palabras(eventos)["falla"], 2)


if __name__ == "__main__":
    unittest.main()
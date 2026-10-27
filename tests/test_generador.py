from dominio.text_analyzer import PALABRAS_ALERTA
import unittest

from datos.generador import generar_eventos


class TestGenerador(unittest.TestCase):

    def test_largo_correcto(self):
        self.assertEqual(len(generar_eventos(100)), 100)

    def test_n_cero_lista_vacia(self):
        self.assertEqual(generar_eventos(0), [])

    def test_misma_semilla_mismo_resultado(self):
        self.assertEqual(generar_eventos(50, semilla=7), generar_eventos(50, semilla=7))

    def test_orden_invalido(self):
        with self.assertRaises(ValueError):
            generar_eventos(10, orden="cualquiercosa")


    def test_ids_unicos(self):
        eventos = generar_eventos(100)
        ids = [evento.id for evento in eventos]
        self.assertEqual(len(set(ids)), len(ids))

 
    def test_semilla_distinta_resultado_distinto(self):
        eventos1 = generar_eventos(50, semilla=42)
        eventos2 = generar_eventos(50, semilla=43)
        self.assertNotEqual(eventos1, eventos2)

    def test_aleatorio(self):
        eventos = generar_eventos(100, orden="aleatorio")
        timestamps = [evento.timestamp for evento in eventos]
        self.assertNotEqual(timestamps, sorted(timestamps))
   
    def test_ordenado_por_timestamp(self):
        eventos = generar_eventos(100, orden="ordenado")
        timestamps = [evento.timestamp for evento in eventos]
        self.assertEqual(timestamps, sorted(timestamps))

  
    def test_invertido(self):
        eventos = generar_eventos(100, orden="invertido")
        timestamps = [evento.timestamp for evento in eventos]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))


    def test_origin_distinto_de_destination(self):
        eventos = generar_eventos(100)
        for evento in eventos:
            self.assertNotEqual(evento.origin, evento.destination)


    def test_n_negativo(self):
        with self.assertRaises(ValueError):
            generar_eventos(-5)

    def test_hay_timestamps_repetidos(self):
        timestamps = [e.timestamp for e in generar_eventos(1000)]
        # si hay repetidos, el set (sin duplicados) es más chico que la lista
        self.assertLess(len(set(timestamps)), len(timestamps))

    def test_hay_textos_con_alerta_y_vacios(self):
        textos = [e.text for e in generar_eventos(1000)]
        hay_alerta = any(p in t for t in textos for p in PALABRAS_ALERTA)
        self.assertTrue(hay_alerta)
        self.assertIn("", textos)

if __name__ == "__main__":
    unittest.main()
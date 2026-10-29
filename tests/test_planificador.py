import random
import unittest

from dominio.event import Event
from dominio.planificador import seleccionar_incidentes
from genericos.dp import mochila_fuerza_bruta

HORAS = {"red": 2, "seguridad": 4, "hardware": 3}


def ev(i, cat, prio):
    return Event(i, i, cat, prio, "x", "A", "B")


def horas(e):
    return HORAS[e.category]


class TestPlanificador(unittest.TestCase):
    def test_no_siempre_conviene_el_mas_grave(self):
        # El más grave (prio 5) cuesta 4h; con 4h conviene tomar dos de 2h (3+3=6 > 5)
        eventos = [ev(1, "seguridad", 5), ev(2, "red", 3), ev(3, "red", 3)]
        valor, elegidos = seleccionar_incidentes(eventos, 4, horas)
        self.assertEqual(valor, 6)
        self.assertEqual([e.id for e in elegidos], [2, 3])

    def test_respeta_presupuesto_y_valor(self):
        eventos = [ev(1, "red", 2), ev(2, "hardware", 4), ev(3, "seguridad", 5)]
        valor, elegidos = seleccionar_incidentes(eventos, 7, horas)
        self.assertLessEqual(sum(horas(e) for e in elegidos), 7)
        self.assertEqual(valor, sum(e.priority for e in elegidos))

    def test_bordes(self):
        self.assertEqual(seleccionar_incidentes([], 10, horas), (0, []))
        self.assertEqual(seleccionar_incidentes([ev(1, "red", 3)], 0, horas), (0, []))
        self.assertEqual(seleccionar_incidentes([ev(1, "seguridad", 5)], 3, horas), (0, []))

    def test_errores(self):
        with self.assertRaises(ValueError):
            seleccionar_incidentes([], -1, horas)
        with self.assertRaises(ValueError):
            seleccionar_incidentes([ev(1, "red", 3)], 5, lambda e: 0)
        with self.assertRaises(ValueError):
            seleccionar_incidentes([ev(1, "red", 3)], 5, lambda e: 1.5)

    def test_optimo_contra_fuerza_bruta(self):
        rng = random.Random(11)
        cats = list(HORAS)
        for _ in range(60):
            eventos = [ev(i, rng.choice(cats), rng.randint(1, 5)) for i in range(rng.randint(0, 9))]
            W = rng.randint(0, 20)
            valor, _ = seleccionar_incidentes(eventos, W, horas)
            self.assertEqual(valor, mochila_fuerza_bruta([horas(e) for e in eventos],
                                                         [e.priority for e in eventos], W))


if __name__ == "__main__":
    unittest.main()
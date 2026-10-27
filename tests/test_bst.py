import unittest

from genericos.bst import BST


class TestBST(unittest.TestCase):

    def setUp(self):
        self.arbol = BST()
        for clave in [50, 30, 70, 30, 60, 80]:
            self.arbol.insertar(clave, f"ev{clave}")

    def test_rango_normal(self):
        resultado = self.arbol.buscar_rango(30, 60)
        self.assertEqual(sorted(resultado), sorted(["ev30", "ev30", "ev50", "ev60"]))

    def test_rango_vacio(self):
        self.assertEqual(self.arbol.buscar_rango(90, 100), [])

    def test_rango_con_repetidos(self):
        resultado = self.arbol.buscar_rango(30, 30)
        self.assertEqual(sorted(resultado), sorted(["ev30", "ev30"]))

    def test_arbol_vacio(self):
        arbol_vacio = BST()
        self.assertEqual(arbol_vacio.buscar_rango(0, 100), [])

    def test_bordes_inclusivos(self):
        resultado = self.arbol.buscar_rango(50, 70)
        self.assertEqual(sorted(resultado), sorted(["ev50", "ev60", "ev70"]))

    def test_degenerado_sin_recursion_error(self):
        arbol_degenerado = BST()
        for clave in range(2000):
            arbol_degenerado.insertar(clave, f"ev{clave}")
        resultado = arbol_degenerado.buscar_rango(0, 1999)
        self.assertEqual(len(resultado), 2000)

    def test_rango_hueco_interno(self):
        self.assertEqual(self.arbol.buscar_rango(51, 59), [])

    def test_rango_invertido_error(self):
        with self.assertRaises(ValueError):
            self.arbol.buscar_rango(60, 30)


if __name__ == "__main__":
    unittest.main()
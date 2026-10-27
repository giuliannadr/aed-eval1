"""Árbol de búsqueda binaria (BST) genérico con soporte para claves repetidas."""


class _Nodo:
    """Nodo del BST: una clave y la lista de valores que comparten esa clave."""

    def __init__(self, clave, valor):
        self.clave = clave
        self.valores = [valor]
        self.izquierdo = None
        self.derecho = None


class BST:
    """Árbol de búsqueda binaria: claves menores a la izquierda, mayores a la derecha.

    Las claves repetidas no generan nodos nuevos: el valor se agrega a la
    lista del nodo existente. Así la propiedad de orden se mantiene estricta.

    Costo de insertar y buscar: O(h), con h = altura del árbol.
    Balanceado h ≈ log n; con claves que llegan ordenadas el árbol se
    degenera en una lista y h = n (peor caso, M3 2.1).
    """

    def __init__(self):
        self._raiz = None

    def insertar(self, clave, valor):
        """Inserta un valor bajo una clave. O(h).

        Iterativo para no depender del límite de recursión de Python
        en árboles degenerados.
        """
        if self._raiz is None:
            self._raiz = _Nodo(clave, valor)
            return

        actual = self._raiz
        while True:
            if clave == actual.clave:
                actual.valores.append(valor)
                return
            if clave < actual.clave:
                if actual.izquierdo is None:
                    actual.izquierdo = _Nodo(clave, valor)
                    return
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = _Nodo(clave, valor)
                    return
                actual = actual.derecho

    def buscar_rango(self, desde, hasta):
        """Devuelve los valores con clave entre desde y hasta (inclusive).

        Usa la propiedad de orden para podar: no entra a subárboles que
        no pueden tener claves dentro del rango. El orden del resultado
        no está garantizado.

        Costo: O(h + k), con h = altura del árbol y k = cantidad de
        resultados. Con el árbol degenerado, h = n.

        Raises:
            ValueError: si desde es mayor que hasta.
        """
        if desde > hasta:
            raise ValueError("desde no puede ser mayor que hasta")

        resultado = []
        pila = [self._raiz]
        while pila:
            nodo = pila.pop()
            if nodo is None:
                continue
            if desde <= nodo.clave <= hasta:
                resultado.extend(nodo.valores)
            # Poda: a la izquierda solo hay claves menores que nodo.clave.
            # Solo vale la pena bajar si puede haber alguna >= desde.
            if nodo.clave > desde:
                pila.append(nodo.izquierdo)
            # A la derecha solo hay claves mayores que nodo.clave.
            # Solo vale la pena bajar si puede haber alguna <= hasta.
            if nodo.clave < hasta:
                pila.append(nodo.derecho)
        return resultado
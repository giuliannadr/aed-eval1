"""AVL (Modulo 4, Opcion A) y BST simple para comparar.
Clave repetida -> lista de valores (como en la Parte 1)."""


class Nodo:
    def __init__(self, clave, valor):
        self.clave = clave
        self.valores = [valor]
        self.izq = None
        self.der = None
        self.altura = 1


def _alt(n):
    return n.altura if n else 0


def _factor(n):
    return _alt(n.izq) - _alt(n.der)  # debe estar en [-1, 1]


def _actualizar(n):
    n.altura = 1 + max(_alt(n.izq), _alt(n.der))


class AVL:
    """Insercion/busqueda/rango O(log n) en el peor caso."""

    def __init__(self):
        self.raiz = None
        self.rotaciones = 0
        self._n = 0

    def __len__(self):
        return self._n

    def altura(self):
        return _alt(self.raiz)

    # --- rotaciones: preservan el orden in-order ---
    def _rot_der(self, y):  # caso LL
        x = y.izq
        y.izq = x.der
        x.der = y
        _actualizar(y)
        _actualizar(x)
        self.rotaciones += 1
        return x

    def _rot_izq(self, x):  # caso RR
        y = x.der
        x.der = y.izq
        y.izq = x
        _actualizar(x)
        _actualizar(y)
        self.rotaciones += 1
        return y

    def _balancear(self, n):
        _actualizar(n)
        f = _factor(n)
        if f > 1:                       # pesado a la izquierda
            if _factor(n.izq) < 0:      # LR: rotacion doble
                n.izq = self._rot_izq(n.izq)
            return self._rot_der(n)
        if f < -1:                      # pesado a la derecha
            if _factor(n.der) > 0:      # RL: rotacion doble
                n.der = self._rot_der(n.der)
            return self._rot_izq(n)
        return n

    def insertar(self, clave, valor):
        self.raiz = self._ins(self.raiz, clave, valor)

    def _ins(self, n, clave, valor):
        if n is None:
            self._n += 1
            return Nodo(clave, valor)
        if clave < n.clave:
            n.izq = self._ins(n.izq, clave, valor)
        elif clave > n.clave:
            n.der = self._ins(n.der, clave, valor)
        else:
            n.valores.append(valor)  # repetido: no cambia la forma
            self._n += 1
            return n
        return self._balancear(n)

    def buscar(self, clave):
        n = self.raiz
        while n:
            if clave < n.clave:
                n = n.izq
            elif clave > n.clave:
                n = n.der
            else:
                return list(n.valores)
        return []

    def rango(self, desde, hasta):
        """Valores con desde <= clave <= hasta, ordenados. O(log n + k)."""
        if desde > hasta:
            raise ValueError("rango invertido")
        out = []

        def rec(n):
            if n is None:
                return
            if desde < n.clave:
                rec(n.izq)
            if desde <= n.clave <= hasta:
                out.extend(n.valores)
            if n.clave < hasta:
                rec(n.der)
        rec(self.raiz)
        return out

    def buscar_rango(self, desde, hasta):
        """Misma interfaz que BST.buscar_rango (alias de rango)."""
        return self.rango(desde, hasta)

    def es_valido(self):
        """Verifica invariantes: orden BST, alturas y factor de balance."""
        def rec(n, lo, hi):
            if n is None:
                return True
            if (lo is not None and n.clave <= lo) or (hi is not None and n.clave >= hi):
                return False
            if n.altura != 1 + max(_alt(n.izq), _alt(n.der)):
                return False
            if abs(_factor(n)) > 1:
                return False
            return rec(n.izq, lo, n.clave) and rec(n.der, n.clave, hi)
        return rec(self.raiz, None, None)


class BST:
    """BST sin balancear (iterativo), solo para comparar con el AVL."""

    def __init__(self):
        self.raiz = None

    def insertar(self, clave, valor):
        nuevo = Nodo(clave, valor)
        if self.raiz is None:
            self.raiz = nuevo
            return
        n = self.raiz
        while True:
            if clave < n.clave:
                if n.izq is None:
                    n.izq = nuevo
                    return
                n = n.izq
            elif clave > n.clave:
                if n.der is None:
                    n.der = nuevo
                    return
                n = n.der
            else:
                n.valores.append(valor)
                return

    def altura(self):
        if self.raiz is None:
            return 0
        pila, h = [(self.raiz, 1)], 0
        while pila:
            n, d = pila.pop()
            h = max(h, d)
            if n.izq:
                pila.append((n.izq, d + 1))
            if n.der:
                pila.append((n.der, d + 1))
        return h
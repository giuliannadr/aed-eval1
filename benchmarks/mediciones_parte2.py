"""Mediciones Parte 2. Ejecutar: python3 medir.py  (semilla fija 42)."""
import random
import timeit
from genericos.avl import AVL, BST
from genericos.grafo import Grafo
from genericos.texto import fuerza_bruta, kmp


def t(f, rep=3):
    return min(timeit.repeat(f, number=1, repeat=rep)) * 1e6  # microsegundos


def construir(cls, claves):
    est = cls()
    for c in claves:
        est.insertar(c, c)
    return est


def exp_avl():
    print("\n== 1. AVL vs BST con timestamps ORDENADOS (como llegan los incidentes) ==")
    print(f"{'n':>7} {'alt BST':>8} {'alt AVL':>8} {'t BST (us)':>12} {'t AVL (us)':>12} {'rotaciones':>11}")
    for n in (500, 1000, 2000, 4000):
        claves = list(range(n))
        bst, avl = construir(BST, claves), construir(AVL, claves)
        print(f"{n:>7} {bst.altura():>8} {avl.altura():>8} "
              f"{t(lambda: construir(BST, claves)):>12.0f} {t(lambda: construir(AVL, claves)):>12.0f} {avl.rotaciones:>11}")
    claves = list(range(4000))
    avl = construir(AVL, claves)
    bst = construir(BST, claves)
    print("Busqueda de la clave 3999 con n=4000 (us): BST %.1f | AVL %.1f" % (
        t(lambda: _buscar_bst(bst, 3999)), t(lambda: avl.buscar(3999))))


def _buscar_bst(b, c):
    n = b.raiz
    while n:
        if c < n.clave:
            n = n.izq
        elif c > n.clave:
            n = n.der
        else:
            return n.valores
    return []


def exp_texto():
    print("\n== 2. Fuerza bruta vs KMP (comparaciones y tiempo) ==")
    print(f"{'caso':<14} {'n':>7} {'comp FB':>10} {'comp KMP':>10} {'t FB (us)':>11} {'t KMP (us)':>11}")
    casos = []
    for n in (10000, 20000, 40000):
        casos.append(("peor (a..ab)", "a" * n, "a" * 99 + "b"))
    rng = random.Random(42)
    for n in (10000, 20000, 40000):
        txt = "".join(rng.choice("abcdefgh") for _ in range(n))
        casos.append(("aleatorio", txt, "abcdefgh"))
    for nombre, txt, pat in casos:
        pf, cf = fuerza_bruta(txt, pat)
        pk, ck = kmp(txt, pat)
        assert pf == pk
        print(f"{nombre:<14} {len(txt):>7} {cf:>10} {ck:>10} "
              f"{t(lambda: fuerza_bruta(txt, pat)):>11.0f} {t(lambda: kmp(txt, pat)):>11.0f}")


def exp_grafo():
    print("\n== 3. Dijkstra y Prim/Kruskal al crecer el grafo (E = 5V) ==")
    print(f"{'V':>6} {'E':>7} {'Dijkstra us':>12} {'Kruskal us':>11} {'Prim us':>9} {'costo K':>9} {'costo P':>9}")
    for V in (500, 1000, 2000, 4000):
        rng = random.Random(42)
        g = Grafo(dirigido=False)
        for i in range(V):
            g.agregar_nodo(i)
        for i in range(1, V):  # garantiza conexo
            g.agregar_arista(i, rng.randrange(i), rng.randint(1, 100))
        for _ in range(4 * V):
            u, v = rng.randrange(V), rng.randrange(V)
            if u != v:
                g.agregar_arista(u, v, rng.randint(1, 100))
        E = len(g.aristas())
        ck = g.kruskal()[1]
        cp = g.prim()[1]
        assert ck == cp
        print(f"{V:>6} {E:>7} {t(lambda: g.dijkstra(0)):>12.0f} {t(g.kruskal):>11.0f} {t(g.prim):>9.0f} {ck:>9} {cp:>9}")


if __name__ == "__main__":
    exp_avl()
    exp_texto()
    exp_grafo()

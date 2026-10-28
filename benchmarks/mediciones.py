"""Mediciones empíricas reproducibles para el informe.

Ejecutar desde la raíz:  python -m benchmarks.mediciones

Genera un CSV por experimento en resultados/ e imprime cada tabla.
Los tamaños se duplican y la columna "cociente" es t(2n) / t(n):
~1 indica O(log n), ~2 O(n), algo más de 2 O(n log n) y ~4 O(n²).
Los tiempos absolutos dependen de la máquina: lo que se compara es
cómo crecen (M2 8.1). Semilla fija para que los datos sean siempre
los mismos.
"""

import csv
import random
import sys
import timeit
from collections import deque
from pathlib import Path

from datos.generador import generar_eventos
from dominio.event_store import EventStore
from genericos.bst import BST
from genericos.busqueda import (
    busqueda_binaria,
    busqueda_bisect,
    busqueda_secuencial,
)
from genericos.indice_ordenado import IndiceOrdenado
from genericos.ordenamiento import insercion, mergesort

RESULTADOS = Path(__file__).resolve().parent.parent / "resultados"
SEMILLA = 42


def medir(funcion, number=1, repeticiones=3):
    """Tiempo en microsegundos de una ejecución de funcion.

    Corre varias tandas con timeit y se queda con la mínima: es la
    medición menos afectada por otros procesos de la máquina.
    """
    mejor = min(timeit.repeat(funcion, repeat=repeticiones, number=number))
    return round(mejor / number * 1_000_000, 3)


def con_cocientes(filas):
    """Agrega a cada fila el cociente contra la fila anterior del mismo caso."""
    anterior = {}
    for fila in filas:
        previo = anterior.get(fila["caso"])
        fila["cociente"] = round(fila["tiempo_us"] / previo, 2) if previo else ""
        anterior[fila["caso"]] = fila["tiempo_us"]
    return filas


def guardar_y_mostrar(nombre, filas):
    """Guarda las filas en resultados/<nombre>.csv (M1 4.1.2) y las imprime."""
    RESULTADOS.mkdir(exist_ok=True)
    columnas = list(filas[0].keys())
    with open(RESULTADOS / f"{nombre}.csv", "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"\n=== {nombre} ===")
    print(" | ".join(columnas))
    for fila in filas:
        print(" | ".join(str(fila[c]) for c in columnas))


def exp_busqueda():
    """1. Secuencial vs binaria vs bisect, buscando una clave ausente (peor caso)."""
    filas = []
    for n in (100_000, 200_000, 400_000, 800_000):
        claves = list(range(0, 2 * n, 2))
        ausente = 2 * n + 1
        casos = (
            ("secuencial", busqueda_secuencial, 5),
            ("binaria", busqueda_binaria, 10_000),
            ("bisect", busqueda_bisect, 10_000),
        )
        for nombre, buscar, veces in casos:
            t = medir(lambda: buscar(claves, ausente), number=veces)
            filas.append({"n": n, "caso": nombre, "tiempo_us": t})
    return con_cocientes(filas)


def exp_ordenamiento():
    """2. Inserción vs mergesort vs sorted(), con los tres órdenes de datos.

    Cada ejecución recibe una copia (list(eventos)) por si alguna
    implementación ordenara en el lugar: copiar es O(n), igual para todos.
    """
    filas = []
    por_timestamp = lambda e: e.timestamp
    algoritmos = (
        ("insercion", insercion),
        ("mergesort", mergesort),
        ("sorted", lambda lista, key: sorted(lista, key=key)),
    )
    for orden in ("aleatorio", "ordenado", "invertido"):
        for n in (250, 500, 1000, 2000):
            eventos = generar_eventos(n, semilla=SEMILLA, orden=orden)
            for nombre, ordenar in algoritmos:
                t = medir(lambda: ordenar(list(eventos), key=por_timestamp))
                filas.append({"n": n, "caso": f"{nombre}-{orden}", "tiempo_us": t})
    return con_cocientes(filas)


def exp_memoria():
    """3. Memoria de la lista sola vs los índices.

    sys.getsizeof mide la estructura y sus referencias, no los eventos:
    todas las estructuras apuntan a los mismos objetos (son inmutables).
    """
    filas = []
    for n in (1_000, 10_000, 100_000):
        eventos = generar_eventos(n, semilla=SEMILLA)
        por_id = {e.id: e for e in eventos}
        por_categoria = {}
        for e in eventos:
            por_categoria.setdefault(e.category, []).append(e)
        bytes_categoria = sys.getsizeof(por_categoria) + sum(
            sys.getsizeof(lista) for lista in por_categoria.values()
        )
        filas.append({"n": n, "estructura": "lista (sin indice)",
                      "bytes": sys.getsizeof(list(eventos))})
        filas.append({"n": n, "estructura": "dict por id", "bytes": sys.getsizeof(por_id)})
        filas.append({"n": n, "estructura": "indice por categoria", "bytes": bytes_categoria})
    return filas


def exp_punto_de_cruce():
    """4. k búsquedas secuenciales vs ordenar una vez + k binarias."""
    filas = []
    n = 5_000
    rng = random.Random(SEMILLA)
    datos = [rng.randint(0, 10 * n) for _ in range(n)]
    for k in (1, 10, 100, 1_000):
        objetivos = [rng.randint(0, 10 * n) for _ in range(k)]

        def ordenar_y_buscar():
            ordenados = sorted(datos)
            return [busqueda_binaria(ordenados, x) for x in objetivos]

        t_sec = medir(lambda: [busqueda_secuencial(datos, x) for x in objetivos])
        t_bin = medir(ordenar_y_buscar)
        filas.append({"k": k, "caso": "k secuenciales", "tiempo_us": t_sec})
        filas.append({"k": k, "caso": "ordenar + k binarias", "tiempo_us": t_bin})
    return filas


def exp_indice_vs_recorrido():
    """5. Consulta con índice (dict / Index) vs recorrer la lista completa.

    El store se limita a 8.000 eventos porque cargar datos aleatorios en
    el IndiceOrdenado cuesta O(n) por inserción (hallazgo para el informe).
    """
    filas = []
    for n in (1_000, 2_000, 4_000, 8_000):
        eventos = generar_eventos(n, semilla=SEMILLA)
        store = EventStore()
        for e in eventos:
            store.agregar(e)
        objetivo = n // 2
        casos = (
            ("id-dict", lambda: store.buscar_por_id(objetivo), 10_000),
            ("id-secuencial",
             lambda: next((e for e in eventos if e.id == objetivo), None), 100),
            ("categoria-index", lambda: store.buscar_por_categoria("red"), 1_000),
            ("categoria-filtro",
             lambda: [e for e in eventos if e.category == "red"], 100),
        )
        for nombre, consulta, veces in casos:
            filas.append({"n": n, "caso": nombre,
                          "tiempo_us": medir(consulta, number=veces)})
    return con_cocientes(filas)


def exp_colas():
    """6. Vaciar n elementos: list.pop(0) (O(n) cada uno) vs deque.popleft() (O(1))."""
    filas = []
    for n in (10_000, 20_000, 40_000, 80_000):

        def vaciar_lista():
            lista = list(range(n))
            while lista:
                lista.pop(0)

        def vaciar_deque():
            cola = deque(range(n))
            while cola:
                cola.popleft()

        filas.append({"n": n, "caso": "list.pop(0)", "tiempo_us": medir(vaciar_lista)})
        filas.append({"n": n, "caso": "deque.popleft", "tiempo_us": medir(vaciar_deque)})
    return con_cocientes(filas)


def exp_bst():
    """7. Construir BST vs IndiceOrdenado con datos aleatorios y ordenados,
    y consulta por rango con cada uno. Con datos ordenados el BST se
    degenera (M3 2.1) y la lista solo agrega al final."""
    filas = []
    for n in (500, 1_000, 2_000, 4_000):
        for orden in ("aleatorio", "ordenado"):
            eventos = generar_eventos(n, semilla=SEMILLA, orden=orden)

            def construir_bst():
                arbol = BST()
                for e in eventos:
                    arbol.insertar(e.timestamp, e)
                return arbol

            def construir_lista():
                indice = IndiceOrdenado()
                for e in eventos:
                    indice.agregar(e.timestamp, e)
                return indice

            filas.append({"n": n, "caso": f"construir-BST-{orden}",
                          "tiempo_us": medir(construir_bst)})
            filas.append({"n": n, "caso": f"construir-lista-{orden}",
                          "tiempo_us": medir(construir_lista)})

        # Rango sobre las estructuras construidas con datos aleatorios
        aleatorios = generar_eventos(n, semilla=SEMILLA)
        arbol, indice = BST(), IndiceOrdenado()
        for e in aleatorios:
            arbol.insertar(e.timestamp, e)
            indice.agregar(e.timestamp, e)
        desde, hasta = 2 * n, 3 * n   # timestamps crecen ~5 por evento
        filas.append({"n": n, "caso": "rango-BST",
                      "tiempo_us": medir(lambda: arbol.buscar_rango(desde, hasta), number=100)})
        filas.append({"n": n, "caso": "rango-bisect",
                      "tiempo_us": medir(lambda: indice.buscar_rango(desde, hasta), number=100)})
    return con_cocientes(filas)


if __name__ == "__main__":
    print(f"Python {sys.version.split()[0]} | semilla {SEMILLA}")
    experimentos = (
        ("1_busqueda", exp_busqueda),
        ("2_ordenamiento", exp_ordenamiento),
        ("3_memoria", exp_memoria),
        ("4_punto_de_cruce", exp_punto_de_cruce),
        ("5_indice_vs_recorrido", exp_indice_vs_recorrido),
        ("6_colas", exp_colas),
        ("7_bst_vs_bisect", exp_bst),
    )
    for nombre, experimento in experimentos:
        guardar_y_mostrar(nombre, experimento())
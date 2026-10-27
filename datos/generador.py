"""Generador de eventos de prueba reproducibles.

Decisiones de diseño:
- 5 categorías y 8 nodos: pocas claves que se repiten mucho, como en datos reales.
- Textos: ~5% vacíos, ~20% con palabra de alerta, el resto normales.
- Timestamps: incremento aleatorio de 0 a 10, así ~1 de cada 11 se repite
  sin importar n. Permite probar el desempate del heap y la estabilidad.
- Las palabras de alerta se importan de dominio/ para que el generador y
  TextAnalyzer no se desincronicen.
"""

import random

from dominio.event import Event
from dominio.text_analyzer import PALABRAS_ALERTA

CATEGORIAS = ("red", "seguridad", "hardware", "software", "energia")
NODOS = ("A", "B", "C", "D", "E", "F", "G", "H")
FRASES_NORMALES = (
    "consulta de rutina",
    "mantenimiento programado",
    "reporte de uso",
    "actualización de configuración",
)
ORDENES_VALIDOS = ("aleatorio", "ordenado", "invertido")


def _generar_texto(rng):
    """Genera un texto: ~5% vacío, ~20% con palabra de alerta, resto normal."""
    r = rng.random()  # número entre 0 y 1
    if r < 0.05:
        return ""
    if r < 0.25:
        return f"{rng.choice(PALABRAS_ALERTA)} en el servicio"
    return rng.choice(FRASES_NORMALES)


def generar_eventos(n, semilla=42, orden="aleatorio"):
    """Genera n eventos pseudoaleatorios y reproducibles.

    Con la misma semilla devuelve siempre la misma lista.

    Args:
        n (int): cantidad de eventos a generar (0 devuelve lista vacía).
        semilla (int): semilla del generador aleatorio.
        orden (str): orden de la lista según timestamp:
            "aleatorio" (mezclada), "ordenado" (creciente)
            o "invertido" (decreciente).

    Returns:
        list[Event]: lista de n eventos. Los ids son únicos pero están
        mezclados, independientemente del orden elegido.

    Raises:
        TypeError: si n no es int.
        ValueError: si n es negativo u orden no es uno de los valores válidos.
    """
    if not isinstance(n, int):
        raise TypeError("n debe ser int")
    if n < 0:
        raise ValueError("n debe ser no negativo")
    if orden not in ORDENES_VALIDOS:
        raise ValueError(f"orden debe ser uno de {ORDENES_VALIDOS}, no '{orden}'")

    # Instancia propia en vez de random.seed() global: así ningún otro
    # código que use random puede alterar la secuencia.
    rng = random.Random(semilla)

    ids = list(range(n))
    rng.shuffle(ids)

    eventos = []
    timestamp = 0
    for i in range(n):
        # Incremento entre 0 y 10: cuando es 0 el timestamp se repite,
        # lo que permite probar el desempate del heap y la estabilidad.
        timestamp += rng.randint(0, 10)

        # sample elige sin repetición: origin y destination nunca son iguales
        origin, destination = rng.sample(NODOS, 2)

        # Argumentos con nombre: como category, text, origin y destination
        # son todos str, un error de orden pasaría las validaciones sin avisar.
        evento = Event(
            id=ids[i],
            timestamp=timestamp,
            category=rng.choice(CATEGORIAS),
            priority=rng.randint(1, 5),
            text=_generar_texto(rng),
            origin=origin,
            destination=destination,
        )
        eventos.append(evento)

    # Acá la lista ya está ordenada por timestamp (de menor a mayor).
    if orden == "aleatorio":
        rng.shuffle(eventos)
    elif orden == "invertido":
        eventos.reverse()
    # (si es "ordenado", no se hace nada)

    return eventos
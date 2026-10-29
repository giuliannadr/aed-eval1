"""Planificación de la atención de incidentes con un presupuesto de recursos."""

from genericos.dp import mochila_01


def seleccionar_incidentes(eventos, presupuesto, costo):
    """Elige qué incidentes atender para maximizar la gravedad total sin
    pasar el presupuesto (mochila 0/1 con programación dinámica).

    Cada incidente es un ítem: su valor es su prioridad (1-5) y su peso es
    lo que cuesta atenderlo, que define la función costo (mismo patrón
    key de la Parte 1: la estructura no conoce los campos del evento).
    Un incidente se atiende entero o no se atiende (0/1), por eso no sirve
    el criterio voraz "más grave primero": puede dejar presupuesto sin usar.

    Args:
        eventos: iterable de Event.
        presupuesto (int): recursos disponibles (ej. horas de técnicos), >= 0.
        costo: función Event -> int (> 0) con lo que cuesta atenderlo.

    Returns:
        (valor_total, lista de Event elegidos en el orden recibido).

    Costo: O(n · presupuesto) en tiempo y espacio (pseudo-polinomial).

    Raises:
        ValueError: si el presupuesto es negativo o algún costo no es un
            entero positivo.
    """
    if not isinstance(presupuesto, int) or presupuesto < 0:
        raise ValueError("presupuesto debe ser un entero no negativo")
    eventos = list(eventos)
    pesos = [costo(e) for e in eventos]
    for p in pesos:
        if not isinstance(p, int) or p <= 0:
            raise ValueError("el costo de cada incidente debe ser un entero positivo")
    valor, indices = mochila_01(pesos, [e.priority for e in eventos], presupuesto)
    return valor, [eventos[i] for i in indices]
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """Representa un incidente registrado por la organización.

    Es inmutable: un incidente es un registro histórico y no debe
    modificarse una vez creado (evita desordenar heaps e índices).

    Atributos:
        id (int): identificador del incidente (la unicidad la garantiza EventStore).
        timestamp (int): segundos desde el inicio del registro (no negativo).
        category (str): categoría del incidente (ej. "red", "seguridad").
        priority (int): prioridad del incidente (escala: 1 = menos grave,
            5 = más grave).
        text (str): descripción del incidente. Puede estar vacía; en ese
            caso TextAnalyzer no detecta alertas.
        origin (str): nodo de origen de la ruta (vértice del grafo del Router).
        destination (str): nodo de destino de la ruta (vértice del grafo del Router).
    """

    id: int
    timestamp: int
    category: str
    priority: int
    text: str
    origin: str
    destination: str

    def __post_init__(self):
        if not isinstance(self.id, int):
            raise TypeError("id debe ser int")

        # Se valida el tipo antes que el rango: si timestamp fuera un str,
        # la comparación "< 0" fallaría con un error poco claro.
        if not isinstance(self.timestamp, int):
            raise TypeError("timestamp debe ser int")
        if self.timestamp < 0:
            raise ValueError("timestamp debe ser no negativo")

        if not isinstance(self.priority, int):
            raise TypeError("priority debe ser int")
        if not 1 <= self.priority <= 5:
            raise ValueError("priority debe ser un número entre 1 y 5")

        # category, origin y destination se usan como claves del índice
        # y como nodos del grafo: deben ser texto, no vacío y sin espacios
        # en los costados (si no, "red" y "red " serían claves distintas).
        for nombre in ("category", "origin", "destination"):
            valor = getattr(self, nombre)
            if not isinstance(valor, str):
                raise TypeError(f"{nombre} debe ser str")
            if not valor.strip():
                raise ValueError(f"{nombre} no puede estar vacío")
            if valor != valor.strip():
                raise ValueError(f"{nombre} no puede tener espacios en los costados")

        # text puede estar vacío, pero tiene que ser str porque
        # TextAnalyzer lo va a recorrer.
        if not isinstance(self.text, str):
            raise TypeError("text debe ser str")
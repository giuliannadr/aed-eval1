"""Detección de alertas en el texto de los incidentes."""

from collections import Counter

# Palabras que indican un incidente de alerta. Las usa TextAnalyzer para
# detectar alertas y el generador para fabricar textos de prueba:
# al estar en un solo lugar, no se pueden desincronizar.
PALABRAS_ALERTA = ("caída", "falla", "urgente", "intrusión")


class TextAnalyzer:
    """Analiza textos de incidentes: detecta alertas y cuenta palabras.

    Las palabras de alerta se guardan en un frozenset: comprobar si una
    palabra pertenece cuesta O(1) promedio (M1 3.4), así que analizar un
    texto de m palabras cuesta O(m), sin importar cuántas alertas haya.

    Limitación: separa por espacios, así que no detecta una alerta pegada
    a un signo de puntuación (ej. "falla,").
    """

    def __init__(self, palabras_alerta=PALABRAS_ALERTA):
        self._alertas = frozenset(p.lower() for p in palabras_alerta)

    def es_alerta(self, texto):
        """True si el texto contiene alguna palabra de alerta. O(m)."""
        palabras = set(texto.lower().split())
        return not palabras.isdisjoint(self._alertas)   # ¿comparten algo?

    def filtrar_alertas(self, eventos):
        """Devuelve los eventos cuyo texto contiene una alerta. O(n·m)."""
        return [e for e in eventos if self.es_alerta(e.text)]

    def contar_palabras(self, eventos):
        """Frecuencia de cada palabra en todos los textos (bag of words,
        M3 3.12). Counter es un dict: cada actualización es O(1) promedio."""
        contador = Counter()
        for e in eventos:
            contador.update(e.text.lower().split())
        return contador
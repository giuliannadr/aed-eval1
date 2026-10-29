"""Detección de alertas en el texto de los incidentes."""

from collections import Counter

from genericos.texto import kmp

PALABRAS_ALERTA = ("caída", "falla", "urgente", "intrusión")


class TextAnalyzer:
    """Analiza textos de incidentes: detecta alertas y cuenta palabras.

    Las palabras de alerta se guardan en un frozenset: comprobar si una
    palabra pertenece cuesta O(1) promedio (M1 3.4), así que analizar un
    texto de m palabras cuesta O(m), sin importar cuántas alertas haya.

    Limitación: separa por espacios, así que no detecta una alerta pegada
    a un signo de puntuación (ej. "falla,").

    Parte 2: es_alerta_kmp busca las alertas como subcadenas con KMP, lo
    que sí detecta "falla," o "fallas", a costa de poder dar falsos
    positivos (ver docstring).
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

    def es_alerta_kmp(self, texto):
        """True si el texto contiene alguna alerta como SUBCADENA (KMP).

        Busca cada alerta con KMP: O(a·(n + m)) por texto (a alertas, n
        largo del texto, m largo de la alerta), sin retroceder en el texto.
        Diferencia con es_alerta: busca subcadenas, no palabras completas,
        así que detecta "falla," y "fallas" pero también "fallaron" o
        "sinfalla" (posibles falsos positivos).
        """
        minusculas = texto.lower()
        return any(kmp(minusculas, alerta)[0] for alerta in self._alertas if alerta)

    def filtrar_alertas_kmp(self, eventos):
        """Eventos cuyo texto contiene una alerta como subcadena (KMP)."""
        return [e for e in eventos if self.es_alerta_kmp(e.text)]
"""Estructuras lineales genéricas: cola FIFO y cola de prioridad."""

import heapq
from collections import deque
from itertools import count


class Cola:
    """Cola FIFO: el primero en entrar es el primero en salir.

    Implementada con collections.deque, que permite agregar al final y
    sacar del principio en O(1). Con una lista, sacar del principio
    (pop(0)) costaría O(n) porque desplaza todos los elementos (M2 4.4).
    Solo expone las operaciones del TDA cola (M2 2.1), así no se puede
    usar mal (por ejemplo, colar un elemento adelante).
    """

    def __init__(self):
        self._datos = deque()

    def encolar(self, valor):
        """Agrega un valor al final. O(1)."""
        self._datos.append(valor)

    def desencolar(self):
        """Saca y devuelve el primer valor. O(1).

        Raises:
            IndexError: si la cola está vacía.
        """
        if not self._datos:
            raise IndexError("desencolar de una cola vacía")
        return self._datos.popleft()

    def ver_siguiente(self):
        """Devuelve el primer valor sin sacarlo. O(1).

        Raises:
            IndexError: si la cola está vacía.
        """
        if not self._datos:
            raise IndexError("ver_siguiente de una cola vacía")
        return self._datos[0]

    def __len__(self):
        """Cantidad de elementos en la cola."""
        return len(self._datos)


class ColaPrioridad:
    """Cola de prioridad: siempre sale el valor con menor clave.

    Implementada con heapq (min-heap, M2 5.3). La clave la calcula una
    función recibida desde afuera, así la estructura no conoce el dominio.

    Internamente guarda tuplas (clave, contador, valor). El contador es
    un desempate final que crece con cada inserción: garantiza que
    Python nunca llegue a comparar dos valores entre sí y que, a igual
    clave, salga el que entró primero.

    Args:
        key (callable): función que recibe un valor y devuelve su clave
            de prioridad (menor clave = sale primero).
    """

    def __init__(self, key):
        self._key = key
        self._heap = []
        self._contador = count()  # genera 0, 1, 2, ... en cada next()

    def encolar(self, valor):
        """Agrega un valor. O(log n)."""
        entrada = (self._key(valor), next(self._contador), valor)
        heapq.heappush(self._heap, entrada)

    def desencolar(self):
        """Saca y devuelve el valor de menor clave. O(log n).

        Raises:
            IndexError: si la cola está vacía.
        """
        if not self._heap:
            raise IndexError("desencolar de una cola de prioridad vacía")
        return heapq.heappop(self._heap)[2]

    def ver_siguiente(self):
        """Devuelve el próximo valor sin sacarlo. O(1).

        Raises:
            IndexError: si la cola está vacía.
        """
        if not self._heap:
            raise IndexError("ver_siguiente de una cola de prioridad vacía")
        return self._heap[0][2]

    def __len__(self):
        """Cantidad de elementos en la cola."""
        return len(self._heap)
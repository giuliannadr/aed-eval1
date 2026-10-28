# Plataforma de análisis de incidentes y rutas

Evaluación integradora (parte 1) de Algoritmos y Estructura de Datos, UBP.
Sistema en Python que almacena, indexa, prioriza, busca y ordena incidentes,
con pruebas y mediciones reproducibles.

**Requisitos:** Python 3.13.13 Sin dependencias externas (solo biblioteca estándar).

## Comandos (desde la raíz del proyecto)

| Qué | Comando |
|---|---|
| Demo | `python main.py` |
| Tests | `python -m unittest discover tests` |
| Mediciones | `python -m benchmarks.mediciones` (genera los CSV en `resultados/`) |

## Estructura

- `dominio/`: clases que conocen el caso (Event, EventStore, Router, TextAnalyzer).
- `genericos/`: estructuras y algoritmos reutilizables, sin dependencia del dominio
  (Index, BST, IndiceOrdenado, colas, búsqueda, ordenamiento).
  `dominio/` usa `genericos/`, nunca al revés.
- `datos/`: generador de eventos de prueba reproducibles (semilla fija).
- `tests/`: pruebas con unittest.
- `benchmarks/`: mediciones con timeit.
- `resultados/`: CSV generados por las mediciones.
"""Demo del sistema de análisis de incidentes. Ejecutar: python main.py"""

from datos.generador import generar_eventos
from dominio.event import clave_atencion
from dominio.event_store import EventStore
from dominio.router import Router
from dominio.text_analyzer import TextAnalyzer
from genericos.estructuras import Cola, ColaPrioridad


def main():
    """Recorre el flujo completo: mesa de entrada, store, consultas,
    atención por prioridad, red de rutas y alertas."""
    # 1. Llegan incidentes en orden de tiempo a la mesa de entrada (FIFO)
    eventos = generar_eventos(30, semilla=42, orden="ordenado")
    mesa_de_entrada = Cola()
    for e in eventos:
        mesa_de_entrada.encolar(e)
    print(f"Mesa de entrada: {len(mesa_de_entrada)} incidentes en espera")

    # 2. Procesamiento: de la mesa al store y a la cola de atención
    store = EventStore()
    atencion = ColaPrioridad(key=clave_atencion)
    while len(mesa_de_entrada):
        e = mesa_de_entrada.desencolar()
        store.agregar(e)
        atencion.encolar(e)
    print(f"Store: {len(store)} incidentes registrados")

    # 3. Consultas
    print("\nIncidente con id 7:", store.buscar_por_id(7))
    print("Incidentes de categoría 'red':", len(store.buscar_por_categoria("red")))
    por_bst = store.buscar_por_rango(20, 60)
    por_bisect = store.buscar_por_rango_ordenado(20, 60)
    coinciden = sorted(e.id for e in por_bst) == sorted(e.id for e in por_bisect)
    print(f"Rango 20-60: BST {len(por_bst)} | bisect {len(por_bisect)} | coinciden: {coinciden}")

    # 4. Atención de los 5 más graves
    print("\nAtención de los 5 más graves:")
    for _ in range(5):
        e = atencion.desencolar()
        print(f"  prioridad {e.priority} | t={e.timestamp} | id {e.id} | {e.text or '(sin texto)'}")

    # 5. Red de rutas
    router = Router(store.todos())
    inicio = eventos[0].origin
    print(f"\nDistancias en saltos desde {inicio} (BFS):", router.distancias_bfs(inicio))
    print(f"Recorrido en profundidad desde {inicio} (DFS):", router.recorrido_dfs(inicio))

    # 6. Alertas en los textos
    analizador = TextAnalyzer()
    alertas = analizador.filtrar_alertas(store.todos())
    print(f"\nAlertas detectadas: {len(alertas)} de {len(store)}")
    print("Palabras más frecuentes:", analizador.contar_palabras(store.todos()).most_common(3))


if __name__ == "__main__":
    main()
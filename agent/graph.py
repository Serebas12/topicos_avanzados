from langgraph.graph import StateGraph, END
from agent.ai_graph_state import GraphState
from agent.nodes import GraphNodes

def GraphWorkflow(project_id: str):
    """
    Construye el grafo de procesamiento con dos nodos:
    búsqueda (RAG) y generación con Gemini.
    """
    # Inicializa clase contenedora de nodos
    graph_nodes = GraphNodes(project_id)

    # Crea el grafo declarando el tipo de estado
    workflow = StateGraph(GraphState)

    # Agrega nodos y conexiones
    workflow.add_node("search", graph_nodes.search_node)
    workflow.add_node("generate", graph_nodes.generate_node)

    # Define el flujo del grafo
    workflow.set_entry_point("search")
    workflow.add_edge("search", "generate")
    workflow.add_edge("generate", END)

    # Compila el grafo
    run_app = workflow.compile()

    return run_app

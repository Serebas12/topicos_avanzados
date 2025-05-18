from agent.graph import GraphWorkflow
from agent.ai_graph_state import GraphState
from langchain.schema import HumanMessage
from langfuse.callback import CallbackHandler


class IAInvoker:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.graph = GraphWorkflow(project_id)

        self.langfuse_handler = CallbackHandler(
            secret_key="sk-lf-56370169-c6ad-4385-81bf-f41bc51f6f0a",
            public_key="pk-lf-6a980f45-feca-4ee5-a230-6eaa2a0e5d07",
            host="https://us.cloud.langfuse.com"
        )

    def run(self, question: str, chat_history: list = None) -> str:
        """
        Ejecuta el grafo, permitiendo mantener historial conversacional.
        """
        # 1. Arma el historial acumulado: histórico + turno actual
        messages = (chat_history or []) + [HumanMessage(content=question)]

        # 2. Define el estado inicial del grafo
        initial_state: GraphState = {
            "question": question,
            "messages": messages,
            "documentos": [],
            "generation": ""
        }

        # 3. Invoca el grafo
        result = self.graph.invoke(
            initial_state,
            config={"callbacks": [self.langfuse_handler]}
        )

        # 4. Extrae la respuesta generada
        return result["generation"]

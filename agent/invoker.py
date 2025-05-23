# invoker.py

from agent.graph import GraphWorkflow
from agent.ai_graph_state import GraphState
from langchain.schema import HumanMessage
from langfuse.callback import CallbackHandler

class IAInvoker:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.graph = GraphWorkflow(project_id)
        # Guarda tus credenciales para poder reutilizarlas
        self._lf_secret = "sk-lf-56370169-c6ad-4385-81bf-f41bc51f6f0a"
        self._lf_public = "pk-lf-6a980f45-feca-4ee5-a230-6eaa2a0e5d07"
        self._lf_host   = "https://us.cloud.langfuse.com"

    def run(self, question: str, chat_history: list = None, session_id: str = None) -> str:
        # 1) Construye el historial de mensajes para LangGraph
        messages = (chat_history or []) + [HumanMessage(content=question)]

        initial_state: GraphState = {
            "question": question,
            "messages": messages,
            "documentos": [],
            "generation": ""
        }

        # 2) Crea un CallbackHandler CON session_id para agrupar la sesión
        langfuse_handler = CallbackHandler(
            secret_key=self._lf_secret,
            public_key=self._lf_public,
            host=self._lf_host,
            session_id=session_id      # ← aquí pasas el mismo session_id cada vez
        )

        # 3) Invoca el grafo con ese handler
        result = self.graph.invoke(
            initial_state,
            config={"callbacks": [langfuse_handler]}
        )

        # 4) Devuelve la generación del modelo
        return result["generation"]

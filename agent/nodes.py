# nodes.py

from langchain.schema import Document, SystemMessage, HumanMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

from utils.chat_utils import OpenSearchSearcher, VertexAILLM, PromptLoader
from agent.ai_graph_state import GraphState
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import SystemMessage, HumanMessage


class GraphNodes:
    def __init__(self, project_id: str):
        self.searcher = OpenSearchSearcher(project_id)
        self.llm = VertexAILLM(project=project_id).get_model()

    def search_node(self, state: GraphState) -> GraphState:
        question = state["question"]
        docs = self.searcher.buscar(question)
        return {
            **state,
            "documentos": docs
        }

    def generate_node(self, state: GraphState) -> GraphState:
        # Prompt compuesto con archivo externo y messages del grafo
        generate_prompt = ChatPromptTemplate.from_messages([
            ("system", PromptLoader.load_txt_prompt("prompts/prompt_generate.txt")),
            MessagesPlaceholder(variable_name="messages")
        ])

        # Extraer estado
        question = state["question"]
        documentos = state["documentos"]
        messages = state["messages"]

        # Ejecutar cadena: prompt -> llm -> output parser
        chain_generate = generate_prompt | self.llm | StrOutputParser()

        # Llamado al chain con el estado adecuado
        generation = chain_generate.invoke({
            "messages": messages,
            "context": documentos,
            "query": question
        })

        # Retornar nuevo estado actualizado
        return {
            **state,
            "generation": generation
        }





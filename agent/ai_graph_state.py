from typing import TypedDict, Annotated
from langchain.schema import Document
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    question: str
    messages: Annotated[list, add_messages]
    documentos: list[Document]
    generation: str

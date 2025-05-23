# app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from agent.invoker import IAInvoker
from typing import List, Dict
from langchain.schema import HumanMessage, AIMessage

app = FastAPI()

# Inicializa el invocador
invoker = IAInvoker(project_id="mestria-puj-s2")

# Modelo de solicitud
class QuestionRequest(BaseModel):
    question: str
    session_id: str
    history: List[Dict] = []



# Modelo de respuesta
class AnswerResponse(BaseModel):
    response: str

# Endpoint simple
@app.post("/ask", response_model=AnswerResponse)
def ask(req: QuestionRequest):
    messages = []
    for msg in req.history:
        if msg["type"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["type"] == "ai" or msg["type"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    response = invoker.run(req.question, chat_history=messages, session_id=req.session_id)
    return AnswerResponse(response=response)


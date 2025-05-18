# app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from agent.invoker import IAInvoker

app = FastAPI()

# Inicializa el invocador
invoker = IAInvoker(project_id="mestria-puj-s2")

# Modelo de solicitud
class QuestionRequest(BaseModel):
    question: str

# Modelo de respuesta
class AnswerResponse(BaseModel):
    response: str

# Endpoint simple
@app.post("/ask", response_model=AnswerResponse)
def ask(req: QuestionRequest):
    response = invoker.run(req.question)
    return AnswerResponse(response=response)

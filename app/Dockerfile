# Dockerfile dentro de /app

FROM python:3.10-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente del proyecto (relativo al contexto del build)
COPY ../app ./app
COPY ../agent ./agent
COPY ../utils ./utils
COPY ../prompts ./prompts

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

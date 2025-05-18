# llm_config.py

from langchain_google_vertexai import ChatVertexAI

class VertexAILLM:
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash-preview-04-17",
        temperature: float = 0.5,
        max_output_tokens: int = 500,
        project: str = "maestria-ia-puj",
        location: str = "global"
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.project = project
        self.location = location

        # Inicializa el modelo al crear la clase
        self.llm = ChatVertexAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            project=self.project,
            location=self.location,
        )

    def get_model(self):
        """Devuelve la instancia del modelo configurado"""
        return self.llm

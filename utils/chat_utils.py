# chat_utils.py

from langchain_google_vertexai import ChatVertexAI
from langchain.schema import Document
from vertexai.language_models import TextEmbeddingModel
from opensearchpy import OpenSearch
from google.cloud import aiplatform


# -------------------------------
# Clase para configurar Vertex AI LLM
# -------------------------------
class VertexAILLM:
    def __init__(
        self,
        project: str,
        model_name: str = "gemini-2.5-flash-preview-04-17",
        temperature: float = 0,
        max_output_tokens: int = 4000,
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


# -------------------------------
# Clase para buscar documentos en OpenSearch
# -------------------------------
class OpenSearchSearcher:
    def __init__(self, project_id: str, index_name: str = "topicosindex", top_k: int = 5):
        self.index_name = index_name
        self.top_k = top_k

        # Inicializa Vertex AI
        aiplatform.init(project=project_id, location="us-central1")
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")

        # Inicializa cliente OpenSearch
        self.client = OpenSearch(
            hosts=[{"host": "opensearch", "port": 9200}],
            http_auth=("admin", "Nagato123!"),
            use_ssl=True,
            verify_certs=False
        )

    def buscar(self, pregunta: str) -> list[Document]:
        # Obtener embedding
        embedding = self.embedding_model.get_embeddings([pregunta])[0].values

        # Construir consulta knn
        query = {
            "size": self.top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": embedding,
                        "k": self.top_k
                    }
                }
            }
        }

        # Ejecutar búsqueda
        respuesta = self.client.search(index=self.index_name, body=query)

        # Convertir a documentos LangChain
        documentos = []
        for hit in respuesta["hits"]["hits"]:
            doc = Document(
                page_content=hit["_source"]["text"],
                metadata={
                    "pagina": hit["_source"]["metadata"]["filename"]
                }
            )
            documentos.append(doc)

        return documentos

# -------------------------------
# Clase para cargar prompts desde archivos .txt
# -------------------------------
class PromptLoader:
    @staticmethod
    def load_txt_prompt(path: str) -> str:
        """
        Carga el contenido de un archivo .txt y lo retorna como string.
        
        Args:
            path (str): Ruta al archivo .txt
        
        Returns:
            str: Contenido del archivo
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo '{path}' no fue encontrado.")
        except Exception as e:
            raise RuntimeError(f"Error al leer el archivo '{path}': {e}")

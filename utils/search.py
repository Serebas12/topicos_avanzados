from langchain.schema import Document
from vertexai.language_models import TextEmbeddingModel
from opensearchpy import OpenSearch
from google.cloud import aiplatform

class OpenSearchSearcher:
    def __init__(self, project_id: str, index_name: str = "topicosindex", top_k: int = 3):
        self.index_name = index_name
        self.top_k = top_k

        # Inicializa Vertex AI
        aiplatform.init(project=project_id, location="us-central1")
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")

        # Inicializa cliente OpenSearch
        self.client = OpenSearch(
            hosts=[{"host": "localhost", "port": 9200}],
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
                    "titulo": hit["_source"]["metadata"]["title"],
                    "departamento": hit["_source"]["metadata"]["keyword"],
                    "id_documento": hit["_source"]["metadata"]["id_documento"],
                    "score": hit["_score"]
                }
            )
            documentos.append(doc)

        return documentos

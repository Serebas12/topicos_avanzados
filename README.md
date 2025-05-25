# Asistente Conversacional con RAG, LangGraph y Gemini 2.5 Flash

Este proyecto implementa un asistente conversacional especializado que combina técnicas de Recuperación de Información (RAG), arquitectura modular con **LangGraph**, el modelo **Gemini Flash 2.5** de Google Vertex AI, y trazabilidad completa con **Langfuse**. Además, incluye una API desarrollada en **FastAPI** y una interfaz de conversación construida en **Streamlit**.

---

## 📁 Estructura del Proyecto

```
TOPICOS_AVANZADOS/
├── agent/                  # Componentes del grafo LangGraph
│   ├── ai_graph_state.py
│   ├── graph.py
│   ├── invoker.py
│   └── nodes.py
├── app/                    # Backend FastAPI + Dockerfile
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── prompts/                # Archivos .txt utilizados como system prompts
│   └── prompt_generate.txt
├── utils/                  # Utilidades como Vertex AI y OpenSearch config
│   └── chat_utils.py
├── notebooks/              # Scripts exploratorios y de embeddings
│   ├── embedding.ipynb
│   └── probando.ipynb
├── app.py                  # Aplicación Streamlit (interfaz de usuario)
├── docker-compose.yaml     # Orquestación de FastAPI + OpenSearch
├── bulk_embeddings.json    # Archivo auxiliar de embeddings (carga masiva)
├── base_conocimiento_colombia.xlsx
└── README.md
```

---

## 🧠 Componentes Principales

### 1. **LangGraph con Gemini 2.5 Flash**
- Flujo modular con 2 nodos:
  - `search_node`: realiza búsqueda semántica en OpenSearch usando embeddings de Vertex AI.
  - `generate_node`: genera respuestas contextualizadas usando Gemini Flash 2.5.
- El grafo se compila con `graph.py` y se ejecuta desde `invoker.py`.

### 2. **OpenSearch como fuente documental**

El asistente utiliza OpenSearch como motor de búsqueda para implementar RAG (Retrieval-Augmented Generation). Los documentos se cargan con embeddings vectoriales y se consultan mediante búsquedas semánticas (`knn_vector`). A continuación se describe el proceso completo para preparar el entorno:

#### 🧱 Requisitos previos de sistema

Antes de desplegar OpenSearch, asegúrate de aumentar el límite de memoria de mapeo:

```bash
sudo sysctl -w vm.max_map_count=262144
```

#### 🚀 Despliegue del entorno (FastAPI + OpenSearch + Dashboards)

```bash
docker-compose up -d --build
```

Este comando levanta tres servicios:
- `opensearch` en `https://localhost:9200`
- `opensearch-dashboards` en `http://localhost:5601`
- `ia-assistant` en `http://localhost:8000`

> 🔒 Asegúrate de que los nombres de host en `chat_utils.py` usen `"opensearch"` (no `localhost`) al estar en contenedor.

#### 🏗️ Creación del índice para embeddings

Una vez levantado OpenSearch, se debe crear el índice `topicosindex` con soporte para búsqueda vectorial (KNN). Ejecuta el siguiente comando:

```bash
curl -X PUT "https://localhost:9200/topicosindex" \
  -k \
  -u admin:Nagato123! \
  -H 'Content-Type: application/json' \
  -d '{
    "settings": {
      "index": {
        "knn": true,
        "number_of_shards": 1,
        "number_of_replicas": 0
      }
    },
    "mappings": {
      "properties": {
        "embedding": {
          "type": "knn_vector",
          "dimension": 768
        },
        "metadata": {
          "type": "object",
          "properties": {
            "filename": {
              "type": "keyword"
            },
            "tags": {
              "type": "keyword"
            },
            "id_documento": {
              "type": "integer"
            },
            "keyword": {
              "type": "keyword"
            },
            "title": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            }
          }
        },
        "text": {
          "type": "text"
        }
      }
    }
  }'
```

#### 🧠 Generación del archivo con embeddings (`bulk_embeddings.json`)

1. Dirígete a la carpeta `notebooks/` del proyecto.
2. Abre y ejecuta el archivo `embedding.ipynb`.
3. El notebook toma información estructurada (por ejemplo, desde `base_conocimiento_colombia.xlsx`) y genera un archivo llamado `bulk_embeddings.json`, compatible con el formato de carga masiva de OpenSearch.

> 📝 Actualmente, este procesamiento aplica a datos tabulares. Se puede extender para formatos adicionales como `.txt`, `.pdf`, `.docx`, etc.

#### 📥 Carga masiva de documentos en OpenSearch

Una vez generado el archivo `bulk_embeddings.json`, puedes cargarlo directamente al índice creado:

```bash
curl -X POST "https://localhost:9200/topicosindex/_bulk" \
  -u admin:Nagato123! \
  -H "Content-Type: application/json" \
  --data-binary @embedding_manual.json \
  -k
```

---

### 3. **FastAPI para servir el asistente**
- Expuesto en el puerto `8000`.
- Endpoint POST `/ask` que recibe una pregunta y retorna la respuesta generada.
- Historial conversacional no se gestiona aquí (lo maneja Streamlit).

### 4. **Streamlit como interfaz de usuario**
- Título fijo: `Chatea con nuestro asesor interno`.
- Permite enviar mensajes y visualizar el historial.
- Botón `🗑️ Borrar conversación` que reinicia el historial e ID de sesión.
- Input de texto siempre en la parte inferior.
- Mensajes del usuario alineados a la derecha.
- Mensajes de la IA alineados a la izquierda.
- El historial se gestiona dentro del frontend y se mantiene por sesión.

### 5. **Langfuse para trazabilidad**
- Cada interacción con el modelo queda registrada.
- Se integró mediante `LangfuseCallbackHandler` en `invoker.py`.
- Las claves están quemadas directamente en el código por simplicidad.

---

## 🚀 Instrucciones de Uso

### 1. Posicionarte en el directorio raíz del proyecto

```bash
cd TOPICOS_AVANZADOS
```

### 2. Construir y levantar los servicios

```bash
docker-compose up --build
```

---

### 3. Ejecutar la interfaz en Streamlit

```bash
streamlit run app.py
```

---

## 🧪 Endpoint disponible

**POST /ask**

- **Input JSON:**
```json
{ "question": "¿Qué es el cambio climático?" }
```

- **Output JSON:**
```json
{ "response": "El cambio climático es..." }
```

---

## 📝 Notas finales

- Todos los prompts están cargados desde archivos `.txt` en `prompts/`, lo cual permite su modificación en tiempo real durante desarrollo.
- Las claves de Langfuse están quemadas directamente en `invoker.py`.
- La gestión del historial y la experiencia conversacional completa se maneja desde el frontend en Streamlit.

---

## 🛠️ Requisitos técnicos

- Docker y Docker Compose
- Python 3.10+
- Acceso habilitado a Vertex AI y al modelo `gemini-2.5-flash-preview-04-17`
- OpenSearch correctamente configurado localmente

---

## Exponer ngrok 

```bash
ngrok http --url=correct-bengal-whole.ngrok-free.app 8501
```


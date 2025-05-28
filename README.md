# Proyecto Tópicos avanzados en IA - Grupo 4

**Integrantes**

- **Julio César Roa Dávila**  
  <jcesarroa@javeriana.edu.co>

- **Jair Sebastián Saavedra Alvarado**  
  <saavedra.jairs@javeriana.edu.co>

## Visión general y arquitectura del asistente de consultas del Reglamento Estudiantil PUJ

Este proyecto implementa un **asistente de inteligencia artificial** cuyo propósito es facilitar a los estudiantes de la **Pontificia Universidad Javeriana** la consulta ágil y precisa del **Reglamento Estudiantil**.  

La solución se diseñó y desplegó **íntegramente en Google Cloud Platform (GCP)**, aprovechando los servicios incluidos en la capa gratuita. Para habilitar respuestas contextuales, se construyó una **base de conocimiento** donde **cada página del reglamento** se trata como un documento independiente. Esa granularidad permite aplicar la técnica de **Retrieval-Augmented Generation (RAG)**, garantizando que el asistente recupere los fragmentos relevantes del reglamento y genere respuestas fundamentadas en el texto oficial. Adicionalmente, para el desarrollo del proyecto se utilizo la siguiente arquitectura:


<div align="center">
  <img src="images/arquitectura_poc.png" alt="streamlit" width="1000"/>
</div>


| # | Componente | Descripción |
|---|------------|-------------|
| 1 | **Generación de embeddings** | 1. El PDF del Reglamento se **divide por páginas** y cada página se transforma a imagen.<br>2. Sobre cada imagen se ejecuta **Gemini 2.5 Flash (multimodal)** para extraer el texto con alta fidelidad.<br>3. El texto se normaliza y se genera la representación vectorial con el modelo **`text-multilingual-embedding-002`** de Vertex AI (768 dim).<br>4. Todo el proceso se orquesta desde un **Notebook** alojado en la misma VM y al final se produce un archivo `embedding_manual.json`. |
| 2 | **Base de conocimiento (OpenSearch)** | - Se despliega **OpenSearch** en un contenedor dentro de la VM.<br>- Se crea el índice `topicosindex` con soporte **KNN** y dimensión **768**.<br>- El archivo `embedding_manual.json` se carga vía API `_bulk`, quedando cada página del reglamento como un documento con su vector. |
| 3 | **Asistente (LangChain + LangGraph + FastAPI)** | - Implementado con **LangGraph**: dos nodos.<br>  • `search_node` → recupera los `k` documentos más relevantes desde OpenSearch.<br>  • `generate_node` → construye el mensaje de sistema y llama a **Gemini 2.5 Pro** para redactar la respuesta.<br>- Se eligió Gemini 2.5 Pro porque está en *preview* (sin coste) y ofrece mayor capacidad de razonamiento.<br>- El grafo se expone a través de un **backend FastAPI** (endpoint `POST /ask`).<br>- Todo el stack (FastAPI, OpenSearch y Dashboards) se **orquesta mediante `docker-compose.yaml`**, facilitando la puesta en marcha con un solo comando. |
| 4 | **Frontend (Streamlit + ngrok)** | - Streamlit expone una interfaz chat que:<br>  • Mantiene el historial de la conversación.<br>  • Permite reiniciar sesión.<br>- Para compartir la app públicamente sin exponer puertos se usa **ngrok**, que crea un túnel HTTPS temporal hacia la instancia de Streamlit. |
| 5 | **Observabilidad (Langfuse)** | - **Langfuse** registra cada conversación de principio a fin bajo un mismo **ID de sesión**, de forma que todas las preguntas y respuestas quedan agrupadas.<br>- En su panel se pueden ver métricas como tiempo de respuesta, uso de tokens y los pasos internos que siguió el asistente, lo que facilita el seguimiento y la mejora continua. |

> **Todo el stack corre en una única VM de Compute Engine** (entorno de desarrollo/experimentación) aprovechando la capa gratuita de Google Cloud Platform.


## Estructura del repositorio y guía de ejecución

El código se gestiona en **GitHub**, garantizando buenas prácticas de control de versiones y colaboración. A continuación se detalla la estructura del repositorio:


### 📂 Estructura del repositorio
```
TOPICOS_AVANZADOS/
├── agent/                  # Lógica del asistente y del grafo LangGraph
│ ├── ai_graph_state.py     # Definición del estado que circula por el grafo
│ ├── graph.py              # Construcción del grafo (nodos y conexiones)
│ ├── invoker.py            # Clase que invoca el grafo y gestiona Langfuse
│ └── nodes.py              # Implementación de los nodos (search / generate)
│
├── app/ # Backend FastAPI + Dockerfile
│ ├── Dockerfile            # Imagen para FastAPI + dependencias
│ ├── main.py               # Endpoints (POST /ask)
│ └── requirements.txt      # Librerías Python para FastAPI
│
├── embeddings/             # Insumos y notebook para generar embeddings
│ ├── Proceso_embeddings.ipynb
│ ├── reglamento-de-estudiantes-universidad-javeriana.pdf
│ └── imagenes/             # Páginas del PDF rasterizadas
│
├── images/                 # Recursos gráficos (diagramas, etc.)
│
├── prompts/                # Prompts del sistema en texto plano
│ └── prompt_generate.txt
│
├── utils/
│ └── chat_utils.py         # Clase VertexAILLM, OpenSearchSearcher, etc.
│
├── app.py                  # Frontend Streamlit
├── docker-compose.yaml     # Orquestación (FastAPI + OpenSearch + Dashboards)
├── embedding_manual.json   # Ejemplo de carga masiva en formato bulk
└── README.md
```

A continuación se detallan los requisitos previos y los pasos necesarios para desplegar el asistente en un entorno local o de laboratorio.

| Requisito / Herramienta | Detalle o versión mínima recomendada |
|-------------------------|--------------------------------------|
| **Cuenta de Google Cloud** | Proyecto activo con acceso a **Vertex AI** (modelos Gemini 2.5 Pro/Flash y Vector Search). |
| **Cuenta de Langfuse**  | Espacio de trabajo (public / secret keys) para registrar las trazas de la aplicación. |
| **Docker**             | 24.x |
| **Docker Compose**     | 1.29.x |
| **Python** *(opcional)* | 3.10 + <br><sub>Solo necesario si se ejecutarán los notebooks o Streamlit fuera de contenedor.</sub> |

Una vez cubiertos estos prerrequisitos, puede procederse al despliegue del asistente virtual.


1. Antes de iniciar OpenSearch es necesario ampliar el límite de memoria de mapeo:

```bash
sudo sysctl -w vm.max_map_count=262144
```

2. Desde la raíz del repositorio, ejecute el siguiente comando para **construir e iniciar** todos los servicios (OpenSearch, Dashboards y FastAPI) mediante Docker Compose:

```bash
docker-compose up --build -d
```

Una vez finalizado, los servicios estarán disponibles en:

- **OpenSearch**: https://localhost:9200  
- **OpenSearch Dashboards**: http://localhost:5601  
- **FastAPI (asistente)**: http://localhost:8000/docs



3. Con OpenSearch en ejecución, cree el índice **`topicosindex`** con soporte para búsqueda vectorial (KNN) ejecutando:

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


4. Una vez generado el archivo `embedding_manual.json`, se puede importar directamente en el índice `topicosindex` usando la API Bulk de OpenSearch:

```bash
curl -X POST "https://localhost:9200/topicosindex/_bulk" \
  -u admin:Nagato123! \
  -H "Content-Type: application/json" \
  --data-binary @embedding_manual.json \
  -k
```

> **Nota:** Para actualizar o modificar la base de conocimiento, basta con ejecutar nuevamente el notebook `embeddings/Proceso_embeddings.ipynb` y repetir los pasos de generación y carga de embeddings.


5. Para lanzar la aplicación de Streamlit y comenzar a interactuar con el asistente, ejecute:

```bash
streamlit run app.py
```

6. Para habilitar el acceso desde un dominio distinto a `localhost`, puede emplearse ngrok con el siguiente comando:

```bash
ngrok http --url=<domain> 8501
```

> **Nota:** Sustituir `<domain>` por el subdominio asignado a la cuenta de ngrok en uso.


## Consideraciones

El despliegue descrito corresponde a un **entorno de desarrollo (Proof of Concept)**. Antes de llevar la solución a producción, se recomienda que usted tenga en cuenta los siguientes aspectos:

1. **Infraestructura limitada y no escalable**  
   Al ejecutarse en una única instancia de Compute Engine, la arquitectura carece de alta disponibilidad y elasticidad. Ante picos de carga, el servicio podría experimentar latencias elevadas o interrupciones.

2. **Cuenta de prueba de Google Cloud**  
   La PoC utiliza la capa gratuita de GCP. Para un entorno productivo se requiere una suscripción que cubra los recursos consumidos y el acceso a servicios gestionados (Vertex AI, Cloud Logging, etc.).

3. **Modelos en modo *preview***  
   Gemini 2.5 Pro se emplea en modalidad *preview* — útil para experimentación, pero no recomendado en producción debido a límites de uso y ausencia de SLA. Debería sustituirse por un modelo estable y con soporte.

4. **Cobertura de pruebas**  
   El prototipo no incluye pruebas unitarias, de integración ni de carga. Antes de la liberación se deben incorporar suites de pruebas alineadas con las políticas de calidad de la organización.

5. **Políticas de seguridad y protección de datos**  
   Si la información consultada es sensible, resulta obligatorio aplicar controles de seguridad (cifrado en reposo y en tránsito, control de acceso, registro de auditoría, etc.) conforme a la normativa interna de la entidad.

6. **Observabilidad ampliada**  
   Langfuse ofrece trazabilidad a nivel de aplicación; sin embargo, para operación continua se aconseja integrar métricas de infraestructura (CPU, memoria, I/O) y alertas en un sistema de monitoreo centralizado (Cloud Monitoring, Prometheus, etc.).

Estas consideraciones deben evaluarse y ajustarse de acuerdo con los estándares de Gobierno de TI vigentes en su organización.

## Propuesta de arquitectura productiva en Google Cloud Platform

Con el fin de llevar la solución a un entorno productivo, se recomienda la arquitectura ilustrada en el diagrama precedente. Esta propuesta amplía la PoC y añade robustez, escalabilidad y buenas prácticas de gobernanza:

<div align="center">
  <img src="images/arquitectura_prod.png" alt="streamlit" width="1000"/>
</div>


1. **Automatización de embeddings y actualización de la base vectorial**  
   - Los archivos fuente se cargan en **Cloud Storage**.  
   - Un mensaje de **Pub/Sub** actúa como disparador para **Cloud Run (Embeddings)**, servicio que:  
     1. Extrae el texto con **Gemini 2.5 Flash** (multimodal).  
     2. Genera embeddings mediante **`text-multilingual-embedding-002`**.  
     3. Actualiza la colección en **Vertex AI Vector Search**.  

2. **Consumo del asistente**  
   - La interfaz de usuario se implementa en **Apps Script**, facilitando la integración con entornos Google Workspace.  
   - Apps Script invoca un **Cloud Run (Backend)** que contiene la lógica del asistente (LangGraph + FastAPI).  
   - El backend consulta la base vectorial, genera la respuesta con **Gemini 2.5 Pro** y registra la traza en **Langfuse**.

3. **Analítica y mejora continua**  
   - Las trazas almacenadas en Langfuse se exportan de forma periódica mediante un **Cloud Run (ELT)** hacia **BigQuery**.  
   - Los equipos de datos pueden explotar esta información para obtener métricas de uso, tiempos de respuesta y oportunidades de optimización.

4. **Gobernanza y operaciones transversales**  
   - **GitHub** aloja el código fuente, permitiendo CI/CD y revisión de cambios.  
   - Los artefactos de contenedor se publican en **Artifact Registry**.  
   - Los permisos de servicio y el acceso a los recursos se gestionan con **IAM**, garantizando principios de mínimo privilegio.

Esta arquitectura proporciona escalabilidad automática, alta disponibilidad y un flujo continuo de observabilidad y analítica, cumpliendo con los estándares empresariales para una puesta en producción segura y mantenible.

> **Nota:** La arquitectura propuesta debe evaluarse y ajustarse por cada equipo que desee adoptarla, de modo que quede alineada con las políticas internas de la organización. Entre los puntos que suelen revisarse se incluyen:  
> 1. **Seguridad** – definición de autenticación/ autorización para las API y cifrado de datos en reposo y en tránsito conforme a los requisitos corporativos.  
> 2. **Infraestructura como código (IaC)** – uso de herramientas como Terraform para garantizar despliegues reproducibles y auditables.  
> 3. **Cuotas y alertamiento** – establecimiento de límites de consumo y notificaciones cuando se alcancen umbrales, especialmente si existe un presupuesto fijo asignado al proyecto o a los servicios en la nube.

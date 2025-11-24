# 📁 Estructura Final del Proyecto - v3.0

## Directorio Raíz

```
agente/
│
├── 📄 README.md                    # Documentación principal (v3.0)
├── 📄 requirements.txt             # Dependencias Python (simplificadas)
├── 📄 .env                         # Variables de entorno (OPENROUTER_API_KEY)
├── 📄 .gitignore                   # Archivos ignorados
│
├── 📂 api/
│   └── main.py                     # FastAPI - Endpoints REST (v3.0)
│
├── 📂 core/                        # ⭐ MÓDULOS PRINCIPALES (4 archivos)
│   ├── analyzer.py                 # Análisis estático básico
│   ├── knowledge_graph.py          # Grafo + análisis de dependencias
│   ├── semantic_reasoner.py        # Razonamiento con IA (OpenRouter)
│   └── diagram_generator.py        # Generación de diagramas Mermaid
│
├── 📂 examples/
│   └── test_simple.py              # Ejemplo de uso del sistema
│
├── 📂 utils/
│   └── zip_utils.py                # Utilidades para manejo de archivos ZIP
│
├── 📂 uploads/                     # Proyectos subidos (ignorado en git)
│
└── 📂 docs/                        # Documentación adicional
    ├── ARCHITECTURE.md             # Arquitectura del sistema
    ├── QUICKSTART.md               # Guía rápida
    ├── INSTALL.md                  # Instalación detallada
    ├── CHANGELOG.md                # Historial de versiones
    ├── SUMMARY.md                  # Resumen del proyecto
    ├── REFACTORING_SUMMARY.md      # Resumen de cambios v3.0
    ├── RESULTADO_FINAL.md          # Estado final del sistema
    ├── RESPUESTA_FINAL.md          # Documentación final
    ├── TEST_C4_DIAGRAMS.md         # Tests de diagramas C4
    └── README.old.md               # README anterior (backup)
```

## 🎯 Módulos Core (Detalle)

### 1. `analyzer.py` - Análisis Estático Básico
```python
# Funciones principales:
- analyze_project(zip_path: str) -> dict
- detect_actors(analysis: dict) -> list
- _extract_zip(zip_path: str) -> str
- _detect_project_type(path: str) -> str
- _extract_containers(project_path: str) -> list
- _extract_components(container_path: str) -> list
- _extract_dependencies(component_path: str) -> list
```

**Responsabilidades:**
- Extracción de archivos ZIP
- Detección de tipo de proyecto (Python, Node.js, Java, etc.)
- Identificación de contenedores (módulos, packages)
- Identificación de componentes (clases, funciones)
- Detección de actores (usuarios, sistemas externos)
- Análisis de dependencias básicas

### 2. `knowledge_graph.py` - Grafo de Conocimiento
```python
# Clase principal:
class KnowledgeGraph:
    # Construcción
    - add_node(node_id, node_type, **attrs)
    - add_component(name, container, comp_type, **attrs)
    - add_module(name, **attrs)
    - add_class(name, module, **attrs)
    - add_function(name, module, **attrs)
    
    # Relaciones
    - add_dependency(from_node, to_node, dep_type, **attrs)
    - add_call(caller, callee, **attrs)
    - add_inheritance(child, parent, **attrs)
    
    # Análisis
    - calculate_metrics() -> dict
    - detect_cycles() -> list
    - find_critical_nodes(top_n: int) -> list
    - find_bottlenecks() -> list
    - calculate_layer_depth() -> dict
    - analyze_dependencies() -> dict  # ⭐ NUEVO v3.0
    
    # Visualización
    - visualize_stats() -> str
    - export_to_json() -> dict

# Funciones de construcción:
- build_knowledge_graph_from_analysis(analysis: dict) -> KnowledgeGraph
- enhance_graph_with_code_analysis(kg, analysis) -> KnowledgeGraph  # ⭐ NUEVO v3.0
```

**Responsabilidades:**
- Representación del proyecto como grafo dirigido (NetworkX)
- Almacenamiento de nodos (módulos, clases, funciones, etc.)
- Almacenamiento de aristas (dependencias, llamadas, herencia)
- Cálculo de métricas (centralidad, complejidad, etc.)
- Detección de ciclos de dependencias
- Análisis de acoplamiento y cohesión ⭐ NUEVO
- Generación de recomendaciones ⭐ NUEVO
- Enriquecimiento con análisis de código (regex) ⭐ NUEVO

### 3. `semantic_reasoner.py` - Razonamiento con IA
```python
# Función principal:
- generate_semantic_mermaid_openrouter(
    analysis_result: dict,
    actors: list,
    diagram_level: str = "C2"
  ) -> str
```

**Responsabilidades:**
- Generación de prompts contextualizados
- Llamadas a API de OpenRouter (LLM)
- Generación de diagramas C1, C2, C3 con IA
- Post-procesamiento de respuestas
- Validación de formato Mermaid

### 4. `diagram_generator.py` - Generación de Diagramas
```python
# Funciones principales:
- generate_mermaid_c2(analysis: dict) -> str
- generate_mermaid_from_graph(kg: KnowledgeGraph, diagram_type: str) -> str
- generate_component_diagram(kg: KnowledgeGraph) -> str
- generate_dependency_graph(kg: KnowledgeGraph) -> str
- generate_class_diagram(kg: KnowledgeGraph) -> str
- generate_sequence_diagram(kg: KnowledgeGraph, scenario: str) -> str
- generate_dependency_matrix(kg: KnowledgeGraph) -> dict
- generate_metrics_visualization(metrics: dict) -> str
```

**Responsabilidades:**
- Generación de diagramas Mermaid determinísticos (sin IA)
- Diagrama C2 de contenedores
- Diagrama de componentes
- Grafo de dependencias
- Diagrama de clases
- Diagrama de secuencia
- Matriz de dependencias
- Visualización de métricas

## 📡 API Endpoints

### GET `/`
- **Descripción**: Información del sistema
- **Respuesta**: Versión, endpoints disponibles

### GET `/health`
- **Descripción**: Estado del servicio
- **Respuesta**: `{"status": "healthy"}`

### GET `/docs`
- **Descripción**: Documentación interactiva (Swagger UI)
- **Respuesta**: Interfaz web interactiva

### POST `/analyze`
- **Input**: Archivo ZIP del proyecto
- **Salida**: Análisis completo + Diagramas C1/C2/C3 con IA
- **Uso**: Análisis estándar con razonamiento semántico

### POST `/analyze/advanced`
- **Input**: Archivo ZIP del proyecto
- **Query Params**: `diagram_type` (architecture, dependencies, components, classes)
- **Salida**: Análisis de grafo + Métricas + Diagramas
- **Uso**: Análisis profundo con grafo de conocimiento

### POST `/analyze/dependencies`
- **Input**: Archivo ZIP del proyecto
- **Salida**: Análisis de dependencias + Ciclos + Recomendaciones
- **Uso**: Enfoque en problemas arquitectónicos

### POST `/analyze/metrics`
- **Input**: Archivo ZIP del proyecto
- **Salida**: Métricas de calidad + Nodos críticos + Cuellos de botella
- **Uso**: Evaluación de calidad del código

## 📦 Dependencias

### Esenciales (requirements.txt)
```txt
fastapi              # Framework web REST
uvicorn              # Servidor ASGI
pydantic             # Validación de datos
python-multipart     # Manejo de uploads
python-dotenv        # Variables de entorno
requests             # Cliente HTTP para IA

networkx>=3.0        # Análisis de grafos
matplotlib           # Visualización (opcional)
```

### Variables de Entorno (.env)
```bash
OPENROUTER_API_KEY=tu_api_key_aqui  # Opcional, solo para IA
```

## 🧪 Uso del Sistema

### 1. Desde Python
```python
from core.analyzer import analyze_project
from core.knowledge_graph import build_knowledge_graph_from_analysis, enhance_graph_with_code_analysis

# Analizar proyecto
result = analyze_project("proyecto.zip")

# Construir grafo
kg = build_knowledge_graph_from_analysis(result)
kg = enhance_graph_with_code_analysis(kg, result)

# Obtener métricas
metrics = kg.calculate_metrics()
cycles = kg.detect_cycles()
dep_analysis = kg.analyze_dependencies()

print(kg.visualize_stats())
```

### 2. Desde API REST
```bash
# PowerShell
curl -X POST "http://localhost:8000/analyze" -F "file=@proyecto.zip"

# Python requests
import requests
with open("proyecto.zip", "rb") as f:
    response = requests.post("http://localhost:8000/analyze", files={"file": f})
    print(response.json())
```

### 3. Interfaz Web
```
http://localhost:8000/docs
```

## 📊 Salida del Sistema

### Análisis Básico (`/analyze`)
```json
{
  "actors_detected": ["Usuario", "Sistema Externo"],
  "result": {
    "project_name": "mi-proyecto",
    "project_type": "python",
    "total_files": 42,
    "containers": [...],
    "components": [...]
  },
  "mermaid_c2": "graph TD...",
  "semantic_c1": "C4Context...",
  "semantic_c2": "C4Container...",
  "semantic_c3": "C4Component..."
}
```

### Análisis Avanzado (`/analyze/advanced`)
```json
{
  "project_info": {...},
  "graph_metrics": {
    "total_nodes": 125,
    "total_edges": 203,
    "avg_dependencies": 1.62
  },
  "dependency_analysis": {
    "cycles": {"total_cycles": 2, "severity": "low"},
    "coupling": {...},
    "cohesion": {...},
    "recommendations": [...]
  },
  "diagrams": {
    "mermaid": "graph TD...",
    "dependency_matrix": {...}
  }
}
```

## 🔄 Flujo de Datos

```
1. Usuario → Upload ZIP
2. analyzer.py → Análisis estático básico
3. knowledge_graph.py → Construcción del grafo
4. enhance_graph_with_code_analysis → Análisis de código (regex)
5. analyze_dependencies → Métricas + Recomendaciones
6. diagram_generator.py → Generación de diagramas
7. semantic_reasoner.py → Diagramas con IA (opcional)
8. API → Respuesta JSON
```

## ✅ Estado Actual

- ✅ 4 módulos core implementados
- ✅ 6 endpoints API funcionales
- ✅ Documentación completa
- ✅ Ejemplo de uso disponible
- ✅ Servidor corriendo en http://localhost:8000
- ✅ Sin dependencias externas complejas
- ✅ Sistema académicamente sólido

---

**Versión**: 3.0.0  
**Última actualización**: 2025-11-13  
**Estado**: ✅ Funcionando

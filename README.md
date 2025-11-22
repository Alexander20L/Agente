# 🤖 Agente Inteligente C4 - Sistema de Análisis de Código

Sistema académico y modular para análisis estático de proyectos con generación de diagramas C4 usando IA.

## 📋 Arquitectura del Sistema

### Módulos Core (4 archivos principales)

```
core/
├── analyzer.py          # Análisis estático básico + detección de actores
├── knowledge_graph.py   # Grafo de conocimiento + análisis de dependencias
├── semantic_reasoner.py # Razonamiento con IA (OpenRouter)
└── diagram_generator.py # Generación de diagramas Mermaid
```

### ✨ Características

- ✅ **Análisis estático**: Detección de contenedores, componentes y dependencias
- ✅ **Grafo de conocimiento**: Representación NetworkX con métricas avanzadas
- ✅ **Detección de ciclos**: Identificación de dependencias circulares
- ✅ **Métricas de calidad**: Acoplamiento, cohesión, complejidad ciclomática
- ✅ **Recomendaciones**: Sugerencias automáticas basadas en análisis
- ✅ **Diagramas C4**: Generación con IA (C1, C2, C3) en formato Mermaid
- ✅ **API REST**: FastAPI con múltiples endpoints

## 🚀 Instalación Rápida

```powershell
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar API key (opcional, para IA)
echo "OPENROUTER_API_KEY=tu_api_key" > .env

# 3. Iniciar servidor
uvicorn api.main:app --reload
```

## 📡 Endpoints API

### `/analyze` - Análisis Completo con IA
```bash
POST http://localhost:8000/analyze
```
- Análisis estático básico
- Detección de actores
- Diagramas C1, C2, C3 con IA (OpenRouter)

### `/analyze/advanced` - Análisis Avanzado con Grafo
```bash
POST http://localhost:8000/analyze/advanced
```
- Grafo de conocimiento completo
- Análisis de código con regex
- Métricas avanzadas
- Diagramas desde el grafo

### `/analyze/dependencies` - Análisis de Dependencias
```bash
POST http://localhost:8000/analyze/dependencies
```
- Detección de ciclos
- Métricas de acoplamiento
- Recomendaciones arquitectónicas

### `/analyze/metrics` - Métricas de Calidad
```bash
POST http://localhost:8000/analyze/metrics
```
- Complejidad ciclomática
- Nodos críticos
- Cuellos de botella

## 🧪 Ejemplo de Uso

```python
from core.analyzer import analyze_project
from core.knowledge_graph import build_knowledge_graph_from_analysis, enhance_graph_with_code_analysis

# 1. Análisis básico
result = analyze_project("proyecto.zip")

# 2. Construir grafo
kg = build_knowledge_graph_from_analysis(result)

# 3. Enriquecer con análisis de código
kg = enhance_graph_with_code_analysis(kg, result)

# 4. Obtener métricas
metrics = kg.calculate_metrics()
cycles = kg.detect_cycles()
dep_analysis = kg.analyze_dependencies()

print(kg.visualize_stats())
```

Ver `examples/test_simple.py` para ejemplo completo.

## 📊 Diagramas Soportados

- **C1 (Context)**: Sistema en su contexto con actores externos
- **C2 (Container)**: Arquitectura de contenedores (web, API, DB)
- **C3 (Component)**: Componentes internos por contenedor
- **Dependency Graph**: Grafo de dependencias completo
- **Component Diagram**: Vista de componentes del sistema
- **Class Diagram**: Diagrama de clases extraído del código

## 🔧 Dependencias

### Esenciales
- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `networkx` - Análisis de grafos
- `requests` - Cliente HTTP para IA

### Opcionales
- `matplotlib` - Visualización de métricas
- Variable de entorno `OPENROUTER_API_KEY` para diagramas con IA

## 📁 Estructura de Proyecto

```
agente/
├── api/
│   └── main.py              # FastAPI endpoints
├── core/
│   ├── analyzer.py          # Análisis estático
│   ├── knowledge_graph.py   # Grafo + análisis dependencias
│   ├── semantic_reasoner.py # Razonamiento IA
│   └── diagram_generator.py # Generación de diagramas
├── examples/
│   └── test_simple.py       # Ejemplo de uso
├── uploads/                 # Proyectos analizados
├── requirements.txt         # Dependencias Python
└── README.md               # Este archivo
```

## 🧠 Flujo de Análisis

1. **Upload** → Usuario sube archivo `.zip`
2. **Static Analysis** → `analyzer.py` extrae estructura
3. **Graph Building** → `knowledge_graph.py` construye grafo
4. **Code Enhancement** → Análisis adicional con regex
5. **Dependency Analysis** → Detección de problemas
6. **Diagram Generation** → Mermaid + IA
7. **Response** → JSON con análisis completo

## 📈 Métricas Calculadas

### Grafo
- Total de nodos y aristas
- Tipos de nodos (módulos, clases, funciones)
- Promedio/máximo de dependencias

### Dependencias
- Ciclos de dependencias (con severidad)
- Acoplamiento aferente/eferente
- Inestabilidad de módulos
- Cohesión interna

### Complejidad
- Complejidad ciclomática
- Profundidad máxima
- Fan-out promedio/máximo

## 🎯 Casos de Uso

1. **Análisis arquitectónico** de proyectos legacy
2. **Detección de code smells** y anti-patrones
3. **Documentación automática** con diagramas C4
4. **Evaluación de calidad** de código
5. **Refactoring guidance** con recomendaciones

## 📖 Documentación Adicional

- `ARCHITECTURE.md` - Arquitectura detallada del sistema
- `QUICKSTART.md` - Guía rápida de inicio
- `INSTALL.md` - Instrucciones de instalación
- `VISUALIZATION.md` - Visualización de diagramas

## 🤝 Contribuir

Sistema académico modular. Cada módulo tiene responsabilidad única:
- `analyzer.py` → Análisis estático
- `knowledge_graph.py` → Representación y métricas
- `semantic_reasoner.py` → IA y razonamiento
- `diagram_generator.py` → Visualización

## 📄 Licencia

Proyecto académico para investigación en análisis estático y generación automática de diagramas.

---

**Versión 3.0.0** - Sistema unificado y simplificado 🎉

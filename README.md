# 🏗️ Analizador de Arquitectura C4

Sistema inteligente de análisis de proyectos de software que genera automáticamente diagramas C4 (Context, Container, Component) con detección de módulos de negocio y autenticación de usuarios.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()

## 🎯 Características Principales

### ✨ Análisis Inteligente
- 🔍 **Detección de módulos de negocio** - Identifica automáticamente módulos funcionales (user, product, order, payment, etc.)
- 📊 **Diagramas escalables** - Genera diagramas que escalan con el tamaño del proyecto (4-26 containers)
- 🌐 **Soporte multilenguaje** - Java, Python, C++, C#, Go, Ruby, PHP, Rust, Kotlin, Swift, TypeScript
- 📈 **Métricas avanzadas** - PageRank, betweenness centrality, análisis de dependencias

### 🔐 Sistema de Autenticación
- 👤 **Login y Registro** - Sistema completo con validación
- 🗄️ **Base de datos SQLite** - Compatible con despliegue en la nube
- 🔒 **Contraseñas seguras** - Hasheadas con bcrypt
- 🍪 **Sesión persistente** - Manejo de estado con Streamlit

### 📊 Generación de Diagramas
- **C1 (Context)** - Sistema en su contexto con actores externos
- **C2 (Container)** - Arquitectura de contenedores basada en módulos de negocio
- **C3 (Component)** - Componentes internos por capa arquitectónica
- **Formato Mermaid** - Compatible con GitHub, GitLab, Notion, etc.

## 🚀 Instalación Rápida

### Requisitos
- Python 3.12+
- Git

### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/Alexander20L/Agente.git
cd Agente

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar aplicación
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## 📖 Uso

### 1. **Iniciar Sesión**
- Usuario demo: `admin` / `admin123`
- O crear nueva cuenta en "Regístrate aquí"

### 2. **Subir Proyecto**
- Subir archivo `.zip` con tu proyecto
- Soporta cualquier lenguaje de programación

### 3. **Analizar**
- El sistema detecta automáticamente:
  - Módulos de negocio
  - Dependencias
  - Estructura arquitectónica
  - Componentes principales

### 4. **Visualizar Diagramas**
- Ver diagramas C1, C2, C3 generados
- Descargar archivos `.mmd` (Mermaid)
- Copiar código para documentación

## 🏗️ Arquitectura del Sistema

```
agente/
├── app.py                           # Aplicación principal Streamlit
├── core/
│   ├── analyzer.py                  # Análisis estático + detección módulos
│   ├── diagram_generator_deterministic.py  # Generación diagramas C4
│   ├── knowledge_graph.py           # Grafo de dependencias (NetworkX)
│   └── semantic_reasoner.py         # Análisis semántico avanzado
├── requirements.txt                 # Dependencias Python
├── Procfile                         # Configuración Heroku/Railway
├── runtime.txt                      # Versión Python
└── .streamlit/
    └── config.toml                  # Configuración Streamlit Cloud
```

## 🔧 Tecnologías Utilizadas

### Backend
- **Python 3.12** - Lenguaje principal
- **NetworkX** - Análisis de grafos y métricas
- **SQLite** - Base de datos de usuarios
- **bcrypt** - Encriptación de contraseñas

### Frontend
- **Streamlit** - Framework web interactivo
- **Mermaid** - Renderizado de diagramas

### Deployment
- **Streamlit Cloud** - Hosting recomendado
- **Heroku / Railway** - Alternativas soportadas

## 📊 Ejemplo de Resultados

### Proyecto Pequeño (45 archivos)
- **4 containers** detectados: GUI, Core, Data, Utils
- **14 componentes** en C3
- **Tiempo de análisis**: ~2 segundos

### Proyecto Mediano (262 archivos - Spring PetClinic)
- **7 containers** detectados: Owner, Vet, System, Model, etc.
- **42 componentes** en C3
- **Tiempo de análisis**: ~5 segundos

### Proyecto Grande (1,399 archivos - Triton Compiler)
- **26 containers** detectados: AMD, NVIDIA, HIP, Transforms, etc.
- **67 módulos** identificados
- **Tiempo de análisis**: ~15 segundos
- **Mejora**: +766% más detalle vs. versión anterior

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

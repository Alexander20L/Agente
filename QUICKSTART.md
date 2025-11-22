# 🚀 Guía de Inicio Rápido

## Instalación en 3 Pasos

### 1️⃣ Instalar dependencias

**Windows (PowerShell):**
```powershell
.\install.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Iniciar el servidor API

```bash
# Activar entorno virtual (si no está activo)
# Windows: .\venv\Scripts\Activate.ps1
# Linux/Mac: source venv/bin/activate

# Iniciar servidor
uvicorn api.main:app --reload
```

El servidor estará disponible en: http://localhost:8000

### 3️⃣ Usar el agente

#### Opción A: API REST

```bash
# Analizar un proyecto
curl -X POST "http://localhost:8000/analyze/advanced" \
  -F "file=@proyecto.zip" \
  -F "include_ast=true" \
  -F "include_dependencies=true"
```

#### Opción B: Script Python

```python
python examples/analyze_example.py
```

## 📚 Documentación de la API

Visita: http://localhost:8000/docs

## 🎯 Casos de Uso

### Análisis Básico
```bash
POST /analyze
```
- Análisis estático rápido
- Diagramas C4
- Detección de actores

### Análisis Avanzado
```bash
POST /analyze/advanced?include_ast=true&include_dependencies=true
```
- Grafo de conocimiento completo
- Análisis AST profundo
- Métricas de calidad
- Detección de problemas

### Solo Dependencias
```bash
POST /analyze/dependencies
```
- Ciclos de dependencias
- Acoplamiento
- Violaciones arquitectónicas

### Solo Métricas
```bash
POST /analyze/metrics
```
- Métricas de complejidad
- Nodos críticos
- Bottlenecks

## 🛠️ Solución de Problemas

### Error: "tree_sitter not found"
```bash
pip install tree-sitter tree-sitter-python tree-sitter-javascript
```

### Error: "networkx not found"
```bash
pip install networkx
```

### El servidor no inicia
Verifica que el puerto 8000 esté libre:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

## 📝 Ejemplo de Uso Programático

```python
from core.analyzer import analyze_project
from core.knowledge_graph import build_knowledge_graph_from_analysis
from core.dependency_analyzer import DependencyAnalyzer

# 1. Analizar proyecto
analysis = analyze_project("proyecto.zip")

# 2. Crear grafo
kg = build_knowledge_graph_from_analysis(analysis)

# 3. Analizar dependencias
analyzer = DependencyAnalyzer(kg)
report = analyzer.analyze_all()

# 4. Ver resultados
print(kg.visualize_stats())
print(f"Ciclos: {len(report['cycles']['cycles'])}")
```

## 🎨 Visualizar Diagramas

Los diagramas Mermaid generados se pueden visualizar en:
- https://mermaid.live
- VS Code con extensión "Mermaid Preview"
- GitHub (soporta Mermaid nativamente)

## ⚙️ Configuración Avanzada

### Variables de Entorno (.env)
```env
OPENROUTER_API_KEY=tu_clave_aqui  # Opcional: para IA generativa
LOG_LEVEL=INFO
MAX_FILE_SIZE=100MB
```

### Personalizar Análisis

Edita `core/analyzer.py` para:
- Agregar nuevos tipos de componentes
- Personalizar detección de contenedores
- Ajustar umbrales de métricas

## 📊 Métricas Explicadas

- **Acoplamiento Aferente (Ca)**: Cuántos módulos dependen de este
- **Acoplamiento Eferente (Ce)**: De cuántos módulos depende este
- **Inestabilidad (I)**: Ce / (Ca + Ce) - Propensión a cambios
- **Cohesión**: Qué tan relacionados están los componentes internos
- **PageRank**: Importancia relativa del nodo en el grafo

## 🚀 Próximos Pasos

1. Analiza tu primer proyecto
2. Revisa los diagramas generados
3. Implementa las recomendaciones
4. Monitorea las métricas de calidad

¿Preguntas? Abre un issue en el repositorio.

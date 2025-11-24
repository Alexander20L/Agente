# 🎯 Guía Completa: Generar Diagramas C4 en Mermaid

## Tu Agente YA HACE ESTO ✅

Tu agente **ya genera código Mermaid para diagramas C4** que puedes visualizar en https://mermaid.live

## 📊 Diagramas C4 Disponibles

### 1. C1 - Context Diagram (con IA)
Muestra el sistema y sus actores externos

### 2. C2 - Container Diagram (estático + IA)
Muestra contenedores (Backend, Frontend, DB, etc.)

### 3. C3 - Component Diagram (con IA)
Muestra componentes internos (Controllers, Services, etc.)

---

## 🚀 FORMA 1: Usar el Endpoint Original (Simple)

### Paso 1: Iniciar el servidor
```bash
uvicorn api.main:app --reload
```

### Paso 2: Subir tu proyecto
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@mi-proyecto.zip" \
  -o resultado.json
```

### Paso 3: Extraer los diagramas Mermaid
```bash
# El resultado.json contiene:
{
  "mermaid_c2": "graph TD...",      # C2 estático
  "semantic_c1": "C4Context...",    # C1 con IA
  "semantic_c2": "C4Container...",  # C2 con IA
  "semantic_c3": "C4Component..."   # C3 con IA
}
```

### Paso 4: Copiar el código Mermaid
1. Abre resultado.json
2. Copia el contenido de "mermaid_c2" o "semantic_c1/c2/c3"
3. Ve a https://mermaid.live
4. Pega el código
5. ¡Visualiza tu diagrama C4!

---

## 🎨 FORMA 2: Script Python Directo

```python
from core.analyzer import analyze_project, detect_actors
from core.semantic_reasoner import generate_semantic_mermaid_openrouter

# 1. Analizar proyecto
analysis = analyze_project("mi-proyecto.zip")

# 2. Detectar actores
actors = detect_actors(analysis)

# 3. Generar C1 (Context)
c1_mermaid = generate_semantic_mermaid_openrouter(
    analysis, 
    actors, 
    diagram_level="C1"
)

# 4. Generar C2 (Container)
c2_mermaid = generate_semantic_mermaid_openrouter(
    analysis, 
    actors, 
    diagram_level="C2"
)

# 5. Generar C3 (Component)
c3_mermaid = generate_semantic_mermaid_openrouter(
    analysis, 
    actors, 
    diagram_level="C3"
)

# 6. Guardar para visualizar
with open("c1_context.mmd", "w") as f:
    f.write(c1_mermaid)
    
with open("c2_container.mmd", "w") as f:
    f.write(c2_mermaid)
    
with open("c3_component.mmd", "w") as f:
    f.write(c3_mermaid)

print("✅ Diagramas C4 generados!")
print("Abre los archivos .mmd en https://mermaid.live")
```

---

## 🔥 FORMA 3: Con las Nuevas Funcionalidades

Si quieres TAMBIÉN aprovechar el grafo de conocimiento:

```python
from core.analyzer import analyze_project
from core.knowledge_graph import build_knowledge_graph_from_analysis
from core.diagram_generator import generate_mermaid_from_graph

# Análisis
analysis = analyze_project("proyecto.zip")

# Crear grafo
kg = build_knowledge_graph_from_analysis(analysis)

# Generar diagrama de arquitectura (similar a C2)
architecture_diagram = generate_mermaid_from_graph(kg, 'architecture')

# Generar diagrama de componentes (similar a C3)
component_diagram = generate_mermaid_from_graph(kg, 'components')

# Guardar
with open("architecture.mmd", "w") as f:
    f.write(architecture_diagram)
    
with open("components.mmd", "w") as f:
    f.write(component_diagram)
```

---

## 📱 FORMA 4: Usando la API Web

### Desde Postman o cualquier cliente HTTP:

```http
POST http://localhost:8000/analyze
Content-Type: multipart/form-data

file: [tu-proyecto.zip]
```

**Respuesta JSON:**
```json
{
  "mermaid_c2": "graph TD\n  A0[\"Sistema\"]...",
  "semantic_c1": "C4Context\n  Person(user, \"Usuario\")...",
  "semantic_c2": "C4Container\n  Container(web, \"Web App\")...",
  "semantic_c3": "C4Component\n  Component(ctrl, \"Controller\")..."
}
```

Copia cualquiera de estos campos y pégalos en https://mermaid.live

---

## 🎯 EJEMPLO COMPLETO: Script Todo en Uno

```python
"""
Script para generar todos los diagramas C4 de un proyecto
y guardarlos listos para visualizar en Mermaid Live
"""

from core.analyzer import analyze_project, detect_actors
from core.semantic_reasoner import generate_semantic_mermaid_openrouter
from core.diagram_generator import generate_mermaid_c2
import os

def generar_diagramas_c4(proyecto_zip):
    """
    Genera todos los diagramas C4 de un proyecto.
    
    Args:
        proyecto_zip: Ruta al archivo .zip del proyecto
        
    Returns:
        dict con los códigos Mermaid de cada diagrama
    """
    print(f"📦 Analizando {proyecto_zip}...")
    
    # 1. Análisis estático
    analysis = analyze_project(proyecto_zip)
    print(f"✅ Proyecto: {analysis['project_name']}")
    print(f"✅ Tipo: {analysis['project_type']}")
    
    # 2. Detectar actores
    actors = detect_actors(analysis)
    print(f"✅ Actores: {len(actors['actors'])}")
    
    # 3. Generar diagramas
    diagramas = {}
    
    # C2 estático (rápido, sin IA)
    print("\n🎨 Generando C2 estático...")
    diagramas['c2_estatico'] = generate_mermaid_c2(analysis)
    
    # C1 con IA (Context)
    print("🎨 Generando C1 con IA (Context)...")
    diagramas['c1_context'] = generate_semantic_mermaid_openrouter(
        analysis, actors, diagram_level="C1"
    )
    
    # C2 con IA (Container)
    print("🎨 Generando C2 con IA (Container)...")
    diagramas['c2_container'] = generate_semantic_mermaid_openrouter(
        analysis, actors, diagram_level="C2"
    )
    
    # C3 con IA (Component)
    print("🎨 Generando C3 con IA (Component)...")
    diagramas['c3_component'] = generate_semantic_mermaid_openrouter(
        analysis, actors, diagram_level="C3"
    )
    
    # 4. Guardar archivos
    output_dir = "diagramas_c4"
    os.makedirs(output_dir, exist_ok=True)
    
    for nombre, codigo in diagramas.items():
        archivo = f"{output_dir}/{nombre}.mmd"
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(codigo)
        print(f"✅ Guardado: {archivo}")
    
    print(f"\n🎉 ¡Listo! Diagramas guardados en '{output_dir}/'")
    print("\n📱 Para visualizar:")
    print("1. Ve a https://mermaid.live")
    print("2. Abre cualquier archivo .mmd")
    print("3. Copia y pega el contenido")
    print("4. ¡Disfruta tu diagrama C4!")
    
    return diagramas


# USAR ASÍ:
if __name__ == "__main__":
    # Cambia esto por tu proyecto
    proyecto = "uploads/demo-proyecto.zip"
    
    if os.path.exists(proyecto):
        diagramas = generar_diagramas_c4(proyecto)
    else:
        print(f"❌ No se encuentra: {proyecto}")
        print("Sube tu proyecto .zip a la carpeta 'uploads/'")
```

---

## 🎬 Flujo Visual Completo

```
Tu Proyecto (ZIP)
    ↓
[Agente Análisis]
    ↓
Extrae: Contenedores, Componentes, Actores
    ↓
[Generador de Diagramas]
    ↓
Código Mermaid C4
    ↓
Copiar texto
    ↓
https://mermaid.live
    ↓
¡Diagrama C4 Visualizado! 🎨
```

---

## 📋 Checklist para Generar C4

- [ ] Proyecto empaquetado en .zip
- [ ] Servidor corriendo (`uvicorn api.main:app --reload`)
- [ ] Subir proyecto al endpoint `/analyze`
- [ ] Extraer campos `mermaid_c2`, `semantic_c1/c2/c3` del JSON
- [ ] Copiar código Mermaid
- [ ] Abrir https://mermaid.live
- [ ] Pegar código
- [ ] ✅ ¡Ver diagrama C4!

---

## 🔧 Troubleshooting

### "No genera el código Mermaid"
- Verifica que el .env tenga `OPENROUTER_API_KEY` (para diagramas con IA)
- Si no tienes API key, usa solo `mermaid_c2` (no requiere IA)

### "El diagrama no se ve bien"
- Algunos proyectos grandes generan muchos nodos
- Edita el código Mermaid manualmente para simplificar
- O usa filtros en el análisis

### "Quiero personalizar el diagrama"
- El código Mermaid generado es texto plano
- Puedes editarlo manualmente antes de visualizar
- Cambia colores, etiquetas, relaciones, etc.

---

## 🎯 RESUMEN

**Tu agente YA hace exactamente lo que quieres:**

1. ✅ Analiza cualquier proyecto
2. ✅ Genera código Mermaid para C4
3. ✅ Listo para visualizar en mermaid.live
4. ✅ Soporta C1, C2, C3

**Lo único que necesitas:**
1. Subir tu proyecto.zip
2. Llamar al endpoint `/analyze`
3. Copiar el código Mermaid
4. Pegarlo en mermaid.live

**¡Ya está todo implementado!** 🚀

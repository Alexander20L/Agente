# 📦 Guía de Instalación de Dependencias

## Instalación Automática (Recomendado)

### Windows
```powershell
.\install.ps1
```

### Linux/Mac
```bash
chmod +x install.sh
./install.sh
```

## Instalación Manual

### 1. Crear entorno virtual
```bash
python -m venv venv

# Activar
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Actualizar pip
```bash
python -m pip install --upgrade pip
```

### 3. Instalar dependencias principales
```bash
pip install -r requirements.txt
```

## Dependencias Detalladas

### Core (Obligatorias)
```bash
pip install fastapi uvicorn pydantic python-multipart python-dotenv requests
```

### Análisis de Grafos (Obligatorio)
```bash
pip install networkx
```

### Parser AST (Obligatorio para análisis profundo)
```bash
pip install tree-sitter
pip install tree-sitter-python
pip install tree-sitter-javascript
```

### Visualización (Opcional)
```bash
pip install matplotlib
```

### Exportación Avanzada de Grafos (Opcional)
```bash
# Requiere Graphviz instalado en el sistema
pip install pygraphviz
```

## Instalación de Graphviz (Opcional)

### Windows
1. Descargar desde: https://graphviz.org/download/
2. Instalar y agregar al PATH
3. Verificar: `dot -V`

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install graphviz graphviz-dev
```

### Linux (Fedora/CentOS)
```bash
sudo yum install graphviz graphviz-devel
```

### macOS
```bash
brew install graphviz
```

## Solución de Problemas

### Error: "tree-sitter not found"

**Solución:**
```bash
pip install --upgrade tree-sitter
```

Si persiste:
```bash
pip uninstall tree-sitter
pip install tree-sitter --no-cache-dir
```

### Error: "Microsoft Visual C++ required"

**Windows:** Instalar Microsoft C++ Build Tools
- Descargar desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- O instalar Visual Studio Community

### Error: "networkx not found"

**Solución:**
```bash
pip install networkx>=3.0
```

### Error: tree-sitter-python no se instala

**Solución alternativa:**
```bash
pip install tree-sitter-languages
```

Luego modificar `ast_analyzer.py`:
```python
from tree_sitter_languages import get_language, get_parser

# Reemplazar:
# self.languages['python'] = Language(tspython.language())
# Por:
self.languages['python'] = get_language('python')
```

### Error: "Failed building wheel"

**Solución:**
```bash
pip install wheel
pip install --upgrade setuptools
```

### Problemas con pygraphviz

Si `pygraphviz` falla al instalarse, puedes omitirla:
1. Editar `requirements.txt` y comentar la línea: `# pygraphviz`
2. La funcionalidad básica seguirá funcionando

## Verificar Instalación

### Script de verificación:
```python
# verify_install.py
import sys

packages = {
    'fastapi': 'FastAPI',
    'networkx': 'NetworkX',
    'tree_sitter': 'Tree-sitter',
    'tree_sitter_python': 'Tree-sitter Python',
    'tree_sitter_javascript': 'Tree-sitter JavaScript',
}

print("Verificando instalación...\n")
all_ok = True

for package, name in packages.items():
    try:
        __import__(package)
        print(f"✅ {name}")
    except ImportError:
        print(f"❌ {name} - NO instalado")
        all_ok = False

if all_ok:
    print("\n✅ Todas las dependencias principales están instaladas!")
else:
    print("\n⚠️  Algunas dependencias faltan. Ejecuta:")
    print("    pip install -r requirements.txt")
```

Ejecutar:
```bash
python verify_install.py
```

## Requisitos del Sistema

### Mínimos
- Python 3.8+
- 2 GB RAM
- 500 MB espacio en disco

### Recomendados
- Python 3.10+
- 4 GB RAM
- 1 GB espacio en disco
- CPU multi-core para análisis paralelo

## Dependencias por Módulo

### api/main.py
- fastapi
- uvicorn
- pydantic
- python-multipart
- python-dotenv

### core/knowledge_graph.py
- networkx
- json (stdlib)

### core/ast_analyzer.py
- tree-sitter
- tree-sitter-python
- tree-sitter-javascript
- re (stdlib)

### core/dependency_analyzer.py
- networkx
- collections (stdlib)

### core/diagram_generator.py
- (sin dependencias externas)

### core/semantic_reasoner.py
- requests
- python-dotenv

## Versiones Probadas

```
Python: 3.8, 3.9, 3.10, 3.11
FastAPI: 0.104+
NetworkX: 3.0+
tree-sitter: 0.21+
```

## Instalación en Entornos Especiales

### Docker
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Anaconda/Miniconda
```bash
conda create -n agente python=3.10
conda activate agente
pip install -r requirements.txt
```

### Poetry
```bash
poetry init
poetry add fastapi uvicorn networkx tree-sitter
poetry install
```

## Siguiente Paso

Después de instalar las dependencias:
```bash
# Iniciar servidor
uvicorn api.main:app --reload

# O ejecutar ejemplo
python examples/analyze_example.py
```

## Soporte

Si tienes problemas con la instalación:
1. Verifica la versión de Python: `python --version`
2. Verifica pip: `pip --version`
3. Actualiza pip: `python -m pip install --upgrade pip`
4. Intenta instalar en un entorno virtual limpio
5. Revisa los logs de error para identificar el paquete problemático

Para más ayuda, abre un issue en el repositorio.

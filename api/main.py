from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse
from core.analyzer import analyze_project, detect_actors
from core.diagram_generator import (
    generate_mermaid_c2, 
    generate_mermaid_from_graph,
    generate_dependency_matrix,
    generate_metrics_visualization
)
from core.semantic_reasoner import generate_semantic_mermaid_openrouter
from core.knowledge_graph import build_knowledge_graph_from_analysis, enhance_graph_with_code_analysis
import os, shutil

app = FastAPI(
    title="Agente Inteligente C4 - Advanced Code Analysis",
    description="Análisis estático con grafos de conocimiento y razonamiento semántico",
    version="3.0.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    """Endpoint de bienvenida."""
    return {
        "message": "Agente Inteligente C4 - Advanced Code Analysis API",
        "version": "3.0.0",
        "endpoints": {
            "analyze": "POST /analyze - Análisis completo con IA",
            "analyze_advanced": "POST /analyze/advanced - Análisis con grafo de conocimiento",
            "analyze_dependencies": "POST /analyze/dependencies - Análisis de dependencias",
            "analyze_metrics": "POST /analyze/metrics - Métricas de calidad",
            "health": "GET /health - Estado del servicio"
        }
    }


@app.get("/health")
async def health_check():
    """Verifica el estado del servicio."""
    return {"status": "healthy", "service": "code-analysis-agent"}


@app.post("/query")
async def query_knowledge_graph(
    file: UploadFile = File(...),
    question: str = Query(..., description="Pregunta en lenguaje natural sobre el proyecto")
):
    """
    Herramienta de consulta inteligente al grafo de conocimiento.
    
    Ejemplos:
    - "What depends on UserService?"
    - "Who calls authenticate()?"
    - "Show structure of auth module"
    - "Find patterns in UserRepository"
    - "What's the path from Controller to Database?"
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Solo archivos .zip")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        # Construir grafo
        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        # Consultar con lenguaje natural
        result = kg.query_graph(question)
        
        return {
            "question": question,
            "understood": result["understood"],
            "answer": result["answer"],
            "project": analysis_result.get('project_name')
        }
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/tools/dependencies")
async def get_node_dependencies(
    file: UploadFile = File(...),
    node_name: str = Query(..., description="Nombre del nodo (clase, función, módulo)")
):
    """
    Herramienta: Obtiene las dependencias de un nodo específico.
    Retorna qué usa/importa/llama este nodo.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Solo archivos .zip")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        dependencies = kg.get_dependencies(node_name)
        
        return {
            "node": node_name,
            "dependencies": dependencies,
            "count": len(dependencies)
        }
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/tools/callers")
async def find_node_callers(
    file: UploadFile = File(...),
    node_name: str = Query(..., description="Nombre del nodo")
):
    """
    Herramienta: Encuentra quién usa/llama a un nodo específico.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Solo archivos .zip")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        callers = kg.find_callers(node_name)
        
        return {
            "node": node_name,
            "callers": callers,
            "count": len(callers)
        }
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/tools/structure")
async def get_module_structure_endpoint(
    file: UploadFile = File(...),
    module: str = Query(None, description="Nombre del módulo (opcional)")
):
    """
    Herramienta: Obtiene la estructura de un módulo o del proyecto completo.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Solo archivos .zip")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        structure = kg.get_module_structure(module)
        
        return structure
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/tools/patterns")
async def analyze_design_patterns_endpoint(
    file: UploadFile = File(...),
    component: str = Query(..., description="Nombre del componente a analizar")
):
    """
    Herramienta: Detecta patrones de diseño en un componente.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Solo archivos .zip")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        patterns = kg.analyze_design_patterns(component)
        
        return patterns
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/tools/path")
async def find_dependency_path(
    file: UploadFile = File(...),
    source: str = Query(..., description="Nodo origen"),
    target: str = Query(..., description="Nodo destino")
):
    """
    Herramienta: Encuentra el camino de dependencias entre dos nodos.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Solo archivos .zip")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        path = kg.find_path(source, target)
        
        return {
            "source": source,
            "target": target,
            "path": path,
            "found": len(path) > 0,
            "hops": len(path) - 1 if path else 0
        }
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/tools/info")
async def get_node_info_endpoint(
    file: UploadFile = File(...),
    node_name: str = Query(..., description="Nombre del nodo")
):
    """
    Herramienta: Obtiene información detallada de un nodo específico.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Solo archivos .zip")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        info = kg.get_node_info(node_name)
        
        return info
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/analyze")
async def analyze_project_api(file: UploadFile = File(...)):
    """
    Análisis estático básico del proyecto (compatible con versión anterior).
    
    Retorna:
    - Análisis de contenedores y componentes
    - Detección de actores
    - Diagramas C2/C3
    - Diagramas semánticos con IA (opcional)
    """
    # Guardar archivo subido
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # === Paso 1: Análisis estático (C2/C3) ===
    analysis_result = analyze_project(file_path)

    # === Paso 2: Detectar actores (C1) ===
    actors_detected = detect_actors(analysis_result)

    # === Paso 3: Diagrama C2 determinístico (NO IA) ===
    mermaid_c2 = generate_mermaid_c2(analysis_result)

    # === Paso 4: Diagramas semánticos con IA (opcional) ===
    try:
        semantic_c1 = generate_semantic_mermaid_openrouter(
            analysis_result,
            actors_detected,
            diagram_level="C1"
        )
        semantic_c2 = generate_semantic_mermaid_openrouter(
            analysis_result,
            actors_detected,
            diagram_level="C2"
        )
        semantic_c3 = generate_semantic_mermaid_openrouter(
            analysis_result,
            actors_detected,
            diagram_level="C3"
        )
    except Exception as e:
        semantic_c1 = f"Error: {str(e)}"
        semantic_c2 = f"Error: {str(e)}"
        semantic_c3 = f"Error: {str(e)}"

    # === Paso 5: Respuesta unificada ===
    return {
        "message": "Análisis completado",
        "actors_detected": actors_detected,
        "result": analysis_result,
        "mermaid_c2": mermaid_c2,
        "semantic_c1": semantic_c1,
        "semantic_c2": semantic_c2,
        "semantic_c3": semantic_c3
    }


@app.post("/analyze/advanced")
async def analyze_project_advanced(
    file: UploadFile = File(...),
    diagram_type: str = Query("architecture", description="Tipo de diagrama: architecture, dependencies, components, classes")
):
    """
    Análisis avanzado con grafo de conocimiento y métricas de calidad.
    
    Características:
    - Grafo de conocimiento completo
    - Detección de ciclos de dependencias
    - Métricas de acoplamiento y cohesión
    - Identificación de hotspots
    - Recomendaciones automáticas
    """
    try:
        # Guardar archivo subido
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # === 1. Análisis estático básico ===
        analysis_result = analyze_project(file_path)
        extract_dir = analysis_result['project_path']

        # === 2. Construir grafo de conocimiento ===
        kg = build_knowledge_graph_from_analysis(analysis_result)

        # === 3. Enriquecer con análisis de código ===
        kg = enhance_graph_with_code_analysis(kg, analysis_result)

        # === 4. Análisis de dependencias integrado ===
        dependency_report = kg.analyze_dependencies()

        # === 5. Generar diagramas desde el grafo ===
        diagram_mermaid = generate_mermaid_from_graph(kg, diagram_type)
        
        # === 6. Métricas del grafo ===
        metrics = kg.calculate_metrics()
        critical_nodes = kg.find_critical_nodes(10)
        
        # === 7. Estadísticas visuales ===
        stats_text = kg.visualize_stats()

        # === 8. Matriz de dependencias ===
        dependency_matrix = generate_dependency_matrix(kg)

        # === 9. Detectar actores ===
        actors_detected = detect_actors(analysis_result)

        # === Respuesta completa ===
        return {
            "message": "Análisis avanzado completado",
            "project_info": {
                "name": analysis_result.get('project_name'),
                "type": analysis_result.get('project_type'),
                "total_files": analysis_result.get('total_files'),
                "path": extract_dir
            },
            "graph_metrics": metrics,
            "critical_nodes": [
                {"node": node, "score": score}
                for node, score in critical_nodes
            ],
            "actors": actors_detected,
            "dependency_analysis": dependency_report,
            "diagrams": {
                "type": diagram_type,
                "mermaid": diagram_mermaid,
                "dependency_matrix": dependency_matrix
            },
            "statistics": stats_text
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Error durante el análisis avanzado"
            }
        )


@app.post("/analyze/dependencies")
async def analyze_dependencies_only(file: UploadFile = File(...)):
    """
    Análisis enfocado únicamente en dependencias y problemas arquitectónicos.
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        report = kg.analyze_dependencies()

        return {
            "message": "Análisis de dependencias completado",
            "project": analysis_result.get('project_name'),
            "report": report
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/analyze/metrics")
async def analyze_metrics_only(file: UploadFile = File(...)):
    """
    Análisis enfocado en métricas de calidad del código.
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        analysis_result = analyze_project(file_path)
        kg = build_knowledge_graph_from_analysis(analysis_result)
        kg = enhance_graph_with_code_analysis(kg, analysis_result)
        
        metrics = kg.calculate_metrics()
        critical_nodes = kg.find_critical_nodes(10)
        bottlenecks = kg.find_bottlenecks()

        return {
            "message": "Análisis de métricas completado",
            "project": analysis_result.get('project_name'),
            "metrics": metrics,
            "critical_nodes": [{"node": n, "score": s} for n, s in critical_nodes],
            "bottlenecks": bottlenecks,
            "visualization": generate_metrics_visualization(metrics)
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# ═══════════════════════════════════════════════════════════════════════════
# AGENT TOOLS ENDPOINTS (Herramientas Avanzadas)
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/agent/tools/list")
async def list_agent_tools(file: UploadFile = File(...)):
    """
    Lista todas las herramientas disponibles para el agente.
    
    Returns:
        Lista de herramientas con descripción y ejemplos
    """
    try:
        from core.agent_tools import AgentTools
        
        # Guardar archivo
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Analizar y crear AgentTools
        result = analyze_project(file_path)
        tools = AgentTools(result["knowledge_graph"])
        
        return {
            "available_tools": tools.get_available_tools(),
            "summary": tools.summarize_graph()
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/agent/explore-impact")
async def explore_impact(
    file: UploadFile = File(...),
    node_name: str = Query(..., description="Componente a analizar"),
    max_depth: int = Query(2, description="Profundidad de exploración")
):
    """
    Explora el impacto de modificar un componente.
    
    Ejemplo: ¿Si modifico Database, qué se rompe?
    """
    try:
        from core.agent_tools import AgentTools
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        result = analyze_project(file_path)
        tools = AgentTools(result["knowledge_graph"])
        
        impact = tools.explore_impact(node_name, max_depth)
        
        return {
            "impact_analysis": impact,
            "recommendation": f"Risk level: {impact['risk_level']} - {impact['total_affected']} components affected"
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/agent/critical-nodes")
async def get_critical_nodes(
    file: UploadFile = File(...),
    top_n: int = Query(5, description="Cantidad de nodos críticos")
):
    """
    Obtiene los componentes más críticos del sistema.
    
    Ejemplo: ¿Qué componentes debería revisar primero?
    """
    try:
        from core.agent_tools import AgentTools
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        result = analyze_project(file_path)
        tools = AgentTools(result["knowledge_graph"])
        
        critical = tools.get_critical_nodes(top_n)
        
        return {
            "critical_nodes": critical,
            "recommendation": f"Focus on these {critical['count']} components first"
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/agent/communities")
async def get_communities(file: UploadFile = File(...)):
    """
    Obtiene las comunidades/módulos del sistema.
    
    Ejemplo: ¿Qué módulos están fuertemente acoplados?
    """
    try:
        from core.agent_tools import AgentTools
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        result = analyze_project(file_path)
        tools = AgentTools(result["knowledge_graph"])
        
        communities = tools.get_communities()
        
        return {
            "communities": communities,
            "insight": f"System organized in {communities['count']} modules/clusters"
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/agent/find-path")
async def find_component_path(
    file: UploadFile = File(...),
    source: str = Query(..., description="Componente origen"),
    target: str = Query(..., description="Componente destino")
):
    """
    Encuentra el camino entre dos componentes.
    
    Ejemplo: ¿Cómo llega la petición desde Controller hasta Database?
    """
    try:
        from core.agent_tools import AgentTools
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        result = analyze_project(file_path)
        tools = AgentTools(result["knowledge_graph"])
        
        path = tools.find_path(source, target)
        
        return {
            "path_analysis": path,
            "visualization": " → ".join(path['path']) if path['exists'] else "No connection found"
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

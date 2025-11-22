import os
import json
from dotenv import load_dotenv
import requests


def generate_semantic_mermaid_openrouter(
    analysis_result: dict,
    actors_detected=None,
    diagram_level: str = "C1"
):
    """
    Genera un diagrama C4 usando IA (OpenRouter) con métricas de grafos.
    
    Args:
        analysis_result: Resultado del análisis estático (incluye knowledge_graph y graph_metrics)
        actors_detected: Lista de actores detectados
        diagram_level: Nivel del diagrama ("C1", "C2", "C3")
    
    Returns:
        str: Código Mermaid del diagrama C4
    """
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return "⚠️ Error: no se encontró OPENROUTER_API_KEY en .env"

    # Normalizar actores
    if isinstance(actors_detected, dict):
        actors = actors_detected.get("actors", [])
        external_systems = actors_detected.get("external_systems", [])
    else:
        actors = actors_detected or []
        external_systems = []

    # NUEVO: Extraer métricas del grafo para enriquecer el contexto
    graph_metrics = analysis_result.get("graph_metrics", {})
    
    # Priorizar componentes importantes según PageRank
    important_components = graph_metrics.get("important_components", [])[:5]
    bottleneck_components = graph_metrics.get("bottleneck_components", [])[:3]
    hub_components = graph_metrics.get("hub_components", [])[:3]
    
    # NUEVO: Escalado inteligente según tamaño del proyecto
    total_files = analysis_result.get("total_files", 0)
    all_containers = analysis_result.get("containers_detected", [])
    all_components = analysis_result.get("components_detected", [])
    all_relations = analysis_result.get("relations_detected", [])
    
    # Escalar límites según tamaño del proyecto
    if total_files < 20:
        # Proyecto pequeño
        container_limit = min(5, len(all_containers))
        component_limit = min(10, len(all_components))
        relation_limit = min(15, len(all_relations))
    elif total_files < 100:
        # Proyecto mediano
        container_limit = min(15, len(all_containers))
        component_limit = min(30, len(all_components))
        relation_limit = min(50, len(all_relations))
    else:
        # Proyecto grande
        container_limit = min(30, len(all_containers))
        component_limit = min(50, len(all_components))
        relation_limit = min(100, len(all_relations))
    
    # Contexto enriquecido con métricas del grafo
    context = {
        "project_name": analysis_result.get("project_name"),
        "project_type": analysis_result.get("project_type"),
        "project_size": {
            "files": total_files,
            "category": "small" if total_files < 20 else "medium" if total_files < 100 else "large"
        },
        "containers": all_containers[:container_limit],
        "components": all_components[:component_limit],
        "relations": all_relations[:relation_limit],
        "actors": actors,
        "external_systems": external_systems,
        "diagram_level": diagram_level,
        # NUEVO: Métricas del grafo para decisiones inteligentes
        "graph_insights": {
            "important_components": important_components,  # Los más centrales por PageRank
            "bottlenecks": bottleneck_components,  # Cuellos de botella por Betweenness
            "hubs": hub_components,  # Componentes con más conexiones
            "total_components": graph_metrics.get("total_nodes", 0),
            "total_relations": graph_metrics.get("total_edges", 0)
        }
    }

    instructions = """Eres un experto en arquitectura de software especializado en el modelo C4.

Reglas obligatorias:
- Si diagram_level = "C1": genera SOLO un C4Context.
- Si diagram_level = "C2": genera SOLO un C4Container.
- Si diagram_level = "C3": genera SOLO un C4Component.
- PROHIBIDO mezclar niveles.
- PROHIBIDO agregar explicaciones.
- PROHIBIDO agregar texto fuera de Mermaid.
- Devuelve SOLO el código Mermaid limpio, sin delimitadores.

ESCALADO SEGÚN TAMAÑO DEL PROYECTO:
- Proyecto PEQUEÑO (<20 archivos): Muestra TODO (máx 5 containers, 10 componentes)
- Proyecto MEDIANO (20-100 archivos): Muestra elementos principales (máx 15 containers, 30 componentes)
- Proyecto GRANDE (>100 archivos): Muestra arquitectura completa (máx 30 containers, 50 componentes)

IMPORTANTE: Para proyectos GRANDES, debes generar diagramas COMPLETOS:
- C1: Incluir TODOS los sistemas principales y externos detectados
- C2: Incluir TODOS los containers (microservicios, APIs, DBs, caches, workers, etc.)
- C3: Priorizar "important_components" (PageRank alto) pero mostrar la mayor cantidad posible
- Usar "bottlenecks" para identificar componentes críticos
- Usar "hubs" para componentes con muchas conexiones
- NO simplificar excesivamente: Un proyecto de 500 archivos NO puede tener solo 4 containers

Ejemplo C1:
C4Context
    title Sistema de Gestión
    Person(user, "Usuario", "Usuario del sistema")
    System(system, "Sistema Principal", "Sistema web")
    System_Ext(external, "Sistema Externo", "API externa")
    Rel(user, system, "Usa")
    Rel(system, external, "Consume")

Ejemplo C2:
C4Container
    title Contenedores del Sistema
    Person(user, "Usuario")
    Container(web, "Aplicación Web", "React")
    Container(api, "API", "FastAPI")
    ContainerDb(db, "Base de Datos", "PostgreSQL")
    Rel(user, web, "Usa")
    Rel(web, api, "Consume")
    Rel(api, db, "Lee/Escribe")

Ejemplo C3:
C4Component
    title Componentes de la API
    Component(controller, "Controller", "Maneja requests")
    Component(service, "Service", "Lógica de negocio")
    Component(repository, "Repository", "Acceso a datos")
    Rel(controller, service, "Usa")
    Rel(service, repository, "Usa")

Genera el diagrama basándote en el contexto del proyecto Y las métricas del grafo."""

    prompt = f"""Contexto del proyecto:
{json.dumps(context, indent=2, ensure_ascii=False)}

{instructions}

Genera el diagrama {diagram_level} en formato Mermaid."""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Agente C4 Analyzer"
            },
            json={
                "model": "deepseek/deepseek-chat",  # Muy barato: $0.14/1M tokens
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        
        # Extraer contenido
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Limpiar respuesta (remover bloques de código si existen)
        content = content.strip()
        if content.startswith("```mermaid"):
            content = content[10:]  # Remover ```mermaid
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        # Validar que tenga contenido C4
        if not any(keyword in content for keyword in ["C4Context", "C4Container", "C4Component"]):
            return f"⚠️ Error: La respuesta no contiene un diagrama C4 válido.\n\nRespuesta recibida:\n{content}"
        
        return content

    except requests.exceptions.Timeout:
        return "⚠️ Error: Timeout al conectar con OpenRouter (30s)"
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error de conexión con OpenRouter: {str(e)}"
    except Exception as e:
        return f"⚠️ Error inesperado: {str(e)}"

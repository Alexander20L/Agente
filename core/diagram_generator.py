"""
Generador de Diagramas Mermaid (LEGACY)

⚠️ NOTA: Este módulo contiene funciones legacy.
   
   Las funciones principales han sido movidas a:
   - diagram_generator_deterministic.py (generación C1/C2/C3)
   - business_c4_generator.py (enriquecimiento con IA)
   
   Este archivo se mantiene por compatibilidad con código legacy.
"""

from typing import Dict, List, Any


def generate_mermaid_c2(analysis_result: Dict) -> str:
    """
    Genera un diagrama C2 (Container) determinístico en formato Mermaid.
    Sin IA, basado puramente en el análisis estático.
    """
    lines = ["graph TB"]
    
    containers = analysis_result.get("containers_detected", [])
    
    if not containers:
        return "graph TB\n    A[No se detectaron contenedores]"
    
    # Generar nodos para cada contenedor
    for i, container in enumerate(containers[:10], 1):  # Limitar a 10
        name = container.get("name", f"Container{i}")
        tech = container.get("type", "")
        node_id = f"C{i}"
        
        if tech:
            lines.append(f'    {node_id}["{name}<br/><small>{tech}</small>"]')
        else:
            lines.append(f'    {node_id}["{name}"]')
    
    # Detectar relaciones básicas (secuenciales)
    for i in range(1, min(len(containers), 10)):
        lines.append(f"    C{i} --> C{i+1}")
    
    return "\n".join(lines)


def generate_mermaid_from_graph(kg, diagram_type: str = "architecture") -> str:
    """
    Genera un diagrama Mermaid desde el grafo de conocimiento.
    
    Args:
        kg: KnowledgeGraph instance
        diagram_type: Tipo de diagrama (architecture, dependencies, components, classes)
    """
    if diagram_type == "dependencies":
        return generate_dependency_graph(kg)
    elif diagram_type == "components":
        return generate_component_diagram(kg)
    elif diagram_type == "classes":
        return generate_class_diagram(kg)
    else:
        return generate_architecture_diagram(kg)


def generate_architecture_diagram(kg) -> str:
    """Genera diagrama de arquitectura general."""
    lines = ["graph TB"]
    
    modules = [n for n in kg.graph.nodes() 
               if kg.graph.nodes[n].get("node_type") == "module"]
    
    for i, module in enumerate(modules[:15], 1):
        name = module.split("/")[-1] if "/" in module else module
        lines.append(f'    M{i}["{name}"]')
    
    # Agregar dependencias
    for src, dst in kg.graph.edges():
        if src in modules and dst in modules:
            src_idx = modules.index(src) + 1
            dst_idx = modules.index(dst) + 1
            if src_idx <= 15 and dst_idx <= 15:
                lines.append(f"    M{src_idx} --> M{dst_idx}")
    
    return "\n".join(lines)


def generate_component_diagram(kg) -> str:
    """Genera diagrama de componentes."""
    lines = ["graph LR"]
    
    components = [n for n in kg.graph.nodes() 
                  if kg.graph.nodes[n].get("node_type") in ["component", "class", "function"]]
    
    node_map = {}
    for i, comp in enumerate(components[:20], 1):
        node_id = f"C{i}"
        node_map[comp] = node_id
        
        name = comp.split(".")[-1] if "." in comp else comp
        comp_type = kg.graph.nodes[comp].get("node_type", "component")
        
        lines.append(f'    {node_id}["{name}<br/><small>{comp_type}</small>"]')
    
    # Relaciones
    for src, dst in kg.graph.edges():
        if src in node_map and dst in node_map:
            rel_type = kg.graph.edges[src, dst].get("relation", "uses")
            if rel_type == "calls":
                lines.append(f"    {node_map[src]} -->|calls| {node_map[dst]}")
            elif rel_type == "inherits":
                lines.append(f"    {node_map[src]} -.->|inherits| {node_map[dst]}")
            else:
                lines.append(f"    {node_map[src]} --> {node_map[dst]}")
    
    return "\n".join(lines)


def generate_dependency_graph(kg) -> str:
    """Genera grafo de dependencias."""
    lines = ["graph TD"]
    
    nodes = list(kg.graph.nodes())[:25]  # Limitar a 25 nodos
    node_map = {}
    
    for i, node in enumerate(nodes, 1):
        node_id = f"N{i}"
        node_map[node] = node_id
        
        name = node.split("/")[-1] if "/" in node else node
        node_type = kg.graph.nodes[node].get("node_type", "")
        
        # Colorear por tipo
        if node_type == "module":
            lines.append(f'    {node_id}["{name}"]:::module')
        elif node_type == "class":
            lines.append(f'    {node_id}["{name}"]:::class')
        elif node_type == "function":
            lines.append(f'    {node_id}["{name}"]:::function')
        else:
            lines.append(f'    {node_id}["{name}"]')
    
    # Dependencias
    for src, dst in kg.graph.edges():
        if src in node_map and dst in node_map:
            lines.append(f"    {node_map[src]} --> {node_map[dst]}")
    
    # Estilos
    lines.append("    classDef module fill:#a8d5ff,stroke:#3498db")
    lines.append("    classDef class fill:#ffd6a5,stroke:#ff9800")
    lines.append("    classDef function fill:#c8e6c9,stroke:#4caf50")
    
    return "\n".join(lines)


def generate_class_diagram(kg) -> str:
    """Genera diagrama de clases."""
    lines = ["classDiagram"]
    
    classes = [n for n in kg.graph.nodes() 
               if kg.graph.nodes[n].get("node_type") == "class"]
    
    for cls in classes[:10]:  # Limitar a 10 clases
        class_name = cls.split(".")[-1] if "." in cls else cls
        lines.append(f"    class {class_name}")
        
        # Buscar métodos (funciones contenidas en esta clase)
        methods = [dst for src, dst in kg.graph.edges() 
                   if src == cls and kg.graph.nodes[dst].get("node_type") == "function"]
        
        for method in methods[:5]:  # Máximo 5 métodos
            method_name = method.split(".")[-1] if "." in method else method
            lines.append(f"        {class_name} : +{method_name}()")
    
    # Herencias
    for src, dst in kg.graph.edges():
        if kg.graph.edges[src, dst].get("relation") == "inherits":
            if src in classes and dst in classes:
                src_name = src.split(".")[-1] if "." in src else src
                dst_name = dst.split(".")[-1] if "." in dst else dst
                lines.append(f"    {dst_name} <|-- {src_name}")
    
    return "\n".join(lines)


def generate_sequence_diagram(kg, scenario: str = "default") -> str:
    """Genera diagrama de secuencia."""
    lines = ["sequenceDiagram"]
    
    # Buscar llamadas de función
    calls = [(src, dst) for src, dst in kg.graph.edges() 
             if kg.graph.edges[src, dst].get("relation") == "calls"]
    
    if not calls:
        return "sequenceDiagram\n    Note over User: No se detectaron llamadas"
    
    # Tomar las primeras 10 llamadas
    for src, dst in calls[:10]:
        src_name = src.split(".")[-1] if "." in src else src
        dst_name = dst.split(".")[-1] if "." in dst else dst
        lines.append(f"    {src_name}->>+{dst_name}: call")
        lines.append(f"    {dst_name}-->>-{src_name}: return")
    
    return "\n".join(lines)


def generate_dependency_matrix(kg) -> Dict[str, Any]:
    """
    Genera una matriz de dependencias.
    
    Returns:
        Dict con estructura: {
            "nodes": [...],
            "matrix": [[0, 1, 0], [0, 0, 1], ...]
        }
    """
    nodes = list(kg.graph.nodes())[:20]  # Limitar a 20
    n = len(nodes)
    
    # Crear matriz
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    
    for i, src in enumerate(nodes):
        for j, dst in enumerate(nodes):
            if kg.graph.has_edge(src, dst):
                matrix[i][j] = 1
    
    return {
        "nodes": nodes,
        "size": n,
        "matrix": matrix,
        "total_dependencies": sum(sum(row) for row in matrix)
    }


def generate_metrics_visualization(metrics: Dict) -> str:
    """
    Genera visualización textual de métricas.
    
    Args:
        metrics: Dict con métricas del grafo
    
    Returns:
        str: Representación textual de métricas
    """
    lines = []
    lines.append("=" * 50)
    lines.append("MÉTRICAS DEL PROYECTO")
    lines.append("=" * 50)
    
    lines.append(f"\n📊 Nodos Totales: {metrics.get('total_nodes', 0)}")
    lines.append(f"🔗 Aristas Totales: {metrics.get('total_edges', 0)}")
    lines.append(f"📈 Dependencias Promedio: {metrics.get('avg_dependencies', 0):.2f}")
    lines.append(f"⚡ Dependencias Máximas: {metrics.get('max_dependencies', 0)}")
    
    # Tipos de nodos
    node_types = metrics.get('node_types', {})
    if node_types:
        lines.append("\n📦 Tipos de Nodos:")
        for ntype, count in node_types.items():
            lines.append(f"   - {ntype}: {count}")
    
    # Tipos de componentes
    comp_types = metrics.get('component_types', {})
    if comp_types:
        lines.append("\n🔧 Tipos de Componentes:")
        for ctype, count in comp_types.items():
            lines.append(f"   - {ctype}: {count}")
    
    lines.append("=" * 50)
    
    return "\n".join(lines)

"""
Agent Tools - Herramientas para Agentes IA
═══════════════════════════════════════════════════════════════════════════════

Capa de abstracción que permite a agentes IA navegar el Knowledge Graph
de manera inteligente, tomando decisiones sobre qué explorar según necesidad.

Implementa el enfoque: Análisis Estático + Grafo de Conocimiento (IDEAL)

Ejemplo de uso por un agente:
    tools = AgentTools(knowledge_graph)
    
    # Agente decide qué explorar
    deps = tools.get_dependencies("UserRepository")
    callers = tools.find_callers("authenticate")
    structure = tools.get_module_structure("auth")
    patterns = tools.analyze_design_patterns("UserController")
"""

from typing import Dict, List, Any, Optional
from core.knowledge_graph import KnowledgeGraph
import json


class AgentTools:
    """
    Conjunto de herramientas para que agentes IA naveguen el Knowledge Graph.
    
    Filosofía:
    - El agente decide qué nodos explorar según su objetivo
    - Las herramientas son atómicas y componibles
    - El agente puede hacer preguntas específicas al grafo
    - Optimiza para descubrimiento incremental (no cargar todo)
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Inicializa las herramientas con un Knowledge Graph.
        
        Args:
            knowledge_graph: Grafo de conocimiento del proyecto
        """
        self.kg = knowledge_graph
    
    # ═══════════════════════════════════════════════════════════════════════
    # HERRAMIENTAS BÁSICAS (4 core tools)
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_dependencies(self, class_name: str) -> Dict[str, Any]:
        """
        ¿De qué depende este componente?
        
        Pregunta del agente: "Necesito saber qué imports tiene UserRepository"
        
        Args:
            class_name: Nombre del componente/clase
            
        Returns:
            {
                "target": "UserRepository",
                "dependencies": ["Database", "Logger", "Config"],
                "count": 3,
                "critical": ["Database"]  # Dependencias con alta betweenness
            }
        """
        deps = self.kg.get_dependencies(class_name)
        
        # Enriquecer con métricas del grafo
        metrics = self.kg.calculate_importance_metrics()
        bottlenecks = {b['node'] for b in metrics.get('bottleneck_components', [])}
        
        return {
            "target": class_name,
            "dependencies": deps,
            "count": len(deps),
            "critical": [d for d in deps if d in bottlenecks],
            "description": f"{class_name} depende de {len(deps)} componentes"
        }
    
    def find_callers(self, method_name: str) -> Dict[str, Any]:
        """
        ¿Quién usa este método/clase?
        
        Pregunta del agente: "¿Qué servicios dependen de authenticate()?"
        
        Args:
            method_name: Nombre del método/clase
            
        Returns:
            {
                "target": "authenticate",
                "callers": ["LoginController", "ApiAuth", "SessionManager"],
                "count": 3,
                "impact": "high"  # Basado en cantidad de callers
            }
        """
        callers = self.kg.find_callers(method_name)
        
        # Calcular impacto
        impact = "low"
        if len(callers) > 10:
            impact = "critical"
        elif len(callers) > 5:
            impact = "high"
        elif len(callers) > 2:
            impact = "medium"
        
        return {
            "target": method_name,
            "callers": callers,
            "count": len(callers),
            "impact": impact,
            "description": f"{method_name} es usado por {len(callers)} componentes"
        }
    
    def get_module_structure(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        ¿Cómo está organizado este módulo?
        
        Pregunta del agente: "Muéstrame la estructura del módulo 'auth'"
        
        Args:
            module: Nombre del módulo (None = estructura completa)
            
        Returns:
            {
                "module": "auth",
                "classes": ["UserAuth", "TokenManager"],
                "functions": ["validate_token", "refresh_token"],
                "submodules": ["providers", "middleware"],
                "total_nodes": 15
            }
        """
        structure = self.kg.get_module_structure(module)
        
        # Añadir métricas adicionales
        total = sum([
            len(structure.get('classes', [])),
            len(structure.get('functions', [])),
            len(structure.get('submodules', []))
        ])
        
        return {
            **structure,
            "total_nodes": total,
            "description": f"Módulo '{module or 'root'}' con {total} elementos"
        }
    
    def analyze_design_patterns(self, component: str) -> Dict[str, Any]:
        """
        ¿Qué patrones usa este componente?
        
        Pregunta del agente: "¿UserController usa algún patrón de diseño?"
        
        Args:
            component: Nombre del componente
            
        Returns:
            {
                "component": "UserController",
                "patterns": ["MVC", "Repository", "Dependency Injection"],
                "confidence": {"MVC": 0.9, "Repository": 0.8},
                "recommendations": ["Consider using CQRS"]
            }
        """
        return self.kg.analyze_design_patterns(component)
    
    # ═══════════════════════════════════════════════════════════════════════
    # HERRAMIENTAS AVANZADAS (navegación inteligente)
    # ═══════════════════════════════════════════════════════════════════════
    
    def explore_impact(self, node_name: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        ¿Qué impacto tendría modificar este componente?
        
        Pregunta del agente: "Si modifico Database, ¿qué se rompe?"
        
        Args:
            node_name: Componente a analizar
            max_depth: Profundidad de exploración
            
        Returns:
            {
                "node": "Database",
                "direct_impact": ["UserRepository", "Logger"],
                "indirect_impact": ["UserService", "AuthService"],
                "total_affected": 10,
                "risk_level": "high"
            }
        """
        # Obtener dependientes directos
        direct = self.kg.find_callers(node_name)
        
        # Obtener dependientes indirectos (depth = 2)
        indirect = set()
        if max_depth > 1:
            for caller in direct:
                indirect.update(self.kg.find_callers(caller))
            indirect -= set(direct)  # Remover duplicados
        
        total = len(direct) + len(indirect)
        
        # Calcular nivel de riesgo
        risk = "low"
        if total > 20:
            risk = "critical"
        elif total > 10:
            risk = "high"
        elif total > 5:
            risk = "medium"
        
        return {
            "node": node_name,
            "direct_impact": direct,
            "indirect_impact": list(indirect),
            "total_affected": total,
            "risk_level": risk,
            "description": f"Modificar {node_name} afectaría {total} componentes"
        }
    
    def find_path(self, source: str, target: str) -> Dict[str, Any]:
        """
        ¿Cómo se conectan dos componentes?
        
        Pregunta del agente: "¿Cómo llega la petición desde Controller hasta Database?"
        
        Args:
            source: Componente origen
            target: Componente destino
            
        Returns:
            {
                "source": "UserController",
                "target": "Database",
                "path": ["UserController", "UserService", "UserRepository", "Database"],
                "length": 4,
                "exists": True
            }
        """
        path = self.kg.find_path(source, target)
        
        return {
            "source": source,
            "target": target,
            "path": path if path else [],
            "length": len(path) if path else 0,
            "exists": bool(path),
            "description": f"Camino de {source} a {target}: {' → '.join(path) if path else 'No existe'}"
        }
    
    def get_critical_nodes(self, top_n: int = 5) -> Dict[str, Any]:
        """
        ¿Cuáles son los componentes más críticos?
        
        Pregunta del agente: "¿Qué componentes debería revisar primero?"
        
        Args:
            top_n: Cantidad de nodos a retornar
            
        Returns:
            {
                "critical_nodes": [
                    {"name": "BaseEntity", "score": 0.026, "reason": "high_pagerank"},
                    {"name": "UserRepository", "score": 0.015, "reason": "bottleneck"}
                ],
                "count": 5
            }
        """
        metrics = self.kg.calculate_importance_metrics()
        
        critical = []
        
        # Top por PageRank (importancia)
        for node in metrics.get('important_components', [])[:top_n]:
            critical.append({
                "name": node['node'],
                "score": node['score'],
                "reason": "high_pagerank",
                "description": "Componente central en el sistema"
            })
        
        # Top por Betweenness (cuellos de botella)
        for node in metrics.get('bottleneck_components', [])[:top_n]:
            if node['score'] > 0:  # Solo si hay betweenness significativo
                critical.append({
                    "name": node['node'],
                    "score": node['score'],
                    "reason": "bottleneck",
                    "description": "Cuello de botella crítico"
                })
        
        # Deduplicar por nombre
        seen = set()
        unique_critical = []
        for c in critical:
            if c['name'] not in seen:
                seen.add(c['name'])
                unique_critical.append(c)
        
        return {
            "critical_nodes": unique_critical[:top_n],
            "count": len(unique_critical[:top_n]),
            "description": f"Top {top_n} componentes críticos del sistema"
        }
    
    def get_communities(self) -> Dict[str, Any]:
        """
        ¿Cómo se agrupa el código?
        
        Pregunta del agente: "¿Qué módulos están fuertemente acoplados?"
        
        Returns:
            {
                "communities": [
                    {"id": 0, "components": ["Auth", "User", "Token"], "size": 3},
                    {"id": 1, "components": ["Product", "Cart"], "size": 2}
                ],
                "count": 2,
                "largest": 3
            }
        """
        metrics = self.kg.calculate_importance_metrics()
        communities = metrics.get('communities', [])
        
        largest = max([c['size'] for c in communities]) if communities else 0
        
        return {
            "communities": communities,
            "count": len(communities),
            "largest": largest,
            "description": f"Sistema organizado en {len(communities)} comunidades/módulos"
        }
    
    def query_graph(self, query: str) -> Dict[str, Any]:
        """
        Pregunta en lenguaje natural al grafo.
        
        Pregunta del agente: "¿Hay ciclos de dependencias?"
        
        Args:
            query: Pregunta en lenguaje natural
            
        Returns:
            Respuesta estructurada según la pregunta
        """
        return self.kg.query_graph(query)
    
    # ═══════════════════════════════════════════════════════════════════════
    # HERRAMIENTAS META (para planificación del agente)
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """
        Lista todas las herramientas disponibles para el agente.
        
        Returns:
            Lista de herramientas con nombre, descripción y parámetros
        """
        return [
            {
                "name": "get_dependencies",
                "description": "¿De qué depende este componente?",
                "params": ["class_name: str"],
                "example": 'get_dependencies("UserRepository")'
            },
            {
                "name": "find_callers",
                "description": "¿Quién usa este método/clase?",
                "params": ["method_name: str"],
                "example": 'find_callers("authenticate")'
            },
            {
                "name": "get_module_structure",
                "description": "¿Cómo está organizado este módulo?",
                "params": ["module: Optional[str]"],
                "example": 'get_module_structure("auth")'
            },
            {
                "name": "analyze_design_patterns",
                "description": "¿Qué patrones usa este componente?",
                "params": ["component: str"],
                "example": 'analyze_design_patterns("UserController")'
            },
            {
                "name": "explore_impact",
                "description": "¿Qué impacto tendría modificar este componente?",
                "params": ["node_name: str", "max_depth: int = 2"],
                "example": 'explore_impact("Database", max_depth=3)'
            },
            {
                "name": "find_path",
                "description": "¿Cómo se conectan dos componentes?",
                "params": ["source: str", "target: str"],
                "example": 'find_path("Controller", "Database")'
            },
            {
                "name": "get_critical_nodes",
                "description": "¿Cuáles son los componentes más críticos?",
                "params": ["top_n: int = 5"],
                "example": 'get_critical_nodes(10)'
            },
            {
                "name": "get_communities",
                "description": "¿Cómo se agrupa el código?",
                "params": [],
                "example": 'get_communities()'
            },
            {
                "name": "query_graph",
                "description": "Pregunta en lenguaje natural al grafo",
                "params": ["query: str"],
                "example": 'query_graph("¿Hay ciclos de dependencias?")'
            }
        ]
    
    def summarize_graph(self) -> Dict[str, Any]:
        """
        Resumen ejecutivo del grafo para el agente.
        
        Returns:
            Estadísticas clave y recomendaciones
        """
        metrics = self.kg.calculate_importance_metrics()
        
        return {
            "total_nodes": metrics.get('total_nodes', 0),
            "total_edges": metrics.get('total_edges', 0),
            "communities": metrics.get('num_communities', 0),
            "top_important": [c['node'] for c in metrics.get('important_components', [])[:3]],
            "top_bottlenecks": [c['node'] for c in metrics.get('bottleneck_components', [])[:3]],
            "top_hubs": [c['node'] for c in metrics.get('hub_components', [])[:3]],
            "description": f"Sistema con {metrics.get('total_nodes', 0)} componentes organizados en {metrics.get('num_communities', 0)} módulos"
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def to_json(self, data: Dict) -> str:
        """Serializa respuesta a JSON para el agente."""
        return json.dumps(data, indent=2, ensure_ascii=False)

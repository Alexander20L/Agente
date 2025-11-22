"""
Knowledge Graph - Grafo de Conocimiento para Análisis de Proyectos
Representa el proyecto como un grafo dirigido usando NetworkX.
Incluye análisis de dependencias, métricas de calidad y recomendaciones.
"""

try:
    import networkx as nx
except ImportError:
    print("⚠️  NetworkX no instalado. Ejecuta: pip install networkx")
    raise

import json
import re
import os
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class KnowledgeGraph:
    """
    Grafo de conocimiento que representa la estructura y relaciones de un proyecto.
    """
    
    def __init__(self):
        """Inicializa el grafo dirigido."""
        self.graph = nx.DiGraph()
    
    # ===== MÉTODOS DE CONSTRUCCIÓN =====
    
    def add_node(self, node_id: str, node_type: str, **attributes):
        """Agrega un nodo al grafo."""
        self.graph.add_node(node_id, node_type=node_type, **attributes)
    
    def add_component(self, name: str, container: str, comp_type: str, **attributes):
        """Agrega un componente."""
        self.graph.add_node(
            name,
            node_type="component",
            container=container,
            comp_type=comp_type,
            **attributes
        )
    
    def add_module(self, name: str, **attributes):
        """Agrega un módulo."""
        self.graph.add_node(name, node_type="module", **attributes)
    
    def add_class(self, name: str, module: str, **attributes):
        """Agrega una clase."""
        self.graph.add_node(name, node_type="class", module=module, **attributes)
    
    def add_function(self, name: str, module: str, **attributes):
        """Agrega una función."""
        self.graph.add_node(name, node_type="function", module=module, **attributes)
    
    # ===== MÉTODOS DE RELACIONES =====
    
    def add_dependency(self, from_node: str, to_node: str, dep_type: str = "depends", **attributes):
        """Agrega una dependencia entre nodos."""
        if from_node in self.graph.nodes() and to_node in self.graph.nodes():
            self.graph.add_edge(from_node, to_node, relation=dep_type, **attributes)
    
    def add_call(self, caller: str, callee: str, **attributes):
        """Agrega una llamada de función."""
        if caller in self.graph.nodes() and callee in self.graph.nodes():
            self.graph.add_edge(caller, callee, relation="calls", **attributes)
    
    def add_inheritance(self, child: str, parent: str, **attributes):
        """Agrega una relación de herencia."""
        if child in self.graph.nodes() and parent in self.graph.nodes():
            self.graph.add_edge(child, parent, relation="inherits", **attributes)
    
    # ===== MÉTODOS DE ANÁLISIS =====
    
    def calculate_metrics(self) -> Dict:
        """Calcula métricas generales del grafo."""
        metrics = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": defaultdict(int),
            "component_types": defaultdict(int),
            "avg_dependencies": 0,
            "max_dependencies": 0
        }
        
        # Contar tipos de nodos
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get("node_type", "unknown")
            metrics["node_types"][node_type] += 1
            
            if node_type == "component":
                comp_type = self.graph.nodes[node].get("comp_type", "unknown")
                metrics["component_types"][comp_type] += 1
        
        # Calcular dependencias
        if metrics["total_nodes"] > 0:
            degrees = [self.graph.out_degree(n) for n in self.graph.nodes()]
            metrics["avg_dependencies"] = sum(degrees) / len(degrees)
            metrics["max_dependencies"] = max(degrees) if degrees else 0
        
        return dict(metrics)
    
    def detect_cycles(self) -> List[List[str]]:
        """Detecta ciclos de dependencias."""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []
    
    def find_critical_nodes(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Encuentra nodos críticos usando PageRank."""
        if self.graph.number_of_nodes() == 0:
            return []
        
        try:
            pagerank = nx.pagerank(self.graph)
            sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
            return sorted_nodes[:top_n]
        except:
            return []
    
    def find_bottlenecks(self) -> List[str]:
        """Encuentra cuellos de botella (nodos con alto in-degree)."""
        bottlenecks = []
        avg_in_degree = sum(d for n, d in self.graph.in_degree()) / max(self.graph.number_of_nodes(), 1)
        
        for node, in_degree in self.graph.in_degree():
            if in_degree > avg_in_degree * 2:
                bottlenecks.append(node)
        
        return bottlenecks
    
    def calculate_layer_depth(self) -> Dict[str, int]:
        """Calcula la profundidad de capas."""
        if not nx.is_directed_acyclic_graph(self.graph):
            return {}
        
        try:
            layers = {}
            for node in nx.topological_sort(self.graph):
                predecessors = list(self.graph.predecessors(node))
                if not predecessors:
                    layers[node] = 0
                else:
                    layers[node] = max(layers.get(p, 0) for p in predecessors) + 1
            return layers
        except:
            return {}
    
    def calculate_importance_metrics(self) -> Dict:
        """
        Calcula métricas de importancia basadas en teoría de grafos
        - PageRank: componentes más importantes/referenciados
        - Betweenness: cuellos de botella/puntos críticos
        - Clustering: detección de comunidades/módulos
        """
        if self.graph.number_of_nodes() == 0:
            return {
                'important_components': [],
                'bottlenecks': [],
                'clusters': [],
                'hub_components': []
            }
        
        # PageRank: importancia basada en referencias
        # Forzar implementación Python pura (no scipy)
        try:
            from networkx.algorithms.link_analysis.pagerank_alg import _pagerank_python
            pagerank = _pagerank_python(self.graph, alpha=0.85, max_iter=100, tol=1e-06)
        except:
            # Si falla, usar degree centrality normalizado como proxy
            degrees = dict(self.graph.degree())
            max_degree = max(degrees.values()) if degrees else 1
            pagerank = {node: degree / max_degree for node, degree in degrees.items()}
        important = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Betweenness: componentes que conectan muchos otros
        betweenness = nx.betweenness_centrality(self.graph)
        bottlenecks = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Degree centrality: componentes con más conexiones directas
        degree_cent = dict(self.graph.degree())
        hubs = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Clustering: detección de comunidades (requiere grafo no dirigido)
        clusters = []
        try:
            undirected = self.graph.to_undirected()
            if undirected.number_of_edges() > 0:
                # Intentar Louvain (requiere scipy)
                try:
                    communities = nx.community.louvain_communities(undirected, seed=42)
                    clusters = [list(c) for c in communities]
                except (ImportError, AttributeError):
                    # Fallback: usar componentes conectados (no requiere scipy)
                    components = list(nx.connected_components(undirected))
                    clusters = [list(c) for c in components if len(c) > 1]
        except:
            pass
        
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'num_communities': len(clusters),
            'important_components': [
                {'node': name, 'score': float(score)} 
                for name, score in important
            ],
            'bottleneck_components': [
                {'node': name, 'score': float(score)} 
                for name, score in bottlenecks
            ],
            'hub_components': [
                {'node': name, 'connections': connections} 
                for name, connections in hubs
            ],
            'communities': [
                {'id': i, 'components': cluster, 'size': len(cluster)}
                for i, cluster in enumerate(clusters)
            ]
        }
    
    def analyze_dependencies(self) -> Dict:
        """
        Analiza dependencias y calcula métricas de calidad.
        Integra funcionalidad de dependency_analyzer.
        """
        analysis = {
            'cycles': self._analyze_cycles(),
            'coupling': self._analyze_coupling(),
            'cohesion': self._analyze_cohesion(),
            'complexity': self._analyze_complexity(),
            'issues': [],
            'recommendations': []
        }
        
        # Generar recomendaciones
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_cycles(self) -> Dict:
        """Detecta y evalúa ciclos de dependencias."""
        cycles = self.detect_cycles()
        
        result = {
            'total_cycles': len(cycles),
            'cycles': [],
            'severity': 'none'
        }
        
        for cycle in cycles:
            severity = 'high' if len(cycle) == 2 else 'medium' if len(cycle) <= 4 else 'low'
            result['cycles'].append({
                'nodes': cycle,
                'length': len(cycle),
                'severity': severity
            })
        
        if len(cycles) == 0:
            result['severity'] = 'none'
        elif len(cycles) <= 2:
            result['severity'] = 'low'
        elif len(cycles) <= 5:
            result['severity'] = 'medium'
        else:
            result['severity'] = 'high'
        
        return result
    
    def _analyze_coupling(self) -> Dict:
        """Calcula métricas de acoplamiento."""
        modules = [n for n in self.graph.nodes() 
                  if self.graph.nodes[n].get('node_type') == 'module']
        
        coupling_data = {}
        
        for module in modules:
            ca = len([n for n in self.graph.predecessors(module)])  # Afferent
            ce = len([n for n in self.graph.successors(module)])    # Efferent
            total = ca + ce
            instability = ce / total if total > 0 else 0
            
            coupling_data[module] = {
                'afferent_coupling': ca,
                'efferent_coupling': ce,
                'instability': round(instability, 2),
                'stability': round(1 - instability, 2)
            }
        
        if coupling_data:
            avg_ca = sum(d['afferent_coupling'] for d in coupling_data.values()) / len(coupling_data)
            avg_ce = sum(d['efferent_coupling'] for d in coupling_data.values()) / len(coupling_data)
            avg_instability = sum(d['instability'] for d in coupling_data.values()) / len(coupling_data)
        else:
            avg_ca = avg_ce = avg_instability = 0
        
        return {
            'modules': coupling_data,
            'averages': {
                'afferent_coupling': round(avg_ca, 2),
                'efferent_coupling': round(avg_ce, 2),
                'instability': round(avg_instability, 2)
            }
        }
    
    def _analyze_cohesion(self) -> Dict:
        """Calcula cohesión de módulos."""
        modules = [n for n in self.graph.nodes() 
                  if self.graph.nodes[n].get('node_type') == 'module']
        
        cohesion_data = {}
        
        for module in modules:
            children = [n for n in self.graph.successors(module)
                       if self.graph.edges[module, n].get('relation') == 'contains']
            
            if len(children) == 0:
                cohesion_data[module] = {'cohesion_score': 0, 'component_count': 0}
                continue
            
            internal_edges = sum(1 for c1 in children for c2 in children 
                               if c1 != c2 and self.graph.has_edge(c1, c2))
            
            max_edges = len(children) * (len(children) - 1)
            cohesion_score = internal_edges / max_edges if max_edges > 0 else 0
            
            cohesion_data[module] = {
                'cohesion_score': round(cohesion_score, 2),
                'component_count': len(children),
                'internal_connections': internal_edges
            }
        
        avg_cohesion = sum(d['cohesion_score'] for d in cohesion_data.values()) / len(cohesion_data) if cohesion_data else 0
        
        return {
            'modules': cohesion_data,
            'average_cohesion': round(avg_cohesion, 2)
        }
    
    def _analyze_complexity(self) -> Dict:
        """Calcula métricas de complejidad."""
        edges = self.graph.number_of_edges()
        nodes = self.graph.number_of_nodes()
        
        if nodes == 0:
            return {
                'cyclomatic_complexity': 0,
                'max_depth': 0,
                'avg_fanout': 0,
                'max_fanout': 0,
                'total_components': 0
            }
        
        connected_components = nx.number_weakly_connected_components(self.graph)
        cyclomatic = edges - nodes + 2 * connected_components
        
        try:
            longest_path = nx.dag_longest_path_length(self.graph) if nx.is_directed_acyclic_graph(self.graph) else 0
        except:
            longest_path = 0
        
        out_degrees = [self.graph.out_degree(n) for n in self.graph.nodes()]
        avg_fanout = sum(out_degrees) / len(out_degrees) if out_degrees else 0
        max_fanout = max(out_degrees) if out_degrees else 0
        
        return {
            'cyclomatic_complexity': max(0, cyclomatic),
            'max_depth': longest_path,
            'avg_fanout': round(avg_fanout, 2),
            'max_fanout': max_fanout,
            'total_components': connected_components
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        cycles = analysis['cycles']
        if cycles['total_cycles'] > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'architecture',
                'title': 'Romper Ciclos de Dependencias',
                'description': f"Se encontraron {cycles['total_cycles']} ciclos. Considere usar inversión de dependencias o extraer interfaces.",
                'affected_count': cycles['total_cycles']
            })
        
        coupling = analysis['coupling']
        high_coupling = [m for m, d in coupling['modules'].items() if d['efferent_coupling'] > 10]
        if high_coupling:
            recommendations.append({
                'priority': 'medium',
                'category': 'coupling',
                'title': 'Reducir Acoplamiento Eferente',
                'description': f"{len(high_coupling)} módulos dependen de demasiados otros. Considere patrón facade o agregación de servicios.",
                'affected_count': len(high_coupling)
            })
        
        cohesion = analysis['cohesion']
        if cohesion['average_cohesion'] < 0.3:
            recommendations.append({
                'priority': 'medium',
                'category': 'cohesion',
                'title': 'Mejorar Cohesión de Módulos',
                'description': f"Cohesión promedio baja ({cohesion['average_cohesion']:.2f}). Considere dividir en módulos más enfocados.",
                'affected_count': len([m for m, d in cohesion['modules'].items() if d['cohesion_score'] < 0.3])
            })
        
        return recommendations
    
    # ===== MÉTODOS DE VISUALIZACIÓN =====
    
    def visualize_stats(self) -> str:
        """Genera un resumen textual del grafo."""
        metrics = self.calculate_metrics()
        cycles = self.detect_cycles()
        critical = self.find_critical_nodes(5)
        bottlenecks = self.find_bottlenecks()
        
        stats = []
        stats.append("=" * 60)
        stats.append("KNOWLEDGE GRAPH STATISTICS")
        stats.append("=" * 60)
        stats.append(f"Total Nodes: {metrics['total_nodes']}")
        stats.append(f"Total Edges: {metrics['total_edges']}")
        stats.append(f"\nNode Types:")
        for ntype, count in metrics['node_types'].items():
            stats.append(f"  - {ntype}: {count}")
        stats.append(f"\nComponent Types:")
        for ctype, count in metrics['component_types'].items():
            stats.append(f"  - {ctype}: {count}")
        stats.append(f"\nDependency Metrics:")
        stats.append(f"  - Average dependencies per node: {metrics['avg_dependencies']:.2f}")
        stats.append(f"  - Max dependencies: {metrics['max_dependencies']}")
        stats.append(f"\nComplexity:")
        stats.append(f"  - Dependency cycles detected: {len(cycles)}")
        if cycles:
            stats.append(f"  - First 3 cycles:")
            for i, cycle in enumerate(cycles[:3], 1):
                stats.append(f"    {i}. {' -> '.join(cycle[:5])}")
        stats.append(f"\nCritical Nodes (top 5):")
        for node, score in critical:
            stats.append(f"  - {node}: {score:.4f}")
        stats.append(f"\nBottlenecks: {len(bottlenecks)}")
        if bottlenecks:
            for bn in bottlenecks[:5]:
                stats.append(f"  - {bn}")
        stats.append("=" * 60)
        
        return "\n".join(stats)
    
    def export_to_json(self) -> Dict:
        """Exporta el grafo a formato JSON."""
        data = {
            "nodes": [],
            "edges": []
        }
        
        for node in self.graph.nodes():
            node_data = {"id": node}
            node_data.update(self.graph.nodes[node])
            data["nodes"].append(node_data)
        
        for src, dst in self.graph.edges():
            edge_data = {"from": src, "to": dst}
            edge_data.update(self.graph.edges[src, dst])
            data["edges"].append(edge_data)
        
        return data
    
    # ===== HERRAMIENTAS PARA AGENTES (FASE 1) =====
    
    def get_dependencies(self, node_name: str) -> List[str]:
        """
        Herramienta: ¿Qué depende de este nodo?
        Retorna todos los nodos que este nodo usa/importa/llama.
        """
        if node_name not in self.graph.nodes():
            # Buscar por nombre parcial
            matches = [n for n in self.graph.nodes() if node_name in n]
            if not matches:
                return []
            node_name = matches[0]
        
        return list(self.graph.successors(node_name))
    
    def find_callers(self, node_name: str) -> List[str]:
        """
        Herramienta: ¿Quién usa/llama a este nodo?
        Retorna todos los nodos que dependen de este.
        """
        if node_name not in self.graph.nodes():
            # Buscar por nombre parcial
            matches = [n for n in self.graph.nodes() if node_name in n]
            if not matches:
                return []
            node_name = matches[0]
        
        return list(self.graph.predecessors(node_name))
    
    def get_module_structure(self, module: str = None) -> Dict:
        """
        Herramienta: Obtiene la estructura de un módulo específico.
        Si module=None, retorna estructura general del proyecto.
        """
        if module:
            nodes = [n for n in self.graph.nodes() 
                    if self.graph.nodes[n].get('module') == module or module in n]
        else:
            nodes = list(self.graph.nodes())[:50]  # Top 50 nodos
        
        structure = {
            "module": module or "project",
            "total_nodes": len(nodes),
            "classes": [],
            "functions": [],
            "components": [],
            "dependencies": []
        }
        
        for node in nodes:
            node_type = self.graph.nodes[node].get('node_type', '')
            if node_type == 'class':
                structure["classes"].append({
                    "name": node,
                    "methods": len(list(self.graph.successors(node)))
                })
            elif node_type == 'function':
                structure["functions"].append({
                    "name": node,
                    "calls": len(list(self.graph.successors(node)))
                })
            elif node_type == 'component':
                structure["components"].append({
                    "name": node,
                    "type": self.graph.nodes[node].get('comp_type', 'unknown')
                })
        
        # Dependencias internas del módulo
        for src, dst in self.graph.edges():
            if src in nodes and dst in nodes:
                structure["dependencies"].append({
                    "from": src,
                    "to": dst,
                    "type": self.graph.edges[src, dst].get('relation', 'uses')
                })
        
        return structure
    
    def analyze_design_patterns(self, component: str) -> Dict:
        """
        Herramienta: Detecta patrones de diseño comunes.
        Analiza la estructura del componente para identificar patrones.
        """
        if component not in self.graph.nodes():
            # Buscar por nombre parcial
            matches = [n for n in self.graph.nodes() if component in n]
            if not matches:
                return {"component": component, "found": False, "patterns": []}
            component = matches[0]
        
        patterns = []
        node_type = self.graph.nodes[component].get('node_type', '')
        
        # Análisis de patrones
        successors = list(self.graph.successors(component))
        predecessors = list(self.graph.predecessors(component))
        
        # Singleton: Clase con pocos o ningún hijo, muchos la usan
        if node_type == 'class' and len(predecessors) > 5 and len(successors) <= 2:
            patterns.append({
                "pattern": "Singleton",
                "confidence": "medium",
                "reason": f"{len(predecessors)} callers, {len(successors)} dependencies"
            })
        
        # Factory/Builder: Muchas clases dependen
        if len(predecessors) > 8:
            patterns.append({
                "pattern": "Factory/Builder",
                "confidence": "medium",
                "reason": f"High coupling: {len(predecessors)} dependents"
            })
        
        # Repository: Contiene "repository" en el nombre y tiene dependencias a DB
        if 'repository' in component.lower() or 'repo' in component.lower():
            patterns.append({
                "pattern": "Repository",
                "confidence": "high",
                "reason": "Naming convention + data access pattern"
            })
        
        # Service/Controller: Alto fan-out
        if len(successors) > 10:
            patterns.append({
                "pattern": "Service/Orchestrator",
                "confidence": "medium",
                "reason": f"High fan-out: {len(successors)} dependencies"
            })
        
        return {
            "component": component,
            "found": True,
            "node_type": node_type,
            "patterns": patterns,
            "metrics": {
                "dependencies_out": len(successors),
                "dependencies_in": len(predecessors),
                "complexity": len(successors) + len(predecessors)
            }
        }
    
    def find_path(self, source: str, target: str) -> List[str]:
        """
        Herramienta: Encuentra el camino de dependencias entre dos nodos.
        Útil para entender cómo se conectan dos componentes.
        """
        # Buscar nodos por nombre parcial
        source_node = None
        target_node = None
        
        for node in self.graph.nodes():
            if source in node:
                source_node = node
            if target in node:
                target_node = node
        
        if not source_node or not target_node:
            return []
        
        try:
            path = nx.shortest_path(self.graph, source_node, target_node)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def get_node_info(self, node_name: str) -> Dict:
        """
        Herramienta: Obtiene información detallada de un nodo específico.
        """
        if node_name not in self.graph.nodes():
            # Buscar por nombre parcial
            matches = [n for n in self.graph.nodes() if node_name in n]
            if not matches:
                return {"found": False, "searched": node_name}
            node_name = matches[0]
        
        node_data = dict(self.graph.nodes[node_name])
        
        return {
            "found": True,
            "name": node_name,
            "attributes": node_data,
            "dependencies_out": list(self.graph.successors(node_name)),
            "dependencies_in": list(self.graph.predecessors(node_name)),
            "degree_out": self.graph.out_degree(node_name),
            "degree_in": self.graph.in_degree(node_name)
        }
    
    def query_graph(self, question: str) -> Dict:
        """
        Herramienta universal: Interfaz de lenguaje natural para consultar el grafo.
        Analiza la pregunta y ejecuta la herramienta apropiada.
        """
        question_lower = question.lower()
        
        # Extraer entidad de la pregunta
        words = question.split()
        entity = None
        for word in words:
            if word[0].isupper() or '_' in word:  # Nombres de clases/funciones
                entity = word
                break
        
        result = {
            "question": question,
            "understood": True,
            "answer": None
        }
        
        # Pattern matching de preguntas comunes
        if any(kw in question_lower for kw in ["depend", "use", "import", "call"]):
            if entity:
                result["answer"] = {
                    "type": "dependencies",
                    "data": self.get_dependencies(entity)
                }
        
        elif any(kw in question_lower for kw in ["who", "caller", "used by"]):
            if entity:
                result["answer"] = {
                    "type": "callers",
                    "data": self.find_callers(entity)
                }
        
        elif any(kw in question_lower for kw in ["structure", "module", "component"]):
            module_name = entity if entity else None
            result["answer"] = {
                "type": "structure",
                "data": self.get_module_structure(module_name)
            }
        
        elif any(kw in question_lower for kw in ["pattern", "design"]):
            if entity:
                result["answer"] = {
                    "type": "patterns",
                    "data": self.analyze_design_patterns(entity)
                }
        
        elif any(kw in question_lower for kw in ["path", "connect", "reach"]):
            # Extraer dos entidades
            entities = [w for w in words if w[0].isupper() or '_' in w]
            if len(entities) >= 2:
                result["answer"] = {
                    "type": "path",
                    "data": self.find_path(entities[0], entities[1])
                }
        
        elif any(kw in question_lower for kw in ["info", "detail", "about"]):
            if entity:
                result["answer"] = {
                    "type": "info",
                    "data": self.get_node_info(entity)
                }
        
        else:
            result["understood"] = False
            result["answer"] = {
                "type": "help",
                "data": "Try: 'What depends on X?', 'Who calls X?', 'Show structure of X', 'Find patterns in X'"
            }
        
        return result


# ===== FUNCIONES DE CONSTRUCCIÓN =====

def build_knowledge_graph_from_analysis(analysis_result: dict):
    """
    Construye un grafo de conocimiento desde el resultado del análisis estático.
    """
    kg = KnowledgeGraph()
    
    # Agregar contenedores
    for container in analysis_result.get("containers_detected", []):
        node_id = container["path"]
        kg.graph.add_node(
            node_id,
            node_type="container",
            name=container.get("type", "Container"),
            technology=container.get("technology", ""),
            path=container.get("path"),
            confidence=container.get("confidence", ""),
            score=container.get("score", 0)
        )
    
    # Agregar componentes
    for comp in analysis_result.get("components_detected", []):
        node_id = comp["path"]
        kg.graph.add_node(
            node_id,
            node_type="component",
            name=comp["name"],
            comp_type=comp["type"],
            classes=comp.get("classes", []),
            entry_points=comp.get("entry_points", []),
            path=comp["path"]
        )
        
        # Asignar componente a contenedor
        for container in analysis_result.get("containers_detected", []):
            cont_path = container["path"]
            if node_id.startswith(cont_path):
                kg.graph.add_edge(cont_path, node_id, relation="contains")
    
    # Agregar relaciones
    for rel in analysis_result.get("relations_detected", []):
        src = rel["from"]
        dst = rel["to"]
        
        # Buscar nodos correspondientes
        src_node = None
        dst_node = None
        
        for comp in analysis_result.get("components_detected", []):
            if comp["name"] == src:
                src_node = comp["path"]
            if comp["name"] == dst or dst in comp["path"]:
                dst_node = comp["path"]
        
        if src_node and dst_node:
            kg.graph.add_edge(src_node, dst_node, relation="imports")
    
    return kg


def enhance_graph_with_code_analysis(kg, analysis_result: dict):
    """
    Enriquece el grafo extrayendo información adicional del código fuente.
    Análisis simple con regex (sin dependencias externas).
    """
    project_path = analysis_result.get('project_path', '')
    
    if not project_path or not os.path.exists(project_path):
        return kg
    
    # Analizar archivos Python
    for root, dirs, files in os.walk(project_path):
        # Excluir directorios no deseados
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', 'node_modules', '.git', 'uploads']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                module_name = file.replace('.py', '')
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Extraer clases y métodos
                    _extract_classes_and_methods(kg, module_name, content)
                    
                    # Extraer llamadas de función
                    _extract_function_calls(kg, module_name, content)
                    
                except Exception:
                    continue
    
    return kg


def _extract_classes_and_methods(kg, module: str, content: str):
    """Extrae clases y métodos con regex."""
    # Buscar clases
    class_pattern = r'^\s*class\s+([A-Za-z_]\w*)\s*(?:\(([^)]*)\))?:'
    for match in re.finditer(class_pattern, content, re.MULTILINE):
        class_name = match.group(1)
        bases = match.group(2)
        
        kg.add_class(class_name, module, {'bases': bases.split(',') if bases else []})
        
        # Si tiene herencia, agregar relación
        if bases:
            for base in bases.split(','):
                base = base.strip()
                if base and base not in ['object', 'Exception']:
                    try:
                        kg.add_inheritance(f"{module}.{class_name}", base)
                    except:
                        pass
    
    # Buscar funciones/métodos
    func_pattern = r'^\s*def\s+([A-Za-z_]\w*)\s*\('
    for match in re.finditer(func_pattern, content, re.MULTILINE):
        func_name = match.group(1)
        kg.add_function(func_name, module)


def _extract_function_calls(kg, module: str, content: str):
    """Extrae llamadas de función con regex."""
    # Buscar patrones de llamada comunes
    call_pattern = r'([A-Za-z_]\w*)\s*\('
    
    # Limitar para evitar demasiados falsos positivos
    matches = list(re.finditer(call_pattern, content))[:100]
    
    for match in matches:
        func_name = match.group(1)
        # Filtrar palabras clave de Python
        if func_name not in ['if', 'for', 'while', 'def', 'class', 'return', 'import', 'from', 'print']:
            # Intentar agregar la llamada si ambos nodos existen
            try:
                kg.add_call(f"{module}.{func_name}", func_name)
            except:
                pass

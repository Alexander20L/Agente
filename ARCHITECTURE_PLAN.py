"""
PLAN DE MEJORA: Análisis Estático → Grafos → IA para Mermaid

FLUJO ACTUAL:
1. analyzer.py → extrae componentes, relaciones (análisis estático) ✅
2. knowledge_graph.py → representa como grafo (NetworkX) ⚠️ SUBUTILIZADO
3. semantic_reasoner.py → genera Mermaid con IA ✅

PROBLEMAS IDENTIFICADOS:
- El grafo NO se está usando para mejorar el análisis
- El analyzer devuelve listas simples, no un grafo rico
- La IA recibe datos planos, no aprovecha estructura de grafo
- No hay análisis de métricas de grafo (centralidad, clustering, etc.)

MEJORAS A IMPLEMENTAR:
1. analyzer.py → popula KnowledgeGraph directamente
2. KnowledgeGraph → calcula métricas de grafo (PageRank, betweenness)
3. semantic_reasoner.py → recibe grafo estructurado con métricas
4. IA genera Mermaid usando información rica del grafo

OBJETIVO:
Que el GRAFO sea el centro del análisis, no solo una representación alternativa
"""

import os
import json
from core.analyzer import analyze_project
from core.knowledge_graph import KnowledgeGraph

def demonstrate_current_flow():
    """Demuestra el flujo actual y sus limitaciones"""
    
    print("🔍 ANÁLISIS DEL FLUJO ACTUAL")
    print("=" * 70)
    
    # 1. Análisis estático (analyzer.py)
    print("\n1️⃣ ANÁLISIS ESTÁTICO (analyzer.py)")
    print("   Input: Código fuente")
    print("   Output: Dict con listas de componentes y relaciones")
    print("   ✅ Funciona bien: extrae componentes, relaciones, tecnologías")
    print("   ⚠️  Problema: Datos planos, sin estructura de grafo")
    
    # 2. Knowledge Graph (subutilizado)
    print("\n2️⃣ KNOWLEDGE GRAPH (knowledge_graph.py)")
    print("   Input: Nada (no se usa en el flujo principal)")
    print("   Output: Grafo NetworkX")
    print("   ❌ Problema: NO se integra con analyzer.py")
    print("   ❌ Problema: NO se usa para generar diagramas")
    print("   ❌ Problema: Métricas de grafo no se calculan")
    
    # 3. Semantic Reasoner (IA)
    print("\n3️⃣ SEMANTIC REASONER (semantic_reasoner.py)")
    print("   Input: Dict plano de analyzer.py")
    print("   Output: Código Mermaid generado por IA")
    print("   ✅ Funciona: genera diagramas con IA")
    print("   ⚠️  Limitación: No aprovecha información de grafo")
    
    print("\n" + "=" * 70)
    print("📊 DIAGNÓSTICO:")
    print("=" * 70)
    print("""
El sistema tiene 3 piezas independientes que NO se comunican:
    
    analyzer.py ─────┐
                     ├──> Dict plano ──> semantic_reasoner.py ──> Mermaid
    knowledge_graph  │
    (no se usa) ─────┘

DEBERÍA SER:

    analyzer.py ──> KnowledgeGraph (grafo rico con métricas)
                           │
                           ├──> Análisis de centralidad
                           ├──> Detección de comunidades
                           ├──> Componentes críticos
                           │
                           v
                    semantic_reasoner.py ──> Mermaid mejorado
                    (con info de importancia,
                     clusters, cuellos de botella)
    """)

def propose_improvements():
    """Propone mejoras concretas"""
    
    print("\n🎯 MEJORAS PROPUESTAS")
    print("=" * 70)
    
    print("\n✅ MEJORA 1: Integrar analyzer → KnowledgeGraph")
    print("""
# En analyzer.py, agregar:
def build_knowledge_graph(analysis_result):
    kg = KnowledgeGraph()
    
    # Agregar componentes como nodos
    for comp in analysis_result['components_detected']:
        kg.add_component(comp['name'], comp['type'])
    
    # Agregar relaciones como edges
    for rel in analysis_result['relations_detected']:
        kg.add_dependency(rel['from'], rel['to'])
    
    return kg
    """)
    
    print("\n✅ MEJORA 2: Calcular métricas de grafo importantes")
    print("""
# En knowledge_graph.py, agregar:
def calculate_importance_metrics(self):
    # PageRank: qué componentes son más importantes
    pagerank = nx.pagerank(self.graph)
    
    # Betweenness: qué componentes son cuellos de botella
    betweenness = nx.betweenness_centrality(self.graph)
    
    # Clustering: qué componentes están agrupados
    communities = nx.community.louvain_communities(self.graph.to_undirected())
    
    return {
        'important_components': sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10],
        'bottlenecks': sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5],
        'clusters': [list(c) for c in communities]
    }
    """)
    
    print("\n✅ MEJORA 3: Pasar grafo estructurado a IA")
    print("""
# En semantic_reasoner.py, mejorar prompt:
prompt = f'''
Genera un diagrama C4 considerando:

COMPONENTES IMPORTANTES (PageRank):
{kg.get_important_components()}

CUELLOS DE BOTELLA (Betweenness):
{kg.get_bottlenecks()}

CLUSTERS DETECTADOS:
{kg.get_clusters()}

Esto ayuda a la IA a priorizar qué mostrar en el diagrama.
'''
    """)
    
    print("\n✅ MEJORA 4: Validar diagramas con grafo")
    print("""
# Después de que IA genera Mermaid, validar:
def validate_diagram_with_graph(mermaid_code, knowledge_graph):
    # Extraer nodos del diagrama Mermaid
    diagram_nodes = extract_nodes_from_mermaid(mermaid_code)
    
    # Verificar que incluye componentes importantes
    important = kg.get_important_components()
    missing = [n for n in important if n not in diagram_nodes]
    
    if missing:
        return {"valid": False, "missing_important": missing}
    
    return {"valid": True}
    """)

if __name__ == "__main__":
    demonstrate_current_flow()
    propose_improvements()
    
    print("\n" + "=" * 70)
    print("📋 PRÓXIMOS PASOS:")
    print("=" * 70)
    print("""
1. [ ] Crear método build_knowledge_graph() en analyzer.py
2. [ ] Agregar calculate_importance_metrics() en knowledge_graph.py
3. [ ] Modificar semantic_reasoner.py para recibir KnowledgeGraph
4. [ ] Agregar validación de diagramas con grafo
5. [ ] Actualizar endpoints API para usar flujo mejorado
    """)

"""
🤖 DEMO: Agente IA Navegando el Knowledge Graph
═══════════════════════════════════════════════════════════════════════════════

Simula un agente IA que toma decisiones sobre qué explorar en el grafo
según su objetivo: "Entender la arquitectura del proyecto"

Demuestra el enfoque: Análisis Estático + Grafo de Conocimiento (IDEAL)
"""

import json
from pathlib import Path
from core.analyzer import analyze_project
from core.agent_tools import AgentTools


def simulate_agent_exploration():
    """
    Simula un agente IA explorando el Knowledge Graph de manera inteligente.
    
    Objetivo del agente: Entender la arquitectura del proyecto Spring PetClinic
    """
    
    print("=" * 80)
    print("🤖 AGENTE IA: Explorando Spring PetClinic")
    print("=" * 80)
    
    # Paso 1: Agente analiza el proyecto
    print("\n[AGENTE] 🔍 Paso 1: Analizando el proyecto...")
    zip_path = "spring-petclinic.zip"
    
    if not Path(zip_path).exists():
        print("❌ Error: spring-petclinic.zip no encontrado")
        return
    
    result = analyze_project(zip_path)
    tools = AgentTools(result["knowledge_graph"])
    
    print(f"[AGENTE] ✅ Análisis completado:")
    print(f"   - {result['project_name']} ({result['project_type']})")
    print(f"   - {len(result['components_detected'])} componentes detectados")
    
    # Paso 2: Agente obtiene resumen ejecutivo
    print("\n[AGENTE] 📊 Paso 2: Obteniendo resumen ejecutivo...")
    summary = tools.summarize_graph()
    print(f"[AGENTE] 📈 Resumen del grafo:")
    print(f"   - Nodos: {summary['total_nodes']}")
    print(f"   - Aristas: {summary['total_edges']}")
    print(f"   - Comunidades: {summary['communities']}")
    
    # Paso 3: Agente decide explorar componentes críticos
    print("\n[AGENTE] 🎯 Paso 3: Identificando componentes críticos...")
    print("[AGENTE] 💭 Decisión: Necesito saber qué componentes son más importantes")
    
    critical = tools.get_critical_nodes(top_n=5)
    print(f"[AGENTE] 🌟 Top 5 componentes críticos:")
    for i, node in enumerate(critical['critical_nodes'], 1):
        print(f"   {i}. {node['name']} ({node['reason']})")
    
    # Paso 4: Agente explora dependencias del componente más crítico
    most_critical = critical['critical_nodes'][0]['name']
    print(f"\n[AGENTE] 🔗 Paso 4: Explorando '{most_critical}'...")
    print(f"[AGENTE] 💭 Decisión: Este es el componente más importante, ¿de qué depende?")
    
    deps = tools.get_dependencies(most_critical)
    print(f"[AGENTE] 📦 Dependencias de {most_critical}:")
    print(f"   - Total: {deps['count']}")
    print(f"   - Críticas: {deps['critical']}")
    if deps['dependencies']:
        print(f"   - Lista: {', '.join(deps['dependencies'][:5])}")
    
    # Paso 5: Agente explora quién usa este componente
    print(f"\n[AGENTE] 👥 Paso 5: ¿Quién usa '{most_critical}'?")
    print(f"[AGENTE] 💭 Decisión: Necesito saber el impacto de este componente")
    
    callers = tools.find_callers(most_critical)
    print(f"[AGENTE] 📢 Callers de {most_critical}:")
    print(f"   - Total: {callers['count']}")
    print(f"   - Impacto: {callers['impact']}")
    if callers['callers']:
        print(f"   - Primeros 5: {', '.join(callers['callers'][:5])}")
    
    # Paso 6: Agente analiza el impacto de modificar este componente
    print(f"\n[AGENTE] 💥 Paso 6: Analizando impacto de modificar '{most_critical}'")
    print(f"[AGENTE] 💭 Decisión: ¿Qué pasaría si modifico este componente?")
    
    impact = tools.explore_impact(most_critical, max_depth=2)
    print(f"[AGENTE] ⚠️  Análisis de impacto:")
    print(f"   - Impacto directo: {len(impact['direct_impact'])} componentes")
    print(f"   - Impacto indirecto: {len(impact['indirect_impact'])} componentes")
    print(f"   - Total afectado: {impact['total_affected']}")
    print(f"   - Nivel de riesgo: {impact['risk_level']}")
    
    # Paso 7: Agente busca módulos/comunidades
    print(f"\n[AGENTE] 🏗️  Paso 7: Identificando módulos del sistema")
    print(f"[AGENTE] 💭 Decisión: ¿Cómo está organizado el código?")
    
    communities = tools.get_communities()
    print(f"[AGENTE] 📦 Comunidades detectadas: {communities['count']}")
    print(f"   - Comunidad más grande: {communities['largest']} componentes")
    
    # Mostrar top 3 comunidades
    for i, comm in enumerate(communities['communities'][:3], 1):
        print(f"   - Comunidad {i}: {comm['size']} componentes")
        if comm['size'] <= 5:
            print(f"     → {', '.join(comm['components'])}")
    
    # Paso 8: Agente busca un camino entre componentes
    print(f"\n[AGENTE] 🛤️  Paso 8: Buscando conexiones entre componentes")
    print(f"[AGENTE] 💭 Decisión: ¿Cómo se conectan Controller y Repository?")
    
    # Buscar un controller y un repository
    controller = None
    repository = None
    for comp in result['components_detected']:
        if 'Controller' in comp and not controller:
            controller = comp
        if 'Repository' in comp and not repository:
            repository = comp
        if controller and repository:
            break
    
    if controller and repository:
        path = tools.find_path(controller, repository)
        print(f"[AGENTE] 🔗 Camino encontrado:")
        print(f"   - Origen: {path['source']}")
        print(f"   - Destino: {path['target']}")
        print(f"   - Longitud: {path['length']}")
        if path['exists']:
            print(f"   - Ruta: {' → '.join(path['path'])}")
    
    # Paso 9: Agente obtiene estructura de un módulo
    print(f"\n[AGENTE] 📁 Paso 9: Explorando estructura de módulos")
    print(f"[AGENTE] 💭 Decisión: ¿Qué hay dentro del módulo 'owner'?")
    
    structure = tools.get_module_structure("owner")
    print(f"[AGENTE] 🗂️  Estructura del módulo 'owner':")
    print(f"   - Clases: {len(structure.get('classes', []))}")
    print(f"   - Funciones: {len(structure.get('functions', []))}")
    print(f"   - Submódulos: {len(structure.get('submodules', []))}")
    print(f"   - Total elementos: {structure['total_nodes']}")
    
    # Paso 10: Agente analiza patrones de diseño
    if controller:
        print(f"\n[AGENTE] 🎨 Paso 10: Analizando patrones de diseño")
        print(f"[AGENTE] 💭 Decisión: ¿Qué patrones usa '{controller}'?")
        
        patterns = tools.analyze_design_patterns(controller)
        print(f"[AGENTE] 🏛️  Patrones detectados:")
        if patterns.get('patterns'):
            for pattern in patterns['patterns']:
                print(f"   - {pattern}")
    
    # Paso 11: Agente hace una pregunta al grafo
    print(f"\n[AGENTE] ❓ Paso 11: Consultando al grafo")
    print(f"[AGENTE] 💭 Decisión: ¿Hay ciclos de dependencias?")
    
    query_result = tools.query_graph("¿Hay ciclos de dependencias?")
    print(f"[AGENTE] 💡 Respuesta del grafo:")
    print(f"   {json.dumps(query_result, indent=3, ensure_ascii=False)}")
    
    # Paso 12: Agente genera conclusiones
    print("\n" + "=" * 80)
    print("🤖 AGENTE: Conclusiones de la exploración")
    print("=" * 80)
    
    print(f"\n[AGENTE] 📋 He explorado el proyecto usando estas herramientas:")
    available_tools = tools.get_available_tools()
    for i, tool in enumerate(available_tools, 1):
        print(f"   {i}. {tool['name']}: {tool['description']}")
    
    print(f"\n[AGENTE] 🎯 Insights obtenidos:")
    print(f"   1. El componente más crítico es '{most_critical}'")
    print(f"   2. Modificarlo afectaría {impact['total_affected']} componentes")
    print(f"   3. El sistema tiene {communities['count']} módulos bien definidos")
    print(f"   4. Existe conexión entre Controllers y Repositories")
    
    print(f"\n[AGENTE] ✅ Misión completada: Arquitectura entendida")
    print(f"[AGENTE] 💾 Puedo ahora generar diagramas C4 informados por este análisis")
    
    # Guardar reporte
    report = {
        "project": result['project_name'],
        "summary": summary,
        "critical_nodes": critical,
        "most_critical_component": {
            "name": most_critical,
            "dependencies": deps,
            "callers": callers,
            "impact": impact
        },
        "communities": communities,
        "tools_used": [t['name'] for t in available_tools]
    }
    
    with open("agent_exploration_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: agent_exploration_report.json")


def compare_approaches():
    """
    Compara el enfoque de agente vs análisis tradicional.
    """
    print("\n" + "=" * 80)
    print("📊 COMPARACIÓN: Agente vs Análisis Tradicional")
    print("=" * 80)
    
    print("\n❌ ANÁLISIS TRADICIONAL (sin agente):")
    print("   1. Analizar TODO el proyecto (costoso)")
    print("   2. Cargar TODO en memoria (ineficiente)")
    print("   3. Sin priorización (todos los componentes iguales)")
    print("   4. Sin exploración dinámica (path fijo)")
    print("   5. Sin decisiones contextuales")
    
    print("\n✅ ANÁLISIS CON AGENTE (con Knowledge Graph):")
    print("   1. Exploración incremental (solo lo necesario)")
    print("   2. Navegación eficiente (query por demanda)")
    print("   3. Priorización inteligente (PageRank, Betweenness)")
    print("   4. Exploración adaptativa (el agente decide qué explorar)")
    print("   5. Decisiones contextuales (basadas en métricas)")
    
    print("\n🎯 VENTAJAS DEL ENFOQUE CON AGENTE:")
    print("   • Escalabilidad: O(k) queries vs O(n) full scan")
    print("   • Eficiencia: Solo carga lo necesario")
    print("   • Inteligencia: Usa métricas para decisiones")
    print("   • Flexibilidad: El agente adapta su estrategia")
    print("   • Costo: Menos tokens/API calls necesarios")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║  🤖 DEMO: Agente IA Navegando el Knowledge Graph                        ║
    ║                                                                          ║
    ║  Demuestra el enfoque:                                                  ║
    ║  Análisis Estático + Grafo de Conocimiento (IDEAL)                      ║
    ║                                                                          ║
    ║  El agente toma decisiones sobre qué explorar según su objetivo.        ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    simulate_agent_exploration()
    compare_approaches()
    
    print("\n" + "=" * 80)
    print("✅ Demo completada")
    print("=" * 80)

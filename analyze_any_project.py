"""
Analiza CUALQUIER proyecto ZIP y genera diagramas C1, C2, C3
Uso: python analyze_any_project.py <ruta-al-zip>
Ejemplo: python analyze_any_project.py uploads/mi-proyecto.zip
"""

import sys
import os
import json
from core.analyzer import analyze_project
from core.diagram_generator_deterministic import (
    generate_c1_diagram,
    generate_c2_diagram,
    generate_c3_diagram
)

def analyze_and_generate_diagrams(zip_path):
    """Analiza un proyecto y genera sus diagramas"""
    
    print("="*80)
    print("Analizador de Proyectos - Generador de Diagramas C4")
    print("="*80)
    
    # Validar que existe el archivo
    if not os.path.exists(zip_path):
        print(f"\nERROR: No se encontró el archivo: {zip_path}")
        print("\nUso: python analyze_any_project.py <ruta-al-zip>")
        print("Ejemplo: python analyze_any_project.py uploads/mi-proyecto.zip")
        return 1
    
    # Obtener nombre del proyecto
    project_name = os.path.basename(zip_path).replace(".zip", "").replace("-master", "").replace("-main", "")
    
    print(f"\nProyecto: {project_name}")
    print(f"Archivo: {zip_path}")
    print(f"Tamaño: {os.path.getsize(zip_path) / 1024 / 1024:.2f} MB")
    
    # ============================================
    # PASO 1: ANÁLISIS ESTÁTICO
    # ============================================
    print(f"\n{'='*80}")
    print("PASO 1: Análisis Estático")
    print("="*80)
    print("Analizando código fuente...")
    
    try:
        analysis = analyze_project(zip_path)
        
        if analysis.get("error"):
            print(f"\nERROR: {analysis['error']}")
            return 1
        
        # Extraer información
        project_type = analysis.get("project_type", "unknown")
        language = analysis.get("language", "Unknown")
        total_files = analysis.get("total_files", 0)
        components = len(analysis.get("components_detected", []))
        containers = len(analysis.get("containers_detected", []))
        
        print(f"\n✅ Análisis completado:")
        print(f"   - Tipo de proyecto: {project_type}")
        print(f"   - Lenguaje principal: {language}")
        print(f"   - Archivos totales: {total_files}")
        print(f"   - Componentes detectados: {components}")
        print(f"   - Contenedores detectados: {containers}")
        
        # Guardar análisis
        analysis_file = f"analysis_{project_name}.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n📝 Análisis guardado: {analysis_file}")
        
    except Exception as e:
        print(f"\n❌ Error durante análisis: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    # ============================================
    # PASO 2: GENERACIÓN DE DIAGRAMAS
    # ============================================
    print(f"\n{'='*80}")
    print("PASO 2: Generación de Diagramas C4")
    print("="*80)
    print("Generando diagramas C1, C2, C3...")
    
    try:
        # C1 - System Context
        print("\n   >> Generando C1 (System Context)...")
        c1_code = generate_c1_diagram(analysis)
        c1_file = f"{project_name}_c1.mmd"
        with open(c1_file, "w", encoding="utf-8") as f:
            f.write(c1_code)
        print(f"      ✅ {c1_file} ({len(c1_code)} chars)")
        
        # C2 - Container
        print("   >> Generando C2 (Container)...")
        c2_code = generate_c2_diagram(analysis)
        c2_file = f"{project_name}_c2.mmd"
        with open(c2_file, "w", encoding="utf-8") as f:
            f.write(c2_code)
        print(f"      ✅ {c2_file} ({len(c2_code)} chars)")
        
        # C3 - Component
        print("   >> Generando C3 (Component)...")
        c3_code = generate_c3_diagram(analysis)
        c3_file = f"{project_name}_c3.mmd"
        with open(c3_file, "w", encoding="utf-8") as f:
            f.write(c3_code)
        print(f"      ✅ {c3_file} ({len(c3_code)} chars)")
        
        print("\n✨ Diagramas generados exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error generando diagramas: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    # ============================================
    # RESUMEN FINAL
    # ============================================
    print(f"\n{'='*80}")
    print("RESUMEN")
    print("="*80)
    print(f"\n📊 Proyecto analizado: {project_name}")
    print(f"   Tipo: {project_type}")
    print(f"   Lenguaje: {language}")
    print(f"   Componentes: {components}")
    print(f"\n📁 Archivos generados:")
    print(f"   - {analysis_file} (análisis completo)")
    print(f"   - {c1_file} (diagrama C1 - System Context)")
    print(f"   - {c2_file} (diagrama C2 - Container)")
    print(f"   - {c3_file} (diagrama C3 - Component)")
    
    print(f"\n💡 Puedes abrir los archivos .mmd en VS Code con la extensión Mermaid")
    print(f"   o visualizarlos en https://mermaid.live")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("="*80)
        print("Analizador de Proyectos - Generador de Diagramas C4")
        print("="*80)
        print("\nUso: python analyze_any_project.py <ruta-al-zip>")
        print("\nEjemplos:")
        print("  python analyze_any_project.py uploads/mi-proyecto.zip")
        print("  python analyze_any_project.py C:\\Descargas\\proyecto-nuevo.zip")
        print("\nLenguajes soportados:")
        print("  - Python, JavaScript/TypeScript, Java, C#, Go")
        print("  - Rust, PHP, Ruby, Kotlin, Swift, Dart")
        print("\nTipos de proyecto detectados:")
        print("  - web-framework, api-backend, cli-tool, library")
        print("  - gui-application, mobile-app, microservice")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    sys.exit(analyze_and_generate_diagrams(zip_path))

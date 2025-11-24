#!/usr/bin/env python3
"""
Genera diagramas C1, C2, C3 para los 12 proyectos del test extendido
Usa el generador determinístico (sin IA)
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.analyzer import analyze_project
from core.diagram_generator_deterministic import (
    generate_c1_diagram,
    generate_c2_diagram,
    generate_c3_diagram
)

def generate_diagrams_for_project(project_name, project_path):
    """Genera los 3 niveles de diagramas para un proyecto"""
    
    print(f"\n{'='*80}")
    print(f"📊 Generando diagramas para: {project_name}")
    print(f"{'='*80}")
    
    try:
        # Verificar que el directorio exists
        if not os.path.exists(project_path):
            print(f"❌ Error: No existe {project_path}")
            return False
        
        # Analizar proyecto
        print(f"🔍 Analizando proyecto...")
        analysis_result = analyze_project(project_path)
        
        if analysis_result.get("error"):
            print(f"❌ Error en análisis: {analysis_result['error']}")
            return False
        
        project_type = analysis_result.get("type", "unknown")
        language = analysis_result.get("language", "Unknown")
        files = analysis_result.get("files", 0)
        components = len(analysis_result.get("components", []))
        
        print(f"✅ Proyecto analizado:")
        print(f"   - Tipo: {project_type}")
        print(f"   - Lenguaje: {language}")
        print(f"   - Archivos: {files}")
        print(f"   - Componentes: {components}")
        
        # Generar diagramas
        print(f"\n📐 Generando diagramas C1, C2, C3...")
        
        # C1 - System Context
        c1_code = generate_c1_diagram(analysis_result)
        c1_file = f"{project_name}_c1.mmd"
        with open(c1_file, 'w', encoding='utf-8') as f:
            f.write(c1_code)
        print(f"   ✅ C1 generado: {c1_file}")
        
        # C2 - Container
        c2_code = generate_c2_diagram(analysis_result)
        c2_file = f"{project_name}_c2.mmd"
        with open(c2_file, 'w', encoding='utf-8') as f:
            f.write(c2_code)
        print(f"   ✅ C2 generado: {c2_file}")
        
        # C3 - Component
        c3_code = generate_c3_diagram(analysis_result)
        c3_file = f"{project_name}_c3.mmd"
        with open(c3_file, 'w', encoding='utf-8') as f:
            f.write(c3_code)
        print(f"   ✅ C3 generado: {c3_file}")
        
        print(f"\n✨ Diagramas completados para {project_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error generando diagramas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Genera diagramas para todos los proyectos"""
    
    # Proyectos a procesar (los 12 del test extendido)
    projects = [
        ("ripgrep", "uploads/ripgrep-main/ripgrep-main"),
        ("laravel", "uploads/laravel-main/laravel-main"),
        ("echo", "uploads/echo-main/echo-main"),
        ("cleanarchitecture", "uploads/clean-architecture-manga-main/clean-architecture-manga-main"),
        ("fastapi", "uploads/fastapi-main/fastapi-main"),
        ("django", "uploads/django-main/django-main"),
        ("express", "uploads/express-main/express-main"),
        ("tokio", "uploads/tokio-main/tokio-main"),
        ("gin", "uploads/gin-main/gin-main"),
        ("rails", "uploads/rails-main/rails-main"),
        ("nestjs", "uploads/nest-main/nest-main"),
        ("ktor", "uploads/ktor-main/ktor-main"),
    ]
    
    print("🚀 Iniciando generación de diagramas para 12 proyectos")
    print(f"📍 Directorio de trabajo: {os.getcwd()}")
    
    successful = 0
    failed = 0
    
    for project_name, project_path in projects:
        success = generate_diagrams_for_project(project_name, project_path)
        if success:
            successful += 1
        else:
            failed += 1
    
    # Resumen final
    print(f"\n{'='*80}")
    print(f"📊 RESUMEN FINAL")
    print(f"{'='*80}")
    print(f"✅ Exitosos: {successful}/12")
    print(f"❌ Fallidos: {failed}/12")
    print(f"\n💾 Archivos generados en: {os.getcwd()}")
    print(f"   - *_c1.mmd: Diagramas de contexto del sistema")
    print(f"   - *_c2.mmd: Diagramas de contenedores")
    print(f"   - *_c3.mmd: Diagramas de componentes")
    
    if successful == 12:
        print(f"\n🎉 ¡Todos los diagramas generados exitosamente!")
    
    return 0 if successful == 12 else 1

if __name__ == "__main__":
    sys.exit(main())

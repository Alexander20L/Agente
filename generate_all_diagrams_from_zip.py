#!/usr/bin/env python3
"""
Genera diagramas C1, C2, C3 para los proyectos ya analizados
Lee los datos de análisis y genera los diagramas sin re-analizar
"""

import sys
import os
import json

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.analyzer import analyze_project
from core.diagram_generator_deterministic import (
    generate_c1_diagram,
    generate_c2_diagram,
    generate_c3_diagram
)

def generate_diagrams_from_zip(project_name, zip_path):
    """Genera los 3 niveles de diagramas desde un archivo ZIP"""
    
    print(f"\n{'='*80}")
    print(f">> Generando diagramas para: {project_name}")
    print(f"{'='*80}")
    
    try:
        # Verificar que el ZIP existe
        if not os.path.exists(zip_path):
            print(f"ERROR: No existe {zip_path}")
            return False
        
        # Analizar proyecto desde ZIP
        print(f">> Analizando proyecto desde ZIP...")
        analysis_result = analyze_project(zip_path)
        
        if analysis_result.get("error"):
            print(f"ERROR en análisis: {analysis_result['error']}")
            return False
        
        project_type = analysis_result.get("type", "unknown")
        language = analysis_result.get("language", "Unknown")
        files = analysis_result.get("files", 0)
        components = len(analysis_result.get("components", []))
        
        print(f">> Proyecto analizado:")
        print(f"   - Tipo: {project_type}")
        print(f"   - Lenguaje: {language}")
        print(f"   - Archivos: {files}")
        print(f"   - Componentes: {components}")
        
        # Generar diagramas
        print(f"\n>> Generando diagramas C1, C2, C3...")
        
        # C1 - System Context
        c1_code = generate_c1_diagram(analysis_result)
        c1_file = f"{project_name}_c1.mmd"
        with open(c1_file, 'w', encoding='utf-8') as f:
            f.write(c1_code)
        print(f"   OK C1: {c1_file}")
        
        # C2 - Container
        c2_code = generate_c2_diagram(analysis_result)
        c2_file = f"{project_name}_c2.mmd"
        with open(c2_file, 'w', encoding='utf-8') as f:
            f.write(c2_code)
        print(f"   OK C2: {c2_file}")
        
        # C3 - Component
        c3_code = generate_c3_diagram(analysis_result)
        c3_file = f"{project_name}_c3.mmd"
        with open(c3_file, 'w', encoding='utf-8') as f:
            f.write(c3_code)
        print(f"   OK C3: {c3_file}")
        
        print(f">> Diagramas completados")
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Genera diagramas para todos los proyectos"""
    
    # Proyectos con sus archivos ZIP
    projects = [
        ("ripgrep", "uploads/ripgrep-master.zip"),
        ("laravel", "uploads/laravel-master.zip"),
        ("echo", "uploads/echo-master.zip"),
        ("cleanarchitecture", "uploads/CleanArchitecture-main.zip"),
        ("fastapi", "uploads/fastapi-master.zip"),
        ("django", "uploads/django-main.zip"),
        ("express", "uploads/express-master.zip"),
        ("tokio", "uploads/tokio-master.zip"),
        ("gin", "uploads/gin-master.zip"),
        ("rails", "uploads/rails-main.zip"),
        ("nestjs", "uploads/nest-master.zip"),
        ("ktor", "uploads/ktor-main.zip"),
    ]
    
    print(">> Generando diagramas C1, C2, C3 para 12 proyectos")
    print(">> Directorio de trabajo:", os.getcwd())
    print(">> Usando: Generador deterministic (sin IA)")
    
    successful = 0
    failed = 0
    results = []
    
    for project_name, zip_path in projects:
        success = generate_diagrams_from_zip(project_name, zip_path)
        results.append({
            "project": project_name,
            "success": success,
            "files": [
                f"{project_name}_c1.mmd" if success else None,
                f"{project_name}_c2.mmd" if success else None,
                f"{project_name}_c3.mmd" if success else None,
            ]
        })
        if success:
            successful += 1
        else:
            failed += 1
    
    # Resumen final
    print(f"\n{'='*80}")
    print(f">> RESUMEN FINAL")
    print(f"{'='*80}")
    print(f"OK Exitosos: {successful}/12")
    print(f"FAIL Fallidos: {failed}/12")
    
    if successful > 0:
        print(f"\n>> Archivos generados:")
        for result in results:
            if result["success"]:
                print(f"\n   {result['project']}:")
                for file in result["files"]:
                    if file and os.path.exists(file):
                        size_kb = os.path.getsize(file) / 1024
                        print(f"      - {file} ({size_kb:.1f} KB)")
    
    if successful == 12:
        print(f"\n>> Todos los diagramas generados exitosamente!")
    elif successful > 0:
        print(f"\n>> Algunos proyectos fallaron, revisa los errores arriba")
    
    # Guardar resumen
    with open("diagrams_generation_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n>> Resumen guardado en: diagrams_generation_summary.json")
    
    return 0 if successful == 12 else 1

if __name__ == "__main__":
    sys.exit(main())

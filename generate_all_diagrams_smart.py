"""
Script INTELIGENTE para generar diagramas C1, C2, C3
- Analiza solo proyectos sin análisis previo
- Reutiliza análisis guardados para ahorrar tiempo
- Genera diagramas para todos los proyectos
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.analyzer import analyze_project
from core.diagram_generator_deterministic import (
    generate_c1_diagram,
    generate_c2_diagram,
    generate_c3_diagram
)

# Proyectos a procesar
PROJECTS = [
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

def load_or_analyze_project(project_name, zip_path):
    """Carga análisis previo o analiza el proyecto"""
    
    analysis_file = f"analysis_{project_name}.json"
    
    # Intentar cargar análisis existente
    if os.path.exists(analysis_file):
        print(f"   >> Cargando análisis previo: {analysis_file}")
        with open(analysis_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Si no existe, analizar
    if not os.path.exists(zip_path):
        print(f"   ERROR: No existe {zip_path}")
        return None
    
    print(f"   >> Analizando proyecto desde ZIP...")
    try:
        analysis = analyze_project(zip_path)
        
        # Guardar análisis para futura reutilización
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"   >> Análisis guardado: {analysis_file}")
        
        return analysis
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return None

def generate_all_diagrams(project_name, analysis):
    """Genera los 3 diagramas C1, C2, C3"""
    
    if not analysis:
        return False
    
    try:
        # C1
        c1_code = generate_c1_diagram(analysis)
        with open(f"{project_name}_c1.mmd", "w", encoding="utf-8") as f:
            f.write(c1_code)
        
        # C2
        c2_code = generate_c2_diagram(analysis)
        with open(f"{project_name}_c2.mmd", "w", encoding="utf-8") as f:
            f.write(c2_code)
        
        # C3
        c3_code = generate_c3_diagram(analysis)
        with open(f"{project_name}_c3.mmd", "w", encoding="utf-8") as f:
            f.write(c3_code)
        
        return True
    except Exception as e:
        print(f"   ERROR generando diagramas: {str(e)}")
        return False

def main():
    print("=" * 80)
    print("Generador Inteligente de Diagramas C1, C2, C3")
    print("=" * 80)
    print(f"Total de proyectos: {len(PROJECTS)}")
    print(f"Directorio: {os.getcwd()}")
    print()
    
    successful = 0
    failed = 0
    skipped = 0
    
    for i, (project_name, zip_path) in enumerate(PROJECTS, 1):
        print(f"\n[{i}/{len(PROJECTS)}] {project_name}")
        print("-" * 60)
        
        # Cargar o analizar
        analysis = load_or_analyze_project(project_name, zip_path)
        
        if not analysis:
            failed += 1
            continue
        
        # Mostrar info
        ptype = analysis.get("project_type", "unknown")
        files = analysis.get("total_files", 0)
        comps = len(analysis.get("components_detected", []))
        
        print(f"   Tipo: {ptype} | Archivos: {files} | Componentes: {comps}")
        
        # Verificar si ya existen diagramas
        c1_exists = os.path.exists(f"{project_name}_c1.mmd")
        c2_exists = os.path.exists(f"{project_name}_c2.mmd")
        c3_exists = os.path.exists(f"{project_name}_c3.mmd")
        
        if c1_exists and c2_exists and c3_exists:
            print(f"   >> Diagramas ya existen, saltando...")
            skipped += 1
            successful += 1  # Contar como exitoso
            continue
        
        # Generar diagramas
        print(f"   >> Generando diagramas C1, C2, C3...")
        if generate_all_diagrams(project_name, analysis):
            print(f"   OK: Diagramas completados")
            successful += 1
        else:
            failed += 1
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"Exitosos: {successful}/{len(PROJECTS)}")
    print(f"Fallidos: {failed}/{len(PROJECTS)}")
    print(f"Ya existian: {skipped}/{len(PROJECTS)}")
    
    if successful == len(PROJECTS):
        print("\n>> Todos los diagramas disponibles!")
    
    # Listar archivos generados
    print("\nArchivos generados:")
    for name, _ in PROJECTS:
        if os.path.exists(f"{name}_c1.mmd"):
            size_c1 = os.path.getsize(f"{name}_c1.mmd") / 1024
            size_c2 = os.path.getsize(f"{name}_c2.mmd") / 1024
            size_c3 = os.path.getsize(f"{name}_c3.mmd") / 1024
            print(f"  {name}: C1={size_c1:.1f}KB, C2={size_c2:.1f}KB, C3={size_c3:.1f}KB")

if __name__ == "__main__":
    main()

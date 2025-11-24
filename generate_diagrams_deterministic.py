"""
Genera diagramas C4 del Spring PetClinic SIN IA (determinístico)
"""

import os
import sys
import zipfile
from core.analyzer import analyze_project
from core.diagram_generator_deterministic import generate_all_diagrams_deterministic

def create_zip_from_folder(folder_path, zip_path):
    """Crea un ZIP del proyecto"""
    print(f"📦 Creando ZIP de {folder_path}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'target', 'node_modules', '__pycache__']]
            
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    
    print(f"   ✅ ZIP creado: {zip_path}")

def main():
    project_folder = os.path.join("uploads", "spring-petclinic")
    zip_path = "spring-petclinic.zip"
    
    if not os.path.exists(project_folder):
        print(f"❌ Error: No se encontró el proyecto en {project_folder}")
        return
    
    print("🎨 GENERANDO DIAGRAMAS C4 (DETERMINÍSTICO - SIN IA)")
    print("=" * 70)
    
    # 1. Crear ZIP
    create_zip_from_folder(project_folder, zip_path)
    
    # 2. Analizar proyecto
    print("\n🔍 PASO 1: Analizando proyecto...")
    analysis = analyze_project(zip_path)
    
    print(f"   ✅ Análisis completado:")
    print(f"      - Proyecto: {analysis['project_name']}")
    print(f"      - Tipo: {analysis['project_type']}")
    print(f"      - Componentes: {len(analysis['components_detected'])}")
    
    # Mostrar capas
    if "architectural_layers" in analysis:
        layers = analysis["architectural_layers"]
        print(f"\n   📊 Capas Arquitectónicas:")
        print(f"      - Presentation: {layers['presentation']['count']}")
        print(f"      - Application: {layers['application']['count']}")
        print(f"      - Domain: {layers['domain']['count']}")
        print(f"      - Infrastructure: {layers['infrastructure']['count']}")
    
    # Mostrar patrones
    if "architecture_patterns" in analysis:
        patterns = analysis["architecture_patterns"]
        if patterns:
            print(f"\n   🏗️  Patrones Detectados:")
            for p in patterns[:3]:
                print(f"      - {p['name']} ({int(p['confidence']*100)}%)")
    
    # 3. Generar diagramas
    print("\n🎨 PASO 2: Generando diagramas C4...")
    results = generate_all_diagrams_deterministic(analysis, "spring_petclinic")
    
    print("\n📊 RESULTADOS:")
    for level, result in results.items():
        if result["status"] == "success":
            print(f"   ✅ {level.upper()}: {result['file']}")
        else:
            print(f"   ❌ {level.upper()}: {result.get('message', 'Error')}")
    
    # Limpiar
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    print("\n✅ PROCESO COMPLETADO")
    print("\nPara visualizar los diagramas:")
    print("1. Abre los archivos .mmd en VS Code")
    print("2. Usa Ctrl+Shift+P → 'Mermaid: Preview'")
    print("3. O copia el contenido a https://mermaid.live")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

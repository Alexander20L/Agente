"""
Genera diagramas C4 del Spring PetClinic usando el analyzer multi-lenguaje
"""

import os
import sys
import zipfile
import shutil
from core.analyzer import analyze_project, detect_actors
from core.semantic_reasoner import generate_semantic_mermaid_openrouter

def create_zip_from_folder(folder_path, zip_path):
    """Crea un ZIP del proyecto"""
    print(f"📦 Creando ZIP de {folder_path}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            # Excluir directorios innecesarios
            dirs[:] = [d for d in dirs if d not in ['.git', 'target', 'node_modules', '__pycache__']]
            
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    
    print(f"   ✅ ZIP creado: {zip_path}")

def generate_spring_petclinic_diagrams():
    """Genera diagramas C1, C2 y C3 del Spring PetClinic"""
    
    project_folder = os.path.join("uploads", "spring-petclinic")
    zip_path = "spring-petclinic.zip"
    
    if not os.path.exists(project_folder):
        print(f"❌ Error: No se encontró el proyecto en {project_folder}")
        return
    
    print("🎨 GENERANDO DIAGRAMAS C4 DE SPRING PETCLINIC")
    print("=" * 70)
    
    # 1. Crear ZIP del proyecto
    create_zip_from_folder(project_folder, zip_path)
    
    # 2. Analizar proyecto
    print("\n🔍 PASO 1: Analizando proyecto...")
    analysis_result = analyze_project(zip_path)
    
    print(f"   ✅ Análisis completado:")
    print(f"      - Proyecto: {analysis_result.get('project_name', 'N/A')}")
    print(f"      - Tipo: {analysis_result.get('project_type', 'N/A')}")
    print(f"      - Archivos: {analysis_result.get('total_files', 0)}")
    print(f"      - Contenedores: {len(analysis_result.get('containers_detected', []))}")
    print(f"      - Componentes: {len(analysis_result.get('components_detected', []))}")
    
    # Mostrar información mejorada
    if "architectural_layers" in analysis_result:
        layers = analysis_result["architectural_layers"]
        print(f"\n   📊 Capas Arquitectónicas:")
        print(f"      - Presentation: {layers['presentation']['count']}")
        print(f"      - Application: {layers['application']['count']}")
        print(f"      - Domain: {layers['domain']['count']}")
        print(f"      - Infrastructure: {layers['infrastructure']['count']}")
    
    if "technologies" in analysis_result:
        techs = analysis_result["technologies"]
        print(f"\n   🔧 Tecnologías:")
        if techs["backend"]:
            print(f"      - Backend: {', '.join(techs['backend'])}")
        if techs["frontend"]:
            print(f"      - Frontend: {', '.join(techs['frontend'])}")
        if techs["database"]:
            print(f"      - Database: {', '.join(techs['database'])}")
    
    if "architecture_patterns" in analysis_result:
        patterns = analysis_result["architecture_patterns"]
        if patterns:
            print(f"\n   🏗️  Patrones Arquitectónicos:")
            for pattern in patterns:
                print(f"      - {pattern['name']} ({int(pattern['confidence']*100)}%)")
    
    if "system_responsibilities" in analysis_result:
        resp = analysis_result["system_responsibilities"]
        if resp:
            print(f"\n   📋 Responsabilidades del Sistema:")
            for r in resp:
                print(f"      - {r}")
    
    # 3. Detectar actores
    print("\n👥 PASO 2: Detectando actores...")
    actors_data = detect_actors(analysis_result)
    actors_list = actors_data.get("actors", [])
    external_systems = actors_data.get("external_systems", [])
    
    print(f"   ✅ Actores humanos: {len(actors_list)}")
    for actor in actors_list:
        print(f"      - {actor['name']} ({actor['type']}): {actor['interaction']}")
    
    print(f"   ✅ Sistemas externos: {len(external_systems)}")
    for system in external_systems:
        print(f"      - {system['name']} ({system['type']}): {system['interaction']}")
    
    # 4. Generar C1
    print("\n🎨 PASO 3: Generando diagrama C1 (Contexto)...")
    try:
        c1_diagram = generate_semantic_mermaid_openrouter(
            analysis_result, 
            actors_data, 
            diagram_level="C1"
        )
        
        if c1_diagram and "error" not in c1_diagram.lower():
            c1_file = "spring_petclinic_c1.mmd"
            with open(c1_file, 'w', encoding='utf-8') as f:
                f.write(c1_diagram)
            print(f"   ✅ C1 generado: {c1_file}")
        else:
            print(f"   ❌ Error en C1: {c1_diagram}")
    except Exception as e:
        print(f"   ❌ Error generando C1: {type(e).__name__}: {str(e)}")
    
    # 5. Generar C2
    print("\n🎨 PASO 4: Generando diagrama C2 (Contenedores)...")
    try:
        c2_diagram = generate_semantic_mermaid_openrouter(
            analysis_result, 
            actors_data, 
            diagram_level="C2"
        )
        
        if c2_diagram and "error" not in c2_diagram.lower():
            c2_file = "spring_petclinic_c2.mmd"
            with open(c2_file, 'w', encoding='utf-8') as f:
                f.write(c2_diagram)
            print(f"   ✅ C2 generado: {c2_file}")
        else:
            print(f"   ❌ Error en C2: {c2_diagram}")
    except Exception as e:
        print(f"   ❌ Error generando C2: {type(e).__name__}: {str(e)}")
    
    # 6. Generar C3
    print("\n🎨 PASO 5: Generando diagrama C3 (Componentes)...")
    try:
        c3_diagram = generate_semantic_mermaid_openrouter(
            analysis_result, 
            actors_data, 
            diagram_level="C3"
        )
        
        if c3_diagram and "error" not in c3_diagram.lower():
            c3_file = "spring_petclinic_c3.mmd"
            with open(c3_file, 'w', encoding='utf-8') as f:
                f.write(c3_diagram)
            print(f"   ✅ C3 generado: {c3_file}")
        else:
            print(f"   ❌ Error en C3: {c3_diagram}")
    except Exception as e:
        print(f"   ❌ Error generando C3: {type(e).__name__}: {str(e)}")
    
    # 7. Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE DIAGRAMAS GENERADOS")
    print("=" * 70)
    
    diagrams_created = []
    for diagram_file in ["spring_petclinic_c1.mmd", "spring_petclinic_c2.mmd", "spring_petclinic_c3.mmd"]:
        if os.path.exists(diagram_file):
            diagrams_created.append(diagram_file)
            print(f"✅ {diagram_file}")
    
    if not diagrams_created:
        print("❌ No se pudo generar ningún diagrama")
        print("\nPosibles causas:")
        print("1. No hay créditos en OpenRouter (error 402)")
        print("2. Problema con la API key")
        print("3. Error en la generación del prompt")
        print("\nSolución:")
        print("- Verificar OPENROUTER_API_KEY en .env")
        print("- Agregar créditos en https://openrouter.ai")
    else:
        print(f"\n✅ {len(diagrams_created)}/3 diagramas generados exitosamente")
        print("\nPara visualizar:")
        print("1. Abre los archivos .mmd en VS Code")
        print("2. Usa la extensión Mermaid Preview")
        print("3. O copia el contenido a https://mermaid.live")
    
    # Limpiar ZIP temporal
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"\n🧹 ZIP temporal eliminado: {zip_path}")

if __name__ == "__main__":
    try:
        generate_spring_petclinic_diagrams()
    except Exception as e:
        print(f"\n❌ Error crítico:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

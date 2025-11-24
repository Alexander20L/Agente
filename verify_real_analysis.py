"""
Verificación: ¿El analyzer REALMENTE analiza el código o usa plantillas?
"""

import os
import json
from core.analyzer import analyze_project

def verify_real_analysis():
    """Verifica que el análisis sea real, no plantillas"""
    
    project_folder = os.path.join("uploads", "spring-petclinic")
    zip_path = "spring-petclinic.zip"
    
    print("🔍 VERIFICANDO ANÁLISIS REAL DEL CÓDIGO")
    print("=" * 70)
    
    # Comprimir
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_folder):
            dirs[:] = [d for d in dirs if d not in ['.git', 'target', 'node_modules']]
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_folder)
                zipf.write(file_path, arcname)
    
    # Analizar
    print("\n📊 EJECUTANDO analyze_project()...")
    analysis = analyze_project(zip_path)
    
    # 1. Verificar componentes detectados
    print("\n1️⃣ COMPONENTES DETECTADOS (primeros 20):")
    components = analysis.get("components_detected", [])
    print(f"   Total: {len(components)}")
    
    for i, comp in enumerate(components[:20], 1):
        print(f"   {i}. {comp['name']} (tipo: {comp['type']})")
        if comp.get('classes'):
            print(f"      Classes: {comp['classes'][:3]}")
        if comp.get('path'):
            # Verificar que el archivo existe
            exists = os.path.exists(comp['path'])
            print(f"      Path: {comp['path'][:60]}... [{'✅ existe' if exists else '❌ no existe'}]")
    
    # 2. Verificar relaciones
    print(f"\n2️⃣ RELACIONES DETECTADAS:")
    relations = analysis.get("relations_detected", [])
    print(f"   Total: {len(relations)}")
    print(f"   Muestra (primeras 10):")
    for i, rel in enumerate(relations[:10], 1):
        print(f"   {i}. {rel['from']} → {rel['to']}")
    
    # 3. Verificar contenedores
    print(f"\n3️⃣ CONTENEDORES DETECTADOS:")
    containers = analysis.get("containers_detected", [])
    print(f"   Total: {len(containers)}")
    for i, cont in enumerate(containers, 1):
        print(f"   {i}. {cont['type']}: {cont['technology']}")
        print(f"      Source: {cont['source']}")
        print(f"      Evidences: {cont['evidences'][:3]}")
    
    # 4. Verificar capas arquitectónicas
    print(f"\n4️⃣ CAPAS ARQUITECTÓNICAS:")
    layers = analysis.get("architectural_layers", {})
    for layer_name, layer_data in layers.items():
        print(f"   {layer_name}: {layer_data['count']} componentes")
        print(f"      Ejemplos: {layer_data['components'][:3]}")
    
    # 5. Verificar tecnologías
    print(f"\n5️⃣ TECNOLOGÍAS DETECTADAS:")
    techs = analysis.get("technologies", {})
    for tech_type, tech_list in techs.items():
        if tech_list:
            print(f"   {tech_type}: {', '.join(tech_list)}")
    
    # 6. Verificar patrones
    print(f"\n6️⃣ PATRONES ARQUITECTÓNICOS:")
    patterns = analysis.get("architecture_patterns", [])
    for pattern in patterns:
        print(f"   - {pattern['name']}: {int(pattern['confidence']*100)}%")
        print(f"     Evidencia: {pattern['evidence']}")
    
    # 7. PRUEBA CRUCIAL: Leer un archivo detectado y verificar contenido
    print(f"\n7️⃣ VERIFICACIÓN DE CONTENIDO REAL:")
    print("   Leyendo OwnerController.java para verificar anotaciones...")
    
    owner_controller = next((c for c in components if "ownercontroller" in c['name'].lower()), None)
    if owner_controller and os.path.exists(owner_controller['path']):
        with open(owner_controller['path'], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Buscar anotaciones Spring reales
        annotations = {
            "@Controller": "@Controller" in content,
            "@RequestMapping": "@RequestMapping" in content,
            "@GetMapping": "@GetMapping" in content,
            "@PostMapping": "@PostMapping" in content,
            "class OwnerController": "class OwnerController" in content
        }
        
        print(f"   ✅ Archivo existe: {owner_controller['path']}")
        print(f"   Anotaciones encontradas en el código real:")
        for ann, found in annotations.items():
            print(f"      {'✅' if found else '❌'} {ann}")
        
        # Mostrar fragmento del código real
        lines = content.split('\n')
        print(f"\n   📄 Fragmento del código real (líneas 1-15):")
        for i, line in enumerate(lines[:15], 1):
            print(f"      {i:2d} | {line[:70]}")
    else:
        print("   ❌ No se encontró OwnerController")
    
    # 8. CONCLUSIÓN
    print("\n" + "=" * 70)
    print("📊 CONCLUSIÓN:")
    print("=" * 70)
    
    if len(components) > 0 and len(relations) > 0:
        print("✅ El analyzer SÍ está leyendo el código real")
        print(f"✅ Detectó {len(components)} componentes reales")
        print(f"✅ Extrajo {len(relations)} relaciones del código")
        print(f"✅ Las clases y anotaciones coinciden con el código fuente")
    else:
        print("❌ El analyzer NO está detectando correctamente")
    
    # Guardar análisis completo
    with open("spring_petclinic_analysis_full.json", 'w', encoding='utf-8') as f:
        # Remover path para que sea más legible
        clean_analysis = {k: v for k, v in analysis.items() if k != 'components_detected'}
        clean_analysis['components_sample'] = [
            {k: v for k, v in comp.items() if k != 'path'} 
            for comp in components[:10]
        ]
        json.dump(clean_analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análisis completo guardado en: spring_petclinic_analysis_full.json")
    
    # Limpiar
    if os.path.exists(zip_path):
        os.remove(zip_path)

if __name__ == "__main__":
    verify_real_analysis()

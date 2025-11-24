"""
Regenerar solo C3 con detección de componentes arreglada
"""
import sys
sys.path.insert(0, r'C:\Users\alex_\OneDrive\Escritorio\agente')

from core.analyzer import analyze_project, detect_actors
from core.semantic_reasoner import generate_semantic_mermaid_openrouter
import os
import shutil

print("\n" + "="*80)
print("🔧 REGENERANDO C3 CON DETECCIÓN DE COMPONENTES MEJORADA")
print("="*80 + "\n")

# Forzar re-análisis eliminando carpeta extraída
zip_path = r"C:\Users\alex_\OneDrive\Escritorio\agente\test_project.zip"
extract_dir = zip_path.replace(".zip", "")
if os.path.exists(extract_dir):
    print(f"🗑️ Eliminando análisis anterior para forzar re-análisis...")
    try:
        shutil.rmtree(extract_dir)
        print("✅ Eliminado\n")
    except:
        print("⚠️ No se pudo eliminar, continuando...\n")

print("📊 Re-analizando con exclude_dirs corregido...")
analysis = analyze_project(zip_path)

print(f"✅ Proyecto: {analysis.get('project_name')}")
print(f"✅ Tipo: {analysis.get('project_type')}")
print(f"✅ Componentes detectados: {len(analysis.get('components_detected', []))}\n")

if len(analysis.get('components_detected', [])) == 0:
    print("❌ ERROR: Todavía no se detectan componentes")
    print("Verificando archivos en el directorio...\n")
    import glob
    py_files = glob.glob(os.path.join(extract_dir, "**", "*.py"), recursive=True)
    print(f"Archivos .py encontrados: {len(py_files)}")
    for f in py_files[:10]:
        print(f"  - {os.path.basename(f)}")
    print("\n❌ ABORTANDO: No se puede generar C3 sin componentes detectados")
    exit(1)

print("🔧 COMPONENTES DETECTADOS:")
for comp in analysis.get('components_detected', [])[:15]:
    print(f"   [{comp.get('type')}] {comp.get('name')}")
    if comp.get('classes'):
        print(f"      Clases: {', '.join(comp.get('classes', [])[:3])}")
print()

actors = detect_actors(analysis)

print("="*80)
print("🎨 Generando diagrama C3 con IA...")
print("="*80 + "\n")

mermaid_c3 = generate_semantic_mermaid_openrouter(
    analysis_result=analysis,
    actors_detected=actors,
    diagram_level="C3"
)

print("📐 DIAGRAMA C3 REGENERADO:")
print("-"*80)
print(mermaid_c3)
print("-"*80 + "\n")

with open("simulator_c3_diagram_fixed.mmd", 'w', encoding='utf-8') as f:
    f.write(mermaid_c3)

print("✅ C3 guardado en: simulator_c3_diagram_fixed.mmd")
print("="*80 + "\n")

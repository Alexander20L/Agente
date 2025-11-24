"""
Generación MEJORADA de diagramas C4 para Simulator Resistance
Con detección correcta de PyQt5 y componentes críticos
"""
import sys
sys.path.insert(0, r'C:\Users\alex_\OneDrive\Escritorio\agente')

from core.analyzer import analyze_project, detect_actors
from core.semantic_reasoner import generate_semantic_mermaid_openrouter
import os

print("\n" + "="*80)
print("🔄 REGENERANDO DIAGRAMAS C4 CON ANÁLISIS MEJORADO")
print("="*80 + "\n")

# Eliminar análisis anterior para forzar re-análisis
zip_path = r"C:\Users\alex_\OneDrive\Escritorio\agente\test_project.zip"
extract_dir = zip_path.replace(".zip", "")
if os.path.exists(extract_dir):
    import shutil
    print(f"🗑️ Eliminando análisis anterior: {extract_dir}")
    try:
        shutil.rmtree(extract_dir)
    except PermissionError:
        print("   ⚠️ No se pudo eliminar (archivos en uso), continuando con análisis...")

print("📊 Analizando proyecto con detección mejorada...")
print("   ✓ Detección de PyQt5/PyQt6")
print("   ✓ Detección de genetic_algorithm.py")
print("   ✓ Detección de componentes críticos\n")

analysis = analyze_project(zip_path)

print(f"✅ Proyecto: {analysis.get('project_name')}")
print(f"✅ Tipo: {analysis.get('project_type')}")
print(f"✅ Archivos: {analysis.get('total_files')}")
print(f"✅ Contenedores detectados: {len(analysis.get('containers_detected', []))}")
print(f"✅ Componentes detectados: {len(analysis.get('components_detected', []))}\n")

# Mostrar contenedores encontrados
print("📦 CONTENEDORES DETECTADOS:")
for container in analysis.get('containers_detected', [])[:5]:
    print(f"   - {container.get('type')}: {container.get('technology')} (confianza: {container.get('confidence')})")
print()

# Mostrar componentes críticos
print("🔧 COMPONENTES CRÍTICOS DETECTADOS:")
for comp in analysis.get('components_detected', [])[:10]:
    print(f"   - {comp.get('name')} [{comp.get('type')}]")
print()

print("🤖 Detectando actores...")
actors = detect_actors(analysis)
print(f"✅ Actores: {len(actors.get('actors', []))}")
for actor in actors.get('actors', []):
    print(f"   - {actor.get('name')} ({actor.get('type')})")
print(f"✅ Sistemas externos: {len(actors.get('external_systems', []))}")
for ext in actors.get('external_systems', []):
    print(f"   - {ext.get('name')} ({ext.get('type')})")
print()

# === GENERAR C1 ===
print("="*80)
print("🎨 Generando diagrama C1 con IA...")
print("="*80 + "\n")

mermaid_c1 = generate_semantic_mermaid_openrouter(
    analysis_result=analysis,
    actors_detected=actors,
    diagram_level="C1"
)

print("📐 DIAGRAMA C1:")
print("-"*80)
print(mermaid_c1)
print("-"*80 + "\n")

with open("simulator_c1_diagram_fixed.mmd", 'w', encoding='utf-8') as f:
    f.write(mermaid_c1)
print("✅ C1 guardado en: simulator_c1_diagram_fixed.mmd\n")

# === GENERAR C2 ===
print("="*80)
print("🎨 Generando diagrama C2 con IA...")
print("="*80 + "\n")

mermaid_c2 = generate_semantic_mermaid_openrouter(
    analysis_result=analysis,
    actors_detected=actors,
    diagram_level="C2"
)

print("📐 DIAGRAMA C2:")
print("-"*80)
print(mermaid_c2)
print("-"*80 + "\n")

with open("simulator_c2_diagram_fixed.mmd", 'w', encoding='utf-8') as f:
    f.write(mermaid_c2)
print("✅ C2 guardado en: simulator_c2_diagram_fixed.mmd\n")

# === GENERAR C3 ===
print("="*80)
print("🎨 Generando diagrama C3 con IA...")
print("="*80 + "\n")

mermaid_c3 = generate_semantic_mermaid_openrouter(
    analysis_result=analysis,
    actors_detected=actors,
    diagram_level="C3"
)

print("📐 DIAGRAMA C3:")
print("-"*80)
print(mermaid_c3)
print("-"*80 + "\n")

with open("simulator_c3_diagram_fixed.mmd", 'w', encoding='utf-8') as f:
    f.write(mermaid_c3)
print("✅ C3 guardado en: simulator_c3_diagram_fixed.mmd\n")

print("="*80)
print("✅ TODOS LOS DIAGRAMAS REGENERADOS CON ANÁLISIS MEJORADO")
print("="*80)
print("Archivos generados:")
print("  📄 simulator_c1_diagram_fixed.mmd")
print("  📄 simulator_c2_diagram_fixed.mmd")
print("  📄 simulator_c3_diagram_fixed.mmd")
print("="*80 + "\n")

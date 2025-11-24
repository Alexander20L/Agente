"""
Generación de diagramas C4 para Triton (proyecto grande)
"""
import sys
sys.path.insert(0, r'C:\Users\alex_\OneDrive\Escritorio\agente')

from core.analyzer import analyze_project, detect_actors
from core.semantic_reasoner import generate_semantic_mermaid_openrouter
import os

print("\n" + "="*80)
print("🚀 GENERANDO DIAGRAMAS C4 PARA TRITON")
print("="*80 + "\n")

zip_path = r"C:\Users\alex_\OneDrive\Escritorio\agente\triton_test.zip"

# Verificar que existe el zip
if not os.path.exists(zip_path):
    print(f"❌ No se encontró: {zip_path}")
    print("\n🔧 Creando zip de Triton...")
    import subprocess
    result = subprocess.run([
        'powershell', '-Command',
        f'Compress-Archive -Path "C:\\Users\\alex_\\OneDrive\\Escritorio\\agente\\uploads\\triton-main\\triton-main\\*" -DestinationPath "{zip_path}" -Force'
    ])
    if result.returncode != 0:
        print("❌ Error al crear zip")
        exit(1)
    print("✅ Zip creado\n")

print("📊 Analizando Triton (esto puede tardar 30-60 segundos)...")
print("⚠️ Proyecto GRANDE: 1399 archivos, análisis extenso\n")

analysis = analyze_project(zip_path)

print(f"✅ Proyecto: {analysis.get('project_name')}")
print(f"✅ Tipo: {analysis.get('project_type')}")
print(f"✅ Archivos: {analysis.get('total_files')}")
print(f"✅ Contenedores: {len(analysis.get('containers_detected', []))}")
print(f"✅ Componentes: {len(analysis.get('components_detected', []))}")
print(f"✅ Relaciones: {len(analysis.get('relations_detected', []))}\n")

# Mostrar contenedores
print("📦 CONTENEDORES PRINCIPALES:")
for container in analysis.get('containers_detected', [])[:8]:
    print(f"   [{container.get('type')}] {container.get('technology')} (confianza: {container.get('confidence')})")
print()

# Mostrar componentes críticos
print("🔧 COMPONENTES CLAVE (primeros 15):")
for comp in analysis.get('components_detected', [])[:15]:
    classes_str = f" - {', '.join(comp.get('classes', [])[:2])}" if comp.get('classes') else ""
    print(f"   [{comp.get('type')}] {comp.get('name')}{classes_str}")
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
print("🎨 Generando C1 (Context) para Triton...")
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

with open("triton_c1_diagram.mmd", 'w', encoding='utf-8') as f:
    f.write(mermaid_c1)
print("✅ Guardado: triton_c1_diagram.mmd\n")

# === GENERAR C2 ===
print("="*80)
print("🎨 Generando C2 (Container) para Triton...")
print("⚠️ Puede tardar 30-50 segundos por la complejidad...")
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

with open("triton_c2_diagram.mmd", 'w', encoding='utf-8') as f:
    f.write(mermaid_c2)
print("✅ Guardado: triton_c2_diagram.mmd\n")

# === GENERAR C3 ===
print("="*80)
print("🎨 Generando C3 (Component) para Triton...")
print("⚠️ Puede tardar 40-60 segundos por la cantidad de componentes...")
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

with open("triton_c3_diagram.mmd", 'w', encoding='utf-8') as f:
    f.write(mermaid_c3)
print("✅ Guardado: triton_c3_diagram.mmd\n")

print("="*80)
print("✅ DIAGRAMAS C4 DE TRITON COMPLETADOS")
print("="*80)
print("Archivos generados:")
print("  📄 triton_c1_diagram.mmd")
print("  📄 triton_c2_diagram.mmd")
print("  📄 triton_c3_diagram.mmd")
print("\n📊 Estadísticas finales:")
print(f"  - Proyecto: {analysis.get('project_name')}")
print(f"  - Tipo: {analysis.get('project_type')}")
print(f"  - Archivos analizados: {analysis.get('total_files')}")
print(f"  - Componentes detectados: {len(analysis.get('components_detected', []))}")
print(f"  - Ciclos de dependencia: {analysis.get('dependency_analysis', {}).get('cycles', {}).get('total_cycles', 0)}")
print("="*80 + "\n")

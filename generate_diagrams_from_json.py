"""
Genera diagramas C1, C2, C3 desde análisis guardados en JSON
Modo rápido: solo genera diagramas sin re-analizar
"""

import json
import os
from core.diagram_generator_deterministic import (
    generate_c1_diagram,
    generate_c2_diagram,
    generate_c3_diagram
)

# Cargar análisis si existe
analysis_file = "test_single_analysis.json"

if not os.path.exists(analysis_file):
    print(f"ERROR: No existe {analysis_file}")
    print("Ejecuta primero: python test_single_analysis.py")
    exit(1)

with open(analysis_file, "r", encoding="utf-8") as f:
    analysis = json.load(f)

project_name = analysis.get("project_name", "echo")
print(f">> Generando diagramas para: {project_name}")
print(f"   Tipo: {analysis.get('project_type')}")
print(f"   Archivos: {analysis.get('total_files')}")
print(f"   Componentes: {len(analysis.get('components_detected', []))}")

# C1
print("\n>> Generando C1...")
c1_code = generate_c1_diagram(analysis)
c1_file = f"{project_name}_c1.mmd"
with open(c1_file, "w", encoding="utf-8") as f:
    f.write(c1_code)
print(f"   OK: {c1_file}")

# C2
print(">> Generando C2...")
c2_code = generate_c2_diagram(analysis)
c2_file = f"{project_name}_c2.mmd"
with open(c2_file, "w", encoding="utf-8") as f:
    f.write(c2_code)
print(f"   OK: {c2_file}")

# C3
print(">> Generando C3...")
c3_code = generate_c3_diagram(analysis)
c3_file = f"{project_name}_c3.mmd"
with open(c3_file, "w", encoding="utf-8") as f:
    f.write(c3_code)
print(f"   OK: {c3_file}")

print(f"\n>> Diagramas completados para {project_name}")

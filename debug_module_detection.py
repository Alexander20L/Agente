"""
Script de debugging para ver qué módulos se detectan
"""

from core.analyzer import detect_business_modules
import os

# Probar con simulator_resistance
project_path = "simulator_resistance/test_project"

if os.path.exists(project_path):
    print(f"🔍 Analizando estructura de: {project_path}\n")
    
    # Ver estructura
    print("📁 Carpetas encontradas:")
    for root, dirs, files in os.walk(project_path):
        level = root.replace(project_path, '').count(os.sep)
        indent = ' ' * 2 * level
        folder_name = os.path.basename(root)
        py_files = [f for f in files if f.endswith('.py')]
        if py_files:
            print(f"{indent}{folder_name}/ ({len(py_files)} archivos .py)")
        
        # Mostrar solo 2 niveles
        if level >= 2:
            dirs.clear()
    
    print("\n" + "="*80)
    print("🔎 Detectando módulos...")
    print("="*80 + "\n")
    
    modules = detect_business_modules(project_path)
    
    if modules:
        print(f"✅ Detectados {len(modules)} módulos:\n")
        for i, mod in enumerate(modules, 1):
            print(f"{i}. {mod['name']}")
            print(f"   Path: {mod['path']}")
            print(f"   Archivos: {mod['files']}")
            print(f"   Keyword: {mod['keyword']}")
            print()
    else:
        print("❌ No se detectaron módulos")
        print("\nPosibles razones:")
        print("- Las carpetas están en rutas no reconocidas")
        print("- No cumplen con los requisitos mínimos (≥2 archivos)")
        print("- Los nombres no coinciden con palabras clave")

else:
    print(f"❌ No se encontró: {project_path}")

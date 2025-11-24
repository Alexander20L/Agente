"""
Script para depurar detección de Rails y Ktor
"""
import os

# Probar Rails
print("=" * 80)
print("TESTING RAILS")
print("=" * 80)

project_path = "uploads/rails-main/rails-main"
basenames = [f.lower() for f in os.listdir(project_path)]
print(f"'gemfile' in basenames: {'gemfile' in basenames}")

gemspec_files = [f for f in os.listdir(project_path) if f.endswith(".gemspec")]
print(f"Gemspec files: {gemspec_files}")

if gemspec_files:
    gemspec_path = os.path.join(project_path, gemspec_files[0])
    with open(gemspec_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        has_name = 's.name' in content
        has_rails = '"rails"' in content
        print(f"Has 's.name': {has_name}")
        print(f"Has '\"rails\"': {has_rails}")
        print(f"Should detect as web-framework: {has_name and has_rails}")

# Probar Ktor
print("\n" + "=" * 80)
print("TESTING KTOR")
print("=" * 80)

project_path2 = "uploads/ktor-main/ktor-main"
basenames2 = [f.lower() for f in os.listdir(project_path2)]
print(f"'build.gradle.kts' in basenames: {'build.gradle.kts' in basenames2}")

props_path = os.path.join(project_path2, "gradle.properties")
print(f"gradle.properties exists: {os.path.exists(props_path)}")

if os.path.exists(props_path):
    with open(props_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        has_group1 = "group=io.ktor" in content
        has_group2 = "group = io.ktor" in content
        print(f"Has 'group=io.ktor': {has_group1}")
        print(f"Has 'group = io.ktor': {has_group2}")
        print(f"Should detect as web-framework: {has_group1 or has_group2}")

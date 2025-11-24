import os

rails_path = "uploads/rails-main/rails-main"
print(f"Checking Rails: {rails_path}")
print(f"Exists: {os.path.exists(rails_path)}")

# Verificar basenames
basenames = [f.lower() for f in os.listdir(rails_path)]
print(f"'gemfile' in basenames: {'gemfile' in basenames}")

# Verificar gemspec
gemspec_files = [f for f in os.listdir(rails_path) if f.endswith(".gemspec")]
print(f"Gemspec files: {gemspec_files}")

if gemspec_files:
    with open(os.path.join(rails_path, gemspec_files[0]), 'r', encoding='utf-8') as f:
        content = f.read().lower()
        has_name = 's.name' in content
        has_rails = '"rails"' in content
        print(f"  Has 's.name': {has_name}")
        print(f"  Has '\"rails\"': {has_rails}")
        print(f"  Should return web-framework: {has_name and has_rails}")

# Verificar Ktor
ktor_path = "uploads/ktor-main/ktor-main"
print(f"\nChecking Ktor: {ktor_path}")
print(f"Exists: {os.path.exists(ktor_path)}")

basenames_ktor = [f.lower() for f in os.listdir(ktor_path)]
print(f"'build.gradle.kts' in basenames: {'build.gradle.kts' in basenames_ktor}")

gradle_props = os.path.join(ktor_path, "gradle.properties")
if os.path.exists(gradle_props):
    with open(gradle_props, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        has_group = 'group=io.ktor' in content
        print(f"  Has 'group=io.ktor': {has_group}")
        print(f"  Should return web-framework: {has_group}")

# Verificar Tokio
tokio_path = "uploads/tokio-master/tokio-master"
print(f"\nChecking Tokio: {tokio_path}")
print(f"Exists: {os.path.exists(tokio_path)}")

cargo_path = os.path.join(tokio_path, "tokio", "Cargo.toml")
print(f"Cargo.toml exists at tokio/: {os.path.exists(cargo_path)}")

if os.path.exists(cargo_path):
    with open(cargo_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        has_name_tokio = 'name = "tokio"' in content
        print(f"  Has 'name = \"tokio\"': {has_name_tokio}")
        print(f"  Should return library: {has_name_tokio}")

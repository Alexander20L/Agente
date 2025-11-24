import os
from core.analyzer import detect_project_type

# Simular el resultado de análisis para Rails
print("=" * 80)
print("TESTING RAILS DETECTION")
print("=" * 80)

rails_path = "uploads/rails-main/rails-main"
print(f"Path: {rails_path}")
print(f"Exists: {os.path.exists(rails_path)}")

if os.path.exists(rails_path):
    # Verificar gemspec
    gemspec_files = [f for f in os.listdir(rails_path) if f.endswith(".gemspec")]
    print(f"Gemspec files in root: {gemspec_files}")
    
    if gemspec_files:
        with open(os.path.join(rails_path, gemspec_files[0]), 'r', encoding='utf-8') as f:
            content = f.read().lower()
            print(f"Contains 's.name': {'s.name' in content}")
            print(f"Contains '\"rails\"': {'\"rails\"' in content}")
    
    # Simular result para detect_project_type
    mock_result = {
        "project_path": rails_path,
        "total_files": 4850
    }
    
    detected = detect_project_type(mock_result)
    print(f"\nDetected type: {detected}")
    print(f"Expected: web-framework")
    print(f"Match: {detected == 'web-framework'}")

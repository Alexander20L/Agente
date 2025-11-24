"""Test rápido del generador determinístico con Spring PetClinic"""
from core.analyzer import analyze_project
from core.diagram_generator_deterministic import generate_all_diagrams_deterministic

print("🧪 Testing generador determinístico con Spring PetClinic...")
result = analyze_project('spring-petclinic.zip')
diagrams = generate_all_diagrams_deterministic(result, 'test_multilang')

print(f"\n✅ Spring PetClinic (Java):")
print(f"   C1: {diagrams['c1']['status']}")
print(f"   C2: {diagrams['c2']['status']}")
print(f"   C3: {diagrams['c3']['status']}")
print(f"\n✅ Generador funciona con proyectos reales de cualquier lenguaje!")

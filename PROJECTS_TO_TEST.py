"""
Script para descargar proyectos de ejemplo de diferentes tecnologías
y agregarlos a la carpeta uploads/ para testing
"""

# Proyectos sugeridos para testing multi-lenguaje:

PROJECTS_TO_TEST = {
    "Go": {
        "name": "Gin Web Framework",
        "repo": "https://github.com/gin-gonic/gin",
        "type": "web-framework",
        "size": "medium"
    },
    "Rust": {
        "name": "Actix Web",
        "repo": "https://github.com/actix/actix-web",
        "type": "web-framework",
        "size": "medium"
    },
    ".NET/C#": {
        "name": "eShopOnWeb",
        "repo": "https://github.com/dotnet-architecture/eShopOnWeb",
        "type": "api-backend",
        "size": "medium"
    },
    "Node.js": {
        "name": "Express.js Examples",
        "repo": "https://github.com/expressjs/express",
        "type": "web-framework",
        "size": "medium"
    },
    "Ruby": {
        "name": "Rails Sample App",
        "repo": "https://github.com/rails/rails",
        "type": "web-framework",
        "size": "large"
    },
    "PHP": {
        "name": "Laravel Framework",
        "repo": "https://github.com/laravel/laravel",
        "type": "web-framework",
        "size": "medium"
    },
    "Flutter/Dart": {
        "name": "Flutter Gallery",
        "repo": "https://github.com/flutter/gallery",
        "type": "mobile-app",
        "size": "medium"
    },
    "React Native": {
        "name": "React Native Sample",
        "repo": "https://github.com/facebook/react-native",
        "type": "mobile-app",
        "size": "large"
    },
    "TypeScript": {
        "name": "NestJS Sample",
        "repo": "https://github.com/nestjs/nest",
        "type": "api-backend",
        "size": "medium"
    },
    "Kotlin": {
        "name": "Ktor Sample",
        "repo": "https://github.com/ktorio/ktor",
        "type": "web-framework",
        "size": "medium"
    }
}

print("="*80)
print("📋 PROYECTOS SUGERIDOS PARA TESTING MULTI-LENGUAJE")
print("="*80)

for lang, info in PROJECTS_TO_TEST.items():
    print(f"\n{lang}:")
    print(f"  Nombre: {info['name']}")
    print(f"  Repo: {info['repo']}")
    print(f"  Tipo: {info['type']}")
    print(f"  Tamaño: {info['size']}")

print("\n" + "="*80)
print("💡 INSTRUCCIONES:")
print("="*80)
print("""
Para agregar proyectos al test:

1. Descarga el ZIP desde GitHub:
   - Ve al repo
   - Click en "Code" → "Download ZIP"

2. Coloca el ZIP en la carpeta uploads/

3. Agrega la configuración en test_multiple_projects.py:
   {
       "name": "Nombre del Proyecto",
       "path": "uploads/proyecto.zip",
       "expected_type": "api-backend",
       "language": "Go",
       "description": "Descripción"
   }

4. Ejecuta: python test_multiple_projects.py
""")

print("\n🎯 TIPOS DE PROYECTOS SOPORTADOS:")
print("   - api-backend")
print("   - gui-application")
print("   - mobile-app")
print("   - web-frontend")
print("   - compiler")
print("   - cli-tool")
print("   - library")
print("   - microservice")

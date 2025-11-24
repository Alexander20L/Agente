"""
Proyectos Open-Source Reales para Testing
Descarga estos proyectos desde GitHub y colócalos en uploads/
"""

REAL_PROJECTS = {
    "Go": [
        {
            "name": "Fiber Web Framework",
            "url": "https://github.com/gofiber/fiber/archive/refs/heads/master.zip",
            "description": "Popular Go web framework (Express-like)",
            "expected_type": "web-framework",
            "size": "~500 files",
            "filename": "fiber-master.zip"
        },
        {
            "name": "Echo Framework",
            "url": "https://github.com/labstack/echo/archive/refs/heads/master.zip",
            "description": "High performance Go web framework",
            "expected_type": "web-framework",
            "size": "~200 files",
            "filename": "echo-master.zip"
        }
    ],
    "Rust": [
        {
            "name": "Actix Web",
            "url": "https://github.com/actix/actix-web/archive/refs/heads/master.zip",
            "description": "Powerful Rust web framework",
            "expected_type": "web-framework",
            "size": "~400 files",
            "filename": "actix-web-master.zip"
        },
        {
            "name": "Ripgrep",
            "url": "https://github.com/BurntSushi/ripgrep/archive/refs/heads/master.zip",
            "description": "Fast grep alternative (CLI tool)",
            "expected_type": "cli-tool",
            "size": "~150 files",
            "filename": "ripgrep-master.zip"
        }
    ],
    "C#/.NET": [
        {
            "name": "eShopOnWeb",
            "url": "https://github.com/dotnet-architecture/eShopOnWeb/archive/refs/heads/main.zip",
            "description": "Microsoft's reference e-commerce app",
            "expected_type": "api-backend",
            "size": "~300 files",
            "filename": "eShopOnWeb-main.zip"
        },
        {
            "name": "CleanArchitecture",
            "url": "https://github.com/jasontaylordev/CleanArchitecture/archive/refs/heads/main.zip",
            "description": "Clean Architecture template",
            "expected_type": "api-backend",
            "size": "~200 files",
            "filename": "CleanArchitecture-main.zip"
        }
    ],
    "Node.js/TypeScript": [
        {
            "name": "NestJS Sample",
            "url": "https://github.com/nestjs/nest/archive/refs/heads/master.zip",
            "description": "Progressive Node.js framework",
            "expected_type": "web-framework",
            "size": "~800 files",
            "filename": "nest-master.zip"
        }
    ],
    "PHP": [
        {
            "name": "Laravel Framework",
            "url": "https://github.com/laravel/laravel/archive/refs/heads/master.zip",
            "description": "Popular PHP framework",
            "expected_type": "web-framework",
            "size": "~100 files",
            "filename": "laravel-master.zip"
        }
    ]
}

print("="*80)
print("📥 PROYECTOS OPEN-SOURCE REALES PARA TESTING")
print("="*80)

for lang, projects in REAL_PROJECTS.items():
    print(f"\n{'='*80}")
    print(f"🔧 {lang}")
    print("="*80)
    
    for i, proj in enumerate(projects, 1):
        print(f"\n{i}. {proj['name']}")
        print(f"   URL: {proj['url']}")
        print(f"   Descripción: {proj['description']}")
        print(f"   Tipo esperado: {proj['expected_type']}")
        print(f"   Tamaño: {proj['size']}")
        print(f"   Guardar como: uploads/{proj['filename']}")

print("\n" + "="*80)
print("💡 INSTRUCCIONES DE DESCARGA")
print("="*80)
print("""
OPCIÓN 1: Descarga Manual
1. Abre cada URL en tu navegador
2. Se descargará automáticamente el ZIP
3. Mueve el archivo a la carpeta uploads/
4. Asegúrate que el nombre coincida con 'filename'

OPCIÓN 2: Usando PowerShell (más rápido)
Ejecuta estos comandos en PowerShell:
""")

print("\n# Descargar todos los proyectos:")
for lang, projects in REAL_PROJECTS.items():
    for proj in projects:
        print(f"Invoke-WebRequest -Uri '{proj['url']}' -OutFile 'uploads/{proj['filename']}'")

print("\n" + "="*80)
print("🎯 PROYECTOS RECOMENDADOS PARA EMPEZAR (más pequeños)")
print("="*80)
print("""
1. Ripgrep (Rust CLI) - ~150 files ⭐ RECOMENDADO
2. Laravel (PHP) - ~100 files ⭐ RECOMENDADO  
3. Echo (Go) - ~200 files ⭐ RECOMENDADO
4. CleanArchitecture (.NET) - ~200 files ⭐ RECOMENDADO
""")

print("\n📦 Después de descargar, ejecuta:")
print("   python test_real_projects.py")

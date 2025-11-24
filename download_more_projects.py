"""
Script automático para descargar más proyectos open-source reales
Descarga proyectos variados para testing exhaustivo
"""
import subprocess
import os

# Crear carpeta uploads si no existe
os.makedirs("uploads", exist_ok=True)

# Proyectos adicionales para testing
ADDITIONAL_PROJECTS = [
    # Python
    {
        "name": "FastAPI",
        "url": "https://github.com/tiangolo/fastapi/archive/refs/heads/master.zip",
        "file": "uploads/fastapi-master.zip",
        "lang": "Python",
        "expected": "web-framework",
        "stars": "70k+",
        "size": "~400 files"
    },
    {
        "name": "Django",
        "url": "https://github.com/django/django/archive/refs/heads/main.zip",
        "file": "uploads/django-main.zip",
        "lang": "Python",
        "expected": "web-framework",
        "stars": "78k+",
        "size": "~3000 files"
    },
    # Node.js/TypeScript
    {
        "name": "Express",
        "url": "https://github.com/expressjs/express/archive/refs/heads/master.zip",
        "file": "uploads/express-master.zip",
        "lang": "JavaScript",
        "expected": "web-framework",
        "stars": "64k+",
        "size": "~200 files"
    },
    # Rust
    {
        "name": "Tokio",
        "url": "https://github.com/tokio-rs/tokio/archive/refs/heads/master.zip",
        "file": "uploads/tokio-master.zip",
        "lang": "Rust",
        "expected": "library",
        "stars": "26k+",
        "size": "~600 files"
    },
    # Go
    {
        "name": "Gin",
        "url": "https://github.com/gin-gonic/gin/archive/refs/heads/master.zip",
        "file": "uploads/gin-master.zip",
        "lang": "Go",
        "expected": "web-framework",
        "stars": "76k+",
        "size": "~300 files"
    },
    # Ruby
    {
        "name": "Rails",
        "url": "https://github.com/rails/rails/archive/refs/heads/main.zip",
        "file": "uploads/rails-main.zip",
        "lang": "Ruby",
        "expected": "web-framework",
        "stars": "55k+",
        "size": "~4000 files"
    },
    # TypeScript
    {
        "name": "NestJS",
        "url": "https://github.com/nestjs/nest/archive/refs/heads/master.zip",
        "file": "uploads/nest-master.zip",
        "lang": "TypeScript",
        "expected": "web-framework",
        "stars": "65k+",
        "size": "~800 files"
    },
    # Kotlin
    {
        "name": "Ktor",
        "url": "https://github.com/ktorio/ktor/archive/refs/heads/main.zip",
        "file": "uploads/ktor-main.zip",
        "lang": "Kotlin",
        "expected": "web-framework",
        "stars": "12k+",
        "size": "~2000 files"
    }
]

def download_project(project):
    """Descarga un proyecto usando Invoke-WebRequest"""
    print(f"\n📥 Descargando: {project['name']} ({project['lang']})")
    print(f"   ⭐ {project['stars']} | 📦 {project['size']}")
    print(f"   Tipo esperado: {project['expected']}")
    
    # Verificar si ya existe
    if os.path.exists(project['file']):
        print(f"   ⚠️  Ya existe, saltando...")
        return True
    
    try:
        cmd = f"Invoke-WebRequest -Uri '{project['url']}' -OutFile '{project['file']}'"
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"   ✅ Descargado: {project['file']}")
            return True
        else:
            print(f"   ❌ Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout - el archivo es muy grande")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("="*80)
    print("📦 DESCARGADOR AUTOMÁTICO DE PROYECTOS OPEN-SOURCE")
    print("="*80)
    
    print(f"\n📋 Se descargarán {len(ADDITIONAL_PROJECTS)} proyectos:")
    for i, proj in enumerate(ADDITIONAL_PROJECTS, 1):
        print(f"   {i}. {proj['name']} ({proj['lang']}) - {proj['stars']}")
    
    print("\n" + "="*80)
    print("🚀 INICIANDO DESCARGAS...")
    print("="*80)
    
    successful = 0
    failed = 0
    skipped = 0
    
    for project in ADDITIONAL_PROJECTS:
        if os.path.exists(project['file']):
            skipped += 1
        elif download_project(project):
            successful += 1
        else:
            failed += 1
    
    print("\n" + "="*80)
    print("📊 RESUMEN DE DESCARGAS")
    print("="*80)
    print(f"✅ Exitosas: {successful}")
    print(f"⏭️  Saltadas: {skipped}")
    print(f"❌ Fallidas: {failed}")
    print(f"📦 Total: {len(ADDITIONAL_PROJECTS)}")
    
    if successful > 0 or skipped > 0:
        print("\n" + "="*80)
        print("🎯 PRÓXIMOS PASOS")
        print("="*80)
        print("1. Agrega los proyectos descargados a test_real_projects.py:")
        print("   REAL_PROJECTS = [")
        for proj in ADDITIONAL_PROJECTS:
            if os.path.exists(proj['file']):
                print(f"       {{")
                print(f"           'name': '{proj['name']}',")
                print(f"           'path': '{proj['file']}',")
                print(f"           'expected_type': '{proj['expected']}',")
                print(f"           'language': '{proj['lang']}',")
                print(f"           'description': '{proj['name']} framework ({proj['stars']})'")
                print(f"       }},")
        print("   ]")
        print("\n2. Ejecuta: python test_real_projects.py")

if __name__ == "__main__":
    main()

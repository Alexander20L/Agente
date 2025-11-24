import zipfile
import os
import re
import json

# ================================================================
#  PROJECT NAME DETECTION
# ================================================================

def detect_project_name(project_path: str) -> str:
    """Obtiene el nombre real del proyecto desde archivos estándar."""
    # --- pyproject.toml ---
    toml_path = os.path.join(project_path, "pyproject.toml")
    if os.path.exists(toml_path):
        with open(toml_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("name"):
                    # name = "triton" o name = 'triton'
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        name = parts[1].strip().strip('"').strip("'")
                        if name:
                            return name

    # --- setup.py ---
    setup_path = os.path.join(project_path, "setup.py")
    if os.path.exists(setup_path):
        with open(setup_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"name\s*=\s*['\"](.+?)['\"]", content)
            if match:
                return match.group(1)

    # --- paquete raíz (paquete Python con __init__.py) ---
    for item in os.listdir(project_path):
        full = os.path.join(project_path, item)
        if os.path.isdir(full) and os.path.exists(os.path.join(full, "__init__.py")):
            return item

    # fallback: nombre de carpeta
    return os.path.basename(project_path)


# ================================================================
#  PROJECT TYPE DETECTION (VERSIÓN PRO)
# ================================================================

def detect_project_type(analysis_result: dict) -> str:
    """
    Detecta el tipo de proyecto (UNIVERSAL):
    - library
    - compiler (DSL, JIT, backend GPU)
    - api-backend
    - gui-application
    - ml-app
    - mobile-app
    - microservice
    - unknown
    """
    project_path = analysis_result["project_path"]

    all_files = []
    for root, dirs, files in os.walk(project_path):
        for f in files:
            full = os.path.join(root, f)
            all_files.append(full.lower())

    basenames = [os.path.basename(f) for f in all_files]
    extensions = [os.path.splitext(f)[1] for f in all_files]

    # === JAVA / SPRING BOOT ===
    if any(f in basenames for f in ["pom.xml", "build.gradle", "build.gradle.kts"]):
        java_hits = sum(1 for ext in extensions if ext == ".java")
        if java_hits >= 5:
            # Spring Boot indicators
            for root, dirs, files in os.walk(project_path):
                for f in files:
                    if f.endswith(".java"):
                        content = _read_text(os.path.join(root, f)).lower()
                        if any(kw in content for kw in ["@springbootapplication", "@restcontroller", "@controller"]):
                            return "api-backend"
            return "library"

    # === C# / .NET ===
    if any(f.endswith(".csproj") or f.endswith(".sln") for f in basenames):
        csharp_hits = sum(1 for ext in extensions if ext == ".cs")
        if csharp_hits >= 3:
            # Leer .csproj para detectar tipo
            for root, dirs, files in os.walk(project_path):
                for f in files:
                    if f.endswith(".csproj"):
                        csproj_content = _read_text(os.path.join(root, f)).lower()
                        
                        # Web API detection
                        if "microsoft.net.sdk.web" in csproj_content:
                            return "api-backend"
                        if "aspnetcore" in csproj_content or "microsoft.aspnetcore" in csproj_content:
                            return "api-backend"
                        
                        break
            
            # ASP.NET Core indicators en archivos
            for root, dirs, files in os.walk(project_path):
                for f in files:
                    if f.lower() in ["program.cs", "startup.cs"]:
                        content = _read_text(os.path.join(root, f)).lower()
                        # Web indicators
                        web_indicators = ["webapplication", "webhost", "mapcontrollers", "useendpoints", "[apicontroller]"]
                        if any(indicator in content for indicator in web_indicators):
                            return "api-backend"
                    
                    # Detectar controllers
                    if f.endswith("Controller.cs"):
                        content = _read_text(os.path.join(root, f)).lower()
                        if "[apicontroller]" in content or "[controller]" in content:
                            return "api-backend"
            
            # Check for Controllers folder
            has_controllers = any("controllers" in d.lower() for root, dirs, _ in os.walk(project_path) for d in dirs)
            if has_controllers or "appsettings.json" in basenames:
                return "api-backend"
            
            # WPF/WinForms GUI
            if any("window" in f or "form" in f for f in basenames):
                return "gui-application"
            return "library"

    # === GO ===
    if "go.mod" in basenames or "go.sum" in basenames:
        # Leer go.mod para detectar si es framework
        for root, dirs, files in os.walk(project_path):
            if "go.mod" in files:
                go_mod_content = _read_text(os.path.join(root, "go.mod")).lower()
                
                # Web framework detection (sin main.go = es framework/library)
                web_frameworks = ["echo", "gin", "fiber", "chi", "gorilla/mux"]
                if any(fw in go_mod_content for fw in web_frameworks):
                    if "main.go" not in basenames:
                        return "web-framework"
                    else:
                        return "api-backend"
                break
        
        # Si tiene main.go, es aplicación
        if "main.go" in basenames:
            return "api-backend"
        return "library"

    # === RUST ===
    if "cargo.toml" in basenames:
        # Leer Cargo.toml para detectar tipo
        for root, dirs, files in os.walk(project_path):
            if "Cargo.toml" in files:
                cargo_content = _read_text(os.path.join(root, "Cargo.toml")).lower()
                
                # CLI tool detection
                cli_indicators = ["clap", "structopt", "argh", "dialoguer"]
                if any(cli in cargo_content for cli in cli_indicators):
                    return "cli-tool"
                
                # Async runtime library (Tokio, async-std) - verificar name = "tokio"
                async_runtimes = [('name = "tokio"', "tokio"), ('name = "async-std"', "async-std")]
                for name_pattern, runtime in async_runtimes:
                    if name_pattern in cargo_content:
                        # Si NO tiene web framework deps, es solo runtime library
                        web_deps = ["actix", "rocket", "warp", "axum"]
                        has_web = any(w in cargo_content for w in web_deps)
                        if not has_web:
                            return "library"
                
                # Si es un workspace, buscar en subdirectorios
                if "[workspace]" in cargo_content:
                    # Buscar en subdirectorios comunes
                    for subdir in ["tokio", "async-std"]:
                        subdir_cargo = os.path.join(project_path, subdir, "Cargo.toml")
                        if os.path.exists(subdir_cargo):
                            sub_content = _read_text(subdir_cargo).lower()
                            if f'name = "{subdir}"' in sub_content:
                                # Es el runtime library
                                web_deps = ["actix", "rocket", "warp", "axum"]
                                has_web = any(w in sub_content for w in web_deps)
                                if not has_web:
                                    return "library"
                
                # Web framework detection
                web_frameworks = ["actix-web", "rocket", "warp", "axum"]
                if any(fw in cargo_content for fw in web_frameworks):
                    # Si tiene main.rs = aplicación, sino = framework/library
                    if "main.rs" in basenames:
                        return "api-backend"
                    else:
                        return "web-framework"
                
                break
        
        # Fallback: si tiene main.rs, probablemente es CLI o binary
        if "main.rs" in basenames or any("bin" in f for f in basenames):
            # Check si hay web patterns en código
            has_web = any("http" in f or "server" in f or "route" in f for f in basenames)
            if has_web:
                return "api-backend"
            return "cli-tool"
        return "library"

    # === PHP / LARAVEL ===
    if "composer.json" in basenames:
        # Leer composer.json para detectar tipo
        for root, dirs, files in os.walk(project_path):
            if "composer.json" in files:
                composer_content = _read_text(os.path.join(root, "composer.json")).lower()
                
                # Laravel/Symfony framework detection
                if "laravel/framework" in composer_content or "symfony/framework" in composer_content:
                    # Check si es skeleton básico o app real
                    # Skeleton tiene pocos controllers, app real tiene muchos
                    controller_files = [f for f in all_files if "controller" in f.lower()]
                    
                    # Si tiene artisan pero pocos controllers (<5) = framework skeleton
                    if "artisan" in basenames and len(controller_files) < 5:
                        return "web-framework"
                    # Si tiene muchos controllers o models = aplicación real
                    elif len(controller_files) >= 5:
                        return "api-backend"
                break
        
        # Fallback: si tiene artisan o routes = backend
        if any(f in basenames for f in ["artisan", "index.php", "routes"]):
            return "api-backend"
        return "library"

    # Ruby section moved up - see after Rust section

    # === NODE.JS / JAVASCRIPT / TYPESCRIPT ===
    if "package.json" in basenames:
        # Leer package.json para detectar tipo
        for root, dirs, files in os.walk(project_path):
            if "package.json" in files:
                try:
                    import json as json_lib
                    with open(os.path.join(root, "package.json"), 'r', encoding='utf-8') as f:
                        package_data = json_lib.load(f)
                    
                    package_name = package_data.get('name', '').lower()
                    
                    # Web frameworks detection: si name = "express", es el framework
                    framework_names = ['express', 'koa', 'fastify', 'hapi']
                    if package_name in framework_names:
                        return "web-framework"
                    
                    # NestJS: si name = "@nestjs/core", es el framework
                    if '@nestjs/core' in package_name or '@nestjs/common' in package_name:
                        return "web-framework"
                    
                    deps = package_data.get('dependencies', {})
                    if '@nestjs/core' in deps or '@nestjs/common' in deps:
                        # Si tiene dependencias NestJS, es aplicación que lo usa
                        return "api-backend"
                    
                except:
                    pass
                break
    
    # === RUBY / RAILS === (moved here to detect BEFORE fallback api-backend)
    if "gemfile" in basenames:
        # Verificar si es el framework Rails en sí (leer gemspec en raíz primero)
        try:
            gemspec_files = [f for f in os.listdir(project_path) if f.endswith(".gemspec")]
            for gemspec_file in gemspec_files:
                gemspec_content = _read_text(os.path.join(project_path, gemspec_file)).lower()
                # Si s.name = "rails", es el framework
                if 's.name' in gemspec_content and '"rails"' in gemspec_content:
                    return "web-framework"
        except:
            pass
        
        # Leer Gemfile para detectar Rails app
        for root, dirs, files in os.walk(project_path):
            if "Gemfile" in files:
                gemfile_content = _read_text(os.path.join(root, "Gemfile")).lower()
                
                # Rails framework detection
                if "gem 'rails'" in gemfile_content or 'gem "rails"' in gemfile_content:
                    # Check si tiene app/ folder (estructura Rails típica)
                    has_app_folder = any("app" in d for root2, dirs2, _ in os.walk(project_path) for d in dirs2)
                    if has_app_folder and "rakefile" in basenames:
                        return "api-backend"
                break
        
        if any(f in basenames for f in ["rakefile", "config.ru"]):
            return "api-backend"
        return "library"
    
    # === KOTLIN === (moved here to detect BEFORE fallback api-backend)
    if "build.gradle" in basenames or "build.gradle.kts" in basenames:
        # DEBUG
        if "ktor" in project_path.lower():
            print(f"[DEBUG] Entered Kotlin section")
            print(f"[DEBUG] build.gradle in basenames: {'build.gradle' in basenames}")
            print(f"[DEBUG] build.gradle.kts in basenames: {'build.gradle.kts' in basenames}")
        
        # Verificar gradle.properties en raíz primero para group=io.ktor
        gradle_props_path = os.path.join(project_path, "gradle.properties")
        if os.path.exists(gradle_props_path):
            props_content = _read_text(gradle_props_path).lower()
            if "ktor" in project_path.lower():
                print(f"[DEBUG] gradle.properties exists")
                print(f"[DEBUG] Content has 'group=io.ktor': {'group=io.ktor' in props_content}")
            if "group=io.ktor" in props_content or "group = io.ktor" in props_content:
                if "ktor" in project_path.lower():
                    print(f"[DEBUG] Should return web-framework here!")
                return "web-framework"
        
        # Android detection (check first to avoid misclassification)
        android_hits = sum(1 for f in basenames if ".kt" in f or ".java" in f)
        if android_hits >= 5 and "androidmanifest.xml" in basenames:
            return "mobile-app"
    
    # === MOBILE ===
    if any(f in basenames for f in ["package.json", "app.json", "expo.json"]):
        # React Native
        if any("react-native" in f.lower() for f in all_files):
            return "mobile-app"
    if "pubspec.yaml" in basenames:  # Flutter
        return "mobile-app"
    if any(f.endswith(".xcodeproj") or f.endswith(".xcworkspace") for f in basenames):  # iOS
        return "mobile-app"
    if "androidmanifest.xml" in basenames:
        return "mobile-app"

    # === MICROSERVICES ===
    dockerfile_count = sum(1 for f in basenames if f == "dockerfile")
    if dockerfile_count >= 2:
        return "microservice"
    if "docker-compose.yml" in basenames or "docker-compose.yaml" in basenames:
        # Check if multiple services
        for root, dirs, files in os.walk(project_path):
            for f in files:
                if f in ["docker-compose.yml", "docker-compose.yaml"]:
                    content = _read_text(os.path.join(root, f))
                    if content.count("services:") >= 1 and content.count("image:") + content.count("build:") >= 2:
                        return "microservice"

    # === PYTHON ===
    has_setup = "setup.py" in basenames
    has_pyproject = "pyproject.toml" in basenames
    has_app_entry = any(x in basenames for x in ["app.py", "main.py", "server.py", "manage.py"])
    
    # Python web frameworks detection
    if has_setup or has_pyproject:
        for root, dirs, files in os.walk(project_path):
            if "setup.py" in files or "pyproject.toml" in files:
                content = ""
                if "setup.py" in files:
                    content = _read_text(os.path.join(root, "setup.py")).lower()
                elif "pyproject.toml" in files:
                    content = _read_text(os.path.join(root, "pyproject.toml")).lower()
                
                # Framework detection: verificar si ES el framework (name = "fastapi") o lo usa
                # Si name = "fastapi" o "django" = es el framework en sí
                framework_names = ["fastapi", "django", "flask"]
                for fw in framework_names:
                    if f'name = "{fw}"' in content or f"name = '{fw}'" in content:
                        return "web-framework"
                
                # Si tiene manage.py = Django application (app que usa Django)
                if "manage.py" in basenames and "django" in content:
                    return "api-backend"
                
                # Si menciona fastapi/django/flask en dependencias = app que los usa
                if any(fw in content for fw in ["fastapi", "django", "flask"]):
                    if has_app_entry:
                        return "api-backend"
                break

    if (has_setup or has_pyproject) and not has_app_entry:
        # Compiler/DSL detection
        if any("compiler" in f or "jit" in f for f in basenames):
            return "compiler"
        return "library"

    # Compiler / DSL detection (Triton-like)
    compiler_hits = sum(
        1 for f in basenames
        if any(kw in f for kw in ["compiler", "backend", "jit"])
    )
    if compiler_hits >= 5:
        return "compiler"

    # GUI DETECTION FIRST (antes de api-backend)
    # Python GUI: PyQt5/6, PySide, Tkinter, Kivy, wxPython
    gui_file_indicators = ["window.py", "widget.py", "view.py", "dialog.py", "form.py", ".ui"]
    gui_lib_indicators = ["pyqt", "pyside", "tkinter", "kivy", "wxpython"]
    
    gui_file_hits = sum(1 for f in basenames if any(kw in f for kw in gui_file_indicators))
    gui_lib_hits = sum(1 for f in basenames if any(kw in f for kw in gui_lib_indicators))
    
    # Check imports in Python files for GUI libraries
    gui_import_count = 0
    if gui_file_hits > 0 or gui_lib_hits > 0:
        for root, dirs, files in os.walk(project_path):
            for f in files:
                if f.endswith(".py"):
                    content = _read_text(os.path.join(root, f)).lower()
                    if any(lib in content for lib in ["from pyqt5", "from pyqt6", "import pyqt", 
                                                       "from pyside", "import pyside",
                                                       "import tkinter", "from tkinter",
                                                       "from kivy", "import wx"]):
                        gui_import_count += 1
                        if gui_import_count >= 2:  # Al menos 2 archivos con imports GUI
                            return "gui-application"
    
    # .NET GUI: WPF, WinForms
    dotnet_gui_indicators = ["window.cs", "form.cs", ".xaml", "app.xaml", "mainwindow.xaml"]
    dotnet_gui_hits = sum(1 for f in basenames if any(kw in f for kw in dotnet_gui_indicators))
    if dotnet_gui_hits >= 2:
        return "gui-application"
    
    # Check if has main.py with GUI but no API indicators
    if "main.py" in basenames and (gui_file_hits + gui_lib_hits + gui_import_count) > 0:
        # Verify it's not an API
        api_indicators = ["fastapi", "flask", "django", "api", "rest", "endpoint"]
        api_found = False
        for root, dirs, files in os.walk(project_path):
            if "main.py" in files:
                content = _read_text(os.path.join(root, "main.py")).lower()
                if any(indicator in content for indicator in api_indicators):
                    api_found = True
                    break
        if not api_found:
            return "gui-application"

    # Backend API (FastAPI/Flask/Django) - AFTER GUI detection
    if has_app_entry:
        # DEBUG: Verificar qué proyectos llegan aquí
        if "ktor" in project_path.lower() or "tokio" in project_path.lower():
            print(f"[DEBUG] Fallback api-backend triggered for {project_path}")
            print(f"[DEBUG] has_app_entry = {has_app_entry}")
        return "api-backend"

    # Fallback GUI detection by file patterns
    if gui_file_hits + gui_lib_hits >= 2:
        return "gui-application"

    # ML app: train/model files + notebooks
    ml_name_hits = sum(
        1 for f in basenames
        if any(kw in f for kw in ["train", "training", "model", "predict"])
    )
    nb_hits = sum(1 for f in all_files if f.endswith(".ipynb"))
    if ml_name_hits + nb_hits >= 3:
        return "ml-app"

    # === NODE.JS ===
    if "package.json" in basenames:
        # Check if it's backend or frontend
        for root, dirs, files in os.walk(project_path):
            if "package.json" in files:
                pkg = _parse_package_json(os.path.join(root, "package.json"))
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if any(k in deps for k in ["express", "@nestjs/core", "koa", "hapi", "fastify"]):
                    return "api-backend"
                if any(k in deps for k in ["react", "vue", "@angular/core", "svelte"]):
                    return "gui-application"

    return "unknown"


# ================================================================
#  SMALL HELPERS
# ================================================================

def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def _add_container(containers, type_, tech, path, source, evidences, score):
    key = (type_, os.path.abspath(path), tech)
    if not any((c.get("_key") == key) for c in containers):
        containers.append({
            "_key": key,
            "type": type_,
            "technology": tech,
            "path": path,
            "source": source,
            "evidences": evidences[:6],
            "score": round(max(0.0, min(score, 1.0)), 2)
        })


def _is_text_file(fname, valid_ext):
    return os.path.splitext(fname)[1].lower() in valid_ext


def _parse_package_json(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except Exception:
        return {}


# ================================================================
#  ACTOR DETECTOR
# ================================================================

def _extract_architectural_layers(components):
    """
    Agrupa componentes por capas arquitectónicas para mejor visualización en C3
    """
    layers = {
        "presentation": [],  # Controllers, Views, UI
        "application": [],   # Services, Use Cases, Application Logic
        "domain": [],        # Entities, Models, Business Logic
        "infrastructure": [] # Repositories, Database, External APIs
    }
    
    for comp in components:
        comp_type = comp.get("type", "").lower()
        comp_name = comp.get("name", "").lower()
        
        # Presentation Layer
        if any(kw in comp_type for kw in ["controller", "view", "ui", "widget", "form"]):
            layers["presentation"].append(comp)
        
        # Application Layer
        elif any(kw in comp_type for kw in ["service", "usecase", "handler", "processor"]):
            layers["application"].append(comp)
        
        # Domain Layer
        elif any(kw in comp_type for kw in ["model", "entity", "domain", "dto"]):
            layers["domain"].append(comp)
        
        # Infrastructure Layer
        elif any(kw in comp_type for kw in ["repository", "dao", "database", "api"]):
            layers["infrastructure"].append(comp)
        
        # Fallback: Por nombre del archivo
        elif any(kw in comp_name for kw in ["controller", "view"]):
            layers["presentation"].append(comp)
        elif any(kw in comp_name for kw in ["service", "handler"]):
            layers["application"].append(comp)
        elif any(kw in comp_name for kw in ["model", "entity"]):
            layers["domain"].append(comp)
        elif any(kw in comp_name for kw in ["repository", "dao"]):
            layers["infrastructure"].append(comp)
    
    # Agregar conteo por capa
    return {
        "presentation": {
            "count": len(layers["presentation"]),
            "components": [c["name"] for c in layers["presentation"][:10]]  # Top 10
        },
        "application": {
            "count": len(layers["application"]),
            "components": [c["name"] for c in layers["application"][:10]]
        },
        "domain": {
            "count": len(layers["domain"]),
            "components": [c["name"] for c in layers["domain"][:10]]
        },
        "infrastructure": {
            "count": len(layers["infrastructure"]),
            "components": [c["name"] for c in layers["infrastructure"][:10]]
        }
    }


def _extract_technologies(containers, components, root_path):
    """
    Extrae las tecnologías clave del proyecto para contexto en diagramas
    """
    techs = {
        "backend": [],
        "frontend": [],
        "database": [],
        "infrastructure": []
    }
    
    # De los contenedores
    for container in containers:
        tech = container.get("technology", "")
        container_type = container.get("type", "")
        
        if container_type == "api-backend":
            techs["backend"].append(tech)
        elif container_type == "frontend":
            techs["frontend"].append(tech)
        elif container_type == "database":
            techs["database"].append(tech)
        else:
            techs["infrastructure"].append(tech)
    
    # Detectar frameworks por archivos clave
    try:
        for root, dirs, files in os.walk(root_path):
            basenames = [f.lower() for f in files]
            
            # Java/Spring Boot
            if "pom.xml" in basenames or "build.gradle" in basenames:
                if "Spring Boot" not in techs["backend"]:
                    techs["backend"].append("Spring Boot")
            
            # Node.js
            if "package.json" in basenames:
                pkg_path = os.path.join(root, "package.json")
                pkg_content = _read_text(pkg_path)
                if "express" in pkg_content.lower():
                    techs["backend"].append("Express.js")
                if "react" in pkg_content.lower():
                    techs["frontend"].append("React")
                if "vue" in pkg_content.lower():
                    techs["frontend"].append("Vue.js")
            
            # Python
            if "requirements.txt" in basenames or "pyproject.toml" in basenames:
                req_file = "requirements.txt" if "requirements.txt" in basenames else "pyproject.toml"
                req_path = os.path.join(root, req_file)
                req_content = _read_text(req_path).lower()
                if "fastapi" in req_content:
                    techs["backend"].append("FastAPI")
                elif "django" in req_content:
                    techs["backend"].append("Django")
                elif "flask" in req_content:
                    techs["backend"].append("Flask")
                
                if "pyqt" in req_content or "pyside" in req_content:
                    techs["frontend"].append("PyQt5")
    except:
        pass
    
    # Deduplicar
    for key in techs:
        techs[key] = list(dict.fromkeys(techs[key]))
    
    return techs


def _extract_data_flows(components, relations):
    """
    Identifica los flujos de datos principales basados en relaciones
    """
    flows = []
    
    # Contar relaciones por componente
    relation_counts = {}
    for rel in relations:
        from_comp = rel["from"]
        to_comp = rel["to"]
        
        if from_comp not in relation_counts:
            relation_counts[from_comp] = {"in": 0, "out": 0}
        if to_comp not in relation_counts:
            relation_counts[to_comp] = {"in": 0, "out": 0}
        
        relation_counts[from_comp]["out"] += 1
        relation_counts[to_comp]["in"] += 1
    
    # Identificar hubs (componentes con muchas conexiones)
    hubs = []
    for comp, counts in relation_counts.items():
        total = counts["in"] + counts["out"]
        if total >= 5:  # Threshold
            hubs.append({
                "component": comp,
                "connections": total,
                "type": "hub" if counts["out"] > counts["in"] else "sink"
            })
    
    # Ordenar por conexiones
    hubs.sort(key=lambda x: x["connections"], reverse=True)
    
    return {
        "total_relations": len(relations),
        "hubs": hubs[:5],  # Top 5 hubs
        "highly_connected_components": len([c for c in relation_counts.values() if c["in"] + c["out"] >= 3])
    }


def _detect_architecture_patterns(project_type, components, containers):
    """
    Detecta patrones arquitectónicos comunes
    """
    patterns = []
    
    # Contar tipos de componentes
    comp_types = {}
    for comp in components:
        comp_type = comp.get("type", "unknown")
        comp_types[comp_type] = comp_types.get(comp_type, 0) + 1
    
    # MVC / MVP / MVVM
    has_controllers = comp_types.get("controller", 0) > 0
    has_views = comp_types.get("view", 0) > 0
    has_models = comp_types.get("model", 0) > 0
    
    if has_controllers and has_views and has_models:
        patterns.append({
            "name": "MVC (Model-View-Controller)",
            "confidence": 0.9,
            "evidence": f"{comp_types.get('controller', 0)} controllers, {comp_types.get('view', 0)} views, {comp_types.get('model', 0)} models"
        })
    
    # Layered Architecture (N-Tier)
    has_services = comp_types.get("service", 0) > 0
    has_repositories = comp_types.get("repository", 0) > 0
    
    if has_controllers and has_services and has_repositories:
        patterns.append({
            "name": "Layered Architecture (3-Tier)",
            "confidence": 0.85,
            "evidence": f"Presentation ({comp_types.get('controller', 0)}), Business ({comp_types.get('service', 0)}), Data ({comp_types.get('repository', 0)})"
        })
    
    # Repository Pattern
    if has_repositories and has_models:
        patterns.append({
            "name": "Repository Pattern",
            "confidence": 0.9,
            "evidence": f"{comp_types.get('repository', 0)} repositories for data access"
        })
    
    # API-based (RESTful)
    if project_type == "api-backend" and has_controllers:
        patterns.append({
            "name": "RESTful API",
            "confidence": 0.95,
            "evidence": f"Backend API with {comp_types.get('controller', 0)} endpoints"
        })
    
    # Microservices
    if len(containers) > 3:
        patterns.append({
            "name": "Microservices (potential)",
            "confidence": 0.6,
            "evidence": f"{len(containers)} containers detected"
        })
    
    return patterns


def _extract_system_responsibilities(project_type, components, layers):
    """
    Extrae las responsabilidades principales del sistema para el diagrama C1
    """
    responsibilities = []
    
    # Por tipo de proyecto
    if project_type == "api-backend":
        responsibilities.append("Expone API REST para operaciones CRUD")
        responsibilities.append("Gestiona lógica de negocio")
        if layers["infrastructure"]["count"] > 0:
            responsibilities.append("Persiste datos en base de datos")
    
    elif project_type == "gui-application":
        responsibilities.append("Proporciona interfaz gráfica de usuario")
        responsibilities.append("Procesa entrada del usuario")
        if layers["infrastructure"]["count"] > 0:
            responsibilities.append("Gestiona almacenamiento local/remoto")
    
    elif project_type == "ml-app":
        responsibilities.append("Entrena y ejecuta modelos de ML")
        responsibilities.append("Procesa y transforma datos")
        responsibilities.append("Genera predicciones/clasificaciones")
    
    elif project_type == "compiler":
        responsibilities.append("Parsea y analiza código fuente")
        responsibilities.append("Optimiza y transforma representaciones")
        responsibilities.append("Genera código objetivo")
    
    elif project_type == "library":
        responsibilities.append("Proporciona funcionalidades reutilizables")
        responsibilities.append("Expone APIs públicas")
    
    # Por componentes detectados
    if layers["presentation"]["count"] > 0:
        responsibilities.append(f"Gestiona {layers['presentation']['count']} endpoints/vistas")
    
    if layers["domain"]["count"] > 0:
        responsibilities.append(f"Modela {layers['domain']['count']} entidades de negocio")
    
    return responsibilities[:5]  # Top 5 responsibilities


def detect_actors(analysis_result: dict):
    """
    Detecta actores y sistemas externos de forma segura:
    - Librerías / compiladores → sin actores humanos.
    - Si hay GUI → Usuario.
    - Si hay HTTP client/server → APIs externas.
    """
    project_name = analysis_result.get("project_name", "Sistema Analizado")
    project_type = analysis_result.get("project_type", "unknown")

    # Librerías, compiladores, SDKs: no se modelan como sistema con Usuario directo
    if project_type in ["library", "compiler", "framework", "sdk"]:
        return {
            "main_system": project_name,
            "actors": [],
            "external_systems": []
        }

    actors = []
    external_systems = []

    imports = []
    filenames = [c["name"].lower() for c in analysis_result.get("components_detected", [])]

    # recolectar imports desde los componentes (tipo, clases, etc.)
    for c in analysis_result.get("components_detected", []):
        text = json.dumps(c).lower()
        # extrae tokens tipo palabra/punto
        imports.extend(re.findall(r"[a-zA-Z_\.]+", text))

    # GUI → Usuario humano
    gui_keywords = ["window", "form", "view", "widget", "screen", "interface", "gui", "pyqt", "pyside", "tkinter"]
    gui_imports = ["pyqt5", "pyqt6", "pyside2", "pyside6", "tkinter", "wx"]
    has_gui = any(any(k in f for k in gui_keywords) for f in filenames) or any(lib in imports for lib in gui_imports)
    
    if has_gui:
        actors.append({
            "name": "Usuario",
            "type": "Person",
            "interaction": "Interactúa con la interfaz gráfica del sistema."
        })

    # HTTP / APIs externas
    if any(lib in imports for lib in ["requests", "httpx", "fastapi", "flask", "axios"]):
        external_systems.append({
            "name": "API Externa",
            "type": "External System",
            "interaction": "Intercambia datos vía HTTP/REST."
        })

    # DB típica
    db_keywords = ["sqlalchemy", "psycopg2", "sqlite", "mariadb", "postgres", "pymongo", "redis"]
    if any(k in imports for k in db_keywords):
        external_systems.append({
            "name": "Base de Datos",
            "type": "Database",
            "interaction": "Persistencia de datos de la aplicación."
        })

    return {
        "main_system": project_name,
        "actors": actors,
        "external_systems": external_systems
    }


# ================================================================
#  BUSINESS MODULES DETECTION (NUEVO)
# ================================================================

def detect_business_modules(project_path: str) -> list:
    """
    Detecta módulos de negocio por estructura de carpetas y nombres de archivos.
    Esto permite generar C2 con containers por módulo funcional.
    
    Retorna: Lista de módulos con nombre, path, archivos y tipo
    """
    
    # Patrones de nombres de módulos comunes
    module_keywords = {
        "user": "User Management",
        "users": "User Management",
        "customer": "Customer Management",
        "client": "Client Management",
        "account": "Account Management",
        
        "product": "Product Catalog",
        "products": "Product Catalog",
        "item": "Item Management",
        "catalog": "Catalog Service",
        "inventory": "Inventory Management",
        "stock": "Stock Management",
        
        "order": "Order Processing",
        "orders": "Order Processing",
        "purchase": "Purchase Service",
        "cart": "Shopping Cart",
        "checkout": "Checkout Service",
        
        "payment": "Payment Service",
        "billing": "Billing Service",
        "invoice": "Invoice Management",
        "transaction": "Transaction Service",
        
        "auth": "Authentication",
        "authentication": "Authentication",
        "security": "Security Service",
        "login": "Login Service",
        "oauth": "OAuth Service",
        
        "notification": "Notification Service",
        "email": "Email Service",
        "sms": "SMS Service",
        "messaging": "Messaging Service",
        "mail": "Mail Service",
        
        "admin": "Admin Dashboard",
        "dashboard": "Dashboard Service",
        "management": "Management Console",
        
        "report": "Reporting Service",
        "analytics": "Analytics Service",
        "statistics": "Statistics Service",
        "metrics": "Metrics Service",
        
        "shipping": "Shipping Service",
        "delivery": "Delivery Service",
        "logistics": "Logistics Service",
        
        "review": "Review System",
        "rating": "Rating Service",
        "comment": "Comment Service",
        "feedback": "Feedback Service",
        
        "search": "Search Engine",
        "filter": "Filter Service",
        "query": "Query Service",
        
        "api": "API Gateway",
        "gateway": "API Gateway",
        "proxy": "Proxy Service",
        
        "file": "File Management",
        "upload": "Upload Service",
        "storage": "Storage Service",
        "media": "Media Service",
        
        "job": "Job Processor",
        "worker": "Worker Service",
        "queue": "Queue Service",
        "task": "Task Service",
        
        "config": "Configuration Service",
        "settings": "Settings Service",
    }
    
    modules = []
    seen_paths = set()
    
    # NUEVO: Detectar módulos por estructura de paquetes (Java, C#, etc.)
    # Buscar carpetas que están en rutas típicas de módulos
    module_indicators = [
        "/src/main/java/",  # Java
        "/src/",
        "/lib/",
        "/app/",
        "/modules/",
        "/services/",
        "/components/",
        "/packages/",
        "/gui/",  # Python GUI
        "/widgets/",
        "/core/",
        "/data/",
        "/utils/",
        "/include/",  # C++
        "/python/",
        "/backend/",
        "/frontend/",
    ]
    
    # Buscar por estructura de carpetas
    for root, dirs, files in os.walk(project_path):
        # Ignorar SOLO carpetas específicas de tests, no las que contienen "test" en el path
        folder_name = os.path.basename(root).lower()
        if folder_name in ["node_modules", "venv", ".venv", ".git", "__pycache__", "tests", "dist", "build", "target", ".pytest_cache"]:
            continue
            
        folder_name = os.path.basename(root).lower()
        
        # NUEVO: Detectar módulos en estructura de paquetes Java/C#/Python/C++
        # Si la carpeta está en una ruta típica de módulos y tiene archivos de código
        is_in_module_path = any(indicator in root.replace("\\", "/") for indicator in module_indicators)
        
        # MEJORADO: Detectar módulos Python directos (carpetas con __init__.py)
        has_init_py = "__init__.py" in files
        
        # MEJORADO: Detectar módulos C++ (carpetas con headers)
        has_cpp_headers = any(f.endswith(('.h', '.hpp', '.hxx')) for f in files)
        
        if (is_in_module_path or has_init_py or has_cpp_headers) and len(files) >= 2:
            code_extensions = ('.java', '.py', '.cs', '.ts', '.js', '.go', '.rb', '.php', '.rs', '.kt', '.swift', '.cpp', '.cc', '.c', '.h', '.hpp')
            code_files = [f for f in files if f.endswith(code_extensions)]
            
            if len(code_files) >= 2 and root not in seen_paths:
                # Crear nombre descriptivo del módulo
                module_display_name = folder_name.replace("_", " ").replace("-", " ").title()
                
                # Agregar sufijo descriptivo (solo si no está ya en el nombre)
                if "controller" in folder_name or "api" in folder_name:
                    if not module_display_name.endswith("API"):
                        module_display_name += " API"
                elif "service" in folder_name or "business" in folder_name:
                    if not module_display_name.endswith("Service"):
                        module_display_name += " Service"
                elif "model" in folder_name or "entity" in folder_name:
                    if not module_display_name.endswith("Domain"):
                        module_display_name += " Domain"
                elif "repository" in folder_name or "dao" in folder_name:
                    if not module_display_name.endswith("Data Access"):
                        module_display_name += " Data Access"
                elif "gui" in folder_name or "widget" in folder_name:
                    if not module_display_name.endswith("GUI"):
                        module_display_name += " GUI"
                elif "core" in folder_name:
                    # Si el nombre ya es "Core", no agregar nada más
                    if module_display_name == "Core":
                        pass  # Mantener "Core"
                    else:
                        module_display_name += " Core"
                elif "util" in folder_name or "helper" in folder_name:
                    # Si el nombre ya es "Utils" o "Util", no agregar nada más
                    if module_display_name in ["Utils", "Util"]:
                        module_display_name = "Utils"
                    else:
                        module_display_name += " Utils"
                elif "backend" in folder_name:
                    if not module_display_name.endswith("Backend"):
                        module_display_name += " Backend"
                elif "frontend" in folder_name:
                    if not module_display_name.endswith("Frontend"):
                        module_display_name += " Frontend"
                else:
                    module_display_name += " Module"
                
                modules.append({
                    "name": module_display_name,
                    "path": root,
                    "files": len(code_files),
                    "keyword": folder_name,
                    "file_list": code_files[:10]
                })
                seen_paths.add(root)
        
        # Verificar si el nombre de la carpeta coincide con algún módulo conocido
        for keyword, module_name in module_keywords.items():
            if keyword == folder_name or keyword in folder_name:
                # Contar archivos de código en este módulo
                code_extensions = ('.java', '.py', '.cs', '.ts', '.js', '.go', '.rb', '.php', '.rs', '.kt', '.swift')
                code_files = [f for f in files if f.endswith(code_extensions)]
                
                if len(code_files) >= 2 and root not in seen_paths:  # Al menos 2 archivos para ser módulo
                    modules.append({
                        "name": module_name,
                        "path": root,
                        "files": len(code_files),
                        "keyword": keyword,
                        "file_list": code_files[:10]  # Primeros 10 archivos
                    })
                    seen_paths.add(root)
                    break
    
    # También buscar por nombres de archivos (ej: UserController.java)
    for root, dirs, files in os.walk(project_path):
        if any(ignore in root.lower() for ignore in ["node_modules", "venv", ".git", "__pycache__", "test", "tests"]):
            continue
            
        for file in files:
            file_lower = file.lower()
            for keyword, module_name in module_keywords.items():
                if keyword in file_lower and file.endswith(('.java', '.py', '.cs', '.ts', '.js', '.go', '.rb', '.php', '.rs', '.kt', '.swift')):
                    # Si encontramos UserController, agregar módulo "User Management" si no existe
                    if not any(m["keyword"] == keyword for m in modules):
                        modules.append({
                            "name": module_name,
                            "path": root,
                            "files": 1,
                            "keyword": keyword,
                            "file_list": [file]
                        })
                        break
    
    # Ordenar por cantidad de archivos (más importantes primero)
    modules.sort(key=lambda x: x["files"], reverse=True)
    
    # Deduplicar por keyword
    unique_modules = []
    seen_keywords = set()
    
    for module in modules:
        if module["keyword"] not in seen_keywords:
            unique_modules.append(module)
            seen_keywords.add(module["keyword"])
    
    return unique_modules


# ================================================================
#  MAIN STATIC ANALYZER
# ================================================================

def analyze_project(zip_path: str):
    """
    Análisis principal del proyecto MEJORADO:
    - Descomprime el zip
    - Detecta contenedores (C2) + infra
    - Detecta componentes + relaciones (C3)
    - Detecta nombre y tipo de proyecto
    - NUEVO: Estructura componentes por capas arquitectónicas
    - NUEVO: Detecta patrones de diseño
    - NUEVO: Extrae responsabilidades y tecnologías clave
    """
    extract_dir = zip_path.replace(".zip", "")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Verificar si el ZIP tiene una sola carpeta raíz (caso común en GitHub)
    items = os.listdir(extract_dir)
    if len(items) == 1 and os.path.isdir(os.path.join(extract_dir, items[0])):
        extract_dir = os.path.join(extract_dir, items[0])

    # Análisis base
    containers, infra = detect_containers_and_infra(extract_dir)
    component_data = detect_components(extract_dir)
    project_name = detect_project_name(extract_dir)

    total_files = sum(len(f) for _, _, f in os.walk(extract_dir))

    # Estructura básica
    result = {
        "project_path": extract_dir,
        "project_name": project_name,
        "total_files": total_files,
        "containers_detected": [{k: v for k, v in c.items() if k != "_key"} for c in containers],
        "components_detected": component_data["components"],
        "relations_detected": component_data["relations"],
        "dockerfiles_found": len([c for c in containers if c["source"] == "Dockerfile"]),
        "infra_detected": infra,
    }

    # Tipo de proyecto
    result["project_type"] = detect_project_type(result)

    # MEJORAS PARA DIAGRAMAS C4:
    
    # 1. Agrupar componentes por capa arquitectónica
    result["architectural_layers"] = _extract_architectural_layers(component_data["components"])
    
    # 2. Extraer tecnologías clave por contenedor
    result["technologies"] = _extract_technologies(containers, component_data["components"], extract_dir)
    
    # 3. Identificar flujos de datos principales
    result["data_flows"] = _extract_data_flows(component_data["components"], component_data["relations"])
    
    # 4. Detectar patrones arquitectónicos
    result["architecture_patterns"] = _detect_architecture_patterns(
        result["project_type"],
        component_data["components"],
        containers
    )
    
    # 5. Extraer responsabilidades principales del sistema
    result["system_responsibilities"] = _extract_system_responsibilities(
        result["project_type"],
        component_data["components"],
        result["architectural_layers"]
    )
    
    # 6. NUEVO: Detectar módulos de negocio para C2 detallado
    result["business_modules"] = detect_business_modules(extract_dir)

    return result


# ================================================================
#  C2 + INFRA DETECTION
# ================================================================

def detect_containers_and_infra(root_path: str):
    containers = []
    infra = []

    # --- 1) Infraestructura general ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        lower_dirs = [d.lower() for d in dirs]

        # Dockerfile -> contenedor
        for f in files:
            if f.lower() == "dockerfile":
                _add_container(
                    containers,
                    "service",
                    "container (Docker)",
                    os.path.join(root, f),
                    "Dockerfile",
                    [f"Found {f}"],
                    0.95
                )

        # Infra y CI/CD
        if "docker-compose.yml" in lower_files or "docker-compose.yaml" in lower_files:
            infra.append({"type": "orchestration", "tool": "docker-compose", "path": root})
        if any(fn in lower_files for fn in ["deployment.yaml", "deployment.yml", "k8s.yaml", "k8s.yml"]):
            infra.append({"type": "orchestration", "tool": "kubernetes", "path": root})
        if "terraform" in lower_dirs or any(n.endswith(".tf") for n in lower_files):
            infra.append({"type": "infra", "tool": "terraform", "path": root})
        if ".github" in lower_dirs or "azure-pipelines.yml" in lower_files or "gitlab-ci.yml" in lower_files:
            infra.append({"type": "ci", "tool": "pipelines", "path": root})
        if "procfile" in lower_files or "runtime.txt" in lower_files:
            infra.append({"type": "deploy", "tool": "platform (Heroku/Render)", "path": root})

    # --- 2) Detección contextual por carpetas ---
    common_contexts = {
        "api": ("backend", "Generic API"),
        "backend": ("backend", "Generic Backend"),
        "server": ("backend", "Server Logic"),
        "frontend": ("frontend", "Web UI"),
        "ui": ("frontend", "UI Layer"),
        "webapp": ("frontend", "Web Application"),
        "data": ("database", "Data Layer"),
        "database": ("database", "SQL/DB"),
        "infra": ("infra", "Deployment Scripts"),
        "deploy": ("infra", "Deployment Scripts"),
    }
    for root, dirs, files in os.walk(root_path):
        dir_name = os.path.basename(root).lower()
        if dir_name in common_contexts:
            t, tech = common_contexts[dir_name]
            _add_container(
                containers,
                t,
                tech,
                root,
                "folder",
                [f"Context folder: {dir_name}"],
                0.6
            )

    # --- 3) Python backend (FastAPI, Flask, etc.) ---
    py_api_keywords = ("from fastapi import", "from flask import", "@app.get(", "app = fastapi(")
    for root, dirs, files in os.walk(root_path):
        evid, score = [], 0.0
        lower_files = [f.lower() for f in files]

        if any(x in lower_files for x in ["requirements.txt", "pyproject.toml", "main.py", "app.py", "manage.py"]):
            evid.append("Python project entry")
            score += 0.4

        for f in files:
            if f.endswith(".py"):
                content = _read_text(os.path.join(root, f)).lower()
                if any(k in content for k in py_api_keywords):
                    evid.append(f"API keyword in {f}")
                    score += 0.4
                    break

        if score > 0:
            _add_container(
                containers,
                "backend",
                "Python",
                root,
                "structure/content",
                evid,
                min(score, 0.9)
            )

    # --- 4) Python GUI frontend (PyQt5/Tkinter/Kivy/Streamlit) ---
    for root, dirs, files in os.walk(root_path):
        gui_tech = None
        gui_files = []
        for f in files:
            if f.endswith(".py") or f.endswith(".ui"):
                full_path = os.path.join(root, f)
                if f.endswith(".ui"):
                    gui_tech = "PyQt5"
                    gui_files.append(f)
                    continue
                    
                content = _read_text(full_path).lower()
                if "pyqt5" in content or "qtwidgets" in content or "qapplication" in content:
                    gui_tech = "PyQt5"
                    gui_files.append(f)
                elif "pyqt6" in content:
                    gui_tech = "PyQt6"
                    gui_files.append(f)
                elif "pyside" in content:
                    gui_tech = "PySide"
                    gui_files.append(f)
                elif "tkinter" in content:
                    gui_tech = "Tkinter"
                    gui_files.append(f)
                elif "kivy" in content:
                    gui_tech = "Kivy"
                    gui_files.append(f)
                elif "streamlit" in content:
                    gui_tech = "Streamlit"
                    gui_files.append(f)
        
        if gui_tech and len(gui_files) >= 2:
            _add_container(
                containers,
                "frontend",
                f"Python GUI ({gui_tech})",
                root,
                "content",
                [f"{gui_tech} detected in {len(gui_files)} files: {', '.join(gui_files[:3])}"],
                0.95
            )
            break

    # --- 5) Node.js backend ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        if "package.json" in lower_files:
            pkg = _parse_package_json(os.path.join(root, "package.json"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            scripts = pkg.get("scripts", {})

            evid, score = [], 0.0
            if any(k in deps for k in ["express", "@nestjs/core", "koa", "hapi"]):
                evid.append("Node backend deps")
                score += 0.5
            if any(k in scripts for k in ["start", "serve", "dev"]):
                evid.append("start/serve scripts")
                score += 0.2
            if any(os.path.exists(os.path.join(root, f)) for f in ["server.js", "app.js", "server.ts"]):
                evid.append("entry JS/TS file")
                score += 0.3

            if score > 0:
                _add_container(
                    containers,
                    "backend",
                    "Node.js",
                    root,
                    "package.json",
                    evid,
                    min(score, 0.95)
                )

    # --- 6) Node.js frontend (React, Vue, Angular, Vite, Electron) ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        if "package.json" in lower_files:
            pkg = _parse_package_json(os.path.join(root, "package.json"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            scripts = pkg.get("scripts", {})

            evid, score = [], 0.0
            web_hit = any(k in deps for k in ["react", "vue", "@angular/core", "vite", "webpack", "next", "nuxt"])
            if web_hit:
                evid.append("Web frontend deps")
                score += 0.6
            if "index.html" in lower_files:
                evid.append("index.html")
                score += 0.2
            if any(k in scripts for k in ["build", "dev", "preview"]):
                evid.append("build/dev scripts")
                score += 0.2

            if score > 0:
                _add_container(
                    containers,
                    "frontend",
                    "Web (React/Vue/Angular/Vite)",
                    root,
                    "package.json",
                    evid,
                    min(score, 0.95)
                )
            if "electron" in deps:
                _add_container(
                    containers,
                    "frontend",
                    "Electron (Desktop)",
                    root,
                    "package.json",
                    ["electron dep"],
                    0.9
                )

    # --- 7) Base de datos y almacenamiento ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        lower_dirs = [d.lower() for d in dirs]

        if any(f.endswith(".sql") for f in files) or "migrations" in lower_dirs:
            _add_container(
                containers,
                "database",
                "SQL",
                root,
                "structure",
                ["schema/migrations"],
                0.8
            )
        if "database.py" in lower_files or "db.js" in lower_files:
            _add_container(
                containers,
                "database",
                "ORM/DB Layer",
                root,
                "content",
                ["database file"],
                0.7
            )

    # --- 8) Machine Learning / Analytics ---
    for root, dirs, files in os.walk(root_path):
        evid, score = [], 0.0
        for f in files:
            if f.endswith(".ipynb"):
                evid.append("notebook")
                score += 0.2
            if f.endswith(".py"):
                content = _read_text(os.path.join(root, f)).lower()
                if any(k in content for k in ["import torch", "import tensorflow", "from sklearn"]):
                    evid.append(f"ML import in {f}")
                    score += 0.4
                if any(k in content for k in ["model.load(", "torch.load(", "joblib.load("]):
                    evid.append(f"model load in {f}")
                    score += 0.2
        if score >= 0.4:
            _add_container(
                containers,
                "service",
                "ML/Analytics",
                root,
                "content",
                evid,
                min(0.9, score)
            )

    # --- 9) Java / Spring Boot backend ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        if "pom.xml" in lower_files or "build.gradle" in lower_files:
            evid, score = [], 0.0
            
            # Check for Spring Boot
            for f in files:
                if f.endswith(".java"):
                    content = _read_text(os.path.join(root, f)).lower()
                    if "@springbootapplication" in content:
                        evid.append("Spring Boot app")
                        score += 0.6
                    if "@restcontroller" in content or "@controller" in content:
                        evid.append("Spring MVC controllers")
                        score += 0.3
                    if score >= 0.6:
                        break
            
            if score >= 0.6:
                _add_container(
                    containers,
                    "backend",
                    "Java (Spring Boot)",
                    root,
                    "content",
                    evid,
                    min(score, 0.95)
                )
                break

    # --- 10) C# / .NET backend ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        if any(f.endswith(".csproj") for f in files):
            evid, score = [], 0.0
            
            # ASP.NET Core detection
            if "program.cs" in lower_files or "startup.cs" in lower_files:
                evid.append("ASP.NET Core structure")
                score += 0.5
            
            if "appsettings.json" in lower_files:
                evid.append("appsettings.json")
                score += 0.2
            
            for f in files:
                if f.endswith(".cs"):
                    content = _read_text(os.path.join(root, f)).lower()
                    if "[apicontroller]" in content or "[route(" in content:
                        evid.append("ASP.NET Web API")
                        score += 0.4
                        break
            
            if score >= 0.5:
                _add_container(
                    containers,
                    "backend",
                    "C# (ASP.NET Core)",
                    root,
                    "content",
                    evid,
                    min(score, 0.95)
                )
                break

    # --- 11) Go backend ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        if "go.mod" in lower_files:
            evid, score = [], 0.0
            evid.append("Go module")
            score += 0.4
            
            if "main.go" in lower_files:
                evid.append("main.go entry point")
                score += 0.4
            
            for f in files:
                if f.endswith(".go"):
                    content = _read_text(os.path.join(root, f)).lower()
                    if "http.listenandserve" in content or "gin.default()" in content or "echo.new()" in content:
                        evid.append("HTTP server")
                        score += 0.3
                        break
            
            if score >= 0.5:
                _add_container(
                    containers,
                    "backend",
                    "Go",
                    root,
                    "content",
                    evid,
                    min(score, 0.9)
                )
                break

    # --- 12) Rust backend ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        if "cargo.toml" in lower_files:
            evid, score = [], 0.0
            evid.append("Rust project")
            score += 0.4
            
            # Check Cargo.toml for web frameworks
            cargo_content = _read_text(os.path.join(root, "Cargo.toml")).lower()
            if any(fw in cargo_content for fw in ["actix-web", "rocket", "warp", "axum"]):
                evid.append("Web framework")
                score += 0.5
            
            if score >= 0.5:
                _add_container(
                    containers,
                    "backend",
                    "Rust",
                    root,
                    "content",
                    evid,
                    min(score, 0.9)
                )
                break

    # --- 13) PHP / Laravel backend ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        if "composer.json" in lower_files:
            evid, score = [], 0.0
            
            composer_content = _read_text(os.path.join(root, "composer.json")).lower()
            if "laravel/framework" in composer_content:
                evid.append("Laravel framework")
                score += 0.6
            elif "symfony" in composer_content:
                evid.append("Symfony framework")
                score += 0.6
            else:
                evid.append("PHP project")
                score += 0.3
            
            if "artisan" in lower_files or "index.php" in lower_files:
                evid.append("PHP entry point")
                score += 0.3
            
            if score >= 0.5:
                _add_container(
                    containers,
                    "backend",
                    "PHP (Laravel/Symfony)",
                    root,
                    "content",
                    evid,
                    min(score, 0.9)
                )
                break

    # --- 14) Ruby on Rails backend ---
    for root, dirs, files in os.walk(root_path):
        lower_files = [f.lower() for f in files]
        if "gemfile" in lower_files:
            evid, score = [], 0.0
            
            gemfile_content = _read_text(os.path.join(root, "Gemfile")).lower()
            if "rails" in gemfile_content:
                evid.append("Rails framework")
                score += 0.7
            else:
                evid.append("Ruby project")
                score += 0.3
            
            if "config.ru" in lower_files or "rakefile" in lower_files:
                evid.append("Rack/Rails structure")
                score += 0.2
            
            if score >= 0.5:
                _add_container(
                    containers,
                    "backend",
                    "Ruby (Rails)",
                    root,
                    "content",
                    evid,
                    min(score, 0.9)
                )
                break

    # --- 9) Fusión por path (hybrid) y limpieza final ---
    # 9.1 agrupar por path
    by_path = {}
    for c in containers:
        path_key = os.path.abspath(c["path"])
        by_path.setdefault(path_key, []).append(c)

    merged_containers = []
    for path_key, items in by_path.items():
        if len(items) == 1:
            c = items[0]
            merged_containers.append(c)
        else:
            # varios roles en el mismo path → hybrid
            techs = sorted(set(i["technology"] for i in items))
            evids = []
            score_sum = 0.0
            for i in items:
                evids.extend(i["evidences"])
                score_sum += i["score"]
            merged_containers.append({
                "_key": ("hybrid", path_key, " + ".join(techs)),
                "type": "hybrid",
                "technology": " + ".join(techs),
                "path": path_key,
                "source": "merged",
                "evidences": list(sorted(set(evids)))[:8],
                "score": round(min(1.0, score_sum / len(items)), 2)
            })

    # --- 10) Etiquetar nivel de confianza ---
    for c in merged_containers:
        if c["score"] >= 0.75:
            c["confidence"] = "high"
        elif c["score"] >= 0.5:
            c["confidence"] = "medium"
        else:
            c["confidence"] = "low"

    return merged_containers, infra


# ================================================================
#  C3: COMPONENT DETECTION
# ================================================================

def detect_components(root_path: str):
    components = []
    relations = []

    exclude_dirs = [
        "tests", "venv", "__pycache__", "node_modules",
        "build", "dist", ".git", ".venv", "target", "bin", "obj",
        "vendor", "public", "assets", "static", "coverage"
    ]
    # No excluir "test" ni "migrations" porque pueden ser parte del proyecto
    valid_ext = [".py", ".java", ".js", ".ts", ".cs", ".go", ".rs", ".php", ".rb", ".kt", ".swift"]

    name_patterns = {
        "controller": re.compile(r".*(controller|resource|route|manager|handler|algorithm|genetic|simulation|simulator|endpoint|api).*", re.IGNORECASE),
        "service":    re.compile(r".*(service|logic|engine|process|reporting|validation|export|usecase|interactor|facade).*", re.IGNORECASE),
        "repository": re.compile(r".*(repo|repository|dao|database|store|persistence).*", re.IGNORECASE),
        "model":      re.compile(r".*(model|entity|schema|dto|domain|aggregate).*", re.IGNORECASE),
        "view":       re.compile(r".*(view|widget|window|dialog|page|component|main_window|form|activity|fragment).*", re.IGNORECASE),
    }

    external_libs = set([
        # stdlib (parcial)
        "os", "sys", "time", "math", "json", "logging", "random", "re",
        "pathlib", "typing", "datetime", "itertools", "functools",
        "subprocess", "threading", "asyncio", "collections",
        # data/ML
        "numpy", "pandas", "scipy", "sklearn", "torch", "tensorflow",
        "joblib", "psutil", "matplotlib", "seaborn",
        # web/gui
        "flask", "fastapi", "django", "starlette", "uvicorn", "gunicorn",
        "jinja2", "pyqt5", "tkinter", "kivy", "pyqtgraph",
        # db
        "sqlalchemy", "psycopg2", "pymysql", "pymongo", "redis",
        # node/javascript
        "react", "vue", "angular", "express", "koa", "nestjs", "rxjs",
        "axios", "next", "nuxt"
    ])

    for dirpath, dirs, files in os.walk(root_path):
        # Excluir solo directorios específicos (no subcadenas)
        dir_name = os.path.basename(dirpath).lower()
        if dir_name in exclude_dirs:
            continue

        for file in files:
            if not _is_text_file(file, valid_ext):
                continue

            file_path = os.path.join(dirpath, file)
            file_lower = file.lower()
            comp_type = None

            # 1) tipo por nombre de archivo
            for t, pat in name_patterns.items():
                if pat.match(file_lower):
                    comp_type = t
                    break

            content = _read_text(file_path)

            # 2) GUI fuerte → view (Python, C#, Java)
            content_lower = content.lower()
            if any(k in content_lower for k in ["pyqt5", "pyqt6", "pyside", "tkinter", "kivy", "qtwidgets", "qapplication", "qwidget", "system.windows.forms", "wpf", "javafx", "swing"]):
                comp_type = "view"

            # 3) tipo por contenido - MULTI-LENGUAJE
            if not comp_type:
                # Controllers (Python, Java, C#, Go, Rust, PHP, Ruby, Node.js)
                if re.search(
                    r"@Controller|@RestController|@RequestMapping|@GetMapping|@PostMapping|"
                    r"\[ApiController\]|\[Route\(|\[HttpGet\]|\[HttpPost\]|"
                    r"app\.route|router\.(get|post|put|delete)|def (get_|post_)|"
                    r"http\.HandleFunc|gin\.|echo\.|"
                    r"#\[get\(|#\[post\(|web::get|web::post|"
                    r"Route::get|Route::post|"
                    r"class.*Controller|function.*controller",
                    content, re.IGNORECASE
                ):
                    comp_type = "controller"
                
                # Services (Java, C#, Python, Go, Node.js)
                elif re.search(
                    r"@Service|@Component|@Injectable|"
                    r"\[Service\]|class .*Service|"
                    r"def (run|process|execute)\(|"
                    r"func.*Service|type.*Service|"
                    r"class.*Interactor|class.*UseCase",
                    content, re.IGNORECASE
                ):
                    comp_type = "service"
                
                # Repositories (Java, C#, Python, Node.js)
                elif re.search(
                    r"@Repository|@Dao|interface.*Repository|"
                    r"\[Repository\]|class .*Repository|"
                    r"connect\(|execute\(|sessionmaker\(|"
                    r"@Entity|@Table|dbContext|"
                    r"class.*Dao|class.*Store",
                    content, re.IGNORECASE
                ):
                    comp_type = "repository"
                
                # Models/Entities (Java, C#, Python, PHP, Ruby)
                elif re.search(
                    r"@Entity|@Table|@Document|@Model|"
                    r"\[Table\(|\[Column\(|class.*Entity|"
                    r"class .*Model|BaseModel|declarative_base\(|"
                    r"belongs_to|has_many|has_one|"
                    r"struct.*\{.*json:",
                    content, re.IGNORECASE
                ):
                    comp_type = "model"
            
            # 4) Si todavía no tiene tipo, detectar por keywords de lenguaje
            if not comp_type:
                # Java
                if file.endswith(".java"):
                    if re.search(r"public class|private class|interface", content):
                        comp_type = "service"
                # C#
                elif file.endswith(".cs"):
                    if re.search(r"public class|private class|interface|namespace", content):
                        comp_type = "service"
                # Go
                elif file.endswith(".go"):
                    if re.search(r"func|type.*struct|interface", content):
                        comp_type = "service"
                # Rust
                elif file.endswith(".rs"):
                    if re.search(r"fn |struct |impl |trait ", content):
                        comp_type = "service"
                # PHP
                elif file.endswith(".php"):
                    if re.search(r"class |interface |trait ", content):
                        comp_type = "service"
                # Ruby
                elif file.endswith(".rb"):
                    if re.search(r"class |module |def ", content):
                        comp_type = "service"
                # Python
                elif file.endswith(".py"):
                    classes = re.findall(r"^\s*class\s+([A-Za-z_]\w*)", content, flags=re.MULTILINE)
                    if classes:
                        comp_type = "service"

            # 5) Extracción de clases y métodos principales - MULTI-LENGUAJE
            classes = []
            mains = []
            
            # Python
            if file.endswith(".py"):
                classes = re.findall(r"^\s*class\s+([A-Za-z_]\w*)", content, flags=re.MULTILINE)
                mains = re.findall(r"^\s*def\s+(main|run|start|create_app)\s*\(", content, flags=re.MULTILINE)
            
            # Java
            elif file.endswith(".java"):
                classes = re.findall(r"(?:public|private|protected)?\s*(?:class|interface|enum)\s+([A-Za-z_]\w*)", content)
                mains = re.findall(r"public\s+static\s+void\s+(main)\s*\(", content)
            
            # C#
            elif file.endswith(".cs"):
                classes = re.findall(r"(?:public|private|protected|internal)?\s*(?:class|interface|struct)\s+([A-Za-z_]\w*)", content)
                mains = re.findall(r"static\s+(?:async\s+)?(?:void|Task|int)\s+(Main)\s*\(", content)
            
            # Go
            elif file.endswith(".go"):
                classes = re.findall(r"type\s+([A-Za-z_]\w*)\s+struct", content)
                mains = re.findall(r"func\s+(main)\s*\(\s*\)", content)
            
            # Rust
            elif file.endswith(".rs"):
                classes = re.findall(r"(?:pub\s+)?struct\s+([A-Za-z_]\w*)", content)
                mains = re.findall(r"fn\s+(main)\s*\(\s*\)", content)
            
            # PHP
            elif file.endswith(".php"):
                classes = re.findall(r"class\s+([A-Za-z_]\w*)", content)
            
            # Ruby
            elif file.endswith(".rb"):
                classes = re.findall(r"class\s+([A-Za-z_]\w*)", content)
            
            # JavaScript/TypeScript
            elif file.endswith((".js", ".ts")):
                classes = re.findall(r"class\s+([A-Za-z_]\w*)", content)
                mains = re.findall(r"(?:function|const|let)\s+(main|start|run)\s*[=\(]", content)

            # 6) Detección de imports y dependencias - MULTI-LENGUAJE
            
            # Python
            if file.endswith(".py"):
                raw_imports = re.findall(r"(?:from|import)\s+([A-Za-z_][\w\.]*)", content)
                for imp in raw_imports:
                    base = imp.split(".")[0]
                    if base in external_libs:
                        continue
                    imp_norm = imp.lstrip(".")
                    relations.append({"from": file, "to": imp_norm})
            
            # Java
            elif file.endswith(".java"):
                for match in re.finditer(r"import\s+([\w\.]+);", content):
                    dep = match.group(1)
                    base_pkg = dep.split(".")[0]
                    if base_pkg not in ["java", "javax", "org.junit", "org.mockito"]:
                        relations.append({"from": file, "to": dep})
            
            # C#
            elif file.endswith(".cs"):
                for match in re.finditer(r"using\s+([\w\.]+);", content):
                    dep = match.group(1)
                    base_ns = dep.split(".")[0]
                    if base_ns not in ["System", "Microsoft", "Xunit", "Moq"]:
                        relations.append({"from": file, "to": dep})
            
            # Go
            elif file.endswith(".go"):
                for match in re.finditer(r"import\s+(?:\"([^\"]+)\"|[\(\s]+\"([^\"]+)\")", content):
                    dep_path = match.group(1) or match.group(2)
                    if dep_path and not dep_path.startswith(("fmt", "os", "io", "net/http", "testing")):
                        relations.append({"from": file, "to": dep_path})
            
            # Rust
            elif file.endswith(".rs"):
                for match in re.finditer(r"use\s+([\w:]+)", content):
                    dep = match.group(1)
                    base_crate = dep.split("::")[0]
                    if base_crate not in ["std", "core", "alloc"]:
                        relations.append({"from": file, "to": dep})
            
            # PHP
            elif file.endswith(".php"):
                for match in re.finditer(r"use\s+([\\A-Za-z0-9_]+);", content):
                    dep = match.group(1)
                    base_ns = dep.split("\\")[0]
                    if base_ns not in ["PHPUnit", "Symfony"]:
                        relations.append({"from": file, "to": dep})
            
            # Ruby
            elif file.endswith(".rb"):
                for match in re.finditer(r"require\s+['\"]([^'\"]+)['\"]", content):
                    dep = match.group(1)
                    if not dep.startswith(("test/", "spec/")):
                        relations.append({"from": file, "to": dep})
            
            # JavaScript/TypeScript
            elif file.endswith((".js", ".ts")):
                for match in re.finditer(r"import\s+(?:.*?\s+from\s+)?['\"]([^'\"]+)['\"]", content):
                    dep_path = match.group(1)
                    if not dep_path.startswith((".", "/")):
                        dep = dep_path.split("/")[0]
                        relations.append({"from": file, "to": dep})

            # 7) Detección de herencia y composición - MULTI-LENGUAJE
            
            # Python: class Foo(Bar)
            if file.endswith(".py"):
                for match in re.finditer(r"class\s+(\w+)\s*\(\s*([A-Za-z_][\w\.,\s]*)\s*\):", content):
                    child = match.group(1)
                    parents_str = match.group(2)
                    parents = [p.strip() for p in parents_str.split(",") if p.strip()]
                    for parent in parents:
                        if parent not in ["object", "ABC", "Exception", "BaseException"]:
                            relations.append({"from": child, "to": parent, "type": "inheritance"})
            
            # Java: class Foo extends Bar implements Baz
            elif file.endswith(".java"):
                for match in re.finditer(r"class\s+(\w+)\s+extends\s+(\w+)", content):
                    relations.append({"from": match.group(1), "to": match.group(2), "type": "inheritance"})
                for match in re.finditer(r"class\s+(\w+)\s+implements\s+([\w\s,]+)", content):
                    child = match.group(1)
                    interfaces = [i.strip() for i in match.group(2).split(",")]
                    for iface in interfaces:
                        relations.append({"from": child, "to": iface, "type": "implementation"})
            
            # C#: class Foo : Bar
            elif file.endswith(".cs"):
                for match in re.finditer(r"class\s+(\w+)\s*:\s*([\w\s,]+)", content):
                    child = match.group(1)
                    bases = [b.strip() for b in match.group(2).split(",")]
                    for base in bases:
                        relations.append({"from": child, "to": base, "type": "inheritance"})
            
            # Go: struct embedding
            elif file.endswith(".go"):
                # Go usa composición con embedded structs
                for match in re.finditer(r"type\s+(\w+)\s+struct\s*\{[^}]*(\w+)\s*\n", content):
                    relations.append({"from": match.group(1), "to": match.group(2), "type": "composition"})
            
            # Rust: struct/impl traits
            elif file.endswith(".rs"):
                for match in re.finditer(r"impl\s+(\w+)\s+for\s+(\w+)", content):
                    relations.append({"from": match.group(2), "to": match.group(1), "type": "trait_impl"})
            
            # PHP: class Foo extends Bar implements Baz
            elif file.endswith(".php"):
                for match in re.finditer(r"class\s+(\w+)\s+extends\s+(\w+)", content):
                    relations.append({"from": match.group(1), "to": match.group(2), "type": "inheritance"})
                for match in re.finditer(r"class\s+(\w+)\s+implements\s+([\w\s,]+)", content):
                    child = match.group(1)
                    interfaces = [i.strip() for i in match.group(2).split(",")]
                    for iface in interfaces:
                        relations.append({"from": child, "to": iface, "type": "implementation"})
            
            # Ruby: class Foo < Bar
            elif file.endswith(".rb"):
                for match in re.finditer(r"class\s+(\w+)\s*<\s*(\w+)", content):
                    relations.append({"from": match.group(1), "to": match.group(2), "type": "inheritance"})
            
            # JavaScript/TypeScript: class Foo extends Bar
            elif file.endswith((".js", ".ts")):
                for match in re.finditer(r"class\s+(\w+)\s+extends\s+(\w+)", content):
                    relations.append({"from": match.group(1), "to": match.group(2), "type": "inheritance"})

            if comp_type:
                components.append({
                    "type": comp_type,
                    "name": file,
                    "path": file_path,
                    "classes": classes[:6],
                    "entry_points": mains[:4]
                })

    # de-dups
    components = list({(c["name"], c["type"], c["path"]): c for c in components}.values())
    relations = [{"from": f, "to": t} for f, t in {(r["from"], r["to"]) for r in relations}]

    return {"components": components, "relations": relations}

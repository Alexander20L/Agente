"""
DETECCIÓN INTELIGENTE DE MÓDULOS
==================================

Analiza la estructura del proyecto para detectar módulos funcionales
SIN requerir patrones predefinidos.

Estrategias:
1. Cohesión de archivos: archivos en la misma carpeta que trabajan juntos
2. Análisis de imports: qué archivos dependen entre sí
3. Patrones de nombres: archivos con prefijos/sufijos comunes
4. Estructura de carpetas: organización funcional del proyecto
"""

import os
import re
from collections import defaultdict
from typing import List, Dict, Set, Tuple


def detect_modules_intelligent(root_path: str, components: list) -> dict:
    """
    Detecta módulos funcionales del proyecto analizando:
    - Estructura de carpetas
    - Cohesión de archivos
    - Patrones de nombres
    - Análisis de imports (opcional)
    
    Retorna:
        {
            "is_modular": bool,
            "architecture_type": str,
            "modules": list[dict],
            "module_structure": str
        }
    """
    
    # PASO 1: Detectar frameworks específicos (rápido, alta precisión)
    framework_result = _detect_framework_modules(root_path, components)
    if framework_result["is_modular"]:
        return framework_result
    
    # PASO 2: Análisis inteligente de estructura de carpetas
    folder_modules = _detect_folder_based_modules(root_path, components)
    
    if len(folder_modules) >= 3:
        return {
            "is_modular": True,
            "architecture_type": "folder-based-modules",
            "modules": folder_modules[:15],  # Limitar a 15 módulos
            "module_structure": f"{len(folder_modules)} módulos detectados por estructura de carpetas"
        }
    
    # PASO 3: Si no hay módulos claros, analizar por cohesión
    cohesion_modules = _detect_cohesion_modules(root_path, components)
    
    if len(cohesion_modules) >= 3:
        return {
            "is_modular": True,
            "architecture_type": "cohesion-based-modules",
            "modules": cohesion_modules[:15],
            "module_structure": f"{len(cohesion_modules)} módulos detectados por cohesión de código"
        }
    
    # FALLBACK: No es modular
    return {
        "is_modular": False,
        "architecture_type": None,
        "modules": [],
        "module_structure": "Arquitectura por capas (MVC/Layered)"
    }


def _detect_framework_modules(root_path: str, components: list) -> dict:
    """
    Detecta módulos en frameworks específicos conocidos.
    (Odoo, Django, NestJS, Laravel, Spring Boot, etc.)
    """
    
    # Validar formato de components
    if not isinstance(components, list):
        return {"is_modular": False}
    
    # Filtrar solo dicts válidos
    valid_components = [c for c in components if isinstance(c, dict)]
    if len(valid_components) == 0:
        return {"is_modular": False}
    
    # 1. ODOO/OPENERP
    addons_path = os.path.join(root_path, "addons")
    if os.path.exists(addons_path) and os.path.isdir(addons_path):
        modules = []
        for item in os.listdir(addons_path):
            module_path = os.path.join(addons_path, item)
            if os.path.isdir(module_path):
                has_manifest = os.path.exists(os.path.join(module_path, "__manifest__.py")) or \
                              os.path.exists(os.path.join(module_path, "__openerp__.py"))
                if has_manifest:
                    modules.append({
                        "name": item,
                        "path": module_path,
                        "type": "odoo-addon"
                    })
        
        if len(modules) >= 2:
            return {
                "is_modular": True,
                "architecture_type": "odoo-modules",
                "modules": modules,
                "module_structure": f"{len(modules)} módulos Odoo en addons/"
            }
    
    # 2. DJANGO
    apps_py_files = [c for c in valid_components if c.get("name", "").lower() == "apps.py"]
    if len(apps_py_files) >= 3:
        django_apps = []
        for app_file in apps_py_files:
            app_path = os.path.dirname(app_file["path"])
            app_name = os.path.basename(app_path)
            django_apps.append({
                "name": app_name,
                "path": app_path,
                "type": "django-app"
            })
        
        return {
            "is_modular": True,
            "architecture_type": "django-apps",
            "modules": django_apps,
            "module_structure": f"{len(django_apps)} Django apps"
        }
    
    # 3. NESTJS
    module_ts_files = [c for c in valid_components if c.get("name", "").lower().endswith(".module.ts")]
    if len(module_ts_files) >= 3:
        nest_modules = []
        for mod_file in module_ts_files:
            mod_name = mod_file["name"].replace(".module.ts", "")
            nest_modules.append({
                "name": mod_name,
                "path": os.path.dirname(mod_file["path"]),
                "type": "nestjs-module"
            })
        
        return {
            "is_modular": True,
            "architecture_type": "nestjs-modules",
            "modules": nest_modules,
            "module_structure": f"{len(nest_modules)} módulos NestJS"
        }
    
    # 4. LARAVEL (Modules package)
    laravel_modules = os.path.join(root_path, "Modules")
    if os.path.exists(laravel_modules) and os.path.isdir(laravel_modules):
        modules = []
        for item in os.listdir(laravel_modules):
            module_path = os.path.join(laravel_modules, item)
            if os.path.isdir(module_path):
                modules.append({
                    "name": item,
                    "path": module_path,
                    "type": "laravel-module"
                })
        
        if len(modules) >= 2:
            return {
                "is_modular": True,
                "architecture_type": "laravel-modules",
                "modules": modules,
                "module_structure": f"{len(modules)} módulos Laravel"
            }
    
    # 5. SPRING BOOT (packages by feature)
    # Buscar paquetes Java organizados por feature
    java_packages = _detect_java_feature_packages(root_path, valid_components)
    if len(java_packages) >= 3:
        return {
            "is_modular": True,
            "architecture_type": "spring-boot-modules",
            "modules": java_packages,
            "module_structure": f"{len(java_packages)} paquetes por feature"
        }
    
    return {"is_modular": False}


def _detect_folder_based_modules(root_path: str, components: list) -> List[Dict]:
    """
    Detecta módulos analizando la estructura de carpetas.
    
    Criterios:
    - Carpetas con ≥3 archivos de código
    - En ubicaciones típicas (src/, lib/, app/, modules/, services/)
    - Con cohesión interna (archivos relacionados)
    
    NUEVO: Si root_path no existe (tests), analiza components directamente.
    """
    modules = []
    seen_paths = set()
    
    # Ignorar estas carpetas
    IGNORE_FOLDERS = {
        "node_modules", "venv", ".venv", ".git", "__pycache__", 
        "dist", "build", "target", ".pytest_cache", "vendor",
        ".idea", ".vscode", "coverage", ".next", "out"
    }
    
    # Extensiones de código válidas
    CODE_EXTENSIONS = (
        '.py', '.java', '.js', '.ts', '.jsx', '.tsx', 
        '.cs', '.go', '.rb', '.php', '.rs', '.kt', 
        '.swift', '.cpp', '.cc', '.c', '.h', '.hpp'
    )
    
    # Carpetas raíz donde buscar módulos
    MODULE_ROOT_PATHS = [
        "src", "lib", "app", "modules", "services", 
        "packages", "components", "features", "domain",
        "backend", "frontend", "server", "api"
    ]
    
    # NUEVO: Si root_path no existe, analizar components directamente (para tests)
    if not os.path.exists(root_path):
        return _detect_folder_modules_from_components(components, CODE_EXTENSIONS)
    
    for root, dirs, files in os.walk(root_path):
        # Filtrar carpetas ignoradas
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
        
        folder_name = os.path.basename(root)
        if folder_name in IGNORE_FOLDERS:
            continue
        
        # Verificar si está en una ruta de módulos
        rel_path = os.path.relpath(root, root_path).replace("\\", "/")
        is_in_module_path = any(rel_path.startswith(module_root) for module_root in MODULE_ROOT_PATHS)
        
        # Si no está en ruta de módulos, debe tener indicadores explícitos
        if not is_in_module_path:
            has_init_py = "__init__.py" in files
            has_package_json = "package.json" in files
            has_module_config = any(f in files for f in ["module.config.js", "module.json", "__manifest__.py"])
            
            if not (has_init_py or has_package_json or has_module_config):
                continue
        
        # Contar archivos de código
        code_files = [f for f in files if f.endswith(CODE_EXTENSIONS)]
        
        # Criterio: ≥3 archivos de código
        if len(code_files) >= 3 and root not in seen_paths:
            # Verificar que no sea una carpeta genérica (utils, common, shared)
            if folder_name.lower() in ["utils", "helpers", "common", "shared", "lib", "core"]:
                # Solo incluir si tiene muchos archivos (≥5)
                if len(code_files) < 5:
                    continue
            
            # Calcular profundidad desde src/ o raíz del proyecto
            depth = len(rel_path.split("/"))
            
            # Preferir carpetas a profundidad media (no muy superficiales ni profundas)
            if depth < 1 or depth > 5:
                continue
            
            # Determinar el nombre del módulo
            module_name = _infer_module_name(folder_name, rel_path, code_files)
            
            # Determinar el tipo de módulo
            module_type = _infer_module_type(code_files, files, folder_name)
            
            modules.append({
                "name": module_name,
                "path": root,
                "type": module_type,
                "file_count": len(code_files),
                "depth": depth
            })
            seen_paths.add(root)
    
    # Ordenar por relevancia: más archivos + profundidad media = más importante
    modules.sort(key=lambda m: (m["file_count"], -abs(m["depth"] - 3)), reverse=True)
    
    return modules


def _detect_folder_modules_from_components(components: list, code_extensions: tuple) -> List[Dict]:
    """
    Detecta módulos agrupando components por carpeta (para tests).
    """
    # Agrupar components por directorio
    folder_groups = defaultdict(list)
    
    for comp in components:
        comp_path = comp.get("path", "")
        comp_name = comp.get("name", "")
        
        # Solo archivos de código
        if not comp_name.endswith(code_extensions):
            continue
        
        # Extraer directorio
        folder = os.path.dirname(comp_path)
        folder_groups[folder].append(comp)
    
    # Convertir en módulos
    modules = []
    for folder, group_components in folder_groups.items():
        if len(group_components) >= 3:
            folder_name = os.path.basename(folder)
            
            # Ignorar carpetas genéricas
            if folder_name.lower() in ["utils", "helpers", "common", "shared"]:
                continue
            
            modules.append({
                "name": folder_name.capitalize(),
                "path": folder,
                "type": "folder-module",
                "file_count": len(group_components),
                "depth": len(folder.split("/"))
            })
    
    modules.sort(key=lambda m: m["file_count"], reverse=True)
    return modules


def _detect_cohesion_modules(root_path: str, components: list) -> List[Dict]:
    """
    Detecta módulos por cohesión: archivos que comparten prefijos/sufijos.
    
    Ejemplo:
    - user_controller.py, user_service.py, user_repository.py → Módulo "User"
    - order_api.js, order_model.js, order_validator.js → Módulo "Order"
    """
    # Agrupar archivos por prefijo
    prefix_groups = defaultdict(list)
    
    CODE_EXTENSIONS = (
        '.py', '.java', '.js', '.ts', '.jsx', '.tsx', 
        '.cs', '.go', '.rb', '.php', '.rs', '.kt'
    )
    
    # Validar components
    valid_components = [c for c in components if isinstance(c, dict)]
    
    for component in valid_components:
        comp_name = component.get("name", "")
        comp_path = component.get("path", "")
        
        # Solo analizar archivos de código
        if not comp_name.endswith(CODE_EXTENSIONS):
            continue
        
        # Extraer prefijo antes de _ o . 
        # Ejemplos: user_controller.py → user, OrderService.java → order
        base_name = os.path.splitext(comp_name)[0]
        
        # Detectar patrón CamelCase (OrderService → Order)
        camel_match = re.match(r'^([A-Z][a-z]+)', base_name)
        if camel_match:
            prefix = camel_match.group(1).lower()
        else:
            # Detectar patrón snake_case (user_controller → user)
            snake_parts = base_name.split('_')
            if len(snake_parts) > 1:
                prefix = snake_parts[0].lower()
            else:
                # Detectar patrón kebab-case (order-service → order)
                kebab_parts = base_name.split('-')
                if len(kebab_parts) > 1:
                    prefix = kebab_parts[0].lower()
                else:
                    continue  # No hay prefijo claro
        
        # Ignorar prefijos genéricos
        if prefix in ["base", "abstract", "common", "util", "helper", "index", "main", "app"]:
            continue
        
        prefix_groups[prefix].append(component)
    
    # Convertir grupos en módulos (solo si tienen ≥2 archivos)
    modules = []
    for prefix, group_components in prefix_groups.items():
        if len(group_components) >= 2:
            # Tomar la carpeta común de los archivos
            paths = [c["path"] for c in group_components]
            common_dir = os.path.commonpath(paths) if len(paths) > 1 else os.path.dirname(paths[0])
            
            modules.append({
                "name": prefix.capitalize(),
                "path": common_dir,
                "type": "cohesion-module",
                "file_count": len(group_components)
            })
    
    # Ordenar por número de archivos
    modules.sort(key=lambda m: m["file_count"], reverse=True)
    
    return modules


def _detect_java_feature_packages(root_path: str, components: list) -> List[Dict]:
    """
    Detecta paquetes Java organizados por feature (no por capas).
    
    Estructura tradicional (por capas - NO MODULAR):
    - com.example.controllers.UserController
    - com.example.services.UserService
    
    Estructura por features (MODULAR):
    - com.example.user.UserController
    - com.example.user.UserService
    - com.example.order.OrderController
    """
    java_files = [c for c in components if c.get("name", "").endswith(".java")]
    
    if len(java_files) < 5:
        return []
    
    # Extraer paquetes de cada archivo
    package_to_files = defaultdict(list)
    
    for java_file in java_files:
        file_path = java_file.get("path", "")
        
        # Extraer el paquete del path
        # Ejemplo: .../src/main/java/com/example/user/UserController.java
        if "/src/main/java/" in file_path or "\\src\\main\\java\\" in file_path:
            parts = file_path.replace("\\", "/").split("/src/main/java/")
            if len(parts) == 2:
                package_path = os.path.dirname(parts[1])
                package_name = package_path.replace("/", ".").replace("\\", ".")
                
                # Solo considerar paquetes de nivel 3+ (com.example.feature)
                package_parts = package_name.split(".")
                if len(package_parts) >= 3:
                    # Tomar el paquete de feature (último nivel antes de Controller/Service/etc.)
                    feature_package = ".".join(package_parts[:4]) if len(package_parts) >= 4 else package_name
                    package_to_files[feature_package].append(java_file)
    
    # Convertir paquetes en módulos (≥2 archivos)
    modules = []
    for package_name, files in package_to_files.items():
        if len(files) >= 2:
            # Nombre del módulo = última parte del paquete
            module_name = package_name.split(".")[-1].capitalize()
            
            # Path común
            common_path = os.path.commonpath([f["path"] for f in files])
            
            modules.append({
                "name": module_name,
                "path": common_path,
                "type": "java-feature-package",
                "file_count": len(files)
            })
    
    return modules


def _infer_module_name(folder_name: str, rel_path: str, code_files: list) -> str:
    """Infiere un nombre descriptivo para el módulo"""
    # Limpiar nombre de carpeta
    clean_name = folder_name.replace("_", " ").replace("-", " ")
    
    # Si es un nombre genérico, usar el path
    if clean_name.lower() in ["src", "lib", "app"]:
        path_parts = rel_path.split("/")
        if len(path_parts) > 1:
            clean_name = path_parts[-1].replace("_", " ").replace("-", " ")
    
    return clean_name.title()


def _infer_module_type(code_files: list, all_files: list, folder_name: str) -> str:
    """Infiere el tipo de módulo basado en los archivos"""
    folder_lower = folder_name.lower()
    
    # Detectar por nombre de carpeta
    if "controller" in folder_lower or "api" in folder_lower:
        return "api-module"
    elif "service" in folder_lower or "business" in folder_lower:
        return "service-module"
    elif "model" in folder_lower or "entity" in folder_lower or "domain" in folder_lower:
        return "domain-module"
    elif "repository" in folder_lower or "dao" in folder_lower:
        return "data-module"
    elif "view" in folder_lower or "ui" in folder_lower or "component" in folder_lower:
        return "ui-module"
    
    # Detectar por extensiones de archivos
    has_python = any(f.endswith(".py") for f in code_files)
    has_java = any(f.endswith(".java") for f in code_files)
    has_typescript = any(f.endswith((".ts", ".tsx")) for f in code_files)
    has_javascript = any(f.endswith((".js", ".jsx")) for f in code_files)
    
    if has_python:
        return "python-module"
    elif has_java:
        return "java-module"
    elif has_typescript:
        return "typescript-module"
    elif has_javascript:
        return "javascript-module"
    
    return "generic-module"

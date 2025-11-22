"""
Generador de diagramas C4 DETERMINÍSTICO (sin IA)
Usa el análisis mejorado para crear diagramas Mermaid precisos
"""


def generate_c1_diagram(analysis):
    """Genera diagrama C1 (Contexto del Sistema) con contexto de negocio inferido"""
    
    project_name = analysis.get("project_name", "Sistema")
    project_type = analysis.get("project_type", "unknown")
    responsibilities = analysis.get("system_responsibilities", [])
    components = analysis.get("components_detected", [])
    
    # Inferir dominio de negocio desde nombres de entidades
    domain_context = _infer_business_domain(project_name, components)
    
    # Título y descripción mejorada
    resp_text = " | ".join(responsibilities[:3]) if responsibilities else domain_context["default_description"]
    
    # Nombres de actores según el dominio
    user_name = domain_context.get("user_name", "Usuario")
    user_desc = domain_context.get("user_desc", "Interactúa con el sistema")
    
    # Adaptar según tipo de proyecto
    is_gui_app = project_type == "gui-application"
    is_mobile_app = project_type == "mobile-app"
    
    diagram = f"""---
title: Sistema {project_name} - Diagrama C1 (Contexto)
---
C4Context
    title Diagrama de Contexto del Sistema - {project_name}

    Person({user_name.lower().replace(" ", "_")}, "{user_name}", "{user_desc}")
    
    System(system, "{project_name}", "{resp_text}")
    
    System_Ext(database, "Base de Datos", "Almacena datos persistentes")
    
"""
    
    # Relaciones según tipo de aplicación
    if is_gui_app or is_mobile_app:
        interaction_type = "Interacción GUI" if is_gui_app else "Interacción Mobile"
        diagram += f"""    Rel({user_name.lower().replace(" ", "_")}, system, "Usa", "{interaction_type}")
"""
    else:
        diagram += f"""    Rel({user_name.lower().replace(" ", "_")}, system, "Usa", "HTTP/HTTPS")
"""
    
    diagram += """    Rel(system, database, "Lee/Escribe", "SQL")
"""
    
    return diagram


def _infer_business_domain(project_name, components):
    """
    Infiere el dominio de negocio analizando nombres de componentes y proyecto
    """
    project_lower = project_name.lower()
    component_names = " ".join([c.get("name", "").lower() for c in components])
    
    # Patrones de dominio
    domains = {
        "petclinic": {
            "domain": "Clínica Veterinaria",
            "user_name": "Veterinario/Recepcionista",
            "user_desc": "Gestiona información de mascotas y dueños",
            "default_description": "Sistema de gestión de clínica veterinaria"
        },
        "ecommerce": {
            "domain": "E-Commerce",
            "user_name": "Cliente",
            "user_desc": "Compra productos en línea",
            "default_description": "Plataforma de comercio electrónico"
        },
        "shop": {
            "domain": "Tienda Online",
            "user_name": "Comprador",
            "user_desc": "Navega y compra productos",
            "default_description": "Sistema de tienda online"
        },
        "blog": {
            "domain": "Blog/CMS",
            "user_name": "Autor/Lector",
            "user_desc": "Publica y lee contenido",
            "default_description": "Sistema de gestión de contenido"
        },
        "bank": {
            "domain": "Banca",
            "user_name": "Cliente Bancario",
            "user_desc": "Realiza operaciones bancarias",
            "default_description": "Sistema bancario"
        },
        "hotel": {
            "domain": "Hotelería",
            "user_name": "Huésped",
            "user_desc": "Reserva y gestiona estadías",
            "default_description": "Sistema de gestión hotelera"
        },
        "library": {
            "domain": "Biblioteca",
            "user_name": "Bibliotecario/Lector",
            "user_desc": "Gestiona préstamos de libros",
            "default_description": "Sistema de gestión bibliotecaria"
        },
        "school": {
            "domain": "Educación",
            "user_name": "Profesor/Estudiante",
            "user_desc": "Gestiona cursos y calificaciones",
            "default_description": "Sistema de gestión educativa"
        },
        "hospital": {
            "domain": "Salud",
            "user_name": "Médico/Paciente",
            "user_desc": "Gestiona historiales médicos",
            "default_description": "Sistema de gestión hospitalaria"
        }
    }
    
    # Buscar coincidencias
    for keyword, domain_info in domains.items():
        if keyword in project_lower or keyword in component_names:
            return domain_info
    
    # Buscar por entidades comunes
    if any(word in component_names for word in ["user", "customer", "client"]):
        return {
            "domain": "Aplicación de Negocio",
            "user_name": "Usuario",
            "user_desc": "Interactúa con el sistema",
            "default_description": "Sistema de gestión empresarial"
        }
    
    # Default genérico
    return {
        "domain": "Software",
        "user_name": "Usuario",
        "user_desc": "Interactúa con el sistema",
        "default_description": "Sistema de software"
    }


def generate_c2_diagram(analysis):
    """
    Genera diagrama C2 (Contenedores) MEJORADO
    - Si detecta módulos de negocio: genera 1 container por módulo
    - Si no: usa el método tradicional por capas
    """
    
    project_name = analysis.get("project_name", "Sistema")
    project_type = analysis.get("project_type", "unknown")
    business_modules = analysis.get("business_modules", [])
    technologies = analysis.get("technologies", {})
    layers = analysis.get("architectural_layers", {})
    components = analysis.get("components_detected", [])
    total_files = analysis.get("total_files", 0)
    
    # Detectar si es GUI app
    is_gui_app = project_type == "gui-application"
    is_mobile_app = project_type == "mobile-app"
    
    # Backend/Frontend tech según tipo
    if is_gui_app:
        frontend_tech = ", ".join(technologies.get("frontend", ["GUI Framework"]))
        backend_tech = frontend_tech
    elif is_mobile_app:
        frontend_tech = ", ".join(technologies.get("frontend", ["Mobile Framework"]))
        backend_tech = frontend_tech
    else:
        backend_tech_list = technologies.get("backend", [])
        if not backend_tech_list:
            type_tech_map = {
                "api-backend": ["Backend Framework"],
                "spring-boot": ["Spring Boot"],
                "django": ["Django"],
                "fastapi": ["FastAPI"],
                "nodejs": ["Node.js"],
                "dotnet": [".NET Core"],
                "go": ["Go"],
                "rust": ["Rust"]
            }
            backend_tech_list = type_tech_map.get(project_type, ["Backend"])
        backend_tech = ", ".join(backend_tech_list)
    
    db_tech = ", ".join(technologies.get("database", ["SQL Database"]))
    
    diagram = f"""---
title: Sistema {project_name} - Diagrama C2 (Contenedores)
---
C4Container
    title Diagrama de Contenedores - {project_name}

    Person(user, "Usuario", "Usuario del sistema")
    
    Container_Boundary(system, "{project_name}") {{
"""
    
    # NUEVO: Si hay módulos de negocio detectados, generar containers por módulo
    if len(business_modules) >= 3:  # Al menos 3 módulos para usar vista modular
        # Escalar según tamaño del proyecto
        if total_files < 50:
            max_modules = 8
        elif total_files < 200:
            max_modules = 15
        else:
            max_modules = 25
        
        selected_modules = business_modules[:max_modules]
        
        for module in selected_modules:
            module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
            module_name = module["name"]
            file_count = module["files"]
            
            # Descripción basada en archivos encontrados
            if file_count == 1:
                desc = f"1 componente"
            else:
                desc = f"{file_count} componentes"
            
            diagram += f"""        Container({module_id}, "{module_name}", "{backend_tech}", "{desc}")
"""
        
        # Agregar contenedores adicionales si hay muchos módulos
        if len(business_modules) > max_modules:
            remaining = len(business_modules) - max_modules
            diagram += f"""        Container(other_services, "Otros Servicios", "{backend_tech}", "{remaining} módulos adicionales")
"""
    
    else:
        # Método tradicional: por capas (cuando no hay suficientes módulos)
        controllers_count = layers.get("presentation", {}).get("count", 0)
        if controllers_count > 0 or len(components) > 0:
            comp_count = controllers_count if controllers_count > 0 else len(components)
            
            if is_gui_app:
                diagram += f"""        Container(gui, "Interfaz Gráfica", "{backend_tech}", "Contiene {comp_count} ventanas y widgets")
"""
            elif is_mobile_app:
                diagram += f"""        Container(mobile, "Aplicación Mobile", "{backend_tech}", "Contiene {comp_count} pantallas y componentes")
"""
            else:
                diagram += f"""        Container(api, "API Backend", "{backend_tech}", "Gestiona {comp_count} endpoints/componentes")
"""
        
        services_count = layers.get("application", {}).get("count", 0)
        if services_count > 0:
            if is_gui_app:
                diagram += f"""        Container(business, "Lógica de Negocio", "{backend_tech}", "Contiene {services_count} controladores y modelos")
"""
            else:
                diagram += f"""        Container(business, "Business Logic", "{backend_tech}", "Contiene {services_count} servicios de negocio")
"""
        
        repos_count = layers.get("infrastructure", {}).get("count", 0)
        if repos_count > 0:
            diagram += f"""        Container(data, "Capa de Acceso a Datos", "{backend_tech}", "{repos_count} repositorios para acceso a datos")
"""
    
    diagram += """    }
    
    ContainerDb(database, "Base de Datos", \""""
    
    diagram += db_tech
    diagram += """", "Almacena entidades del dominio")
    
"""
    
    # Generar relaciones
    if len(business_modules) >= 3:
        # Relaciones para vista modular: usuario usa los módulos principales
        main_modules = business_modules[:min(5, len(business_modules))]
        for module in main_modules:
            module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
            diagram += f"""    Rel(user, {module_id}, "Usa", "HTTP/REST")
"""
        
        # Módulos se conectan a la base de datos
        for module in business_modules[:min(10, len(business_modules))]:
            module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
            diagram += f"""    Rel({module_id}, database, "Lee/Escribe", "SQL")
"""
        
        # Relaciones entre módulos (algunos ejemplos)
        if len(business_modules) >= 2:
            # Ejemplo: auth se usa por otros módulos
            auth_module = next((m for m in business_modules if "auth" in m["keyword"].lower()), None)
            if auth_module:
                auth_id = auth_module["name"].lower().replace(" ", "_").replace("-", "_")
                for module in business_modules[:3]:
                    if module != auth_module:
                        module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
                        diagram += f"""    Rel({module_id}, {auth_id}, "Autentica", "JWT")
"""
                        break
    
    else:
        # Relaciones tradicionales por capas
        if is_gui_app or is_mobile_app:
            interaction_type = "Interacción GUI" if is_gui_app else "Interacción Mobile"
            main_container = "gui" if is_gui_app else "mobile"
            diagram += f"""    Rel(user, {main_container}, "{interaction_type}", "Clicks/Eventos")
"""
        else:
            diagram += """    Rel(user, api, "Envía peticiones HTTP", "JSON/REST")
"""
        
        main_container_var = "gui" if is_gui_app else ("mobile" if is_mobile_app else "api")
        services_count = layers.get("application", {}).get("count", 0)
        repos_count = layers.get("infrastructure", {}).get("count", 0)
        
        if services_count > 0:
            diagram += f"""    Rel({main_container_var}, business, "Invoca", "llamadas internas")
"""
        if repos_count > 0:
            if services_count > 0:
                diagram += """    Rel(business, data, "Usa", "operaciones CRUD")
"""
            diagram += """    Rel(data, database, "Lee/Escribe", "SQL")
"""
        else:
            diagram += f"""    Rel({main_container_var}, database, "Lee/Escribe", "SQL")
"""
    
    return diagram


def _make_safe_mermaid_id(name):
    """
    Convierte un nombre de archivo/componente en un ID válido para Mermaid.
    - Remueve extensiones
    - Solo alfanuméricos y guiones bajos
    - No puede empezar con número
    - Fallback a hash si queda vacío
    """
    # Remover extensiones comunes
    for ext in [".java", ".py", ".js", ".ts", ".cs", ".go", ".rs", ".ui", ".swift", ".kt", ".dart"]:
        name = name.replace(ext, "")
    
    # Solo alfanuméricos y guiones bajos
    safe = "".join(c for c in name if c.isalnum() or c == "_").lower()
    
    # Si empieza con número, agregar prefijo
    if safe and safe[0].isdigit():
        safe = f"comp_{safe}"
    
    # Si quedó vacío, usar hash del nombre original
    if not safe:
        safe = f"component_{abs(hash(name)) % 10000}"
    
    return safe


def generate_c3_diagram(analysis):
    """Genera diagrama C3 (Componentes) - Compatible con cualquier lenguaje"""
    
    project_name = analysis.get("project_name", "Sistema")
    project_type = analysis.get("project_type", "unknown")
    layers = analysis.get("architectural_layers", {})
    patterns = analysis.get("architecture_patterns", [])
    technologies = analysis.get("technologies", {})
    components = analysis.get("components_detected", [])
    
    # Detectar tipo de aplicación
    is_gui_app = project_type == "gui-application"
    is_mobile_app = project_type == "mobile-app"
    
    # Backend/Frontend tech según tipo
    if is_gui_app:
        main_tech = ", ".join(technologies.get("frontend", ["GUI Framework"]))
        container_name = "Interfaz Gráfica"
    elif is_mobile_app:
        main_tech = ", ".join(technologies.get("frontend", ["Mobile Framework"]))
        container_name = "Aplicación Mobile"
    else:
        backend_tech_list = technologies.get("backend", [])
        if not backend_tech_list:
            type_tech_map = {
                "spring-boot": ["Spring Boot"],
                "django": ["Django"],
                "fastapi": ["FastAPI"],
                "nodejs": ["Node.js"],
                "dotnet": [".NET Core"],
                "go": ["Go"],
                "rust": ["Rust"]
            }
            backend_tech_list = type_tech_map.get(project_type, ["Backend"])
        main_tech = ", ".join(backend_tech_list)
        container_name = "API Backend"
    
    # Detectar patrón principal
    main_pattern = "Layered Architecture"
    if patterns:
        main_pattern = patterns[0].get("name", "Layered Architecture")
    
    diagram = f"""---
title: Sistema {project_name} - Diagrama C3 (Componentes)
---
C4Component
    title Diagrama de Componentes - {project_name} ({main_pattern})
    
    Container_Boundary(api, "{container_name} - {main_tech}") {{
"""
    
    has_components = False
    
    # NUEVO: Escalar límites según tamaño del proyecto
    total_files = analysis.get("total_files", 0)
    if total_files < 50:
        comp_limit_per_layer = 5
    elif total_files < 200:
        comp_limit_per_layer = 10
    else:
        comp_limit_per_layer = 15
    
    # Presentation Layer Components
    if layers.get("presentation", {}).get("count", 0) > 0:
        has_components = True
        presentation_comps = layers["presentation"]["components"][:comp_limit_per_layer]
        
        if is_gui_app:
            diagram += """        
        Component(windows, "Ventanas Principales", "GUI", "Ventanas y diálogos de la aplicación")
"""
            # Mostrar más componentes para proyectos grandes
            max_show = min(len(presentation_comps), comp_limit_per_layer)
            for comp in presentation_comps[:max_show]:
                comp_name = comp.replace(".py", "").replace(".ui", "").replace(".java", "").replace(".cs", "")
                safe_name = _make_safe_mermaid_id(comp)
                diagram += f"""        Component({safe_name}, "{comp_name}", "Window/Widget", "Componente visual")
"""
        elif is_mobile_app:
            diagram += """        
        Component(screens, "Pantallas", "Mobile", "Pantallas de la aplicación mobile")
"""
            max_show = min(len(presentation_comps), comp_limit_per_layer)
            for comp in presentation_comps[:max_show]:
                comp_name = comp.replace(".swift", "").replace(".kt", "").replace(".dart", "").replace(".java", "")
                safe_name = _make_safe_mermaid_id(comp)
                diagram += f"""        Component({safe_name}, "{comp_name}", "Screen", "Pantalla específica")
"""
        else:
            diagram += """        
        Component(controllers, "Controllers", "Presentation", "Maneja peticiones HTTP y enruta a servicios")
"""
            max_show = min(len(presentation_comps), comp_limit_per_layer)
            for comp in presentation_comps[:max_show]:
                comp_name = comp.replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "").replace(".cs", "").replace(".go", "").replace(".rs", "")
                safe_name = _make_safe_mermaid_id(comp)
                diagram += f"""        Component({safe_name}, "{comp_name}", "Controller", "Endpoint específico")
"""
    
    # Application Layer Components
    if layers.get("application", {}).get("count", 0) > 0:
        has_components = True
        application_comps = layers["application"]["components"][:comp_limit_per_layer]
        diagram += """
        Component(services, "Services", "Business Logic", "Implementa lógica de negocio")
"""
        max_show = min(len(application_comps), comp_limit_per_layer)
        for comp in application_comps[:max_show]:
            comp_name = comp.replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "").replace(".cs", "").replace(".go", "").replace(".rs", "")
            safe_name = _make_safe_mermaid_id(comp)
            diagram += f"""        Component({safe_name}, "{comp_name}", "Service", "Lógica de negocio")
"""
    
    # Domain Layer Components
    if layers.get("domain", {}).get("count", 0) > 0:
        has_components = True
        domain_comps = layers["domain"]["components"][:comp_limit_per_layer]
        diagram += """
        Component(models, "Domain Models", "Entities", "Representan conceptos del negocio")
"""
        max_show = min(len(domain_comps), comp_limit_per_layer)
        for comp in domain_comps[:max_show]:
            comp_name = comp.replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "").replace(".cs", "").replace(".go", "").replace(".rs", "")
            safe_name = _make_safe_mermaid_id(comp)
            diagram += f"""        Component({safe_name}, "{comp_name}", "Entity", "Modelo de dominio")
"""
    
    # Infrastructure Layer Components
    if layers.get("infrastructure", {}).get("count", 0) > 0:
        has_components = True
        infra_comps = layers["infrastructure"]["components"][:comp_limit_per_layer]
        diagram += """
        Component(repositories, "Repositories", "Data Access", "Abstrae acceso a base de datos")
"""
        max_show = min(len(infra_comps), comp_limit_per_layer)
        for comp in infra_comps[:max_show]:
            comp_name = comp.replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "").replace(".cs", "").replace(".go", "").replace(".rs", "")
            safe_name = _make_safe_mermaid_id(comp)
            diagram += f"""        Component({safe_name}, "{comp_name}", "Repository", "Acceso a datos")
"""
    
    # Fallback: Si no se detectaron capas, usar componentes generales
    if not has_components and len(components) > 0:
        diagram += """
        Component(core, "Core Components", "Application", "Componentes principales del sistema")
"""
        for comp in components[:5]:
            comp_name = comp.get("name", "component").replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "").replace(".cs", "").replace(".go", "").replace(".rs", "")
            safe_name = _make_safe_mermaid_id(comp_name)
            diagram += f"""        Component({safe_name}, "{comp_name}", "Component", "Componente del sistema")
"""
    
    diagram += """    }
    
    ContainerDb(database, "Database", "SQL", "Datos persistentes")
    
"""
    
    # Relaciones condicionales según capas detectadas
    pres_count = layers.get("presentation", {}).get("count", 0)
    app_count = layers.get("application", {}).get("count", 0)
    domain_count = layers.get("domain", {}).get("count", 0)
    infra_count = layers.get("infrastructure", {}).get("count", 0)
    
    if pres_count > 0 and app_count > 0:
        if is_gui_app or is_mobile_app:
            pres_comp = "windows" if is_gui_app else "screens"
            diagram += f"""    Rel({pres_comp}, services, "Invoca", "Eventos/Signals")
"""
        else:
            diagram += """    Rel(controllers, services, "Invoca")
"""
    
    # Solo crear relación si models existe
    if app_count > 0 and domain_count > 0:
        diagram += """    Rel(services, models, "Usa")
"""
    
    if app_count > 0 and infra_count > 0:
        diagram += """    Rel(services, repositories, "Accede a datos via")
"""
    
    if infra_count > 0:
        diagram += """    Rel(repositories, database, "Lee/Escribe", "SQL")
"""
    elif pres_count > 0:
        if is_gui_app or is_mobile_app:
            pres_comp = "windows" if is_gui_app else "screens"
            diagram += f"""    Rel({pres_comp}, database, "Lee/Escribe", "SQL")
"""
        else:
            diagram += """    Rel(controllers, database, "Lee/Escribe", "SQL")
"""
    
    return diagram


def generate_all_diagrams_deterministic(analysis, output_prefix="diagram"):
    """
    Genera los 3 diagramas C4 de forma determinística
    """
    results = {}
    
    # C1
    try:
        c1 = generate_c1_diagram(analysis)
        c1_file = f"{output_prefix}_c1.mmd"
        with open(c1_file, 'w', encoding='utf-8') as f:
            f.write(c1)
        results["c1"] = {"file": c1_file, "status": "success"}
    except Exception as e:
        results["c1"] = {"file": None, "status": "error", "message": str(e)}
    
    # C2
    try:
        c2 = generate_c2_diagram(analysis)
        c2_file = f"{output_prefix}_c2.mmd"
        with open(c2_file, 'w', encoding='utf-8') as f:
            f.write(c2)
        results["c2"] = {"file": c2_file, "status": "success"}
    except Exception as e:
        results["c2"] = {"file": None, "status": "error", "message": str(e)}
    
    # C3
    try:
        c3 = generate_c3_diagram(analysis)
        c3_file = f"{output_prefix}_c3.mmd"
        with open(c3_file, 'w', encoding='utf-8') as f:
            f.write(c3)
        results["c3"] = {"file": c3_file, "status": "success"}
    except Exception as e:
        results["c3"] = {"file": None, "status": "error", "message": str(e)}
    
    return results

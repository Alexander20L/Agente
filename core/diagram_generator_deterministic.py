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
        # Escalar según tamaño del proyecto (OPCIÓN A - aumentado)
        if total_files < 50:
            max_modules = 10
        elif total_files < 200:
            max_modules = 18
        else:
            max_modules = 30
        
        # ORDENAR POR IMPORTANCIA: módulos con más archivos primero (son los centrales)
        sorted_modules = sorted(business_modules, key=lambda m: m.get("files", 0), reverse=True)
        selected_modules = sorted_modules[:max_modules]
        
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
        selected_modules = business_modules[:max_modules] if 'max_modules' in locals() else business_modules[:15]
        
        # 1. USUARIO → MÓDULOS PRINCIPALES (solo user-facing)
        # Filtrar módulos que NO son infraestructura interna
        exclude_keywords = ["config", "model", "domain", "entity", "repository", "util", "helper", "test"]
        user_facing = [m for m in selected_modules 
                      if not any(kw in m["keyword"].lower() for kw in exclude_keywords)]
        user_facing_modules = user_facing[:min(4, len(user_facing))]
        
        for module in user_facing_modules:
            module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
            diagram += f"""    Rel(user, {module_id}, "Usa", "HTTP/REST")
"""
        
        # 2. MÓDULOS → BASE DE DATOS (solo módulos con lógica de persistencia)
        # Excluir config, model/domain (son POJOs), y test
        db_exclude = ["config", "model", "domain", "entity", "test"]
        data_modules = [m for m in selected_modules 
                       if not any(kw in m["keyword"].lower() for kw in db_exclude)]
        
        for module in data_modules:
            module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
            diagram += f"""    Rel({module_id}, database, "Lee/Escribe", "SQL")
"""
        
        # 3. RELACIONES COHERENTES ENTRE MÓDULOS (siguiendo flujo lógico)
        
        # Buscar módulos clave para establecer relaciones lógicas
        auth_module = next((m for m in selected_modules if "auth" in m["keyword"].lower() or "login" in m["keyword"].lower() or "security" in m["keyword"].lower()), None)
        user_module = next((m for m in selected_modules if "user" in m["keyword"].lower() or "account" in m["keyword"].lower() or "customer" in m["keyword"].lower()), None)
        payment_module = next((m for m in selected_modules if "payment" in m["keyword"].lower() or "billing" in m["keyword"].lower()), None)
        order_module = next((m for m in selected_modules if "order" in m["keyword"].lower() or "cart" in m["keyword"].lower() or "purchase" in m["keyword"].lower()), None)
        product_module = next((m for m in selected_modules if "product" in m["keyword"].lower() or "item" in m["keyword"].lower() or "catalog" in m["keyword"].lower()), None)
        notification_module = next((m for m in selected_modules if "notification" in m["keyword"].lower() or "email" in m["keyword"].lower() or "message" in m["keyword"].lower()), None)
        api_module = next((m for m in selected_modules if "api" in m["keyword"].lower() or "controller" in m["keyword"].lower() or "endpoint" in m["keyword"].lower() or "web" in m["keyword"].lower()), None)
        
        # PATRÓN 1: API/Controller recibe peticiones y delega a módulos de negocio
        if api_module:
            api_id = api_module["name"].lower().replace(" ", "_").replace("-", "_")
            # API se conecta con 2-3 módulos principales
            business_modules = [m for m in [user_module, order_module, product_module, payment_module] if m and m != api_module]
            for module in business_modules[:3]:
                module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
                diagram += f"""    Rel({api_id}, {module_id}, "Invoca", "Internal call")
"""
        
        # PATRÓN 2: Auth valida peticiones de otros módulos (flujo coherente)
        if auth_module:
            auth_id = auth_module["name"].lower().replace(" ", "_").replace("-", "_")
            # Solo módulos que necesitan autenticación
            modules_needing_auth = [user_module, order_module, payment_module]
            for module in modules_needing_auth:
                if module and module != auth_module:
                    module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
                    diagram += f"""    Rel({module_id}, {auth_id}, "Valida tokens", "JWT")
"""
        
        # PATRÓN 3: Order/Purchase flujo coherente (Order → User, Product, Payment)
        if order_module:
            order_id = order_module["name"].lower().replace(" ", "_").replace("-", "_")
            if user_module:
                user_id = user_module["name"].lower().replace(" ", "_").replace("-", "_")
                diagram += f"""    Rel({order_id}, {user_id}, "Obtiene datos cliente", "Query")
"""
            if product_module:
                product_id = product_module["name"].lower().replace(" ", "_").replace("-", "_")
                diagram += f"""    Rel({order_id}, {product_id}, "Consulta disponibilidad", "Query")
"""
            if payment_module:
                payment_id = payment_module["name"].lower().replace(" ", "_").replace("-", "_")
                diagram += f"""    Rel({order_id}, {payment_id}, "Procesa pago", "Sync call")
"""
        
        # PATRÓN 4: Notifications recibe eventos de otros módulos (flujo async)
        if notification_module:
            notif_id = notification_module["name"].lower().replace(" ", "_").replace("-", "_")
            event_sources = [m for m in [order_module, payment_module, user_module] if m]
            for module in event_sources[:2]:  # Solo 2 para no saturar
                module_id = module["name"].lower().replace(" ", "_").replace("-", "_")
                diagram += f"""    Rel({module_id}, {notif_id}, "Publica evento", "Message Queue")
"""
    
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
    
    # NUEVO: Escalar límites según tamaño del proyecto (OPCIÓN A - aumentado)
    total_files = analysis.get("total_files", 0)
    if total_files < 50:
        comp_limit_per_layer = 8
    elif total_files < 200:
        comp_limit_per_layer = 12
    else:
        comp_limit_per_layer = 18
    
    # Presentation Layer Components
    if layers.get("presentation", {}).get("count", 0) > 0:
        has_components = True
        # ORDENAR POR IMPORTANCIA: usar PageRank si está disponible
        all_pres_comps = layers["presentation"]["components"]
        
        # FILTRAR: eliminar tests y duplicados
        filtered_pres = []
        seen = set()
        for comp in all_pres_comps:
            comp_lower = comp.lower()
            if "test" not in comp_lower and comp not in seen:
                filtered_pres.append(comp)
                seen.add(comp)
        
        if "important_components" in analysis and analysis["important_components"]:
            pres_important = [c for c in analysis["important_components"] if any(pc in c["component"] for pc in filtered_pres)]
            pres_sorted = [c["component"] for c in pres_important]
            pres_sorted.extend([c for c in filtered_pres if c not in pres_sorted])
            presentation_comps = pres_sorted[:comp_limit_per_layer]
        else:
            presentation_comps = filtered_pres[:comp_limit_per_layer]
        
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
        # ORDENAR POR IMPORTANCIA: usar PageRank si está disponible
        all_app_comps = layers["application"]["components"]
        
        # FILTRAR: eliminar tests, main class, config y duplicados
        filtered_app = []
        seen = set()
        exclude_patterns = ["test", "application", "main", "config", "configuration"]
        for comp in all_app_comps:
            comp_lower = comp.lower()
            if not any(pattern in comp_lower for pattern in exclude_patterns) and comp not in seen:
                filtered_app.append(comp)
                seen.add(comp)
        
        if "important_components" in analysis and analysis["important_components"]:
            app_important = [c for c in analysis["important_components"] if any(ac in c["component"] for ac in filtered_app)]
            app_sorted = [c["component"] for c in app_important]
            app_sorted.extend([c for c in filtered_app if c not in app_sorted])
            application_comps = app_sorted[:comp_limit_per_layer]
        else:
            application_comps = filtered_app[:comp_limit_per_layer]
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
        # ORDENAR POR IMPORTANCIA: usar PageRank si está disponible
        all_domain_comps = layers["domain"]["components"]
        
        # FILTRAR: eliminar duplicados
        filtered_domain = []
        seen = set()
        for comp in all_domain_comps:
            if comp not in seen:
                filtered_domain.append(comp)
                seen.add(comp)
        
        if "important_components" in analysis and analysis["important_components"]:
            domain_important = [c for c in analysis["important_components"] if any(dc in c["component"] for dc in filtered_domain)]
            domain_sorted = [c["component"] for c in domain_important]
            domain_sorted.extend([c for c in filtered_domain if c not in domain_sorted])
            domain_comps = domain_sorted[:comp_limit_per_layer]
        else:
            domain_comps = filtered_domain[:comp_limit_per_layer]
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
        # ORDENAR POR IMPORTANCIA: usar PageRank si está disponible
        all_infra_comps = layers["infrastructure"]["components"]
        
        # FILTRAR: eliminar duplicados
        filtered_infra = []
        seen = set()
        for comp in all_infra_comps:
            if comp not in seen:
                filtered_infra.append(comp)
                seen.add(comp)
        
        if "important_components" in analysis and analysis["important_components"]:
            infra_important = [c for c in analysis["important_components"] if any(ic in c["component"] for ic in filtered_infra)]
            infra_sorted = [c["component"] for c in infra_important]
            infra_sorted.extend([c for c in filtered_infra if c not in infra_sorted])
            infra_comps = infra_sorted[:comp_limit_per_layer]
        else:
            infra_comps = filtered_infra[:comp_limit_per_layer]
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
    
    # Obtener componentes FILTRADOS para crear relaciones específicas
    pres_comps = presentation_comps if layers.get("presentation", {}).get("count", 0) > 0 else []
    app_comps = application_comps if layers.get("application", {}).get("count", 0) > 0 else []
    domain_comps_list = domain_comps if layers.get("domain", {}).get("count", 0) > 0 else []
    infra_comps_list = infra_comps if layers.get("infrastructure", {}).get("count", 0) > 0 else []
    
    # 1. RELACIONES ENTRE CONTENEDORES PRINCIPALES
    if pres_count > 0 and app_count > 0:
        if is_gui_app or is_mobile_app:
            pres_comp = "windows" if is_gui_app else "screens"
            diagram += f"""    Rel({pres_comp}, services, "Invoca", "Eventos/Signals")
"""
        else:
            diagram += """    Rel(controllers, services, "Invoca")
"""
    
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
    
    # 2. RELACIONES COHERENTES ENTRE COMPONENTES (siguiendo flujo arquitectónico)
    
    # FLUJO: Presentation → Application (cada controller invoca servicios relacionados)
    if pres_count > 0 and app_count > 0:
        # Conectar solo 2-3 componentes de presentación con sus servicios correspondientes
        max_connections = min(len(pres_comps), 2)
        
        for i in range(max_connections):
            if i < len(pres_comps) and i < len(app_comps):
                pres_id = _make_safe_mermaid_id(pres_comps[i])
                app_id = _make_safe_mermaid_id(app_comps[i])
                diagram += f"""    Rel({pres_id}, {app_id}, "Invoca")
"""
    
    # FLUJO: Application → Domain (servicios usan modelos relacionados)
    if app_count > 0 and domain_count > 0:
        max_connections = min(len(app_comps), 2)
        
        for i in range(max_connections):
            if i < len(app_comps) and i < len(domain_comps_list):
                app_id = _make_safe_mermaid_id(app_comps[i])
                domain_id = _make_safe_mermaid_id(domain_comps_list[i])
                diagram += f"""    Rel({app_id}, {domain_id}, "Usa")
"""
    
    # FLUJO: Application → Infrastructure (servicios persisten via repositorios)
    if app_count > 0 and infra_count > 0:
        max_connections = min(len(app_comps), min(len(infra_comps_list), 2))
        
        for i in range(max_connections):
            if i < len(app_comps) and i < len(infra_comps_list):
                app_id = _make_safe_mermaid_id(app_comps[i])
                infra_id = _make_safe_mermaid_id(infra_comps_list[i])
                diagram += f"""    Rel({app_id}, {infra_id}, "Persiste via")
"""
    
    # FLUJO: Infrastructure → Database (repositorios ejecutan queries)
    if infra_count > 0:
        max_connections = min(len(infra_comps_list), 3)
        for i in range(max_connections):
            if i < len(infra_comps_list):
                infra_id = _make_safe_mermaid_id(infra_comps_list[i])
                diagram += f"""    Rel({infra_id}, database, "Ejecuta SQL")
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

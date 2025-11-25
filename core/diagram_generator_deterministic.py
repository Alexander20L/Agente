"""
Generador de diagramas C4 DETERMINÍSTICO (sin IA)
Usa el análisis mejorado para crear diagramas Mermaid precisos
"""


def _detect_containers(analysis):
    """
    Detecta los CONTENEDORES reales del sistema (aplicaciones ejecutables)
    según el modelo C4 correcto.
    
    Contenedores = Aplicaciones/Procesos ejecutables, NO módulos internos
    Ejemplos: Desktop App, Web App, API Backend, Database, Cache, Message Queue
    """
    containers = []
    project_type = analysis.get("project_type", "unknown")
    technologies = analysis.get("technologies", {})
    components = analysis.get("components_detected", [])
    
    # 1. APLICACIÓN PRINCIPAL (Desktop, Web, Mobile, CLI, API)
    main_container = _detect_main_application(project_type, technologies, components, analysis)
    if main_container:
        # Si es una lista (múltiples contenedores como Odoo), agregar todos
        if isinstance(main_container, list):
            containers.extend(main_container)
        else:
            containers.append(main_container)
    
    # 2. DATABASE
    db_container = _detect_database_container(technologies, components)
    if db_container:
        containers.append(db_container)
    
    # 3. CACHE (Redis, Memcached)
    cache_container = _detect_cache_container(technologies, components)
    if cache_container:
        containers.append(cache_container)
    
    # 4. MESSAGE QUEUE (RabbitMQ, Kafka)
    mq_container = _detect_message_queue_container(technologies, components)
    if mq_container:
        containers.append(mq_container)
    
    return containers


def _detect_odoo_containers(analysis, components, component_count):
    """
    Detecta contenedores específicos de Odoo/OpenERP.
    Odoo tiene múltiples servicios/procesos que deben mostrarse como contenedores separados.
    """
    containers = []
    
    # Detectar componentes clave de Odoo
    component_names = [c.get("name", "").lower() for c in components if isinstance(c, dict)]
    has_http = any("http" in name for name in component_names)
    has_models = any("model" in name for name in component_names)
    has_api = any("api" in name for name in component_names)
    has_service = any("service" in name for name in component_names)
    
    # 1. HTTP Server (Frontend/Web Interface)
    if has_http:
        containers.append({
            "id": "http_server",
            "name": "HTTP Server",
            "technology": "Python + Werkzeug",
            "description": "Servidor web principal | Interfaz de usuario web",
            "type": "application"
        })
    
    # 2. RPC Server (API Backend)
    if has_api:
        containers.append({
            "id": "rpc_server",
            "name": "RPC Server",
            "technology": "XML-RPC/JSON-RPC",
            "description": "Servidor de APIs | Servicios web externos",
            "type": "application"
        })
    
    # 3. Application Core (Business Logic)
    if has_models or has_service:
        containers.append({
            "id": "app_core",
            "name": "Application Core",
            "technology": "Python + ORM",
            "description": f"Núcleo de negocio | {component_count} módulos | Lógica ERP/CRM",
            "type": "application"
        })
    
    # 4. Background Workers (Cron/Jobs)
    if has_service:
        containers.append({
            "id": "workers",
            "name": "Background Workers",
            "technology": "Python + Cron",
            "description": "Tareas programadas | Procesamiento asíncrono",
            "type": "application"
        })
    
    # Si no se detectaron contenedores específicos, retornar uno genérico
    if not containers:
        containers.append({
            "id": "web_app",
            "name": "Web Application Server",
            "technology": "Python + HTTP Server",
            "description": f"Servidor web con {component_count} componentes | Arquitectura modular",
            "type": "application"
        })
    
    return containers


def _detect_main_application(project_type, technologies, components, analysis):
    """Detecta el contenedor de aplicación principal"""
    frontend_tech = technologies.get("frontend", [])
    backend_tech = technologies.get("backend", [])
    all_tech = ", ".join(frontend_tech + backend_tech)
    
    component_count = len(components)
    business_modules = analysis.get("business_modules", [])
    
    # Web Framework (e.g., Odoo, Django, FastAPI framework itself)
    if project_type == "web-framework":
        project_name = analysis.get("project_name", "").lower()
        
        # Odoo/OpenERP: Sistema complejo con múltiples contenedores
        if "odoo" in project_name or "openerp" in project_name:
            return _detect_odoo_containers(analysis, components, component_count)
        
        # Otros frameworks: contenedor único
        return {
            "id": "web_app",
            "name": "Web Application",
            "technology": all_tech or "Python + HTTP Server",
            "description": f"Servidor web con {component_count} componentes | Arquitectura modular",
            "type": "application"
        }
    
    # GUI Application (Desktop)
    if project_type == "gui-application" or any(gui in all_tech for gui in ["PyQt", "Tkinter", "JavaFX", "Swing", "WPF", "WinForms", "Electron"]):
        tech = next((t for t in ["PyQt5", "PyQt6", "Tkinter", "JavaFX", "Swing", "WPF", "WinForms", "Electron"] if t in all_tech), "GUI Framework")
        return {
            "id": "desktop_app",
            "name": "Desktop Application",
            "technology": tech,
            "description": f"Aplicación de escritorio con interfaz gráfica",
            "type": "application"
        }
    
    # Mobile Application
    elif project_type == "mobile-app" or any(mobile in all_tech for mobile in ["Swift", "Kotlin", "React Native", "Flutter", "Xamarin"]):
        tech = next((t for t in ["Swift", "Kotlin", "React Native", "Flutter", "Xamarin"] if t in all_tech), "Mobile Framework")
        return {
            "id": "mobile_app",
            "name": "Mobile Application",
            "technology": tech,
            "description": f"Aplicación móvil nativa/híbrida",
            "type": "application"
        }
    
    # Web Application (Full Stack)
    elif any(web in all_tech for web in ["React", "Vue", "Angular", "Django", "Flask", "FastAPI", "Express", "Spring MVC"]):
        # Detectar si tiene frontend Y backend
        has_frontend = len(frontend_tech) > 0
        has_backend = len(backend_tech) > 0
        
        if has_frontend and has_backend:
            tech = f"{', '.join(frontend_tech[:2])} + {', '.join(backend_tech[:2])}"
            return {
                "id": "web_app",
                "name": "Web Application",
                "technology": tech,
                "description": f"Aplicación web con frontend y backend",
                "type": "application"
            }
        elif has_frontend:
            tech = ", ".join(frontend_tech[:2])
            return {
                "id": "spa",
                "name": "Single Page Application",
                "technology": tech,
                "description": f"Frontend web en el navegador",
                "type": "application"
            }
        else:
            # Solo backend
            tech = ", ".join(backend_tech[:2])
            return {
                "id": "api_backend",
                "name": "API Backend",
                "technology": tech,
                "description": f"API REST/GraphQL",
                "type": "application"
            }
    
    # API Backend (REST/GraphQL)
    elif project_type in ["api-backend", "spring-boot", "fastapi", "nodejs"] or any(api in all_tech for api in ["Spring Boot", "FastAPI", "Express", "ASP.NET", "Gin", "Ktor"]):
        tech = next((t for t in ["Spring Boot", "FastAPI", "Express", "ASP.NET Core", "Gin", "Ktor"] if t in all_tech), ", ".join(backend_tech[:2]) if backend_tech else "Backend Framework")
        return {
            "id": "api",
            "name": "API Backend",
            "technology": tech,
            "description": f"API REST para servicios de negocio",
            "type": "application"
        }
    
    # CLI Application (Compiler, Tool)
    elif project_type in ["compiler", "cli-tool"] or component_count < 5:
        tech = ", ".join(backend_tech[:2]) if backend_tech else "Command Line"
        return {
            "id": "cli_app",
            "name": "CLI Application",
            "technology": tech,
            "description": f"Herramienta de línea de comandos",
            "type": "application"
        }
    
    # Generic Application (fallback)
    else:
        tech = ", ".join((backend_tech + frontend_tech)[:2]) if (backend_tech or frontend_tech) else "Application"
        return {
            "id": "app",
            "name": "Application",
            "technology": tech,
            "description": f"Aplicación principal del sistema",
            "type": "application"
        }


def _detect_database_container(technologies, components):
    """Detecta contenedor de base de datos"""
    db_tech = technologies.get("database", [])
    
    if db_tech:
        tech = ", ".join(db_tech[:2])  # Máximo 2 tecnologías
        return {
            "id": "database",
            "name": "Database",
            "technology": tech,
            "description": "Almacena datos persistentes del sistema",
            "type": "database"
        }
    
    # Detectar por archivos comunes
    db_files = [c for c in components if isinstance(c, str) and any(db in c.lower() for db in [".db", ".sqlite", "database", "schema.sql", "migrations"])]
    if db_files:
        return {
            "id": "database",
            "name": "Database",
            "technology": "SQL Database",
            "description": "Almacena datos persistentes del sistema",
            "type": "database"
        }
    
    return None


def _detect_cache_container(technologies, components):
    """Detecta contenedor de cache"""
    cache_tech = [t for t in technologies.get("infrastructure", []) if "redis" in t.lower() or "memcached" in t.lower()]
    
    if cache_tech:
        tech = cache_tech[0]
        return {
            "id": "cache",
            "name": "Cache",
            "technology": tech,
            "description": "Cache en memoria para mejorar rendimiento",
            "type": "infrastructure"
        }
    
    return None


def _detect_message_queue_container(technologies, components):
    """Detecta contenedor de message queue"""
    mq_tech = [t for t in technologies.get("infrastructure", []) if any(mq in t.lower() for mq in ["rabbitmq", "kafka", "activemq", "sqs"])]
    
    if mq_tech:
        tech = mq_tech[0]
        return {
            "id": "message_queue",
            "name": "Message Queue",
            "technology": tech,
            "description": "Cola de mensajes para comunicación asíncrona",
            "type": "infrastructure"
        }
    
    return None


def generate_c1_diagram(analysis):
    """Genera diagrama C1 (Contexto del Sistema) con contexto de negocio inferido"""
    
    project_name = analysis.get("project_name", "Sistema")
    project_type = analysis.get("project_type", "unknown")
    responsibilities = analysis.get("system_responsibilities", [])
    components = analysis.get("components_detected", [])
    business_modules = analysis.get("business_modules", [])
    
    # Detectar usuarios específicos desde los módulos
    detected_users = _detect_users_from_modules(business_modules, components)
    
    # Inferir dominio de negocio desde nombres de entidades
    domain_context = _infer_business_domain(project_name, components, business_modules)
    
    # Detectar sistemas externos reales desde los módulos
    external_systems = _detect_external_systems(business_modules, components)
    
    # Generar descripción específica basada en módulos detectados
    system_description = _generate_system_description(business_modules, responsibilities, domain_context)
    
    # Adaptar según tipo de proyecto
    is_gui_app = project_type == "gui-application"
    is_mobile_app = project_type == "mobile-app"
    is_compiler = project_type == "compiler"
    is_cli_tool = project_type == "cli-tool"
    is_web_framework = project_type == "web-framework"
    
    diagram = f"""---
title: Sistema {project_name} - Diagrama C1 (Contexto)
---
C4Context
    title Diagrama de Contexto del Sistema - {project_name}

"""
    
    # Agregar usuarios detectados
    if detected_users:
        for user in detected_users:
            user_id = user["id"]
            user_name = user["name"]
            user_desc = user["description"]
            diagram += f"""    Person({user_id}, "{user_name}", "{user_desc}")
"""
    else:
        # Usuario genérico si no se detecta ninguno
        default_user = domain_context.get("user_name", "Usuario")
        default_desc = domain_context.get("user_desc", "Interactúa con el sistema")
        diagram += f"""    Person(user, "{default_user}", "{default_desc}")
"""
    
    # Sistema principal con descripción específica
    diagram += f"""
    System(system, "{project_name}", "{system_description}")
"""
    
    # Agregar sistemas externos detectados
    if external_systems.get("has_database", True):
        diagram += """    System_Ext(database, "Base de Datos", "Almacena datos persistentes")
"""
    
    for ext_sys in external_systems.get("systems", []):
        sys_id = ext_sys["id"]
        sys_name = ext_sys["name"]
        sys_desc = ext_sys["description"]
        diagram += f"""    System_Ext({sys_id}, "{sys_name}", "{sys_desc}")
"""
    
    diagram += """
"""
    
    # Relaciones de usuarios con el sistema
    if detected_users:
        for user in detected_users:
            user_id = user["id"]
            action = user.get("action", "Usa")
            if is_gui_app:
                tech = "Desktop Application"
            elif is_mobile_app:
                tech = "Mobile App"
            elif is_compiler:
                tech = "Command Line"
            else:
                tech = "Web Browser/HTTPS"
            diagram += f"""    Rel({user_id}, system, "{action}", "{tech}")
"""
    else:
        # Relación genérica
        if is_gui_app:
            diagram += f"""    Rel(user, system, "Usa", "Desktop Application")
"""
        elif is_mobile_app:
            diagram += f"""    Rel(user, system, "Usa", "Mobile App")
"""
        elif is_compiler or is_cli_tool:
            # CLI tools and compilers use command line (NOT web browsers)
            diagram += f"""    Rel(user, system, "Ejecuta via", "Command Line/Terminal")
"""
        elif is_web_framework or project_type in ["api-backend", "microservice"]:
            # Web frameworks, APIs, and microservices use HTTPS (NOT command line)
            diagram += f"""    Rel(user, system, "Usa", "Web Browser/HTTPS")
"""
        else:
            # Default: assume web-based if not explicitly CLI/compiler
            diagram += f"""    Rel(user, system, "Usa", "Web Browser/HTTPS")
"""
    
    # Relaciones con sistemas externos
    if external_systems.get("has_database", True):
        diagram += """    Rel(system, database, "Lee/Escribe datos", "SQL/JDBC")
"""
    
    for ext_sys in external_systems.get("systems", []):
        sys_id = ext_sys["id"]
        rel_desc = ext_sys["relation"]
        protocol = ext_sys["protocol"]
        diagram += f"""    Rel(system, {sys_id}, "{rel_desc}", "{protocol}")
"""
    
    return diagram


def _infer_business_domain(project_name, components, business_modules=None):
    """
    Infiere el dominio de negocio analizando nombres de componentes y proyecto
    """
    project_lower = project_name.lower()
    component_names = " ".join([c.get("name", "").lower() for c in components])
    if business_modules:
        module_names = " ".join([m.get("keyword", "").lower() for m in business_modules])
        component_names += " " + module_names
    
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


def _detect_users_from_modules(business_modules, components):
    """Detecta tipos de usuarios específicos desde los módulos del proyecto"""
    users = []
    module_keywords = " ".join([m.get("keyword", "").lower() for m in business_modules])
    
    # Detectar diferentes tipos de usuarios
    user_patterns = {
        "admin": ("admin", "Administrator", "Administra el sistema y gestiona configuración"),
        "customer": ("customer", "Customer/Client", "Usa los servicios principales del sistema"),
        "employee": ("employee", "Employee/Staff", "Gestiona operaciones del negocio"),
        "user": ("user", "User", "Usuario final del sistema"),
        "vendor": ("vendor", "Vendor/Supplier", "Proveedor de productos o servicios"),
        "manager": ("manager", "Manager", "Supervisa operaciones y aprueba transacciones"),
    }
    
    detected = set()
    for keyword, (user_id, user_name, user_desc) in user_patterns.items():
        if keyword in module_keywords and keyword not in detected:
            users.append({
                "id": user_id,
                "name": user_name,
                "description": user_desc,
                "action": "Gestiona" if keyword == "admin" else "Usa"
            })
            detected.add(keyword)
    
    return users[:2]  # Máximo 2 usuarios para no saturar el C1


def _detect_external_systems(business_modules, components):
    """Detecta sistemas externos reales desde los módulos"""
    external_systems = {"systems": [], "has_database": True}
    module_keywords = " ".join([m.get("keyword", "").lower() for m in business_modules])
    
    # Patrones de sistemas externos
    external_patterns = {
        "email": {
            "keywords": ["mail", "email", "smtp", "notification"],
            "system": {
                "id": "email_system",
                "name": "Email System",
                "description": "Envía notificaciones por correo electrónico",
                "relation": "Envía emails via",
                "protocol": "SMTP"
            }
        },
        "payment": {
            "keywords": ["payment", "billing", "invoice", "stripe", "paypal"],
            "system": {
                "id": "payment_gateway",
                "name": "Payment Gateway",
                "description": "Procesa pagos y transacciones",
                "relation": "Procesa pagos via",
                "protocol": "HTTPS/REST"
            }
        },
        "storage": {
            "keywords": ["s3", "storage", "blob", "file_storage", "upload"],
            "system": {
                "id": "storage_service",
                "name": "Cloud Storage",
                "description": "Almacena archivos y recursos",
                "relation": "Guarda/Lee archivos via",
                "protocol": "S3 API/HTTPS"
            }
        },
        "cache": {
            "keywords": ["cache", "redis", "memcached"],
            "system": {
                "id": "cache_system",
                "name": "Cache Service",
                "description": "Almacenamiento en caché de datos",
                "relation": "Lee/Escribe cache via",
                "protocol": "Redis Protocol"
            }
        },
        "sms": {
            "keywords": ["sms", "twilio", "message"],
            "system": {
                "id": "sms_service",
                "name": "SMS Service",
                "description": "Envía mensajes SMS",
                "relation": "Envía SMS via",
                "protocol": "REST API"
            }
        },
        "auth": {
            "keywords": ["oauth", "auth0", "okta", "saml", "ldap"],
            "system": {
                "id": "auth_provider",
                "name": "Authentication Provider",
                "description": "Servicio de autenticación externo",
                "relation": "Autentica usuarios via",
                "protocol": "OAuth2/SAML"
            }
        },
    }
    
    # Detectar qué sistemas externos existen
    for pattern_name, pattern_data in external_patterns.items():
        keywords = pattern_data["keywords"]
        if any(kw in module_keywords for kw in keywords):
            external_systems["systems"].append(pattern_data["system"])
    
    return external_systems


def _generate_system_description(business_modules, responsibilities, domain_context):
    """Genera una descripción específica del sistema basada en sus módulos"""
    if not business_modules:
        return domain_context.get("default_description", "Sistema de software")
    
    # Agrupar módulos por categoría
    categories = {
        "gestión": ["user", "customer", "employee", "admin", "account"],
        "transacciones": ["payment", "order", "invoice", "billing", "transaction"],
        "productos": ["product", "inventory", "catalog", "item"],
        "comunicación": ["notification", "email", "message", "sms"],
        "reportes": ["report", "analytics", "dashboard", "stats"],
    }
    
    detected_categories = []
    module_keywords = " ".join([m.get("keyword", "").lower() for m in business_modules[:10]])
    
    for category, keywords in categories.items():
        if any(kw in module_keywords for kw in keywords):
            detected_categories.append(category)
    
    # Generar descripción basada en categorías detectadas
    if detected_categories:
        if "transacciones" in detected_categories and "productos" in detected_categories:
            return "Plataforma para gestión de productos y procesamiento de transacciones"
        elif "gestión" in detected_categories and "transacciones" in detected_categories:
            return "Sistema para gestionar usuarios y procesar transacciones del negocio"
        elif "productos" in detected_categories:
            return "Sistema para gestión de catálogo de productos e inventario"
        elif "gestión" in detected_categories:
            return "Plataforma para gestión de usuarios y operaciones administrativas"
        else:
            return f"Sistema para {detected_categories[0]} del negocio"
    
    # Fallback a responsabilidades o dominio
    if responsibilities:
        return " | ".join(responsibilities[:2])
    
    return domain_context.get("default_description", "Sistema de software")


def generate_c2_diagram(analysis):
    """
    Genera diagrama C2 (Contenedores) siguiendo el modelo C4 CORRECTAMENTE
    Contenedores = Aplicaciones ejecutables (Desktop App, API, Database, etc)
    NO módulos internos ni componentes individuales
    """
    
    project_name = analysis.get("project_name", "Sistema")
    project_type = analysis.get("project_type", "unknown")
    
    # Detectar contenedores reales (aplicaciones ejecutables)
    containers = _detect_containers(analysis)
    
    diagram = f"""---
title: Sistema {project_name} - Diagrama C2 (Contenedores)
---
C4Container
    title Diagrama de Contenedores - {project_name}

    Person(user, "Usuario", "Usuario del sistema")
    
    Container_Boundary(system, "{project_name}") {{
"""
    
    # Agregar contenedores detectados (solo aplicaciones, no DB)
    app_containers = [c for c in containers if c.get("type") == "application"]
    for container in app_containers:
        cont_id = container["id"]
        cont_name = container["name"]
        cont_tech = container["technology"]
        cont_desc = container["description"]
        diagram += f"""        Container({cont_id}, "{cont_name}", "{cont_tech}", "{cont_desc}")
"""
    
    diagram += """    }
    
"""
    
    # Agregar base de datos fuera del boundary (si existe)
    db_container = next((c for c in containers if c.get("type") == "database"), None)
    if db_container:
        db_tech = db_container["technology"]
        db_desc = db_container["description"]
        diagram += f"""    ContainerDb(database, "Database", "{db_tech}", "{db_desc}")
    
"""
    
    # Agregar cache (si existe)
    cache_container = next((c for c in containers if c.get("id") == "cache"), None)
    if cache_container:
        cache_tech = cache_container["technology"]
        diagram += f"""    Container_Ext(cache, "Cache", "{cache_tech}", "Cache en memoria")
    
"""
    
    # Agregar message queue (si existe)
    mq_container = next((c for c in containers if c.get("id") == "message_queue"), None)
    if mq_container:
        mq_tech = mq_container["technology"]
        diagram += f"""    Container_Ext(message_queue, "Message Queue", "{mq_tech}", "Cola de mensajes")
    
"""
    
    # RELACIONES entre contenedores
    # 1. Usuario → Aplicación principal
    if app_containers:
        main_app = app_containers[0]  # Primera aplicación (la principal)
        app_id = main_app["id"]
        
        # Determinar tecnología de interacción según tipo
        if project_type == "gui-application":
            tech = "Desktop Application"
            action = "Usa"
        elif project_type == "mobile-app":
            tech = "Mobile App"
            action = "Usa"
        elif project_type in ["api-backend", "spring-boot", "fastapi", "nodejs"]:
            tech = "HTTPS/REST"
            action = "Hace peticiones a"
        else:
            tech = "HTTPS"
            action = "Usa"
        
        diagram += f"""    Rel(user, {app_id}, "{action}", "{tech}")
"""
    
    # 1.5. Relaciones entre contenedores de aplicación (para proyectos como Odoo)
    if len(app_containers) > 1:
        # Detectar si es Odoo/OpenERP por los IDs de contenedores
        container_ids = [c["id"] for c in app_containers]
        is_odoo = "http_server" in container_ids and "app_core" in container_ids
        
        if is_odoo:
            # HTTP Server → Application Core
            if "http_server" in container_ids and "app_core" in container_ids:
                diagram += f"""    Rel(http_server, app_core, "Invoca lógica de negocio", "Python API")
"""
            # RPC Server → Application Core
            if "rpc_server" in container_ids and "app_core" in container_ids:
                diagram += f"""    Rel(rpc_server, app_core, "Ejecuta operaciones", "RPC")
"""
            # Workers → Application Core
            if "workers" in container_ids and "app_core" in container_ids:
                diagram += f"""    Rel(workers, app_core, "Ejecuta tareas programadas", "Internal API")
"""
    
    # 2. Aplicación → Database (si existe)
    if db_container and app_containers:
        # Conectar todos los contenedores de aplicación a la BD
        for app in app_containers:
            app_id = app["id"]
            # Evitar duplicados para Odoo: solo el core se conecta directamente
            if len(app_containers) > 1:
                # En Odoo solo el Application Core se conecta a BD
                if app_id == "app_core":
                    diagram += f"""    Rel({app_id}, database, "Lee y escribe datos", "SQL/ORM")
"""
            else:
                # Para aplicaciones simples, todas se conectan
                diagram += f"""    Rel({app_id}, database, "Lee y escribe datos", "SQL/JDBC")
"""
    
    # 3. Aplicación → Cache (si existe)
    if cache_container and app_containers:
        main_app_id = app_containers[0]["id"]
        diagram += f"""    Rel({main_app_id}, cache, "Lee/Escribe cache", "TCP/IP")
"""
    
    # 4. Aplicación → Message Queue (si existe)
    if mq_container and app_containers:
        main_app_id = app_containers[0]["id"]
        diagram += f"""    Rel({main_app_id}, message_queue, "Publica/Consume mensajes", "AMQP/Kafka")
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
    """Genera diagrama C3 (Componentes) - Muestra arquitectura interna de LA APLICACIÓN PRINCIPAL"""
    
    project_name = analysis.get("project_name", "Sistema")
    project_type = analysis.get("project_type", "unknown")
    layers = analysis.get("architectural_layers", {})
    patterns = analysis.get("architecture_patterns", [])
    technologies = analysis.get("technologies", {})
    components = analysis.get("components_detected", [])
    
    # Detectar contenedor principal usando la misma lógica que C2
    containers = _detect_containers(analysis)
    main_container = next((c for c in containers if c["type"] == "application"), None)
    
    if not main_container:
        # Fallback si no detecta contenedor
        main_container = {
            "name": "Aplicación Principal",
            "technology": ", ".join(technologies.get("backend", ["Backend"]) + technologies.get("frontend", [])),
            "description": "Sistema principal"
        }
    
    container_name = main_container["name"]
    container_tech = main_container["technology"]
    
    # Detectar patrón principal
    main_pattern = "Layered Architecture"
    if patterns:
        main_pattern = patterns[0].get("name", "Layered Architecture")
    
    diagram = f"""---
title: Sistema {project_name} - Diagrama C3 (Componentes)
---
C4Component
    title Diagrama de Componentes - {project_name} ({main_pattern})
    
    Container_Boundary(container, "{container_name}") {{
"""
    
    has_components = False
    
    # Límite simplificado: 5-6 componentes por capa máximo
    total_files = analysis.get("total_files", 0)
    comp_limit_per_layer = 6 if total_files > 100 else 5
    
    # CAPA 1: Presentation/UI Layer (Controllers, Windows, Screens)
    presentation_comps = []
    if layers.get("presentation", {}).get("count", 0) > 0:
        has_components = True
        all_pres = layers["presentation"]["components"]
        
        # Filtrar tests y duplicados
        filtered = [c for c in all_pres if "test" not in c.lower()]
        seen = set()
        for c in filtered:
            if c not in seen:
                presentation_comps.append(c)
                seen.add(c)
        
        # Ordenar por importancia si está disponible
        if "important_components" in analysis and analysis["important_components"]:
            important_names = [comp["component"] for comp in analysis["important_components"]]
            presentation_comps.sort(key=lambda x: important_names.index(x) if x in important_names else 999)
        
        presentation_comps = presentation_comps[:comp_limit_per_layer]
        
        # Detectar tecnología UI
        is_gui = "PyQt" in container_tech or "Tkinter" in container_tech or "Qt" in container_tech
        is_mobile = "Swift" in container_tech or "Kotlin" in container_tech or "Flutter" in container_tech
        
        if is_gui:
            ui_tech = "PyQt5" if "PyQt" in container_tech else "Tkinter" if "Tkinter" in container_tech else "Qt"
            diagram += f"""        Component(ui_layer, "Interfaz Gráfica", "{ui_tech}", "Ventanas y widgets de la aplicación")
"""
            for i, comp in enumerate(presentation_comps[:4]):  # Max 4 ejemplos
                comp_name = comp.replace(".py", "").replace(".ui", "")
                safe_name = _make_safe_mermaid_id(comp)
                diagram += f"""        Component({safe_name}, "{comp_name}", "Window/Dialog", "Componente visual")
"""
        elif is_mobile:
            diagram += """        Component(screens, "Pantallas", "Mobile", "Pantallas de la aplicación")
"""
            for i, comp in enumerate(presentation_comps[:4]):
                comp_name = comp.replace(".swift", "").replace(".kt", "").replace(".dart", "")
                safe_name = _make_safe_mermaid_id(comp)
                diagram += f"""        Component({safe_name}, "{comp_name}", "Screen", "Pantalla")
"""
        else:
            # Web API - Controllers
            controller_tech = "REST Controller"
            if "Spring" in container_tech:
                controller_tech = "Spring MVC"
            elif "Django" in container_tech:
                controller_tech = "Django View"
            elif "FastAPI" in container_tech:
                controller_tech = "FastAPI"
            elif "Express" in container_tech:
                controller_tech = "Express"
            
            diagram += f"""        Component(controllers, "Controllers", "{controller_tech}", "Endpoints HTTP")
"""
            for i, comp in enumerate(presentation_comps[:4]):
                comp_name = comp.replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "")
                safe_name = _make_safe_mermaid_id(comp)
                
                # Buscar el tipo real del componente desde el análisis
                comp_type = "Endpoint"  # Default
                comp_desc = "API REST"
                for component in components:
                    if component.get("name") == comp:
                        detected_type = component.get("type", "").lower()
                        if detected_type == "utility":
                            comp_type = "Utility"
                            comp_desc = "Utilidad/Configuración"
                        elif detected_type == "controller":
                            comp_type = "Controller"
                            comp_desc = "Controlador HTTP"
                        elif detected_type == "model":
                            comp_type = "Model"
                            comp_desc = "Modelo del dominio"
                        break
                
                diagram += f"""        Component({safe_name}, "{comp_name}", "{comp_type}", "{comp_desc}")
"""
    
    # CAPA 2: Application/Business Logic Layer
    application_comps = []
    if layers.get("application", {}).get("count", 0) > 0:
        has_components = True
        all_app = layers["application"]["components"]
        
        # Filtrar tests, config, main
        exclude = ["test", "main", "config", "application"]
        filtered = [c for c in all_app if not any(e in c.lower() for e in exclude)]
        seen = set()
        for c in filtered:
            if c not in seen:
                application_comps.append(c)
                seen.add(c)
        
        application_comps = application_comps[:comp_limit_per_layer]
        
        diagram += """
        Component(services, "Services", "Business Logic", "Lógica de negocio")
"""
        for i, comp in enumerate(application_comps[:3]):  # Max 3 ejemplos
            comp_name = comp.replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "")
            safe_name = _make_safe_mermaid_id(comp)
            
            # Buscar tipo real del componente
            comp_type = "Service"  # Default
            comp_desc = "Lógica de negocio"
            for component in components:
                if component.get("name") == comp:
                    detected_type = component.get("type", "").lower()
                    if detected_type == "utility":
                        comp_type = "Utility"
                        comp_desc = "Utilidad/Configuración"
                    elif detected_type == "repository":
                        comp_type = "Repository"
                        comp_desc = "Acceso a datos"
                    break
            
            diagram += f"""        Component({safe_name}, "{comp_name}", "{comp_type}", "{comp_desc}")
"""
    
    # CAPA 3: Domain Layer (Entities/Models)
    domain_comps = []
    if layers.get("domain", {}).get("count", 0) > 0:
        has_components = True
        all_domain = layers["domain"]["components"]
        
        filtered = list(set(all_domain))[:comp_limit_per_layer]
        domain_comps = filtered
        
        diagram += """
        Component(models, "Models", "Domain", "Entidades del dominio")
"""
        for i, comp in enumerate(domain_comps[:3]):
            comp_name = comp.replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "")
            safe_name = _make_safe_mermaid_id(comp)
            
            # Buscar tipo real del componente
            comp_type = "Entity"  # Default
            comp_desc = "Entidad"
            pattern_info = ""
            for component in components:
                if component.get("name") == comp:
                    detected_type = component.get("type", "").lower()
                    pattern = component.get("pattern")
                    if detected_type == "model":
                        comp_type = "Model"
                        if pattern == "Active Record":
                            comp_desc = "Modelo (Active Record)"
                            pattern_info = " | Patrón: Active Record"
                        else:
                            comp_desc = "Modelo del dominio"
                    elif detected_type == "utility":
                        comp_type = "Utility"
                        comp_desc = "Utilidad"
                    break
            
            diagram += f"""        Component({safe_name}, "{comp_name}", "{comp_type}", "{comp_desc}{pattern_info}")
"""
    
    # CAPA 4: Infrastructure/Data Access Layer
    infra_comps = []
    if layers.get("infrastructure", {}).get("count", 0) > 0:
        has_components = True
        all_infra = layers["infrastructure"]["components"]
        
        filtered = list(set(all_infra))[:comp_limit_per_layer]
        infra_comps = filtered
        
        diagram += """
        Component(repositories, "Repositories", "Data Access", "Acceso a datos")
"""
        for i, comp in enumerate(infra_comps[:3]):
            comp_name = comp.replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "")
            safe_name = _make_safe_mermaid_id(comp)
            
            # Buscar tipo real del componente
            comp_type = "Repository"  # Default
            comp_desc = "Repositorio"
            for component in components:
                if component.get("name") == comp:
                    detected_type = component.get("type", "").lower()
                    if detected_type == "utility":
                        comp_type = "Utility"
                        comp_desc = "Utilidad"
                    elif detected_type == "service":
                        comp_type = "Service"
                        comp_desc = "Servicio"
                    break
            
            diagram += f"""        Component({safe_name}, "{comp_name}", "{comp_type}", "{comp_desc}")
"""
    
    # Fallback si no hay capas detectadas
    if not has_components and len(components) > 0:
        diagram += """
        Component(core, "Componentes Principales", "Application", "Módulos del sistema")
"""
        for comp in components[:4]:
            comp_name = comp.get("name", "component").replace(".java", "").replace(".py", "").replace(".js", "").replace(".ts", "")
            safe_name = _make_safe_mermaid_id(comp_name)
            
            # Usar el tipo real del componente detectado
            comp_type = comp.get("type", "component").capitalize()
            comp_desc = "Módulo"
            pattern = comp.get("pattern")
            
            # Descripciones específicas según tipo
            if comp_type.lower() == "utility":
                comp_desc = "Utilidad/Configuración"
            elif comp_type.lower() == "controller":
                comp_desc = "Controlador HTTP"
            elif comp_type.lower() == "service":
                comp_desc = "Servicio de negocio"
            elif comp_type.lower() == "repository":
                comp_desc = "Acceso a datos"
            elif comp_type.lower() == "model":
                if pattern == "Active Record":
                    comp_desc = "Modelo (Active Record)"
                else:
                    comp_desc = "Modelo del dominio"
            elif comp_type.lower() == "view":
                comp_desc = "Interfaz gráfica"
            
            diagram += f"""        Component({safe_name}, "{comp_name}", "{comp_type}", "{comp_desc}")
"""
    
    diagram += """    }
    
    ContainerDb(database, "Database", "SQL", "Persistencia de datos")
    
"""
    
    # Relaciones simplificadas - FLUJO ARQUITECTÓNICO ESTÁNDAR
    pres_exists = len(presentation_comps) > 0
    app_exists = len(application_comps) > 0
    domain_exists = len(domain_comps) > 0
    infra_exists = len(infra_comps) > 0
    
    # Determinar componente de entrada
    is_gui = "PyQt" in container_tech or "Tkinter" in container_tech
    is_mobile = "Swift" in container_tech or "Kotlin" in container_tech
    entry_point = "ui_layer" if is_gui else ("screens" if is_mobile else "controllers")
    
    # Flujo básico según arquitectura detectada
    if pres_exists and app_exists:
        diagram += f"""    Rel({entry_point}, services, "Invoca")
"""
    
    if app_exists and domain_exists:
        diagram += """    Rel(services, models, "Usa")
"""
    
    if app_exists and infra_exists:
        diagram += """    Rel(services, repositories, "Consulta")
"""
    
    if infra_exists:
        diagram += """    Rel(repositories, database, "Lee/Escribe", "SQL")
"""
    elif pres_exists and not app_exists:
        # Arquitectura simple sin capas intermedias
        diagram += f"""    Rel({entry_point}, database, "Lee/Escribe", "SQL")
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

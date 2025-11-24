"""
Frontend Web con Streamlit para el Analizador de Arquitectura C4
Interfaz simple para subir proyectos ZIP y visualizar diagramas
Incluye sistema de autenticación con login y registro
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from core.analyzer import analyze_project
from core.diagram_generator_deterministic import (
    generate_c1_diagram,
    generate_c2_diagram,
    generate_c3_diagram
)
from core.database import init_database, get_user, create_user, verify_password

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Arquitectura C4",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SISTEMA DE AUTENTICACIÓN (SQLite local / PostgreSQL producción)
# ============================================================================
# Las funciones están importadas desde core.database

def register_user():
    """Formulario de registro de nuevos usuarios"""
    st.markdown('<div class="main-header"><h1>📝 Registro de Usuario</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("register_form"):
            st.markdown("### Crear nueva cuenta")
            
            new_username = st.text_input("👤 Usuario", placeholder="Ej: juan_perez")
            new_name = st.text_input("📛 Nombre completo", placeholder="Ej: Juan Pérez")
            new_email = st.text_input("📧 Email", placeholder="ejemplo@correo.com")
            new_password = st.text_input("🔒 Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            new_password_repeat = st.text_input("🔒 Confirmar contraseña", type="password")
            
            submit_button = st.form_submit_button("Crear cuenta", use_container_width=True)
            
            if submit_button:
                # Validaciones
                if not all([new_username, new_name, new_email, new_password]):
                    st.error("❌ Todos los campos son obligatorios")
                elif new_password != new_password_repeat:
                    st.error("❌ Las contraseñas no coinciden")
                elif len(new_password) < 6:
                    st.error("❌ La contraseña debe tener al menos 6 caracteres")
                elif '@' not in new_email:
                    st.error("❌ Email inválido")
                else:
                    # Intentar crear usuario
                    if create_user(new_username, new_password, new_name, new_email):
                        st.success("✅ ¡Cuenta creada exitosamente!")
                        st.info("👉 Ahora puedes iniciar sesión con tus credenciales")
                        st.balloons()
                        
                        # Marcar que el registro fue exitoso
                        st.session_state['register_success'] = True
                    else:
                        st.error("❌ Este nombre de usuario ya existe")
        
        # Botón fuera del formulario
        st.markdown("---")
        
        if st.button("⬅️ Volver al Login", use_container_width=True):
            st.session_state['show_register'] = False
            st.session_state['register_success'] = False
            st.rerun()
        
        # Si el registro fue exitoso, mostrar botón para ir al login
        if st.session_state.get('register_success', False):
            if st.button("✅ Ir al Login", use_container_width=True, type="primary"):
                st.session_state['show_register'] = False
                st.session_state['register_success'] = False
                st.rerun()

def show_login_page():
    """Página de login personalizada"""
    st.markdown('<div class="main-header"><h1>🏗️ Analizador de Arquitectura C4</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Iniciar Sesión")
        
        with st.form("login_form"):
            username_input = st.text_input("👤 Usuario")
            password_input = st.text_input("🔒 Contraseña", type="password")
            login_button = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit_button:
                user = get_user(username_input)
                
                if user and verify_password(username_input, password_input):
                    st.session_state['authentication_status'] = True
                    st.session_state['name'] = user['name']
                    st.session_state['username'] = user['username']
                    st.success('✅ ¡Inicio de sesión exitoso!')
                    st.rerun()
                else:
                    st.error('❌ Usuario o contraseña incorrectos')
        
        st.info("📝 **Usuario demo:** admin / admin123")
        st.markdown("---")
        
        if st.button("📝 ¿No tienes cuenta? Regístrate aquí", use_container_width=True):
            st.session_state['show_register'] = True
            st.rerun()

# Estilo personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .diagram-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FLUJO PRINCIPAL CON AUTENTICACIÓN
# ============================================================================

# Inicializar base de datos
init_database()

# Inicializar estado de autenticación
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False
    st.session_state['name'] = None
    st.session_state['username'] = None

# Verificar si debe mostrar registro
if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False

# Mostrar página de registro
if st.session_state['show_register']:
    register_user()
    st.stop()

# Si no está autenticado, mostrar login
if not st.session_state['authentication_status']:
    show_login_page()
    st.stop()

# Obtener datos del usuario autenticado
name = st.session_state['name']
username = st.session_state['username']

# ============================================================================
# APLICACIÓN PRINCIPAL (solo si está autenticado)
# ============================================================================

# Header con botón de logout
col_header, col_logout = st.columns([5, 1])

with col_header:
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ Analizador de Arquitectura C4</h1>
        <p>Analiza cualquier proyecto y genera diagramas C4 automáticamente</p>
    </div>
    """, unsafe_allow_html=True)

with col_logout:
    st.write("")
    st.write("")
    st.markdown(f"**👤 {name}**")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state['authentication_status'] = False
        st.session_state['name'] = None
        st.session_state['username'] = None
        st.rerun()

# Sidebar
with st.sidebar:
    st.header("ℹ️ Información")
    st.markdown(f"**Usuario:** {name}")
    st.markdown(f"**Username:** {username}")
    st.markdown("---")
    st.markdown("""
    ### ¿Qué hace esta herramienta?
    
    1. **Sube** tu proyecto en formato ZIP
    2. **Analiza** la arquitectura automáticamente
    3. **Genera** diagramas C4 (C1, C2, C3)
    4. **Visualiza** los resultados
    
    ### Lenguajes soportados:
    - Python, JavaScript, TypeScript
    - Java, C#, Go, Rust
    - PHP, Ruby, Kotlin, Swift
    
    ### Tipos detectados:
    - Web Framework
    - API Backend
    - CLI Tool
    - Library
    - Mobile App
    - Microservice
    """)
    
    st.divider()
    
    st.markdown("""
    ### 📊 Modelo C4
    
    - **C1**: System Context
    - **C2**: Container Diagram
    - **C3**: Component Diagram
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📦 Subir Proyecto")
    
    uploaded_file = st.file_uploader(
        "Selecciona un archivo ZIP de tu proyecto",
        type=['zip'],
        help="Descarga tu proyecto de GitHub como ZIP y súbelo aquí"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Archivo cargado: {uploaded_file.name}")
        st.info(f"📏 Tamaño: {uploaded_file.size / 1024 / 1024:.2f} MB")
        
        if st.button("🚀 Analizar Proyecto", type="primary", use_container_width=True):
            with st.spinner("Analizando proyecto... Esto puede tomar unos segundos..."):
                try:
                    # Guardar archivo temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Analizar proyecto
                    analysis = analyze_project(tmp_path)
                    
                    # Limpiar archivo temporal
                    os.unlink(tmp_path)
                    
                    if analysis.get("error"):
                        st.error(f"❌ Error: {analysis['error']}")
                    else:
                        # Guardar en session state
                        st.session_state['analysis'] = analysis
                        st.session_state['project_name'] = uploaded_file.name.replace('.zip', '')
                        st.success("✅ Análisis completado!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Error durante el análisis: {str(e)}")

with col2:
    st.header("📊 Información del Proyecto")
    
    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        
        # Métricas
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric(
                "Tipo de Proyecto",
                analysis.get('project_type', 'unknown')
            )
        
        with col_b:
            st.metric(
                "Archivos",
                analysis.get('total_files', 0)
            )
        
        with col_c:
            st.metric(
                "Componentes",
                len(analysis.get('components_detected', []))
            )
        
        # Información adicional
        st.markdown("---")
        
        containers = len(analysis.get('containers_detected', []))
        relations = len(analysis.get('relations_detected', []))
        
        col_d, col_e = st.columns(2)
        with col_d:
            st.metric("Contenedores", containers)
        with col_e:
            st.metric("Relaciones", relations)
        
    else:
        st.info("👆 Sube un proyecto ZIP para comenzar el análisis")

# Tabs para diagramas
if 'analysis' in st.session_state:
    st.header("📐 Diagramas C4 Generados")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 C1 - System Context", "🏗️ C2 - Container", "⚙️ C3 - Component", "📄 Análisis JSON"])
    
    analysis = st.session_state['analysis']
    
    with tab1:
        st.subheader("Diagrama C1 - System Context")
        st.caption("Vista general del sistema y sus actores externos")
        
        try:
            c1_code = generate_c1_diagram(analysis)
            
            # Limpiar código (quitar frontmatter que causa problemas)
            c1_lines = c1_code.split('\n')
            c1_clean = '\n'.join([line for line in c1_lines if not line.strip().startswith('---') and not line.strip().startswith('title:')])
            
            # Renderizar con HTML + Mermaid.js
            mermaid_html = f"""
            <html>
            <body>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <script>mermaid.initialize({{startOnLoad:true}});</script>
            <div class="mermaid">
{c1_clean}
            </div>
            </body>
            </html>
            """
            components.html(mermaid_html, height=500, scrolling=True)
            
            with st.expander("📄 Ver código Mermaid"):
                st.code(c1_code, language="mermaid")
            
            # Botón de descarga
            st.download_button(
                label="⬇️ Descargar C1.mmd",
                data=c1_code,
                file_name=f"{st.session_state['project_name']}_c1.mmd",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error generando C1: {str(e)}")
    
    with tab2:
        st.subheader("Diagrama C2 - Container")
        st.caption("Contenedores y sus relaciones dentro del sistema")
        
        try:
            c2_code = generate_c2_diagram(analysis)
            
            # Limpiar código (quitar frontmatter)
            c2_lines = c2_code.split('\n')
            c2_clean = '\n'.join([line for line in c2_lines if not line.strip().startswith('---') and not line.strip().startswith('title:')])
            
            # Renderizar con HTML + Mermaid.js
            mermaid_html = f"""
            <html>
            <body>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <script>mermaid.initialize({{startOnLoad:true}});</script>
            <div class="mermaid">
{c2_clean}
            </div>
            </body>
            </html>
            """
            components.html(mermaid_html, height=600, scrolling=True)
            
            with st.expander("📄 Ver código Mermaid"):
                st.code(c2_code, language="mermaid")
            
            # Botón de descarga
            st.download_button(
                label="⬇️ Descargar C2.mmd",
                data=c2_code,
                file_name=f"{st.session_state['project_name']}_c2.mmd",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error generando C2: {str(e)}")
    
    with tab3:
        st.subheader("Diagrama C3 - Component")
        st.caption("Componentes internos y su arquitectura")
        
        try:
            c3_code = generate_c3_diagram(analysis)
            
            # Limpiar código (quitar frontmatter)
            c3_lines = c3_code.split('\n')
            c3_clean = '\n'.join([line for line in c3_lines if not line.strip().startswith('---') and not line.strip().startswith('title:')])
            
            # Renderizar con HTML + Mermaid.js
            mermaid_html = f"""
            <html>
            <body>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <script>mermaid.initialize({{startOnLoad:true}});</script>
            <div class="mermaid">
{c3_clean}
            </div>
            </body>
            </html>
            """
            components.html(mermaid_html, height=700, scrolling=True)
            
            with st.expander("📄 Ver código Mermaid"):
                st.code(c3_code, language="mermaid")
            
            # Botón de descarga
            st.download_button(
                label="⬇️ Descargar C3.mmd",
                data=c3_code,
                file_name=f"{st.session_state['project_name']}_c3.mmd",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error generando C3: {str(e)}")
    
    with tab4:
        st.subheader("Análisis Completo (JSON)")
        st.caption("Datos detallados del análisis estático")
        
        # Mostrar JSON
        st.json(analysis, expanded=False)
        
        # Botón de descarga
        json_str = json.dumps(analysis, indent=2, ensure_ascii=False, default=str)
        st.download_button(
            label="⬇️ Descargar analysis.json",
            data=json_str,
            file_name=f"{st.session_state['project_name']}_analysis.json",
            mime="application/json"
        )
    
    # Botón para limpiar y empezar de nuevo
    st.divider()
    if st.button("🔄 Analizar otro proyecto", use_container_width=True):
        del st.session_state['analysis']
        del st.session_state['project_name']
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🏗️ Analizador de Arquitectura C4 | Generador Determinístico (sin IA)</p>
    <p>Soporta 11+ lenguajes | Detecta 7+ tipos de proyectos | Genera diagramas Mermaid</p>
</div>
""", unsafe_allow_html=True)

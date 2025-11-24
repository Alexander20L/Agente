# 🔐 Guía del Sistema de Autenticación

## 📋 ¿Qué se agregó?

Se implementó un sistema completo de **login y registro** para el Analizador de Arquitectura C4 usando `streamlit-authenticator`.

## 🎯 Características

### ✅ Login (Inicio de Sesión)
- Autenticación segura con usuario y contraseña
- Contraseñas hasheadas (no se guardan en texto plano)
- Sesión persistente con cookies (30 días)
- Mensajes de error claros
- Usuario demo: `admin` / `admin123`

### ✅ Registro de Usuarios
- Formulario de registro completo
- Validaciones:
  - Todos los campos obligatorios
  - Usuario único
  - Email válido
  - Contraseña mínimo 6 caracteres
  - Confirmación de contraseña
- Contraseñas hasheadas automáticamente
- Confirmación visual con globos 🎈

### ✅ Gestión de Sesión
- Botón "Cerrar Sesión" en la esquina superior
- Muestra nombre de usuario en sidebar
- Sesión persistente entre recargas

## 🗂️ Archivos Creados

### `config_users.yaml`
Archivo automático que almacena usuarios registrados:
```yaml
credentials:
  usernames:
    admin:
      email: admin@example.com
      name: Administrador
      password: $2b$12$... (hash seguro)
    juan_perez:
      email: juan@example.com
      name: Juan Pérez
      password: $2b$12$...
cookie:
  expiry_days: 30
  key: random_signature_key_12345
  name: c4_analyzer_cookie
```

**⚠️ IMPORTANTE**: Agrega `config_users.yaml` a `.gitignore` para no subir usuarios a GitHub.

## 🚀 Cómo Usar

### Para Estudiantes/Usuarios:
1. **Primera vez**:
   - Abrir la app
   - Click en "¿No tienes cuenta? Regístrate aquí"
   - Llenar formulario de registro
   - Click en "Crear cuenta"
   - Volver al login e iniciar sesión

2. **Usuarios existentes**:
   - Ingresar usuario y contraseña
   - Click en "Login"
   - Usar la aplicación normalmente
   - Click en "Cerrar Sesión" cuando termine

### Para el Profesor (Admin):
- Usuario: `admin`
- Contraseña: `admin123`

## 🔧 Modificaciones Realizadas

### 1. `requirements.txt`
```diff
+ streamlit-authenticator>=0.2.3
```

### 2. `app.py`
- ✅ Importaciones de autenticación
- ✅ Función `load_users()` - Carga/crea archivo de usuarios
- ✅ Función `save_users()` - Guarda nuevos usuarios
- ✅ Función `register_user()` - Formulario de registro completo
- ✅ Función `show_login_page()` - Página de login personalizada
- ✅ Flujo principal con verificación de autenticación
- ✅ Integración con la app existente

### 3. `.gitignore` (recomendado)
```diff
+ config_users.yaml
```

## 🎨 Interfaz

### Página de Login:
```
╔══════════════════════════════════════════╗
║   🏗️ Analizador de Arquitectura C4      ║
║   Genera diagramas C4 automáticamente    ║
╚══════════════════════════════════════════╝

    🔐 Iniciar Sesión
    
    👤 Usuario:    [___________]
    🔒 Contraseña: [___________]
    
    [    Login    ]
    
    📝 Usuario demo: admin / admin123
    ─────────────────────────────
    [ ¿No tienes cuenta? Regístrate aquí ]
```

### Página de Registro:
```
╔══════════════════════════════════════════╗
║   📝 Registro de Usuario                 ║
╚══════════════════════════════════════════╝

    Crear nueva cuenta
    
    👤 Usuario:           [___________]
    📋 Nombre completo:   [___________]
    📧 Email:             [___________]
    🔒 Contraseña:        [___________]
    🔒 Confirmar:         [___________]
    
    [    Crear cuenta    ]
    
    ─────────────────────────────
    [    ⬅️ Volver al Login    ]
```

### App Principal (autenticado):
```
╔══════════════════════════════════════════╗
║   🏗️ Analizador de Arquitectura C4      ║  👤 Juan Pérez
║   Analiza cualquier proyecto...          ║  [Cerrar Sesión]
╚══════════════════════════════════════════╝

Sidebar:
┌─────────────────────┐
│ ℹ️ Información      │
│ Usuario: Juan Pérez │
│ Username: juan      │
│─────────────────────│
│ (resto de sidebar)  │
└─────────────────────┘
```

## 🔒 Seguridad

### Implementado:
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Cookies firmadas para sesión
- ✅ Validación de inputs en registro
- ✅ Mensajes de error sin información sensible
- ✅ No se muestran contraseñas en ningún momento

### Recomendaciones Adicionales:
1. **Cambiar la secret key** en `config_users.yaml`:
   ```python
   'key': 'tu_clave_secreta_super_segura_aqui_12345'
   ```

2. **Cambiar contraseña del admin**:
   - Registrar nuevo usuario admin2
   - Editar `config_users.yaml` manualmente
   - Eliminar usuario admin antiguo

3. **Backup de usuarios**:
   ```bash
   cp config_users.yaml config_users.backup.yaml
   ```

## 📊 Flujo de la Aplicación

```
┌─────────────┐
│   Inicio    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐      No     ┌──────────────┐
│ ¿Autenticado?   │────────────>│ Mostrar      │
└─────────────────┘              │ Login        │
       │ Sí                      └──────┬───────┘
       │                                │
       │                         ┌──────▼───────┐
       │                         │ ¿Registrarse?│
       │                         └──────┬───────┘
       │                                │ Sí
       │                         ┌──────▼───────┐
       │                         │ Formulario   │
       │                         │ Registro     │
       │                         └──────┬───────┘
       │                                │
       │                         ┌──────▼───────┐
       │                         │ Guardar      │
       │                         │ Usuario      │
       │                         └──────┬───────┘
       │                                │
       │<───────────────────────────────┘
       │
       ▼
┌─────────────────┐
│ App Principal   │
│ (Analizar ZIP)  │
└─────────────────┘
```

## 🧪 Pruebas

### Test Manual:
1. **Registro**:
   ```bash
   streamlit run app.py
   ```
   - Click en "Regístrate aquí"
   - Crear usuario: `test_user` / `test@example.com` / `test123`
   - Verificar mensaje de éxito
   - Verificar que aparece en `config_users.yaml`

2. **Login**:
   - Ingresar `test_user` / `test123`
   - Verificar que entra a la app principal
   - Verificar nombre en sidebar
   - Subir ZIP y analizar (funcionalidad normal)

3. **Logout**:
   - Click en "Cerrar Sesión"
   - Verificar que vuelve al login
   - Verificar que no puede acceder sin autenticar

4. **Validaciones**:
   - Usuario duplicado → Error
   - Contraseñas no coinciden → Error
   - Campos vacíos → Error
   - Email inválido → Error

## 🎓 Para el Profesor

Este sistema permite:
- ✅ Control de acceso a la herramienta
- ✅ Registro de usuarios automático
- ✅ Contraseñas seguras (hasheadas)
- ✅ Gestión simple de usuarios (archivo YAML)
- ✅ Interfaz profesional y limpia
- ✅ Fácil de demostrar

### Demostración sugerida:
1. Mostrar página de login
2. Hacer registro de usuario en vivo
3. Iniciar sesión con el nuevo usuario
4. Subir proyecto ZIP y analizar
5. Cerrar sesión

## 🔄 Extensiones Futuras (Opcional)

Si el profesor pide más funcionalidades:
- 🔐 Recuperación de contraseña por email
- 👥 Roles de usuario (admin, user, viewer)
- 📊 Historial de análisis por usuario
- 🗄️ Base de datos (SQLite/PostgreSQL) en vez de YAML
- 🔑 Autenticación con Google/GitHub (OAuth)
- 📧 Verificación de email al registrarse
- 🔒 Política de contraseñas (mayúsculas, números, símbolos)
- ⏱️ Bloqueo después de N intentos fallidos

## ✅ Checklist de Entrega

- [x] Login funcional
- [x] Registro funcional
- [x] Validaciones completas
- [x] Contraseñas seguras (hasheadas)
- [x] Sesión persistente (cookies)
- [x] Logout funcional
- [x] Usuario demo (admin/admin123)
- [x] Integración con app existente
- [x] Interfaz profesional
- [x] Documentación completa

¡Todo listo para presentar al profesor! 🎉

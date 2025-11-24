# 🗄️ Configuración de Base de Datos en la Nube

## ✅ Sistema Actual

El proyecto ahora soporta **dos modos**:

1. **Desarrollo Local:** SQLite (`users.db`)
2. **Producción (Streamlit Cloud):** PostgreSQL (Supabase)

---

## 🚀 Paso a Paso: Configurar Supabase

### 1️⃣ Crear Cuenta en Supabase

1. Ve a: https://supabase.com
2. Click en **"Start your project"**
3. Inicia sesión con GitHub
4. Click en **"New project"**

### 2️⃣ Crear el Proyecto

- **Name:** `agente-c4` (o el nombre que prefieras)
- **Database Password:** `[genera una contraseña segura]` (guárdala!)
- **Region:** Selecciona el más cercano (ej: South America)
- **Pricing Plan:** Free tier (suficiente para testing)
- Click en **"Create new project"**

⏱️ Espera 1-2 minutos mientras se crea

### 3️⃣ Obtener Connection String

1. En el panel de Supabase, ve a **Settings** (⚙️)
2. Click en **Database**
3. Scroll hasta **"Connection string"**
4. Selecciona **"URI"**
5. Copia el string completo, se ve así:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
6. **IMPORTANTE:** Reemplaza `[YOUR-PASSWORD]` con la contraseña que usaste al crear el proyecto

### 4️⃣ Configurar en Streamlit Cloud

1. Ve a: https://share.streamlit.io/
2. Click en tu app desplegada
3. Click en **"Settings"** (⚙️)
4. Click en **"Secrets"**
5. Agrega esto:

```toml
DATABASE_URL = "postgresql://postgres:TU_PASSWORD@db.xxxxx.supabase.co:5432/postgres"
```

6. Click en **"Save"**
7. La app se redespliegará automáticamente

### 5️⃣ Verificar que Funciona

1. Ve a tu app: https://agente-c4.streamlit.app
2. Registra un nuevo usuario
3. Ve a Supabase → **Table Editor** → Tabla `users`
4. ¡Deberías ver el nuevo usuario registrado!

---

## 🔍 Ver Usuarios en Supabase

### Opción 1: Dashboard Web
1. Ve a Supabase
2. Click en **"Table Editor"** (🗂️)
3. Selecciona la tabla `users`
4. Verás todos los usuarios registrados en tiempo real

### Opción 2: SQL Editor
1. Click en **"SQL Editor"** (📊)
2. Ejecuta:
   ```sql
   SELECT * FROM users;
   ```

---

## 📊 Ventajas de Supabase

✅ **Gratis hasta 500MB** y 2GB de transferencia  
✅ **Persistencia real** - los datos no se pierden  
✅ **Backups automáticos**  
✅ **Dashboard visual** para ver/editar usuarios  
✅ **API REST automática** (si la necesitas después)  
✅ **Compatible con PostgreSQL** (estándar de la industria)  

---

## 🧪 Testing

### Local (SQLite):
```bash
python app.py
# o
streamlit run app.py
```
Usa tu `users.db` local

### Producción (PostgreSQL):
```bash
# Configura la variable de entorno
set DATABASE_URL=postgresql://postgres:...

streamlit run app.py
```
Se conectará a Supabase

---

## ⚙️ Archivos Modificados

1. **requirements.txt** - Agregado `psycopg2-binary`
2. **core/database.py** - Nuevo módulo unificado
3. **app.py** - Actualizado para usar `core.database`

---

## 🔐 Seguridad

- ❌ **NO** subas el `DATABASE_URL` a GitHub
- ✅ **SÍ** usa Streamlit Secrets para producción
- ✅ Las contraseñas siguen hasheadas con bcrypt
- ✅ La base de datos local (`users.db`) está en `.gitignore`

---

## 🆘 Troubleshooting

### Error: "could not connect to server"
- Verifica que el `DATABASE_URL` sea correcto
- Asegúrate de haber reemplazado `[YOUR-PASSWORD]`

### Error: "relation 'users' does not exist"
- La tabla se crea automáticamente en el primer uso
- Si no, ejecuta en Supabase SQL Editor:
  ```sql
  CREATE TABLE users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(100) UNIQUE NOT NULL,
      password VARCHAR(100) NOT NULL,
      name VARCHAR(200) NOT NULL,
      email VARCHAR(200) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

### Los usuarios no aparecen
- Verifica que estés usando el `DATABASE_URL` correcto
- Revisa los logs de Streamlit Cloud

---

**¿Listo para configurar? Sigue los pasos y cualquier duda me avisas! 🚀**

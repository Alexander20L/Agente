# 🚀 Guía de Despliegue - Analizador C4

## Opciones de Despliegue

### 1️⃣ **Streamlit Community Cloud** (Recomendado - GRATIS)

#### Requisitos
- ✅ Cuenta GitHub
- ✅ Repositorio público
- ✅ Cuenta Streamlit (usar GitHub login)

#### Pasos
1. **Subir código a GitHub**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
   git push -u origin main
   ```

2. **Desplegar en Streamlit Cloud**
   - Ir a: https://share.streamlit.io
   - Click en "New app"
   - Seleccionar tu repositorio
   - Branch: `main`
   - Main file: `app.py`
   - Click "Deploy"

3. **Configurar variables de entorno** (si usas IA)
   - En Streamlit Cloud → Settings → Secrets
   - Agregar:
     ```toml
     OPENROUTER_API_KEY = "tu_api_key_aqui"
     ```

#### ✅ **URL pública**: `https://tu-usuario-tu-repo.streamlit.app`

---

### 2️⃣ **Heroku** (Fácil pero de pago desde 2022)

#### Requisitos
- Cuenta Heroku con tarjeta (mínimo $5/mes)
- Heroku CLI instalado

#### Pasos
```powershell
# 1. Login
heroku login

# 2. Crear app
heroku create nombre-de-tu-app

# 3. Configurar buildpack
heroku buildpacks:set heroku/python

# 4. Variables de entorno (opcional)
heroku config:set OPENROUTER_API_KEY=tu_api_key

# 5. Desplegar
git push heroku main

# 6. Abrir app
heroku open
```

#### ✅ **URL**: `https://nombre-de-tu-app.herokuapp.com`

---

### 3️⃣ **Railway.app** (Gratis hasta $5/mes de uso)

#### Pasos
1. Ir a: https://railway.app
2. Login con GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Seleccionar tu repositorio
5. Railway detectará automáticamente Streamlit
6. Agregar variables de entorno si es necesario

#### ✅ **URL**: Auto-generada por Railway

---

### 4️⃣ **Render.com** (Gratis con limitaciones)

#### Pasos
1. Ir a: https://render.com
2. "New" → "Web Service"
3. Conectar repositorio GitHub
4. Configurar:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Agregar variables de entorno
6. Deploy

#### ✅ **URL**: `https://tu-app.onrender.com`

---

## 📋 **Checklist Pre-Despliegue**

### Archivos requeridos ✅
- [x] `app.py` - Aplicación principal
- [x] `requirements.txt` - Dependencias (con Streamlit)
- [x] `.streamlit/config.toml` - Configuración Streamlit
- [x] `Procfile` - Comando de inicio (Heroku)
- [x] `runtime.txt` - Versión Python
- [x] `.gitignore` - Archivos a ignorar
- [x] `README.md` - Documentación

### Verificaciones
```powershell
# 1. Probar localmente
streamlit run app.py

# 2. Verificar dependencies
pip freeze | Select-String "streamlit"

# 3. Verificar .gitignore
git status

# 4. Commit todo
git add .
git commit -m "Ready for deployment"
```

---

## 🔧 **Configuración Específica**

### Variables de Entorno
Si usas API de IA, configura en cada plataforma:

**Streamlit Cloud**: Settings → Secrets
```toml
OPENROUTER_API_KEY = "sk-or-v1-..."
```

**Heroku/Railway/Render**: Environment Variables
```
OPENROUTER_API_KEY=sk-or-v1-...
```

### Límites de cada plataforma

| Plataforma | Costo | RAM | Disco | Sleeping |
|------------|-------|-----|-------|----------|
| **Streamlit Cloud** | Gratis | 1GB | 1GB | ✅ Sí (inactividad) |
| **Railway** | $5 gratis/mes | 512MB | 1GB | ❌ No |
| **Render** | Gratis | 512MB | - | ✅ Sí (15 min) |
| **Heroku** | Desde $5/mes | 512MB | - | ❌ No |

---

## 🎯 **Recomendación Final**

### Para proyecto académico/demo:
✅ **Streamlit Community Cloud**
- Totalmente gratis
- Deploy en 5 minutos
- Perfecto para demos

### Para producción:
✅ **Railway.app** ($5/mes de uso)
- No duerme
- Mejor performance
- Fácil configuración

---

## 🆘 **Solución de Problemas**

### Error: "Module not found: streamlit"
```powershell
# Verificar requirements.txt tiene:
streamlit>=1.28.0
```

### Error: "Port already in use"
```powershell
# Streamlit Cloud usa $PORT automáticamente
# No necesitas cambiar nada
```

### Error: "Git push rejected"
```powershell
git pull origin main --rebase
git push origin main
```

### App se "duerme" en Render/Streamlit Cloud
- Normal en planes gratuitos
- Se activa en ~30 segundos al visitarla
- Usar Railway si necesitas 24/7

---

## 📱 **Compartir tu App**

Una vez desplegada, comparte:
```
🏗️ Analizador de Arquitectura C4

Sube tu proyecto ZIP y obtén diagramas C4 automáticamente:
🔗 https://tu-usuario-tu-app.streamlit.app

📦 Código: https://github.com/tu-usuario/tu-repo
```

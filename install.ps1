# Instalación Rápida del Agente de Análisis de Código

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🤖 Agente de Análisis de Código - Instalación" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python no encontrado. Por favor instala Python 3.8 o superior." -ForegroundColor Red
    exit 1
}

# 2. Crear entorno virtual
Write-Host ""
Write-Host "🔧 Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Entorno virtual ya existe. Eliminando..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

python -m venv venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "❌ Error al crear entorno virtual" -ForegroundColor Red
    exit 1
}

# 3. Activar entorno virtual
Write-Host ""
Write-Host "🔄 Activando entorno virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 4. Actualizar pip
Write-Host ""
Write-Host "📦 Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 5. Instalar dependencias
Write-Host ""
Write-Host "📥 Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

# 6. Crear directorios necesarios
Write-Host ""
Write-Host "📁 Creando estructura de directorios..." -ForegroundColor Yellow
$dirs = @("uploads", "output", "logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  ✅ Creado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Ya existe: $dir" -ForegroundColor Gray
    }
}

# 7. Verificar instalación
Write-Host ""
Write-Host "✨ Verificando instalación..." -ForegroundColor Yellow

$packages = @("fastapi", "networkx", "tree_sitter")
$allInstalled = $true

foreach ($pkg in $packages) {
    $installed = pip show $pkg 2>$null
    if ($installed) {
        Write-Host "  ✅ $pkg instalado" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $pkg NO instalado" -ForegroundColor Red
        $allInstalled = $false
    }
}

# 8. Resultado final
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
if ($allInstalled) {
    Write-Host "✅ ¡Instalación completada exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para comenzar:" -ForegroundColor Yellow
    Write-Host "  1. Activa el entorno: .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  2. Inicia el servidor: uvicorn api.main:app --reload" -ForegroundColor White
    Write-Host "  3. Visita: http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "O ejecuta el ejemplo:" -ForegroundColor Yellow
    Write-Host "  python examples\analyze_example.py" -ForegroundColor White
} else {
    Write-Host "⚠️  Instalación completada con advertencias" -ForegroundColor Yellow
    Write-Host "Revisa los paquetes faltantes arriba" -ForegroundColor Yellow
}
Write-Host "============================================" -ForegroundColor Cyan

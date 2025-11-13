# Script de Instalación y Configuración - Yedistribuciones Flask
# PowerShell Script

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "     YEDISTRIBUCIONES - Sistema de Gestión de Rutas (Flask)        " -ForegroundColor Cyan
Write-Host "     Instalación y Configuración Automática                         " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python no encontrado. Por favor instale Python 3.11 o superior." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verificar pip
Write-Host "🔍 Verificando pip..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ pip encontrado: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "❌ pip no encontrado." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Crear entorno virtual
Write-Host "🔧 Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️  Entorno virtual ya existe. Saltando creación." -ForegroundColor Yellow
} else {
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Entorno virtual creado exitosamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al crear entorno virtual" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

Write-Host ""

# Actualizar pip
Write-Host "⬆️  Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ""

# Instalar dependencias
Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencias instaladas exitosamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verificar archivo .env
Write-Host "🔍 Verificando configuración (.env)..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ Archivo .env encontrado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Archivo .env no encontrado. Creando plantilla..." -ForegroundColor Yellow
    
    $envContent = @"
# Configuración de Yedistribuciones - Flask

# Base de datos PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=

# Google Maps API (Opcional - para optimización de rutas)
GOOGLE_MAPS_API_KEY=

# Configuración de Flask
FLASK_PORT=5000
DEBUG=True
SECRET_KEY=yedistribuciones-secret-key-change-in-production

# CEDIS (Centro de Distribución) - Coordenadas por defecto: Bogotá
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS=Bogotá, Colombia
"@
    
    Set-Content -Path ".env" -Value $envContent
    Write-Host "✅ Archivo .env creado. Por favor configure las variables necesarias." -ForegroundColor Green
    Write-Host "   Especialmente: DB_PASSWORD y GOOGLE_MAPS_API_KEY (opcional)" -ForegroundColor Cyan
}

Write-Host ""

# Verificar PostgreSQL
Write-Host "🔍 Verificando PostgreSQL..." -ForegroundColor Yellow
$pgCheck = psql --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL encontrado: $pgCheck" -ForegroundColor Green
} else {
    Write-Host "⚠️  PostgreSQL no encontrado en PATH." -ForegroundColor Yellow
    Write-Host "   Asegúrese de tener PostgreSQL instalado y configurado." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "                    INSTALACIÓN COMPLETADA                          " -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure el archivo .env con sus credenciales:" -ForegroundColor White
Write-Host "   - DB_PASSWORD (contraseña de PostgreSQL)" -ForegroundColor Cyan
Write-Host "   - GOOGLE_MAPS_API_KEY (opcional, para optimización)" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Inicialice la base de datos:" -ForegroundColor White
Write-Host "   python scripts/initialize_database.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. (Opcional) Cargar datos de ejemplo:" -ForegroundColor White
Write-Host "   python scripts/init_sample_data.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Ejecutar la aplicación Flask:" -ForegroundColor White
Write-Host "   python main_flask.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Abrir en el navegador:" -ForegroundColor White
Write-Host "   http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Documentación adicional en:" -ForegroundColor Yellow
Write-Host "   - README_FLASK.md" -ForegroundColor Cyan
Write-Host "   - docs/MIGRACION_FLASK.md" -ForegroundColor Cyan
Write-Host "   - docs/QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "¡Gracias por usar Yedistribuciones! 🚚" -ForegroundColor Green
Write-Host ""

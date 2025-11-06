# ========================================
# Script de Instalación - Yedistribuciones
# Migración a PostgreSQL
# ========================================

Write-Host "=" -NoNewline -ForegroundColor Cyan
for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline -ForegroundColor Cyan }
Write-Host ""
Write-Host "🚀 INSTALACIÓN DE YEDISTRIBUCIONES - POSTGRESQL" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline -ForegroundColor Cyan }
Write-Host ""
Write-Host ""

# Verificar Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python instalado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python no encontrado. Por favor instala Python 3.8 o superior." -ForegroundColor Red
    exit 1
}

# Verificar pip
Write-Host "🔍 Verificando pip..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ pip instalado: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "❌ pip no encontrado." -ForegroundColor Red
    exit 1
}

# Actualizar pip
Write-Host ""
Write-Host "📦 Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✅ pip actualizado" -ForegroundColor Green

# Instalar dependencias
Write-Host ""
Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "⚠️  Algunas dependencias pueden no haberse instalado correctamente" -ForegroundColor Yellow
}

# Verificar PostgreSQL
Write-Host ""
Write-Host "🔍 Verificando PostgreSQL..." -ForegroundColor Yellow
$pgVersion = psql --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL instalado: $pgVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  PostgreSQL no encontrado." -ForegroundColor Yellow
    Write-Host "   Descarga PostgreSQL desde: https://www.postgresql.org/download/" -ForegroundColor Cyan
    Write-Host "   O instala con Chocolatey: choco install postgresql" -ForegroundColor Cyan
}

# Verificar archivo .env
Write-Host ""
Write-Host "🔍 Verificando configuración..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ Archivo .env encontrado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Archivo .env no encontrado" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "📝 Creando .env desde .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Archivo .env creado" -ForegroundColor Green
        Write-Host "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales" -ForegroundColor Yellow
    }
}

# Resumen
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline -ForegroundColor Cyan }
Write-Host ""
Write-Host "📋 RESUMEN DE INSTALACIÓN" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline -ForegroundColor Cyan }
Write-Host ""

Write-Host ""
Write-Host "✅ Python y pip configurados" -ForegroundColor Green
Write-Host "✅ Dependencias instaladas" -ForegroundColor Green

# Próximos pasos
Write-Host ""
Write-Host "🎯 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Configurar PostgreSQL:" -ForegroundColor White
Write-Host "   • Asegúrate de que PostgreSQL esté en ejecución" -ForegroundColor Gray
Write-Host "   • Anota tu usuario y contraseña de PostgreSQL" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Editar archivo .env:" -ForegroundColor White
Write-Host "   • Abre el archivo .env en un editor de texto" -ForegroundColor Gray
Write-Host "   • Configura DB_USER y DB_PASSWORD" -ForegroundColor Gray
Write-Host "   • (Opcional) Configura GOOGLE_MAPS_API_KEY" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Inicializar base de datos:" -ForegroundColor White
Write-Host "   python initialize_database.py" -ForegroundColor Green
Write-Host ""
Write-Host "4️⃣  (Opcional) Migrar datos desde SQLite:" -ForegroundColor White
Write-Host "   python migrate_data.py" -ForegroundColor Green
Write-Host ""
Write-Host "5️⃣  Ejecutar la aplicación:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Green
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
for ($i = 0; $i -lt 69; $i++) { Write-Host "=" -NoNewline -ForegroundColor Cyan }
Write-Host ""
Write-Host ""
Write-Host "📚 Documentación completa en: README/MIGRATION_POSTGRESQL.md" -ForegroundColor Cyan
Write-Host ""

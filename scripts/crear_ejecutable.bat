@echo off
REM Script para crear el ejecutable de la aplicación SGPP

title Crear Ejecutable - SGPP
color 0B

echo ========================================
echo   Creando Ejecutable SGPP
echo ========================================
echo.

REM Obtener el directorio del script
cd /d "%~dp0"

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

echo [INFO] Verificando PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller no esta instalado. Instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Limpiando compilaciones anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

echo.
echo [INFO] Creando ejecutable...
echo Esto puede tardar varios minutos...
echo.

cd /d "%~dp0\.."
python scripts\crear_ejecutable.py

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo crear el ejecutable
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Ejecutable creado exitosamente!
echo ========================================
echo.
echo El ejecutable se encuentra en: dist\SGPP - Ejecutable.exe
echo.
echo IMPORTANTE: El ejecutable necesita que estos archivos esten
echo en el mismo directorio:
echo   - app\ (carpeta completa)
echo   - assets\ (carpeta completa)
echo   - config\ (carpeta completa)
echo.
pause


@echo off
REM Instalador de SGPP para Windows
title Instalador - SGPP
color 0B

echo ========================================
echo   INSTALADOR DE SGPP
echo   Sistema de Gestion y Programacion de Proyectos
echo ========================================
echo.

REM Obtener el directorio del script
cd /d "%~dp0\.."

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Verificando que el ejecutable existe...
if not exist "dist\SGPP.exe" (
    echo [ERROR] No se encontro el ejecutable en dist\SGPP.exe
    echo Por favor, crea el ejecutable primero ejecutando:
    echo   python scripts\crear_ejecutable.py
    pause
    exit /b 1
)

echo [OK] Ejecutable encontrado
echo.

echo [INFO] Ejecutando instalador...
python scripts\instalador.py

pause


@echo off
REM Script para iniciar la aplicación SGPP
REM Sistema de Gestión y Programación de Proyectos

title SGPP - Sistema de Gestión y Programación de Proyectos
color 0A

echo ========================================
echo   SGPP - Sistema de Gestion y Programacion de Proyectos
echo ========================================
echo.

REM Obtener el directorio del script
cd /d "%~dp0"

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python detectado
python --version
echo.

REM Verificar si las dependencias principales están instaladas
python -c "import streamlit; import simpy; import pandas; import plotly" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Faltan algunas dependencias. Verificando e instalando...
    echo.
    echo [INFO] Actualizando pip...
    python -m pip install --upgrade pip --quiet
    echo [INFO] Instalando dependencias desde config\requirements.txt...
    echo Esto puede tardar unos minutos la primera vez...
    echo.
    pip install -r config\requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudieron instalar las dependencias
        echo Por favor, verifica tu conexion a internet e intentalo de nuevo
        pause
        exit /b 1
    )
    echo.
    echo [OK] Todas las dependencias instaladas correctamente
    echo.
) else (
    echo [OK] Dependencias principales ya estan instaladas
    echo.
)

REM Verificar que app/app.py existe
if not exist "app\app.py" (
    echo [ERROR] No se encontro el archivo app\app.py
    echo Asegurate de que el script este en el directorio raiz del proyecto
    pause
    exit /b 1
)

echo ========================================
echo   Iniciando aplicacion...
echo ========================================
echo.

REM Verificar si el puerto 8503 está ocupado
netstat -an | findstr ":8503" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] El puerto 8503 esta en uso. Abriendo navegador...
    timeout /t 1 /nobreak >nul
    start http://localhost:8503
    echo [OK] Navegador abierto en http://localhost:8503
    pause
    exit /b 0
)

echo La aplicacion se abrira automaticamente en: http://localhost:8503
echo Presiona Ctrl+C para cerrar la aplicacion
echo.
echo ========================================
echo.

REM Abrir navegador después de 8 segundos usando PowerShell (dar tiempo a que Streamlit inicie)
REM Usaremos un script PowerShell más inteligente que verifica que el puerto esté listo
start /b powershell -Command "$port = 8503; $maxAttempts = 30; $attempt = 0; while ($attempt -lt $maxAttempts) { try { $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue; if ($connection) { Start-Process 'http://localhost:8503'; Write-Host '[OK] Navegador abierto en http://localhost:8503'; break; } } catch { }; Start-Sleep -Seconds 1; $attempt++; }; if ($attempt -eq $maxAttempts) { Write-Host '[ADVERTENCIA] No se pudo verificar que Streamlit este listo. Abre manualmente: http://localhost:8503'; Start-Process 'http://localhost:8503'; }"

REM Ejecutar Streamlit en modo headless (NO abrirá el navegador automáticamente)
REM Agregar --server.address localhost para asegurar que solo escuche en localhost
streamlit run app/app.py --server.port 8503 --server.address localhost --server.headless true --browser.gatherUsageStats false

REM Si el comando anterior falla, intentar con python -m streamlit
if errorlevel 1 (
    echo.
    echo [INFO] Intentando ejecutar con python -m streamlit...
    start /b powershell -Command "$port = 8503; $maxAttempts = 30; $attempt = 0; while ($attempt -lt $maxAttempts) { try { $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue; if ($connection) { Start-Process 'http://localhost:8503'; Write-Host '[OK] Navegador abierto en http://localhost:8503'; break; } } catch { }; Start-Sleep -Seconds 1; $attempt++; }; if ($attempt -eq $maxAttempts) { Write-Host '[ADVERTENCIA] No se pudo verificar que Streamlit este listo. Abre manualmente: http://localhost:8503'; Start-Process 'http://localhost:8503'; }"
    python -m streamlit run app/app.py --server.port 8503 --server.address localhost --server.headless true --browser.gatherUsageStats false
)

echo.
echo ========================================
echo   Aplicacion cerrada
echo ========================================
pause


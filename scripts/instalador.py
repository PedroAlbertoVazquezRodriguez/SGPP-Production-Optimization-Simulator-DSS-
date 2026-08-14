"""
Instalador para SGPP
Permite instalar la aplicación en el sistema Windows
"""
import os
import sys
import shutil
import winreg
from pathlib import Path

def es_admin():
    """Verifica si el script se ejecuta con privilegios de administrador"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def solicitar_privilegios_admin():
    """Solicita privilegios de administrador"""
    if not es_admin():
        import ctypes
        print("Solicitando privilegios de administrador...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

def obtener_ruta_instalacion():
    """Obtiene la ruta de instalación (por defecto Program Files)"""
    ruta_base = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'SGPP')
    return ruta_base

def crear_directorio(ruta):
    """Crea un directorio si no existe"""
    try:
        os.makedirs(ruta, exist_ok=True)
        return True
    except PermissionError:
        print(f"ERROR: No tienes permisos para crear {ruta}")
        return False
    except Exception as e:
        print(f"ERROR al crear directorio: {e}")
        return False

def copiar_archivos(origen, destino):
    """Copia archivos de origen a destino"""
    try:
        if os.path.isdir(origen):
            if os.path.exists(destino):
                shutil.rmtree(destino)
            shutil.copytree(origen, destino)
        else:
            shutil.copy2(origen, destino)
        return True
    except Exception as e:
        print(f"ERROR al copiar archivos: {e}")
        return False

def crear_acceso_directo(ruta_exe, nombre, ubicacion="desktop"):
    """Crea un acceso directo en el escritorio o menú inicio"""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        
        if ubicacion == "desktop":
            # Carpeta de escritorio
            ruta_acceso = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', f"{nombre}.lnk")
        elif ubicacion == "menu":
            # Menú inicio
            ruta_menu = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
            ruta_acceso = os.path.join(ruta_menu, f"{nombre}.lnk")
        else:
            return False
        
        acceso = shell.CreateShortCut(ruta_acceso)
        acceso.Targetpath = ruta_exe
        acceso.WorkingDirectory = os.path.dirname(ruta_exe)
        acceso.IconLocation = ruta_exe  # Usar el icono del .exe
        acceso.save()
        return True
    except ImportError:
        # Si pywin32 no está instalado, crear acceso directo manual
        print(f"[INFO] pywin32 no disponible, creando acceso directo manual en {ubicacion}...")
        return crear_acceso_directo_manual(ruta_exe, nombre, ubicacion)
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo crear acceso directo en {ubicacion}: {e}")
        return False

def crear_acceso_directo_manual(ruta_exe, nombre, ubicacion):
    """Crea un acceso directo usando un script VBS (fallback)"""
    try:
        if ubicacion == "desktop":
            ruta_acceso = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', f"{nombre}.lnk")
        elif ubicacion == "menu":
            ruta_menu = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
            ruta_acceso = os.path.join(ruta_menu, f"{nombre}.lnk")
        else:
            return False
        
        # Crear script VBS temporal para crear acceso directo
        script_vbs = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{ruta_acceso}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{ruta_exe}"
oLink.WorkingDirectory = "{os.path.dirname(ruta_exe)}"
oLink.IconLocation = "{ruta_exe}"
oLink.Save
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vbs', delete=False) as f:
            f.write(script_vbs)
            temp_vbs = f.name
        
        import subprocess
        subprocess.run(['cscript', '//nologo', temp_vbs], check=True)
        os.unlink(temp_vbs)
        return True
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo crear acceso directo: {e}")
        return False

def crear_entrada_registro(ruta_instalacion):
    """Crea una entrada en el registro de Windows para desinstalación"""
    try:
        ruta_desinstalador = os.path.join(ruta_instalacion, 'desinstalar.exe')
        if not os.path.exists(ruta_desinstalador):
            return False
        
        clave = winreg.HKEY_LOCAL_MACHINE
        ruta_reg = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SGPP"
        
        try:
            key = winreg.OpenKey(clave, ruta_reg, 0, winreg.KEY_WRITE)
        except FileNotFoundError:
            key = winreg.CreateKey(clave, ruta_reg)
        
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "SGPP - Sistema de Gestión y Programación de Proyectos")
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{ruta_desinstalador}"')
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, ruta_instalacion)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0")
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "SGPP")
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        
        winreg.CloseKey(key)
        return True
    except PermissionError:
        print("[ADVERTENCIA] No se pudo crear entrada en el registro (requiere privilegios de admin)")
        return False
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo crear entrada en el registro: {e}")
        return False

def crear_desinstalador(ruta_instalacion):
    """Crea el script de desinstalación"""
    script_desinstalador = f"""@echo off
REM Desinstalador de SGPP
echo ========================================
echo   Desinstalando SGPP
echo ========================================
echo.
echo Esta accion eliminara SGPP del sistema.
echo.
pause

REM Eliminar archivos
if exist "{ruta_instalacion}" (
    echo Eliminando archivos...
    rmdir /s /q "{ruta_instalacion}"
)

REM Eliminar accesos directos
set "DESKTOP=%USERPROFILE%\\Desktop"
if exist "%DESKTOP%\\SGPP.lnk" del "%DESKTOP%\\SGPP.lnk"

set "MENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"
if exist "%MENU%\\SGPP.lnk" del "%MENU%\\SGPP.lnk"

REM Eliminar entrada del registro
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SGPP" /f >nul 2>&1

echo.
echo SGPP ha sido desinstalado correctamente.
echo.
pause
"""
    
    ruta_desinstalador = os.path.join(ruta_instalacion, 'desinstalar.bat')
    try:
        with open(ruta_desinstalador, 'w', encoding='utf-8') as f:
            f.write(script_desinstalador)
        
        # Convertir a .exe si es posible (opcional)
        return True
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo crear desinstalador: {e}")
        return False

def instalar():
    """Función principal de instalación"""
    print("=" * 60)
    print("  INSTALADOR DE SGPP")
    print("  Sistema de Gestión y Programación de Proyectos")
    print("=" * 60)
    print()
    
    # Verificar que existe el ejecutable
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_raiz = os.path.dirname(directorio_actual)
    ruta_exe_origen = os.path.join(directorio_raiz, 'dist', 'SGPP.exe')
    
    if not os.path.exists(ruta_exe_origen):
        print(f"ERROR: No se encontró el ejecutable en {ruta_exe_origen}")
        print("Por favor, crea el ejecutable primero ejecutando: python scripts/crear_ejecutable.py")
        input("\nPresiona Enter para salir...")
        return False
    
    print(f"[OK] Ejecutable encontrado: {ruta_exe_origen}")
    print()
    
    # Solicitar ruta de instalación
    ruta_instalacion = obtener_ruta_instalacion()
    print(f"Ruta de instalación por defecto: {ruta_instalacion}")
    respuesta = input("¿Deseas cambiar la ruta de instalación? (S/N): ").strip().upper()
    
    if respuesta == 'S':
        nueva_ruta = input("Ingresa la nueva ruta: ").strip()
        if nueva_ruta:
            ruta_instalacion = nueva_ruta
    
    print()
    print(f"Instalando en: {ruta_instalacion}")
    print()
    
    # Verificar/crear privilegios de admin si es necesario
    if not os.path.exists(os.path.dirname(ruta_instalacion)):
        print("Se requieren privilegios de administrador para instalar en Program Files")
        solicitar_privilegios_admin()
    
    # Crear directorio de instalación
    if not crear_directorio(ruta_instalacion):
        input("\nPresiona Enter para salir...")
        return False
    
    print("[INFO] Copiando archivos...")
    
    # Copiar el ejecutable
    ruta_exe_destino = os.path.join(ruta_instalacion, 'SGPP.exe')
    if not copiar_archivos(ruta_exe_origen, ruta_exe_destino):
        print("ERROR: No se pudo copiar el ejecutable")
        input("\nPresiona Enter para salir...")
        return False
    
    print(f"[OK] Ejecutable copiado: {ruta_exe_destino}")
    
    # Crear desinstalador
    print("[INFO] Creando desinstalador...")
    crear_desinstalador(ruta_instalacion)
    print("[OK] Desinstalador creado")
    
    # Crear accesos directos
    print("[INFO] Creando accesos directos...")
    if crear_acceso_directo(ruta_exe_destino, "SGPP", "desktop"):
        print("[OK] Acceso directo creado en el escritorio")
    if crear_acceso_directo(ruta_exe_destino, "SGPP", "menu"):
        print("[OK] Acceso directo creado en el menú inicio")
    
    # Crear entrada en el registro
    print("[INFO] Creando entrada en el registro de Windows...")
    crear_entrada_registro(ruta_instalacion)
    print("[OK] Entrada en el registro creada (aparecerá en Agregar o quitar programas)")
    
    print()
    print("=" * 60)
    print("  INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print(f"SGPP ha sido instalado en: {ruta_instalacion}")
    print()
    print("Puedes iniciar SGPP desde:")
    print("  - El acceso directo en tu escritorio")
    print("  - El menú de inicio de Windows")
    print()
    print("Para desinstalar, usa 'Agregar o quitar programas' en Windows")
    print("o ejecuta: desinstalar.bat desde la carpeta de instalación")
    print()
    
    respuesta = input("¿Deseas iniciar SGPP ahora? (S/N): ").strip().upper()
    if respuesta == 'S':
        try:
            os.startfile(ruta_exe_destino)
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudo iniciar SGPP: {e}")
    
    input("\nPresiona Enter para salir...")
    return True

if __name__ == "__main__":
    try:
        instalar()
    except KeyboardInterrupt:
        print("\n\nInstalación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)


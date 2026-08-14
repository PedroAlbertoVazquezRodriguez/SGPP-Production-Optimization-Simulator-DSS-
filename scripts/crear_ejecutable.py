"""
Script para crear el ejecutable de la aplicación SGPP
"""
import subprocess
import sys
import os
import shutil

def verificar_pyinstaller():
    """Verifica si PyInstaller está instalado"""
    try:
        import PyInstaller
        print("[OK] PyInstaller ya está instalado")
        return True
    except ImportError:
        print("[INFO] PyInstaller no está instalado. Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("[OK] PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] No se pudo instalar PyInstaller")
            return False

def limpiar_compilaciones_anteriores():
    """Elimina compilaciones anteriores"""
    print("[INFO] Limpiando compilaciones anteriores...")
    directorios = ["build", "dist"]
    archivos = [f for f in os.listdir(".") if f.endswith(".spec")]
    
    for directorio in directorios:
        if os.path.exists(directorio):
            try:
                shutil.rmtree(directorio)
                print(f"  - Eliminado: {directorio}/")
            except Exception as e:
                print(f"  - No se pudo eliminar {directorio}: {e}")
    
    for archivo in archivos:
        try:
            os.remove(archivo)
            print(f"  - Eliminado: {archivo}")
        except Exception as e:
            print(f"  - No se pudo eliminar {archivo}: {e}")

def crear_ejecutable():
    """Crea el ejecutable usando PyInstaller"""
    print()
    print("=" * 50)
    print("  Creando Ejecutable SGPP")
    print("=" * 50)
    print()
    
    if not verificar_pyinstaller():
        return False
    
    print()
    limpiar_compilaciones_anteriores()
    print()
    
    # Cambiar al directorio raíz
    directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(directorio_raiz)
    
    # Verificar que el icono existe
    icono_path = os.path.join(directorio_raiz, "assets", "ss.ico")
    if not os.path.exists(icono_path):
        print(f"[ADVERTENCIA] No se encontró el icono en {icono_path}")
        print("[INFO] El ejecutable se creará sin icono personalizado")
        icono_path = None
    else:
        print(f"[OK] Icono encontrado: {icono_path}")
    
    print()
    print("[INFO] Creando ejecutable...")
    print("Esto puede tardar varios minutos...")
    print()
    
    try:
        # Intentar usar el archivo .spec personalizado
        spec_path = os.path.join(directorio_raiz, "scripts", "SGPP.spec")
        
        if os.path.exists(spec_path):
            print("[INFO] Usando archivo de especificación personalizado (SGPP.spec)...")
            comando = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                spec_path
            ]
        else:
            # Usar comando directo si no hay .spec
            print("[INFO] Usando configuración directa...")
            comando = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",                    # Un solo archivo ejecutable
                "--console",                    # Mostrar consola
                "--name", "SGPP",               # Nombre del ejecutable
                "--clean",                      # Limpiar cache antes de compilar
                "--noconfirm",                  # No confirmar sobrescritura
            ]
            
            # Agregar icono si existe
            if icono_path:
                comando.extend(["--icon", icono_path])
            
            # Agregar archivos de datos necesarios
            comando.extend([
                "--add-data", f"app{os.pathsep}app",        # Carpeta app completa
                "--add-data", f"assets{os.pathsep}assets",  # Carpeta assets
                "--add-data", f"config{os.pathsep}config",  # Carpeta config
            ])
            
            # Archivo principal
            comando.append("scripts/ejecutable.py")
        
        # Ejecutar PyInstaller
        subprocess.check_call(comando, cwd=directorio_raiz)
        
        print()
        print("=" * 50)
        print("  Ejecutable creado exitosamente!")
        print("=" * 50)
        print()
        print("El ejecutable se encuentra en: dist\\SGPP.exe")
        print()
        print("NOTA: Todos los archivos necesarios están incluidos en el .exe")
        print("Puedes distribuir solo el archivo SGPP.exe")
        print()
        
        return True
    except subprocess.CalledProcessError as e:
        print()
        print("[ERROR] No se pudo crear el ejecutable")
        print(f"Error: {e}")
        print()
        print("[INFO] Intentando crear con configuración alternativa...")
        try:
            # Intento alternativo sin --add-data (requerirá copiar carpetas manualmente)
            comando_alt = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--console",
                "--name", "SGPP",
                "--clean",
                "--noconfirm",
            ]
            if icono_path:
                comando_alt.extend(["--icon", icono_path])
            comando_alt.append("scripts/ejecutable.py")
            
            subprocess.check_call(comando_alt)
            
            print()
            print("=" * 50)
            print("  Ejecutable creado (configuración alternativa)")
            print("=" * 50)
            print()
            print("El ejecutable se encuentra en: dist\\SGPP.exe")
            print()
            print("IMPORTANTE: Necesitas copiar estas carpetas junto al .exe:")
            print("  - app\\ (carpeta completa)")
            print("  - assets\\ (carpeta completa)")
            print("  - config\\ (carpeta completa)")
            print()
            return True
        except Exception as e2:
            print(f"[ERROR] También falló el método alternativo: {e2}")
            return False

if __name__ == "__main__":
    if crear_ejecutable():
        input("\nPresiona Enter para salir...")
    else:
        input("\nPresiona Enter para salir...")
        sys.exit(1)


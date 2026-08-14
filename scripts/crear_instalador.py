"""
Crea un instalador .exe usando PyInstaller
Este instalador puede ser distribuido independientemente
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
    """Elimina compilaciones anteriores del instalador"""
    print("[INFO] Limpiando compilaciones anteriores del instalador...")
    directorios = ["build", "dist_instalador"]
    archivos = [f for f in os.listdir(".") if f.endswith(".spec") and "Instalador" in f]
    
    for directorio in directorios:
        if os.path.exists(directorio) and "instalador" in directorio.lower():
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

def crear_instalador_exe():
    """Crea el instalador como .exe"""
    print()
    print("=" * 60)
    print("  Creando Instalador SGPP.exe")
    print("=" * 60)
    print()
    
    if not verificar_pyinstaller():
        return False
    
    print()
    limpiar_compilaciones_anteriores()
    print()
    
    # Cambiar al directorio raíz
    directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(directorio_raiz)
    
    # Verificar que existe el ejecutable a instalar
    ruta_exe = os.path.join(directorio_raiz, 'dist', 'SGPP.exe')
    if not os.path.exists(ruta_exe):
        print("[ADVERTENCIA] No se encontró dist/SGPP.exe")
        print("El instalador funcionará pero necesitarás tener el ejecutable en dist/")
    
    print("[INFO] Creando instalador...")
    print("Esto puede tardar unos minutos...")
    print()
    
    try:
        # Crear instalador con PyInstaller
        comando = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--console",
            "--name", "Instalador_SGPP",
            "--clean",
            "--noconfirm",
            "--distpath", "dist_instalador",
            "--workpath", "build",
            "scripts/instalador.py"
        ]
        
        # Ejecutar
        subprocess.check_call(comando, cwd=directorio_raiz)
        
        print()
        print("=" * 60)
        print("  Instalador creado exitosamente!")
        print("=" * 60)
        print()
        print("El instalador se encuentra en: dist_instalador\\Instalador_SGPP.exe")
        print()
        print("NOTA: Para que el instalador funcione, necesita que el ejecutable")
        print("SGPP.exe esté en la carpeta dist\\ cuando lo ejecutes.")
        print()
        
        return True
    except subprocess.CalledProcessError as e:
        print()
        print("[ERROR] No se pudo crear el instalador")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if crear_instalador_exe():
        input("\nPresiona Enter para salir...")
    else:
        input("\nPresiona Enter para salir...")
        sys.exit(1)


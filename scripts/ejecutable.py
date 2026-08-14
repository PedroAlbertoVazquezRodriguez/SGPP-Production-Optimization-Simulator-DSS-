"""
Ejecutador para la aplicación SGPP
Abre el navegador automáticamente y ejecuta Streamlit
"""
import subprocess
import sys
import os
import webbrowser
import time
import threading
import socket

def verificar_python():
    """Verifica que Python esté instalado"""
    if sys.version_info < (3, 7):
        print("ERROR: Se requiere Python 3.7 o superior")
        input("Presiona Enter para salir...")
        sys.exit(1)
    print(f"[OK] Python {sys.version.split()[0]} detectado")

def verificar_dependencias():
    """Verifica e instala dependencias si es necesario"""
    try:
        # Verificar las dependencias principales
        import streamlit
        import simpy
        import pandas
        import plotly
        print("[OK] Dependencias principales ya están instaladas")
        return True
    except ImportError as e:
        print("[INFO] Faltan algunas dependencias. Verificando e instalando...")
        print(f"[INFO] Módulo faltante: {e.name if hasattr(e, 'name') else 'desconocido'}")
        try:
            print("[INFO] Actualizando pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[INFO] Instalando dependencias desde config/requirements.txt...")
            print("Esto puede tardar unos minutos la primera vez...")
            print()
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "config/requirements.txt"])
            print()
            print("[OK] Todas las dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError:
            print()
            print("[ERROR] No se pudieron instalar las dependencias")
            print("Por favor, verifica tu conexión a internet e inténtalo de nuevo")
            input("Presiona Enter para salir...")
            return False

def obtener_directorio_base():
    """Obtiene el directorio base donde están los archivos"""
    if getattr(sys, 'frozen', False):
        # Si está ejecutándose como .exe (PyInstaller)
        # PyInstaller crea una carpeta temporal en sys._MEIPASS
        if hasattr(sys, '_MEIPASS'):
            # Archivos empaquetados están en sys._MEIPASS
            # Pero necesitamos trabajar desde el directorio del .exe
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(sys.executable)
    else:
        # Si está ejecutándose como script Python
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def verificar_puerto_disponible(puerto):
    """Verifica si un puerto está disponible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            resultado = s.connect_ex(('localhost', puerto))
            return resultado != 0  # True si el puerto está disponible (no se puede conectar)
    except Exception:
        return True  # Si hay error, asumimos que está disponible

def esperar_streamlit_listo(puerto, max_intentos=30):
    """Espera a que Streamlit esté listo en el puerto especificado"""
    for i in range(max_intentos):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex(('localhost', puerto)) == 0:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False

def abrir_navegador(puerto=8501):
    """Espera a que Streamlit esté listo y abre el navegador"""
    # Esperar a que Streamlit esté realmente listo
    print(f"[INFO] Esperando a que Streamlit esté listo en el puerto {puerto}...")
    if esperar_streamlit_listo(puerto):
        try:
            url = f'http://localhost:{puerto}'
            print(f"[OK] Streamlit está listo. Abriendo navegador en {url}...")
            webbrowser.open(url)
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudo abrir el navegador automáticamente: {e}")
            print(f"Por favor, abre manualmente: http://localhost:{puerto}")
    else:
        print(f"[ADVERTENCIA] No se pudo verificar que Streamlit esté listo")
        print(f"Por favor, abre manualmente: http://localhost:{puerto}")

def ejecutar_streamlit(puerto=8501):
    """Ejecuta Streamlit en el puerto especificado"""
    # Si el puerto está ocupado, asumir que Streamlit ya está corriendo y abrir navegador
    if not verificar_puerto_disponible(puerto):
        print(f"[INFO] El puerto {puerto} está en uso. Abriendo navegador...")
        time.sleep(1)
        try:
            url = f'http://localhost:{puerto}'
            webbrowser.open(url)
            print(f"[OK] Navegador abierto en {url}")
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudo abrir el navegador: {e}")
            print(f"Por favor, abre manualmente: http://localhost:{puerto}")
        return
    
    directorio_base = obtener_directorio_base()
    
    # Si es un .exe, los archivos pueden estar en sys._MEIPASS o en el mismo directorio
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller: Los archivos empaquetados están en sys._MEIPASS
        # Necesitamos copiar/extraer los archivos si no están en el directorio del .exe
        meipass_dir = sys._MEIPASS
        
        # Verificar si los archivos están en el directorio del .exe
        exe_dir = os.path.dirname(sys.executable)
        app_path_exe = os.path.join(exe_dir, 'app', 'app.py')
        app_path_meipass = os.path.join(meipass_dir, 'app', 'app.py')
        
        # Si no están en exe_dir, usar meipass_dir
        if os.path.exists(app_path_exe):
            directorio_base = exe_dir
        elif os.path.exists(app_path_meipass):
            directorio_base = meipass_dir
    
    os.chdir(directorio_base)
    
    # Verificar que app/app.py existe
    if not os.path.exists('app/app.py'):
        print("ERROR: No se encontró el archivo app/app.py")
        print(f"Buscando en: {directorio_base}")
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            print(f"También buscando en: {sys._MEIPASS}")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    # Ejecutar Streamlit
    try:
        if getattr(sys, 'frozen', False):
            streamlit_cmd = 'streamlit'
        else:
            streamlit_cmd = [sys.executable, '-m', 'streamlit']
        
        # Usar headless para que Streamlit NO abra el navegador automáticamente
        # Nuestro hilo se encargará de abrirlo una sola vez
        # Agregar --server.address localhost para asegurar que solo escuche en localhost
        if isinstance(streamlit_cmd, str):
            subprocess.run([
                streamlit_cmd, 'run', 'app/app.py',
                '--server.port', str(puerto),
                '--server.address', 'localhost',
                '--server.headless', 'true',
                '--browser.gatherUsageStats', 'false'
            ], check=True)
        else:
            subprocess.run([
                *streamlit_cmd, 'run', 'app/app.py',
                '--server.port', str(puerto),
                '--server.address', 'localhost',
                '--server.headless', 'true',
                '--browser.gatherUsageStats', 'false'
            ], check=True)
    except KeyboardInterrupt:
        print("\nCerrando aplicación...")
        sys.exit(0)
    except FileNotFoundError:
        print("ERROR: Streamlit no está instalado o no está en el PATH")
        print("Por favor, instala Streamlit con: pip install streamlit")
        input("Presiona Enter para salir...")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print("  SGPP - Sistema de Gestión y Programación de Proyectos")
    print("=" * 50)
    print()
    
    verificar_python()
    print()
    
    if not verificar_dependencias():
        sys.exit(1)
    
    print()
    print("=" * 50)
    print("  Iniciando aplicación...")
    print("=" * 50)
    print()
    
    # Puerto por defecto
    PUERTO = 8503
    
    print(f"La aplicación se abrirá automáticamente en: http://localhost:{PUERTO}")
    print("Presiona Ctrl+C para cerrar la aplicación")
    print()
    print("=" * 50)
    print()
    
    # Iniciar hilo para abrir navegador
    thread_navegador = threading.Thread(target=abrir_navegador, args=(PUERTO,), daemon=True)
    thread_navegador.start()
    
    # Ejecutar Streamlit
    ejecutar_streamlit(PUERTO)


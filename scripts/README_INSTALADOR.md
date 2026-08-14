# Instalador de SGPP

Este directorio contiene los scripts necesarios para crear y ejecutar el instalador de SGPP.

## Archivos

- **`instalador.py`** - Script principal del instalador (puede ejecutarse directamente)
- **`instalador.bat`** - Script batch para ejecutar el instalador fácilmente
- **`crear_instalador.py`** - Crea un instalador .exe standalone usando PyInstaller

## Cómo crear el instalador

### Opción 1: Instalador como script Python (Recomendado)

1. Asegúrate de tener el ejecutable creado en `dist/SGPP.exe`
   ```bash
   python scripts/crear_ejecutable.py
   ```

2. Ejecuta el instalador:
   ```bash
   # Opción A: Script batch (Windows)
   scripts\instalador.bat
   
   # Opción B: Python directo
   python scripts\instalador.py
   ```

### Opción 2: Instalador como .exe standalone

Si quieres distribuir un instalador .exe independiente:

```bash
python scripts/crear_instalador.py
```

Esto creará `dist_instalador/Instalador_SGPP.exe` que puedes distribuir.

**Nota**: El instalador .exe necesita que el archivo `dist/SGPP.exe` esté en la misma estructura de carpetas cuando lo ejecutes.

## Qué hace el instalador

1. **Copia el ejecutable** a la ubicación de instalación (por defecto: `C:\Program Files\SGPP\`)
2. **Crea accesos directos** en:
   - Escritorio
   - Menú de inicio de Windows
3. **Registra la aplicación** en Windows para que aparezca en "Agregar o quitar programas"
4. **Crea un desinstalador** (`desinstalar.bat`) en la carpeta de instalación

## Desinstalación

El instalador crea varias opciones para desinstalar:

1. **Desde Windows**:
   - Ve a Configuración > Aplicaciones
   - Busca "SGPP"
   - Haz clic en "Desinstalar"

2. **Desde la carpeta de instalación**:
   - Ejecuta `desinstalar.bat` que está en la carpeta donde se instaló SGPP

## Requisitos

- Windows 10 o superior
- Privilegios de administrador (se solicitarán automáticamente)
- El ejecutable `SGPP.exe` debe existir en `dist/`

## Notas importantes

- El instalador solicitará privilegios de administrador automáticamente si es necesario
- Puedes cambiar la ruta de instalación durante la instalación
- El instalador incluye verificación de que el ejecutable existe antes de continuar


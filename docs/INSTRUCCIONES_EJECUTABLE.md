# Instrucciones para Crear y Usar el Ejecutable

## 🚀 Opción 1: Usar el Script Batch (Más Fácil)

1. Haz doble clic en: `scripts\crear_ejecutable.bat`
2. Espera a que termine (puede tardar varios minutos)
3. El ejecutable estará en: `dist\SGPP - Ejecutable.exe`

## 🐍 Opción 2: Usar el Script Python

1. Abre una terminal/CMD en el directorio del proyecto
2. Ejecuta: `python scripts\crear_ejecutable.py`
3. Espera a que termine
4. El ejecutable estará en: `dist\SGPP - Ejecutable.exe`

## ⚙️ Opción 3: Comando Manual

1. Instala PyInstaller: `pip install pyinstaller`
2. Ejecuta:
   ```bash
   pyinstaller --onefile --console --name "SGPP - Ejecutable" scripts/ejecutable.py
   ```
3. El ejecutable estará en: `dist\SGPP - Ejecutable.exe`

## 📦 Archivos Necesarios para el Ejecutable

El ejecutable necesita que estos archivos estén en el **MISMO directorio** que el .exe:

```
directorio_del_ejecutable/
├── SGPP - Ejecutable.exe
├── app/                    (carpeta completa)
│   ├── __init__.py
│   ├── app.py
│   ├── simulation.py
│   └── utils.py
├── assets/                 (carpeta completa)
│   └── ss.png
└── config/
    └── requirements.txt
```

## 🎯 Uso del Ejecutable

1. Copia el ejecutable y las carpetas necesarias a una ubicación
2. Haz doble clic en `SGPP - Ejecutable.exe`
3. Se abrirá automáticamente:
   - Una ventana de CMD con el servidor Streamlit
   - Tu navegador con la aplicación en `http://localhost:8501`
4. Para cerrar, presiona `Ctrl+C` en la ventana de CMD o cierra el navegador

## ⚠️ Requisitos del Sistema

- **Python 3.7 o superior** debe estar instalado en el sistema
- **Streamlit** se instalará automáticamente si no está presente
- El puerto **8501** debe estar libre
- El sistema debe tener conexión a internet la primera vez (para instalar dependencias)

## 📝 Notas

- La primera vez que ejecutes el .exe puede tardar más en iniciar
- Si el puerto 8501 está ocupado, puedes modificar el script para usar otro puerto
- El ejecutable verifica e instala automáticamente las dependencias si es necesario


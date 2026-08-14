# -*- mode: python ; coding: utf-8 -*-
"""
Archivo de especificación para PyInstaller
Crea el ejecutable SGPP con todas las dependencias incluidas
"""
import os

block_cipher = None

# Obtener directorio raíz (subir dos niveles desde scripts/)
# Cuando PyInstaller ejecuta este spec, estamos en el directorio raíz
root_dir = os.path.dirname(os.path.abspath(SPECPATH))

# Datos adicionales a incluir (rutas relativas desde root_dir)
added_files = [
    (os.path.join(root_dir, 'app'), 'app'),
    (os.path.join(root_dir, 'assets'), 'assets'),
    (os.path.join(root_dir, 'config'), 'config'),
]

# Módulos ocultos que PyInstaller no detecta automáticamente
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.state',
    'simpy',
    'pandas',
    'plotly',
    'plotly.graph_objects',
    'plotly.graph_objs',
    'numpy',
    'scipy',
    'openpyxl',
    'sklearn',
    'PIL',
    'altair',
    'watchdog',
    'tornado',
    'click',
    'typing_extensions',
    'pkg_resources.py2_warn',
]

a = Analysis(
    [os.path.join(root_dir, 'scripts', 'ejecutable.py')],
    pathex=[root_dir],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Ruta del icono
icon_path = os.path.join(root_dir, 'assets', 'ss.ico')
icon_param = icon_path if os.path.exists(icon_path) else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SGPP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_param,
)

# Sistema de Gestión y Programación de Proyectos (SGPP)

Sistema de Soporte a Decisiones (DSS) interactivo para optimización de producción en Sonara.

## 📁 Estructura del Proyecto

```
PIA_MySD_Jueves_N1-N3_E7/
├── app/                    # Código fuente de la aplicación
│   ├── __init__.py
│   ├── app.py             # Aplicación principal Streamlit
│   ├── simulation.py      # Motor de simulación SimPy
│   └── utils.py           # Utilidades para gráficos y análisis
├── assets/                 # Recursos estáticos (imágenes, etc.)
│   └── ss.png
├── docs/                   # Documentación
│   ├── README.md          # Documentación detallada
│   └── INSTRUCCIONES_EJECUTABLE.md
├── scripts/                # Scripts auxiliares
│   ├── crear_ejecutable.bat   # Script para crear ejecutable .exe
│   ├── crear_ejecutable.py    # Script Python para crear ejecutable
│   └── ejecutable.py          # Script Python equivalente al ejecutable.bat
├── config/                # Configuración
│   └── requirements.txt   # Dependencias del proyecto
├── ejecutable.bat         # ⭐ EJECUTABLE PRINCIPAL - Haz doble clic aquí (único fuera)
├── .gitignore            # Archivos ignorados por Git
└── README.md             # Este archivo
```

## 🚀 Inicio Rápido

### Opción 1: Ejecutable (Recomendado)

**Haz doble clic en `ejecutable.bat`** para iniciar la aplicación automáticamente.

También puedes ejecutar: `python ejecutable.py`

### Opción 2: Manual

#### Instalación

```bash
pip install -r config/requirements.txt
```

#### Ejecución

```bash
streamlit run app/app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Crear Ejecutable .exe

Para crear un ejecutable independiente, consulta las [instrucciones detalladas](docs/INSTRUCCIONES_EJECUTABLE.md) o ejecuta:

```bash
python scripts/crear_ejecutable.py
```

## 🎯 Características Principales

- **Simulación de Eventos Discretos (DES)** con SimPy
- **Análisis de cuellos de botella** y optimización
- **Visualizaciones interactivas** con Plotly
- **Interfaz intuitiva** con diseño Bootstrap 5
- **Múltiples escenarios de optimización**
- **Sistema de Semáforo Operacional** en tiempo real
- **Análisis de ahorro económico** y recomendaciones DSS

## 📖 Documentación

Para más detalles, consulta la [documentación completa](docs/README.md).

## 🔧 Tecnologías Utilizadas

- **Streamlit**: Framework para aplicaciones web interactivas
- **SimPy**: Simulación de eventos discretos
- **Plotly**: Gráficos interactivos
- **Pandas**: Manipulación de datos
- **NumPy/Scipy**: Cálculos numéricos y distribuciones estadísticas

## 🌐 Funcionamiento Offline

✅ **La aplicación funciona completamente sin conexión a internet**. Todos los recursos son locales y no requieren acceso a CDNs o servicios externos.


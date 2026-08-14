# SGPP

Aplicación de escritorio (Windows) para simulación de sistemas de producción y análisis de datos, empaquetada como un único ejecutable — no requiere instalar Python, Git ni dependencias adicionales.

## Instalación

No hay instalación. Simplemente:

1. Copia `SGPP.exe` a la carpeta donde quieras tenerlo (por ejemplo, el Escritorio o una carpeta de trabajo).
2. Haz doble clic para ejecutarlo (o usa `ejecutable.bat` si así se distribuye).

## Primer uso

El sistema levantará automáticamente el servidor local y abrirá la interfaz interactiva en tu navegador predeterminado (usualmente en `http://localhost:8501`).

> **Nota:** No cierres la ventana de consola/terminal que se abre en segundo plano; este proceso mantiene la aplicación en ejecución. Para salir, simplemente cierra la consola.

## Requisitos del sistema

- **Sistema Operativo:** Windows 10 / Windows 11 (64-bit).
- **Entorno:** No requiere instalación previa de Python, Git ni dependencias adicionales.
- **Conectividad:** 100% offline (el cómputo y renderizado se ejecutan de forma local).
- **Almacenamiento:** Mínimo 500 MB libres en disco para archivos temporales de ejecución.

## Características principales

- **Motor de Eventos Discretos (DES):** Modelado de flujo de producción, cuellos de botella y capacidades operativas.
- **Análisis Estocástico (Monte Carlo):** Evaluación de variabilidad e incertidumbre en tiempos de ciclo y demanda.
- **Dashboard Interactivo:** Monitoreo y visualización en tiempo real de KPIs operativos clave:
  - Throughput (rendimiento de producción)
  - TCT — Total Cycle Time (tiempo de ciclo total)
  - WIP — Work in Process (trabajo en proceso)
- **Toma de Decisiones (DSS):** Comparativa de escenarios *What-If* para evaluar incrementos de eficiencia.
- **Exportación de Datos:** Descarga de reportes y resultados tabulares en formato Excel/CSV para análisis posterior.

## Estructura del proyecto

```
SGPP/
├── app/              # Código fuente de la aplicación (UI, simulación, lógica)
├── assets/           # Recursos estáticos (imágenes, diagramas)
├── build/            # Archivos temporales de compilación
├── config/           # Archivos de configuración y dependencias (requirements.txt)
├── dist/             # Artefactos y binarios generados
├── docs/             # Documentación técnica extendida
├── scripts/          # Scripts de automatización y empaquetado
├── .gitignore        # Exclusiones de control de versiones
├── ejecutable.bat     # Lanzador principal de la aplicación
└── README.md         # Documentación principal del repositorio
```

## Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| Alerta de Windows Defender / SmartScreen | Ejecutable empaquetado sin firma digital comercial. | Haz clic en "Más información" → "Ejecutar de todas formas" (falso positivo común). |
| No abre el navegador automáticamente | Bloqueo en la instrucción de apertura del navegador. | Abre manualmente tu navegador y entra a `http://localhost:8501` mientras la terminal siga abierta. |
| Error de "Puerto en uso" | Otra instancia de la app quedó abierta en segundo plano. | Abre el Administrador de tareas de Windows, finaliza procesos residuales de Python/SGPP y vuelve a ejecutar. |
| Inicio lento al abrir por primera vez | Descompresión inicial de dependencias en temporales. | Comportamiento normal en el primer arranque; los inicios posteriores serán más rápidos. |

## Soporte

Si algo no funciona como se espera, incluye el mensaje de error exacto y, si existe, el contenido de la ventana de consola al reportarlo.

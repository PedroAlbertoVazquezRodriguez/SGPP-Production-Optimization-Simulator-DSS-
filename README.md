# SGPP-Production-Optimization-Simulator-DSS-
Plataforma integral (Decision Support System) para la simulación, análisis estocástico y optimización de procesos productivos. Desarrollada en Python y empaquetada para Windows como una solución lista para usar, sin necesidad de instalaciones previas ni configuración de dependencias.

---

## Inicio Rápido

1. Descarga o clona este repositorio en tu equipo.
2. Ejecuta el archivo principal haciendo doble clic en:
   ```bash
   ejecutable.bat
El sistema levantará automáticamente el servidor local y abrirá la interfaz interactiva en tu navegador predeterminado (usualmente en http://localhost:8501).Nota: No cierres la ventana de consola/terminal que se abre en segundo plano; este proceso mantiene la aplicación en ejecución. Para salir, simplemente cierra la consola.Requisitos del SistemaSistema Operativo: Windows 10 / Windows 11 (64-bit).Entorno: No requiere instalación previa de Python, Git ni dependencias adicionales.Conectividad: 100% offline (el cómputo y renderizado se ejecutan de forma local).Almacenamiento: Mínimo 500 MB libres en disco para archivos temporales de ejecución.Características PrincipalesMotor de Eventos Discretos (DES): Modelado de flujo de producción, cuellos de botella y capacidades operativas.Análisis Estocástico (Monte Carlo): Evaluación de variabilidad e incertidumbre en tiempos de ciclo y demanda.Dashboard Interactivo: Monitoreo y visualización en tiempo real de KPIs operativos clave:Throughput (Rendimiento de producción)TCT (Total Cycle Time / Tiempo de ciclo total)WIP (Work in Process / Trabajo en proceso)Toma de Decisiones (DSS): Comparativa de escenarios What-If para evaluar incrementos de eficiencia.Exportación de Datos: Descarga de reportes y resultados tabulares en formato Excel/CSV para análisis posterior.Estructura del ProyectoPlaintextSGPP/
├── app/                  # Código fuente de la aplicación (UI, simulación, lógica)
├── assets/               # Recursos estáticos (imágenes, diagramas)
├── build/                # Archivos temporales de compilación
├── config/               # Archivos de configuración y dependencias (requirements.txt)
├── dist/                 # Artefactos y binarios generados
├── docs/                 # Documentación técnica extendida
├── scripts/              # Scripts de automatización y empaquetado
├── .gitignore            # Exclusiones de control de versiones
├── ejecutable.bat        # Lanzador principal de la aplicación
└── README.md             # Documentación principal del repositorio
Solución de ProblemasProblemaCausa ProbableSoluciónAlerta de Windows Defender / SmartScreenEjecutable empaquetado sin firma digital comercial.Haz clic en "Más información" -> "Ejecutar de todas formas" (falso positivo común).No abre el navegador automáticamenteBloqueo en la instrucción de apertura del navegador.Abre manualmente tu navegador y entra a http://localhost:8501 mientras la terminal siga abierta.Error de "Puerto en uso"Otra instancia de la app quedó abierta en segundo plano.Abre el Administrador de tareas de Windows, finaliza procesos residuales de Python/SGPP y vuelve a ejecutar.Inicio lento al abrir por primera vezDescompresión inicial de dependencias en temporales.Comportamiento normal en el primer arranque; los inicios posteriores serán más rápidos.

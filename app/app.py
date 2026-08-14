"""
Sistema de Gestión y Programación de Proyectos (SGPP)
Aplicación Streamlit con diseño Bootstrap 5
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
from simulation import ejecutar_simulacion
from utils import (
    crear_grafico_utilizacion,
    crear_grafico_wip,
    crear_grafico_comparacion_throughput,
    crear_grafico_ahorro_economico,
    crear_semaforo_operacional,
    calcular_recomendaciones,
    calcular_estrategia_operarios,
    obtener_supuestos_modelo,
    crear_grafico_tct_por_modelo,
    crear_grafico_throughput_tiempo,
    crear_visualizacion_linea_produccion,
    crear_grafico_retrabajo,
    crear_animacion_linea_produccion,
    crear_animacion_banda_transportadora_html,
    crear_grafico_comparacion_tiempo_real,
    crear_grafico_productos_completados,
    crear_grafico_velocidad_produccion,
    crear_graficas_tiempo_real_produccion,
    exportar_resultados_excel,
    guardar_historial_simulacion,
    cargar_historial_simulaciones,
    calcular_costos_detallados,
    optimizacion_automatica,
    crear_grafico_comparacion_optimizaciones,
    importar_datos_excel,
    analisis_riesgos,
    analisis_predictivo,
    crear_grafico_analisis_riesgos,
    crear_grafico_prediccion
)

# Configuración de la página
st.set_page_config(
    page_title="SGPP - Sistema de Gestión y Programación de Proyectos",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS y estilos personalizados (funciona sin internet)
st.markdown("""
<style>
    /* Estilos base sin dependencias externas */
    * {
        box-sizing: border-box;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        line-height: 1.5;
    }
    
    .main-header {
        background: linear-gradient(135deg, #6b7280 0%, #374151 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        color: #212529;
    }
    
    .metric-card h5 {
        color: #212529;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .metric-card ul {
        color: #495057;
        margin-left: 1.5rem;
        margin-bottom: 0;
    }
    
    .metric-card ul li {
        color: #495057;
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    
    .metric-card p {
        color: #6c757d;
        margin-top: 1rem;
        margin-bottom: 0;
    }
    
    .semaforo {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
    }
    
    .semaforo-red { background-color: #dc3545; }
    .semaforo-orange { background-color: #ffc107; }
    .semaforo-green { background-color: #28a745; }
    
    .recommendation-card {
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid;
        color: #212529;
    }
    
    .recommendation-card h5 {
        color: #212529;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .recommendation-card p {
        color: #495057;
        margin-bottom: 0;
        line-height: 1.6;
    }
    
    .recommendation-success {
        background-color: #d4edda;
        border-color: #28a745;
    }
    
    .recommendation-info {
        background-color: #d1ecf1;
        border-color: #17a2b8;
    }
    
    .recommendation-warning {
        background-color: #fff3cd;
        border-color: #ffc107;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    
    .stButton > button {
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #c82333;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
    }
    
    .stButton > button:active {
        background-color: #bd2130;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>SGPP - Sistema de Gestión y Programación de Proyectos</h1>
    <p class="mb-0">Sistema de Soporte a Decisiones (DSS) para Gestión y Programación de Proyectos</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Panel de Control Global
with st.sidebar:
    # Logo en la parte superior del sidebar
    # Intentar encontrar el logo en diferentes ubicaciones posibles
    logo_paths = [
        "assets/ss.png",  # Desde la raíz del proyecto (ejecución normal)
        "../assets/ss.png",  # Desde app/ (si se ejecuta desde app/)
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "ss.png")  # Ruta absoluta
    ]
    logo_encontrado = False
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                st.image(logo_path, use_container_width=True)
                logo_encontrado = True
                break
            except Exception as e:
                continue
    
    st.markdown("---")  # Línea separadora
    st.header("Panel de Control")
    
    st.subheader("Parámetros de Simulación")
    horizonte_dias = st.slider(
        "Horizonte de Simulación (días)",
        min_value=7,
        max_value=90,
        value=30,
        step=7,
        help="Período de tiempo a simular"
    )
    
    # Cambiar a unidades en lugar de proporción
    paneles_estandar = st.slider(
        "Cantidad de Paneles Estándar por Día",
        min_value=0,
        max_value=100,
        value=30,
        step=5,
        help="Número de paneles estándar que se procesan por día"
    )
    
    paneles_grandes = st.slider(
        "Cantidad de Paneles Grandes por Día",
        min_value=0,
        max_value=100,
        value=20,
        step=5,
        help="Número de paneles grandes que se procesan por día"
    )
    
    # Calcular proporción para la simulación
    total_paneles_dia = paneles_estandar + paneles_grandes
    mix_estandar = paneles_estandar / total_paneles_dia if total_paneles_dia > 0 else 0.6
    
    st.subheader("Distribución de Modelos (unidades por día)")
    mix_u = st.slider("Modelo U (unidades/día)", 0, 50, 20, 1)
    mix_v = st.slider("Modelo V (unidades/día)", 0, 50, 15, 1)
    mix_lambrin = st.slider("Modelo Lambrín (unidades/día)", 0, 50, 10, 1)
    mix_suspendido = st.slider("Modelo Suspendido (unidades/día)", 0, 50, 5, 1)
    
    # Calcular proporción de modelos basado en unidades
    total_modelos_dia = mix_u + mix_v + mix_lambrin + mix_suspendido
    if total_modelos_dia > 0:
        mix_modelos = {
            'U': mix_u / total_modelos_dia,
            'V': mix_v / total_modelos_dia,
            'Lambrín': mix_lambrin / total_modelos_dia,
            'Suspendido': mix_suspendido / total_modelos_dia
        }
        # Guardar cantidades para usar en simulación
        cantidades_modelos = {
            'U': mix_u,
            'V': mix_v,
            'Lambrín': mix_lambrin,
            'Suspendido': mix_suspendido
        }
    else:
        mix_modelos = {'U': 0.4, 'V': 0.3, 'Lambrín': 0.2, 'Suspendido': 0.1}
        cantidades_modelos = {'U': 20, 'V': 15, 'Lambrín': 10, 'Suspendido': 5}
    
    # Asegurar que las variables estén disponibles globalmente en el contexto
    st.session_state['paneles_estandar'] = paneles_estandar
    st.session_state['paneles_grandes'] = paneles_grandes
    st.session_state['cantidades_modelos'] = cantidades_modelos
    
    # Usar lambda (λ) en lugar de "Seed"
    seed = st.number_input(
        "λ (Reproducibilidad)",
        min_value=1,
        max_value=10000,
        value=42,
        step=1,
        help="Semilla para resultados reproducibles"
    )
    
    st.divider()
    
    st.subheader("Opciones de Optimización")
    priorizar_setup = st.checkbox(
        "Opción A: Priorización de Órdenes",
        help="Minimiza cambios de tamaño de lote (mitigación de setup)"
    )
    
    aislamiento_retrabajo = st.checkbox(
        "Opción B: Aislamiento de Retrabajo",
        help="Asignación dinámica de personal (libera 7-8% de capacidad)"
    )
    
    flujo_paralelo = st.checkbox(
        "Opción C: Configuración Paralela",
        help="Cambia el flujo de Secuencial a Paralelo"
    )

# Cache para resultados de simulación
@st.cache_data
def ejecutar_simulacion_cacheada(horizonte_dias, mix_estandar, mix_modelos, seed, 
                                  flujo_paralelo, priorizar_setup, aislamiento_retrabajo,
                                  paneles_estandar=30, paneles_grandes=20, 
                                  cantidades_modelos=None):
    """Ejecuta simulación con cache para evitar recálculos"""
    return ejecutar_simulacion(
        horizonte_dias=horizonte_dias,
        mix_estandar=mix_estandar,
        mix_modelos=mix_modelos,
        seed=seed,
        flujo_paralelo=flujo_paralelo,
        priorizar_setup=priorizar_setup,
        aislamiento_retrabajo=aislamiento_retrabajo,
        paneles_estandar=paneles_estandar,
        paneles_grandes=paneles_grandes,
        cantidades_modelos=cantidades_modelos
    )

# Pestañas principales
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Modelo Base", 
    "Optimización y DSS", 
    "Validación",
    "Gráficas",
    "Visualización de línea de producción",
    "Análisis Avanzado",
    "Importar/Exportar"
])

# PESTAÑA 1: MODELO BASE
with tab1:
    st.header("Análisis del Modelo Base (Sistema Actual)")
    st.markdown("""
    <p class="lead">Visualización y validación del rendimiento del sistema actual (secuencial)</p>
    """, unsafe_allow_html=True)
    
    if st.button("Ejecutar Simulación Base", type="primary"):
        with st.spinner("Ejecutando simulación del modelo base..."):
            metricas_base = ejecutar_simulacion_cacheada(
                horizonte_dias=horizonte_dias,
                mix_estandar=mix_estandar,
                mix_modelos=mix_modelos,
                seed=seed,
                flujo_paralelo=False,
                priorizar_setup=False,
                aislamiento_retrabajo=False,
                paneles_estandar=paneles_estandar,
                paneles_grandes=paneles_grandes,
                cantidades_modelos=cantidades_modelos
            )
            st.session_state['metricas_base'] = metricas_base
            
            # Guardar en historial
            configuracion = {
                'horizonte_dias': horizonte_dias,
                'mix_estandar': mix_estandar,
                'mix_modelos': mix_modelos,
                'seed': seed,
                'tipo': 'Modelo Base'
            }
            guardar_historial_simulacion(configuracion, metricas_base)
    
    if 'metricas_base' in st.session_state:
        metricas = st.session_state['metricas_base']
        
        # KPIs Críticos
        st.subheader("KPIs Críticos del Sistema")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Throughput Actual",
                value=f"{metricas.get('throughput_dia', 0):.0f}",
                delta="piezas/día"
            )
        
        with col2:
            st.metric(
                label="TCT Promedio",
                value=f"{metricas.get('tct_promedio', 0):.1f}",
                delta="minutos"
            )
        
        with col3:
            st.metric(
                label="Pérdida de Capacidad",
                value=f"{metricas.get('perdida_capacidad', 0):.1f}%",
                delta="por retrabajo"
            )
        
        with col4:
            st.metric(
                label="WIP Promedio",
                value=f"{metricas.get('wip_promedio', 0):.1f}",
                delta="lotes"
            )
        
        st.divider()
        
        # Gráfico de Utilización de Recursos
        st.subheader("Gráfico de Cuellos de Botella - Utilización de Recursos")
        fig_utilizacion = crear_grafico_utilizacion(
            metricas, 
            "Utilización de Recursos por Estación (%)"
        )
        st.plotly_chart(fig_utilizacion, use_container_width=True, key="grafico_utilizacion_base")
        
        # Análisis de cuello de botella
        if 'utilizacion' in metricas:
            utilizacion = metricas['utilizacion']
            max_util = max(utilizacion.values())
            cpb = [k for k, v in utilizacion.items() if v == max_util][0]
            
            st.info(f"**Cuello de Botella Identificado:** {cpb} con {max_util:.1f}% de utilización")
            
            if cpb == 'Ensamblaje':
                st.warning("Ensamblaje es el cuello de botella principal. La inactividad en esta estación puede ser del 20-30%.")
        
        st.divider()
        
        # Gráfico de WIP
        st.subheader("Inventario en Proceso (WIP) - Acumulación de Lotes")
        if 'wip_historial' in metricas and metricas['wip_historial']:
            fig_wip = crear_grafico_wip(metricas['wip_historial'])
            st.plotly_chart(fig_wip, use_container_width=True, key="grafico_wip_base")
            
            # Análisis de WIP
            wip_max = max([w['wip'] for w in metricas['wip_historial']])
            cola_corte = max([w['corte_cola'] for w in metricas['wip_historial']])
            cola_ensamblaje = max([w['ensamblaje_cola'] for w in metricas['wip_historial']])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cola Máxima en Corte", f"{cola_corte:.0f} lotes")
            with col2:
                st.metric("Cola Máxima en Ensamblaje", f"{cola_ensamblaje:.0f} lotes")
            
            st.info(f"**Observación:** La cola antes de Corte típicamente contiene 10-15 lotes, y la acumulación en Ensamblaje/Calidad puede alcanzar aproximadamente 40 paneles.")
        else:
            st.warning("No hay datos de WIP disponibles para esta simulación.")

# PESTAÑA 2: OPTIMIZACIÓN Y DSS
with tab2:
    st.header("Optimización y Sistema de Soporte a Decisiones")
    st.markdown("""
    <p class="lead">Ejecuta escenarios de optimización y obtén recomendaciones operacionales</p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Ejecutar Simulación Optimizada", type="primary"):
            with st.spinner("Ejecutando simulación optimizada..."):
                # Si ninguna opción está seleccionada, activar todas las optimizaciones por defecto
                # para que realmente haya una diferencia con el modelo base
                usar_flujo_paralelo = flujo_paralelo if (flujo_paralelo or priorizar_setup or aislamiento_retrabajo) else True
                usar_priorizar_setup = priorizar_setup if (flujo_paralelo or priorizar_setup or aislamiento_retrabajo) else True
                usar_aislamiento_retrabajo = aislamiento_retrabajo if (flujo_paralelo or priorizar_setup or aislamiento_retrabajo) else True
                
                metricas_optimizado = ejecutar_simulacion_cacheada(
                    horizonte_dias=horizonte_dias,
                    mix_estandar=mix_estandar,
                    mix_modelos=mix_modelos,
                    seed=seed,
                    flujo_paralelo=usar_flujo_paralelo,
                    priorizar_setup=usar_priorizar_setup,
                    aislamiento_retrabajo=usar_aislamiento_retrabajo,
                    paneles_estandar=paneles_estandar,
                    paneles_grandes=paneles_grandes,
                    cantidades_modelos=cantidades_modelos
                )
                st.session_state['metricas_optimizado'] = metricas_optimizado
                
                # Guardar en historial (usar las opciones reales aplicadas)
                configuracion = {
                    'horizonte_dias': horizonte_dias,
                    'mix_estandar': mix_estandar,
                    'mix_modelos': mix_modelos,
                    'seed': seed,
                    'flujo_paralelo': usar_flujo_paralelo,
                    'priorizar_setup': usar_priorizar_setup,
                    'aislamiento_retrabajo': usar_aislamiento_retrabajo,
                    'tipo': 'Optimizado'
                }
                guardar_historial_simulacion(configuracion, metricas_optimizado)
                
                # Mostrar mensaje si se activaron optimizaciones por defecto
                if not (flujo_paralelo or priorizar_setup or aislamiento_retrabajo):
                    st.info("Se activaron automáticamente todas las optimizaciones (Flujo Paralelo, Priorización de Setup, y Aislamiento de Retrabajo) para mostrar mejoras con respecto al modelo base.")
    
    with col2:
        if st.button("Comparar con Modelo Base"):
            if 'metricas_base' not in st.session_state:
                st.warning("Primero ejecuta la simulación del modelo base en la pestaña anterior.")
    
    if 'metricas_optimizado' in st.session_state:
        metricas_opt = st.session_state['metricas_optimizado']
        
        # KPIs de la configuración optimizada
        st.subheader("Métricas de la Configuración Optimizada")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Throughput Optimizado",
                value=f"{metricas_opt.get('throughput_dia', 0):.0f}",
                delta="piezas/día"
            )
        
        with col2:
            st.metric(
                label="TCT Optimizado",
                value=f"{metricas_opt.get('tct_promedio', 0):.1f}",
                delta="minutos"
            )
        
        with col3:
            st.metric(
                label="Pérdida de Capacidad",
                value=f"{metricas_opt.get('perdida_capacidad', 0):.1f}%",
                delta="por retrabajo"
            )
        
        with col4:
            st.metric(
                label="Paneles Completados",
                value=f"{metricas_opt.get('paneles_completados', 0):.0f}",
                delta="unidades"
            )
        
        st.divider()
        
        # Comparación si hay modelo base
        if 'metricas_base' in st.session_state:
            metricas_base = st.session_state['metricas_base']
            
            st.subheader("Comparación: Modelo Base vs. Configuración Óptima")
            
            # Gráfico de comparación de throughput
            fig_comparacion = crear_grafico_comparacion_throughput(metricas_base, metricas_opt)
            st.plotly_chart(fig_comparacion, use_container_width=True, key="grafico_comparacion_throughput")
            
            # Mejora de throughput
            mejora_throughput = ((metricas_opt.get('throughput_dia', 0) - 
                                 metricas_base.get('throughput_dia', 0)) / 
                                metricas_base.get('throughput_dia', 1)) * 100
            
            st.success(f"**Mejora de Throughput:** {mejora_throughput:.1f}% (de {metricas_base.get('throughput_dia', 0):.0f} a {metricas_opt.get('throughput_dia', 0):.0f} piezas/día)")
            
            st.divider()
            
            # Gráfico de ahorro económico
            st.subheader("Análisis de Ahorro Económico")
            fig_ahorro = crear_grafico_ahorro_economico(metricas_base, metricas_opt)
            st.plotly_chart(fig_ahorro, use_container_width=True, key="grafico_ahorro_economico")
            
            # Cálculo de ahorro
            tct_base = metricas_base.get('tct_promedio', 0)
            tct_opt = metricas_opt.get('tct_promedio', 0)
            reduccion_tct = ((tct_base - tct_opt) / tct_base * 100) if tct_base > 0 else 0
            ahorro_cpu = (tct_base - tct_opt) * 5.00  # $5.00 por minuto
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Reducción de TCT", f"{reduccion_tct:.1f}%")
            with col2:
                st.metric("Ahorro en CPU", f"${ahorro_cpu:.2f} MXN/pieza")
            
            st.divider()
            
            # Módulo DSS: Recomendaciones
            st.subheader("Recomendaciones Operacionales (DSS)")
            recomendaciones = calcular_recomendaciones(metricas_base, metricas_opt)
            
            if recomendaciones:
                for rec in recomendaciones:
                    clase_css = f"recommendation-{rec['tipo']}"
                    st.markdown(f"""
                    <div class="recommendation-card {clase_css}">
                        <h5>{rec['titulo']}</h5>
                        <p>{rec['descripcion']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Ejecuta diferentes escenarios de optimización para obtener recomendaciones específicas.")
            
            # Estrategia óptima para asignación de operarios (dinámica basada en configuración)
            estrategia = calcular_estrategia_operarios(
                metricas_opt,
                flujo_paralelo=flujo_paralelo,
                priorizar_setup=priorizar_setup,
                aislamiento_retrabajo=aislamiento_retrabajo,
                mix_estandar=mix_estandar
            )
            razon = estrategia.get('razon', 'Asignación basada en utilización actual')
            st.markdown(f"""
            <div class="metric-card" style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem; border-left: 4px solid #667eea;">
                <h5 style="color: #212529; font-weight: 600; margin-bottom: 1rem; font-size: 1.1rem;">Estrategia Óptima para Asignación de 15 Operarios</h5>
                <ul style="color: #212529; margin-left: 1.5rem; margin-bottom: 0;">
                    <li style="color: #212529; margin-bottom: 0.75rem; line-height: 1.6;"><strong style="color: #212529;">Ensamblaje (CPB):</strong> Asignar {estrategia['ensamblaje']} operarios para maximizar throughput (Utilización: {metricas_opt.get('utilizacion', {}).get('Ensamblaje', 0):.1f}%)</li>
                    <li style="color: #212529; margin-bottom: 0.75rem; line-height: 1.6;"><strong style="color: #212529;">Corte:</strong> {estrategia['corte']} operarios (Utilización: {metricas_opt.get('utilizacion', {}).get('Corte', 0):.1f}%)</li>
                    <li style="color: #212529; margin-bottom: 0.75rem; line-height: 1.6;"><strong style="color: #212529;">Tapizado:</strong> {estrategia['tapizado']} operarios (Utilización: {metricas_opt.get('utilizacion', {}).get('Tapizado', 0):.1f}%)</li>
                    <li style="color: #212529; margin-bottom: 0.75rem; line-height: 1.6;"><strong style="color: #212529;">Calidad:</strong> {estrategia['calidad']} operarios (Utilización: {metricas_opt.get('utilizacion', {}).get('Calidad', 0):.1f}%)</li>
                    <li style="color: #212529; margin-bottom: 0.75rem; line-height: 1.6;"><strong style="color: #212529;">Reserva:</strong> {estrategia['reserva']} operarios para retrabajo y contingencias</li>
                </ul>
                <p style="margin-top: 1rem; color: #6c757d; font-size: 0.9em; margin-bottom: 0;"><em>{razon}</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Semáforo Operacional
            st.subheader("Semáforo Operacional - Estado en Tiempo Real")
            semaforos = crear_semaforo_operacional(metricas_opt)
            
            cols = st.columns(len(semaforos))
            for idx, (estacion, estado) in enumerate(semaforos.items()):
                with cols[idx]:
                    color_class = f"semaforo-{estado['color']}"
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="semaforo {color_class}"></div>
                        <h6>{estacion}</h6>
                        <p style="font-size: 0.9em;">{estado['mensaje']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Explicación del semáforo
            st.markdown("""
            <div class="alert alert-info" role="alert">
                <strong>Interpretación del Semáforo:</strong><br>
                <strong>Verde:</strong> Operación normal o riesgo de inactividad (aumentar ritmo)<br>
                <strong>Amarillo:</strong> Carga moderada - monitorear<br>
                <strong>Rojo:</strong> Alta carga o sobrecarga - reducir velocidad o desviar lote
            </div>
            """, unsafe_allow_html=True)

# PESTAÑA 3: VALIDACIÓN
with tab3:
    st.header("Validación del Modelo")
    st.markdown("""
    <p class="lead">Comparación de métricas operacionales del modelo contra datos históricos</p>
    """, unsafe_allow_html=True)
    
    st.subheader("Comparación con Datos Históricos (Marzo 2025)")
    
    # Datos históricos de ejemplo (el usuario puede modificar)
    st.markdown("### Datos Históricos de Referencia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h5>Datos Históricos - Marzo 2025</h5>
            <ul>
                <li><strong>Throughput Promedio:</strong> 320 piezas/día</li>
                <li><strong>TCT Promedio:</strong> 150 minutos</li>
                <li><strong>Utilización Ensamblaje:</strong> 85%</li>
                <li><strong>WIP Promedio:</strong> 12 lotes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'metricas_base' in st.session_state:
            metricas = st.session_state['metricas_base']
            st.markdown("""
            <div class="metric-card">
                <h5>Resultados del Modelo de Simulación</h5>
                <ul>
                    <li><strong>Throughput Promedio:</strong> {:.0f} piezas/día</li>
                    <li><strong>TCT Promedio:</strong> {:.1f} minutos</li>
                    <li><strong>Utilización Ensamblaje:</strong> {:.1f}%</li>
                    <li><strong>WIP Promedio:</strong> {:.1f} lotes</li>
                </ul>
            </div>
            """.format(
                metricas.get('throughput_dia', 0),
                metricas.get('tct_promedio', 0),
                metricas.get('utilizacion', {}).get('Ensamblaje', 0),
                metricas.get('wip_promedio', 0)
            ), unsafe_allow_html=True)
    
    # Tabla comparativa
    if 'metricas_base' in st.session_state:
        metricas = st.session_state['metricas_base']
        
        datos_historicos = {
            'Métrica': ['Throughput (piezas/día)', 'TCT Promedio (min)', 
                       'Utilización Ensamblaje (%)', 'WIP Promedio (lotes)'],
            'Datos Históricos': [320, 150, 85, 12],
            'Modelo Simulación': [
                metricas.get('throughput_dia', 0),
                metricas.get('tct_promedio', 0),
                metricas.get('utilizacion', {}).get('Ensamblaje', 0),
                metricas.get('wip_promedio', 0)
            ]
        }
        
        df_comparacion = pd.DataFrame(datos_historicos)
        df_comparacion['Diferencia %'] = ((df_comparacion['Modelo Simulación'] - 
                                          df_comparacion['Datos Históricos']) / 
                                         df_comparacion['Datos Históricos'] * 100).round(2)
        
        st.dataframe(df_comparacion, use_container_width=True)
        
        # Análisis de validación
        st.subheader("Análisis de Validación")
        diferencias_aceptables = (df_comparacion['Diferencia %'].abs() < 15).all()
        
        if diferencias_aceptables:
            st.success("**Validación Exitosa:** Las métricas del modelo están dentro del rango aceptable (±15%) respecto a los datos históricos.")
        else:
            st.warning("**Validación con Discrepancias:** Algunas métricas difieren significativamente de los datos históricos. Revisar parámetros del modelo.")
    
    st.divider()
    
    # Documentación de Supuestos
    st.subheader("Documentación de Supuestos del Modelo")
    supuestos_df = obtener_supuestos_modelo()
    st.dataframe(supuestos_df, use_container_width=True, hide_index=True)
    
    st.markdown("""
    <div class="alert alert-secondary" role="alert">
        <h5>Notas Adicionales:</h5>
        <ul>
            <li>Los tiempos de servicio siguen distribuciones exponenciales con variabilidad según el tipo de panel</li>
            <li>El retrabajo se modela con distribución Poisson y afecta principalmente la estación de Ensamblaje</li>
            <li>La capacidad del sistema está limitada por el cuello de botella (Ensamblaje)</li>
            <li>Los tiempos de setup no están explícitamente modelados pero se reflejan en la variabilidad de tiempos</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# PESTAÑA 4: GRÁFICAS
with tab4:
    st.header("Gráficas Detalladas")
    st.markdown("""
    <p class="lead">Visualización avanzada de métricas y análisis del sistema de producción</p>
    """, unsafe_allow_html=True)
    
    if 'metricas_base' in st.session_state:
        metricas = st.session_state['metricas_base']
        paneles_data = metricas.get('paneles_data', [])
        
        # Gráfico de TCT por Modelo
        st.subheader("Distribución de TCT por Modelo")
        if paneles_data:
            fig_tct_modelo = crear_grafico_tct_por_modelo(paneles_data)
            st.plotly_chart(fig_tct_modelo, use_container_width=True, key="grafico_tct_modelo")
        else:
            st.info("Ejecuta una simulación primero para ver los gráficos.")
        
        st.divider()
        
        # Gráfico de Throughput en el Tiempo
        st.subheader("Throughput Acumulado")
        if paneles_data:
            fig_throughput = crear_grafico_throughput_tiempo(paneles_data)
            st.plotly_chart(fig_throughput, use_container_width=True, key="grafico_throughput_tiempo")
        else:
            st.info("Ejecuta una simulación primero para ver los gráficos.")
        
        st.divider()
        
        # Gráfico de Retrabajo
        st.subheader("Análisis de Retrabajo")
        if paneles_data:
            fig_retrabajo = crear_grafico_retrabajo(paneles_data)
            st.plotly_chart(fig_retrabajo, use_container_width=True, key="grafico_retrabajo")
        else:
            st.info("Ejecuta una simulación primero para ver los gráficos.")
        
        st.divider()
        
        # Gráfico de Utilización (duplicado pero útil aquí)
        st.subheader("Utilización de Recursos")
        fig_util = crear_grafico_utilizacion(metricas, "Utilización de Recursos por Estación")
        st.plotly_chart(fig_util, use_container_width=True, key="grafico_utilizacion_graficas")
        
        st.divider()
        
        # Gráfico de WIP
        st.subheader("Inventario en Proceso (WIP)")
        if 'wip_historial' in metricas and metricas['wip_historial']:
            fig_wip = crear_grafico_wip(metricas['wip_historial'])
            st.plotly_chart(fig_wip, use_container_width=True, key="grafico_wip_graficas")
        else:
            st.info("No hay datos de WIP disponibles para esta simulación.")
    else:
        st.warning("Primero ejecuta la simulación del modelo base en la pestaña 'Modelo Base' para ver los gráficos.")

# PESTAÑA 5: VISUALIZACIÓN DE LÍNEA DE PRODUCCIÓN
with tab5:
    st.header("Visualización de Línea de Producción")
    st.markdown("""
    <p class="lead">Animación interactiva de la línea de producción con banda transportadora</p>
    """, unsafe_allow_html=True)
    
    # Sección de animación interactiva de banda transportadora
    st.markdown("""
    <style>
        .animacion-controls {
            background: linear-gradient(135deg, #212529 0%, #343a40 100%);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3), inset 0 1px 2px rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stNumberInput > div > div > input {
            background-color: #495057 !important;
            color: #fff !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            border-radius: 8px !important;
        }
        .stNumberInput > div > div > input:focus {
            border-color: #0d6efd !important;
            box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25) !important;
        }
        .stNumberInput label {
            color: #adb5bd !important;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("Animación de Banda Transportadora")
    
    # Contenedor para controles con diseño Bootstrap 5
    with st.container():
        st.markdown('<div class="animacion-controls">', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            num_productos_input = st.number_input(
                "Cantidad de productos a procesar",
                min_value=1,
                max_value=100,
                value=10,
                step=1,
                key="num_productos_input",
                help="Ingrese cuántos productos desea procesar en la simulación"
            )
        
        with col2:
            iniciar_clicked = st.button("Iniciar Simulación", type="primary", use_container_width=True)
            if st.session_state.get('animacion_activa', False):
                reiniciar_clicked = st.button("Reiniciar", key="reiniciar_btn", use_container_width=True)
            else:
                reiniciar_clicked = False
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Inicializar variables de animación si no existen (para ambas bandas)
    if 'animacion_activa' not in st.session_state:
        st.session_state['animacion_activa'] = False
    if 'productos_total' not in st.session_state:
        st.session_state['productos_total'] = 10
    
    # Variables para la primera banda
    if 'productos_entran_1' not in st.session_state:
        st.session_state['productos_entran_1'] = 0
    if 'productos_salen_1' not in st.session_state:
        st.session_state['productos_salen_1'] = 0
    if 'tiempo_transcurrido_1' not in st.session_state:
        st.session_state['tiempo_transcurrido_1'] = 0.0
    if 'simulacion_finalizada_1' not in st.session_state:
        st.session_state['simulacion_finalizada_1'] = False
    
    # Variables para la segunda banda
    if 'productos_entran_2' not in st.session_state:
        st.session_state['productos_entran_2'] = 0
    if 'productos_salen_2' not in st.session_state:
        st.session_state['productos_salen_2'] = 0
    if 'tiempo_transcurrido_2' not in st.session_state:
        st.session_state['tiempo_transcurrido_2'] = 0.0
    if 'simulacion_finalizada_2' not in st.session_state:
        st.session_state['simulacion_finalizada_2'] = False
    
    # Estado combinado
    if 'simulacion_finalizada' not in st.session_state:
        st.session_state['simulacion_finalizada'] = False
    
    # Historial para gráficas en tiempo real
    if 'historial_graficas' not in st.session_state:
        st.session_state['historial_graficas'] = {
            'tiempo': [],
            'productos_salen_secuencial': [],
            'productos_salen_parallel': [],
            'productos_entran_secuencial': [],
            'productos_entran_parallel': []
        }
    
    # Manejar botón de iniciar
    if iniciar_clicked:
        st.session_state['animacion_activa'] = True
        st.session_state['productos_total'] = num_productos_input
        
        # Inicializar primera banda
        st.session_state['productos_entran_1'] = 0
        st.session_state['productos_salen_1'] = 0
        st.session_state['tiempo_inicio_1'] = None
        st.session_state['tiempo_transcurrido_1'] = 0.0
        st.session_state['simulacion_finalizada_1'] = False
        
        # Inicializar segunda banda
        st.session_state['productos_entran_2'] = 0
        st.session_state['productos_salen_2'] = 0
        st.session_state['tiempo_inicio_2'] = None
        st.session_state['tiempo_transcurrido_2'] = 0.0
        st.session_state['simulacion_finalizada_2'] = False
        
        # Reiniciar historial de gráficas
        st.session_state['historial_graficas'] = {
            'tiempo': [],
            'productos_salen_secuencial': [],
            'productos_salen_parallel': [],
            'productos_entran_secuencial': [],
            'productos_entran_parallel': []
        }
        
        st.session_state['simulacion_finalizada'] = False
        st.rerun()
    
    # Manejar botón de reiniciar
    if reiniciar_clicked:
        st.session_state['animacion_activa'] = False
        
        # Reiniciar primera banda
        st.session_state['productos_entran_1'] = 0
        st.session_state['productos_salen_1'] = 0
        st.session_state['tiempo_inicio_1'] = None
        st.session_state['tiempo_transcurrido_1'] = 0.0
        st.session_state['simulacion_finalizada_1'] = False
        
        # Reiniciar segunda banda
        st.session_state['productos_entran_2'] = 0
        st.session_state['productos_salen_2'] = 0
        st.session_state['tiempo_inicio_2'] = None
        st.session_state['tiempo_transcurrido_2'] = 0.0
        st.session_state['simulacion_finalizada_2'] = False
        
        # Reiniciar historial de gráficas
        st.session_state['historial_graficas'] = {
            'tiempo': [],
            'productos_salen_secuencial': [],
            'productos_salen_parallel': [],
            'productos_entran_secuencial': [],
            'productos_entran_parallel': []
        }
        
        st.session_state['simulacion_finalizada'] = False
        st.rerun()
    
    # Contenedor para la animación que se actualiza dinámicamente
    animacion_container = st.empty()
    
    # Mostrar animación si está activa
    if st.session_state['animacion_activa']:
        import time
        
        # Lógica para primera banda
        if st.session_state.get('tiempo_inicio_1') is None:
            st.session_state['tiempo_inicio_1'] = time.time()
            # Inicializar historial con punto inicial
            historial = st.session_state['historial_graficas']
            historial['tiempo'].append(0.0)
            historial['productos_salen_secuencial'].append(0)
            historial['productos_salen_parallel'].append(0)
            historial['productos_entran_secuencial'].append(0)
            historial['productos_entran_parallel'].append(0)
        
        tiempo_inicio_1 = st.session_state['tiempo_inicio_1']
        tiempo_actual_1 = time.time()
        st.session_state['tiempo_transcurrido_1'] = tiempo_actual_1 - tiempo_inicio_1
        
        intervalo_entrada = 2.0
        productos_que_deben_entrar_1 = min(
            int(st.session_state['tiempo_transcurrido_1'] / intervalo_entrada) + 1,
            st.session_state['productos_total']
        )
        st.session_state['productos_entran_1'] = productos_que_deben_entrar_1
        
        tiempo_para_primer_producto = 5.0
        if st.session_state['tiempo_transcurrido_1'] >= tiempo_para_primer_producto:
            tiempo_procesamiento_1 = st.session_state['tiempo_transcurrido_1'] - tiempo_para_primer_producto
            productos_que_deben_salir_1 = min(
                int(tiempo_procesamiento_1 / 3.0) + 1,
                st.session_state['productos_entran_1']
            )
            st.session_state['productos_salen_1'] = productos_que_deben_salir_1
        else:
            st.session_state['productos_salen_1'] = 0
        
        if (st.session_state['productos_salen_1'] >= st.session_state['productos_total'] and
            st.session_state['productos_entran_1'] >= st.session_state['productos_total']):
            st.session_state['simulacion_finalizada_1'] = True
        
        # Lógica para segunda banda (Pipeline - más rápida)
        if st.session_state.get('tiempo_inicio_2') is None:
            st.session_state['tiempo_inicio_2'] = time.time()
        tiempo_inicio_2 = st.session_state['tiempo_inicio_2']
        tiempo_actual_2 = time.time()
        st.session_state['tiempo_transcurrido_2'] = tiempo_actual_2 - tiempo_inicio_2
        
        # Pipeline: entrada más rápida (cada 1.5 segundos vs 2 segundos)
        intervalo_entrada_pipeline = 1.5
        productos_que_deben_entrar_2 = min(
            int(st.session_state['tiempo_transcurrido_2'] / intervalo_entrada_pipeline) + 1,
            st.session_state['productos_total']
        )
        st.session_state['productos_entran_2'] = productos_que_deben_entrar_2
        
        # Pipeline: procesamiento más rápido (3 segundos vs 5 para primer producto, 2 segundos vs 3 para siguientes)
        tiempo_para_primer_producto_pipeline = 3.0
        if st.session_state['tiempo_transcurrido_2'] >= tiempo_para_primer_producto_pipeline:
            tiempo_procesamiento_2 = st.session_state['tiempo_transcurrido_2'] - tiempo_para_primer_producto_pipeline
            productos_que_deben_salir_2 = min(
                int(tiempo_procesamiento_2 / 2.0) + 1,  # 2 segundos vs 3 segundos
                st.session_state['productos_entran_2']
            )
            st.session_state['productos_salen_2'] = productos_que_deben_salir_2
        else:
            st.session_state['productos_salen_2'] = 0
        
        if (st.session_state['productos_salen_2'] >= st.session_state['productos_total'] and
            st.session_state['productos_entran_2'] >= st.session_state['productos_total']):
            st.session_state['simulacion_finalizada_2'] = True
        
        # Verificar si ambas simulaciones están finalizadas
        if st.session_state['simulacion_finalizada_1'] and st.session_state['simulacion_finalizada_2']:
            st.session_state['simulacion_finalizada'] = True
        
        # Actualizar historial para gráficas en tiempo real
        historial = st.session_state['historial_graficas']
        tiempo_actual = st.session_state['tiempo_transcurrido_1']
        
        # Agregar punto solo cada 0.8 segundos aproximadamente para no saturar
        # Verificar si el historial está vacío o si ha pasado suficiente tiempo
        if not historial['tiempo'] or tiempo_actual - historial['tiempo'][-1] >= 0.8:
            historial['tiempo'].append(tiempo_actual)
            historial['productos_salen_secuencial'].append(st.session_state['productos_salen_1'])
            historial['productos_salen_parallel'].append(st.session_state['productos_salen_2'])
            historial['productos_entran_secuencial'].append(st.session_state['productos_entran_1'])
            historial['productos_entran_parallel'].append(st.session_state['productos_entran_2'])
            
            # Actualizar el estado para forzar re-render
            st.session_state['historial_graficas'] = historial
        
        # Renderizar ambas animaciones
        with animacion_container.container():
            # Primera banda (Secuencial - cajas rojas)
            html_animacion_1 = crear_animacion_banda_transportadora_html(
                num_productos=st.session_state['productos_total'],
                productos_entran=st.session_state['productos_entran_1'],
                productos_salen=st.session_state['productos_salen_1'],
                tiempo_transcurrido=st.session_state['tiempo_transcurrido_1'],
                finalizado=False,  # No mostrar mensaje individual
                auto_refresh=False,
                titulo="Línea de Producción Secuencial",
                color_cajas="#dc3545",  # Rojo para secuencial
                mostrar_tiempo=True  # Mostrar contador de tiempo
            )
            
            # Segunda banda (Pipeline - cajas verdes)
            html_animacion_2 = crear_animacion_banda_transportadora_html(
                num_productos=st.session_state['productos_total'],
                productos_entran=st.session_state['productos_entran_2'],
                productos_salen=st.session_state['productos_salen_2'],
                tiempo_transcurrido=st.session_state['tiempo_transcurrido_2'],
                finalizado=False,  # No mostrar mensaje individual
                auto_refresh=False,
                titulo="Línea de Producción Paralelo (Pipeline)",
                color_cajas="#28a745",  # Verde para pipeline
                mostrar_tiempo=True  # Mostrar contador de tiempo
            )
            
            # Contadores combinados (mostrar solo el total de productos configurado, no la suma de ambas líneas)
            total_entran = st.session_state['productos_total']  # Mostrar el número que el usuario ingresó
            total_salen = st.session_state['productos_salen_1'] + st.session_state['productos_salen_2']
            tiempo_promedio = (st.session_state['tiempo_transcurrido_1'] + st.session_state['tiempo_transcurrido_2']) / 2
            
            # Tiempos individuales de cada línea
            tiempo_secuencial = st.session_state['tiempo_transcurrido_1']
            tiempo_pipeline = st.session_state['tiempo_transcurrido_2']
            
            # Progreso individual de cada línea
            progreso_secuencial = (st.session_state['productos_salen_1'] / st.session_state['productos_total']) * 100 if st.session_state['productos_total'] > 0 else 0
            progreso_pipeline = (st.session_state['productos_salen_2'] / st.session_state['productos_total']) * 100 if st.session_state['productos_total'] > 0 else 0
            
            # Mostrar contadores combinados con estilos
            st.markdown(f"""
            <style>
                .contadores-container {{
                    display: flex;
                    justify-content: space-around;
                    gap: 15px;
                    margin: 20px 0;
                    padding: 0;
                }}
                .contador-item {{
                    text-align: center;
                    flex: 1;
                    background: linear-gradient(135deg, #212529 0%, #343a40 100%);
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3), inset 0 1px 2px rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.1);
                }}
                .contador-label {{
                    font-size: 0.85em;
                    color: #adb5bd;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-weight: 500;
                }}
                .contador-valor {{
                    font-size: 2.5em;
                    font-weight: 700;
                    color: #ffffff;
                }}
                .barra-progreso {{
                    width: 100%;
                    height: 40px;
                    background: #212529;
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 15px 0;
                    box-shadow: inset 0 4px 8px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.2);
                    border: 1px solid rgba(255,255,255,0.1);
                }}
                .barra-progreso-fill-roja {{
                    height: 100%;
                    background: linear-gradient(90deg, #dc3545 0%, #c82333 50%, #dc3545 100%);
                    background-size: 200% 100%;
                    transition: width 0.5s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: 700;
                    font-size: 1em;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                    box-shadow: 0 0 20px rgba(220, 53, 69, 0.5), inset 0 2px 4px rgba(255,255,255,0.2);
                    animation: shimmer 2s linear infinite;
                }}
                .barra-progreso-fill-verde {{
                    height: 100%;
                    background: linear-gradient(90deg, #28a745 0%, #20c997 50%, #28a745 100%);
                    background-size: 200% 100%;
                    transition: width 0.5s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: 700;
                    font-size: 1em;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                    box-shadow: 0 0 20px rgba(40, 167, 69, 0.5), inset 0 2px 4px rgba(255,255,255,0.2);
                    animation: shimmer 2s linear infinite;
                }}
                @keyframes shimmer {{
                    0% {{ background-position: 0% 0%; }}
                    100% {{ background-position: 200% 0%; }}
                }}
                .progreso-label {{
                    font-size: 0.9em;
                    color: #adb5bd;
                    margin-bottom: 5px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
            </style>
            <div class="contadores-container">
                <div class="contador-item">
                    <div class="contador-label">Productos que Entran (Total)</div>
                    <div class="contador-valor">{total_entran}</div>
                </div>
                <div class="contador-item">
                    <div class="contador-label">Productos que Salen (Total)</div>
                    <div class="contador-valor">{total_salen}</div>
                </div>
                <div class="contador-item">
                    <div class="contador-label">Tiempo Promedio</div>
                    <div class="contador-valor">{tiempo_promedio:.1f}s</div>
                </div>
            </div>
            <div style="margin-top: 25px;">
                <div class="progreso-label">Línea Secuencial</div>
                <div class="barra-progreso">
                    <div class="barra-progreso-fill-roja" style="width: {progreso_secuencial}%;">
                        {progreso_secuencial:.1f}%
                    </div>
                </div>
            </div>
            <div style="margin-top: 25px;">
                <div class="progreso-label">Línea Paralelo (Pipeline)</div>
                <div class="barra-progreso">
                    <div class="barra-progreso-fill-verde" style="width: {progreso_pipeline}%;">
                        {progreso_pipeline:.1f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Renderizar ambas animaciones
            st.markdown(html_animacion_1, unsafe_allow_html=True)
            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
            st.markdown(html_animacion_2, unsafe_allow_html=True)
            
            # Mostrar gráficas en tiempo real dentro del contenedor de animación
            if len(historial.get('tiempo', [])) > 0:
                st.markdown("---")
                st.subheader("Gráficas en Tiempo Real")
                
                # Crear historial actualizado con el punto más reciente para mostrar siempre los últimos valores
                historial_actualizado = historial.copy()
                tiempo_actual = st.session_state['tiempo_transcurrido_1']
                
                # Agregar el punto actual si no está en el historial (para mostrar siempre el último valor)
                if len(historial_actualizado['tiempo']) == 0 or historial_actualizado['tiempo'][-1] != tiempo_actual:
                    historial_actualizado['tiempo'] = historial_actualizado['tiempo'].copy() + [tiempo_actual]
                    historial_actualizado['productos_salen_secuencial'] = historial_actualizado['productos_salen_secuencial'].copy() + [st.session_state['productos_salen_1']]
                    historial_actualizado['productos_salen_parallel'] = historial_actualizado['productos_salen_parallel'].copy() + [st.session_state['productos_salen_2']]
                    historial_actualizado['productos_entran_secuencial'] = historial_actualizado['productos_entran_secuencial'].copy() + [st.session_state['productos_entran_1']]
                    historial_actualizado['productos_entran_parallel'] = historial_actualizado['productos_entran_parallel'].copy() + [st.session_state['productos_entran_2']]
                
                graficas = crear_graficas_tiempo_real_produccion(historial_actualizado)
                
                # Usar una key única basada en el tiempo para forzar actualización
                tiempo_key = int(st.session_state['tiempo_transcurrido_1'] * 10)  # Cambia cada 0.1 segundos
                
                # Gráfica de productos que salen
                st.plotly_chart(graficas['productos_salen'], use_container_width=True, key=f"grafico_productos_salen_{tiempo_key}")
                
                st.divider()
                
                # Gráfica de productos que entran
                st.plotly_chart(graficas['productos_entran'], use_container_width=True, key=f"grafico_productos_entran_{tiempo_key}")
                
                st.divider()
                
                # Gráfica de comparación de progreso
                st.plotly_chart(graficas['comparacion'], use_container_width=True, key=f"grafico_comparacion_{tiempo_key}")
            
            # Mostrar mensaje finalizado por separado si ambas simulaciones están finalizadas
            if st.session_state['simulacion_finalizada']:
                st.markdown("""
                <div style="position: relative; width: 100%; margin: 20px 0; z-index: 1000;">
                    <div class="mensaje-finalizado" style="
                        position: relative;
                        background: linear-gradient(135deg, #198754 0%, #20c997 100%);
                        color: white;
                        padding: 30px 50px;
                        border-radius: 12px;
                        text-align: center;
                        box-shadow: 0 8px 24px rgba(0,0,0,0.4), 0 0 20px rgba(25, 135, 84, 0.5);
                        border: 2px solid rgba(255,255,255,0.3);
                        animation: aparecer 0.5s ease-in;
                    ">
                        <h2 style="margin: 0 0 12px 0; font-size: 1.8em; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                            Simulación Finalizada
                        </h2>
                        <p style="margin: 0; font-size: 1.1em; opacity: 0.95;">
                            Todas las líneas de producción han completado el procesamiento exitosamente.
                        </p>
                    </div>
                </div>
                <style>
                    @keyframes aparecer {
                        from {
                            opacity: 0;
                            transform: scale(0.8);
                        }
                        to {
                            opacity: 1;
                            transform: scale(1);
                        }
                    }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("Reiniciar Simulación", type="primary", use_container_width=True):
                        st.session_state['animacion_activa'] = False
                        st.session_state['productos_entran_1'] = 0
                        st.session_state['productos_salen_1'] = 0
                        st.session_state['tiempo_inicio_1'] = None
                        st.session_state['tiempo_transcurrido_1'] = 0.0
                        st.session_state['simulacion_finalizada_1'] = False
                        st.session_state['productos_entran_2'] = 0
                        st.session_state['productos_salen_2'] = 0
                        st.session_state['tiempo_inicio_2'] = None
                        st.session_state['tiempo_transcurrido_2'] = 0.0
                        st.session_state['simulacion_finalizada_2'] = False
                        
                        # Reiniciar historial de gráficas
                        st.session_state['historial_graficas'] = {
                            'tiempo': [],
                            'productos_salen_secuencial': [],
                            'productos_salen_parallel': [],
                            'productos_entran_secuencial': [],
                            'productos_entran_parallel': []
                        }
                        
                        st.session_state['simulacion_finalizada'] = False
                        st.rerun()
            
            # Auto-refrescar del lado del servidor para mantener el estado
            if not st.session_state['simulacion_finalizada']:
                time.sleep(0.8)
                st.rerun()
        
    else:
        # Mostrar instrucciones cuando no hay animación activa
        st.markdown("""
        <div style="background: linear-gradient(135deg, #212529 0%, #343a40 100%); 
                    padding: 20px; 
                    border-radius: 12px; 
                    margin: 20px 0;
                    border: 1px solid rgba(255,255,255,0.1);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <p style="color: #adb5bd; margin: 0; text-align: center;">
                <strong style="color: #0d6efd;">Ingrese la cantidad de productos</strong> y haga clic en 
                <strong style="color: #0d6efd;">'Iniciar Simulación'</strong> para ver las animaciones.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Sección de visualización estática (solo se muestra si hay métricas base de simulación)
    if 'metricas_base' in st.session_state:
        metricas = st.session_state['metricas_base']
        
        # Visualización principal de la línea
        st.subheader("Estado Actual de la Línea de Producción")
        fig_linea = crear_visualizacion_linea_produccion(metricas)
        st.plotly_chart(fig_linea, use_container_width=True, key="grafico_linea_produccion")
        
        st.divider()
        
        # Información detallada por estación
        st.subheader("Información Detallada por Estación")
        
        if 'utilizacion' in metricas:
            col1, col2, col3, col4 = st.columns(4)
            
            estaciones_info = [
                ('Corte', metricas['utilizacion'].get('Corte', 0)),
                ('Ensamblaje', metricas['utilizacion'].get('Ensamblaje', 0)),
                ('Tapizado', metricas['utilizacion'].get('Tapizado', 0)),
                ('Calidad', metricas['utilizacion'].get('Calidad', 0))
            ]
            
            cols = [col1, col2, col3, col4]
            for idx, (estacion, util) in enumerate(estaciones_info):
                with cols[idx]:
                    # Determinar color según utilización
                    if util > 80:
                        color = "#dc3545"
                        estado = "Alta Carga"
                    elif util > 60:
                        color = "#ffc107"
                        estado = "Carga Normal"
                    else:
                        color = "#28a745"
                        estado = "Disponible"
                    
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: {color};">
                        <h5>{estacion}</h5>
                        <h3 style="color: {color};">{util:.1f}%</h3>
                        <p style="color: {color}; font-weight: bold;">{estado}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        
        # Flujo de la línea de producción
        st.subheader("Flujo de la Línea de Producción")
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 2rem; background: #f8f9fa; border-radius: 10px;">
            <div style="text-align: center; flex: 1;">
                <div style="background: #007bff; color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <h4>Corte</h4>
                    <p>Preparación de materiales</p>
                </div>
            </div>
            <div style="font-size: 2rem; color: #666;">→</div>
            <div style="text-align: center; flex: 1;">
                <div style="background: #dc3545; color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <h4>Ensamblaje</h4>
                    <p>Cuello de Botella</p>
                </div>
            </div>
            <div style="font-size: 2rem; color: #666;">→</div>
            <div style="text-align: center; flex: 1;">
                <div style="background: #28a745; color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <h4>Tapizado</h4>
                    <p>Acabado final</p>
                </div>
            </div>
            <div style="font-size: 2rem; color: #666;">→</div>
            <div style="text-align: center; flex: 1;">
                <div style="background: #ffc107; color: black; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <h4>Calidad</h4>
                    <p>Control final</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Métricas de rendimiento
        st.subheader("Métricas de Rendimiento de la Línea")
        if 'paneles_data' in metricas and metricas['paneles_data']:
            df_paneles = pd.DataFrame(metricas['paneles_data'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                tct_promedio = df_paneles['tct_total'].mean()
                st.metric("TCT Promedio", f"{tct_promedio:.1f} min")
            
            with col2:
                tct_min = df_paneles['tct_total'].min()
                st.metric("TCT Mínimo", f"{tct_min:.1f} min")
            
            with col3:
                tct_max = df_paneles['tct_total'].max()
                st.metric("TCT Máximo", f"{tct_max:.1f} min")
        else:
            st.info("Ejecuta una simulación para ver las métricas de rendimiento.")
    else:
        st.warning("Primero ejecuta la simulación del modelo base en la pestaña 'Modelo Base' para ver la visualización de la línea de producción.")

# PESTAÑA 6: ANÁLISIS AVANZADO
with tab6:
    st.header("Análisis Avanzado")
    st.markdown("""
    <p class="lead">Optimización automática, análisis de riesgos y predicciones</p>
    """, unsafe_allow_html=True)
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Optimización Automática", "Análisis de Riesgos", "Análisis Predictivo"])
    
    with sub_tab1:
        st.subheader("Optimización Automática")
        st.markdown("Ejecuta todas las combinaciones de optimización y encuentra la mejor opción")
        
        if st.button("Ejecutar Optimización Automática", type="primary"):
            if 'metricas_base' not in st.session_state:
                st.warning("Primero ejecuta la simulación del modelo base.")
            else:
                with st.spinner("Ejecutando todas las combinaciones de optimización (esto puede tomar varios minutos)..."):
                    resultados_opt = optimizacion_automatica(
                        metricas_base=st.session_state['metricas_base'],
                        horizonte_dias=horizonte_dias,
                        mix_estandar=mix_estandar,
                        mix_modelos=mix_modelos,
                        seed=seed
                    )
                    
                    if resultados_opt:
                        st.session_state['resultados_optimizacion'] = resultados_opt
                        mejor = resultados_opt['mejor_opcion']
                        st.success(f"**Mejor Opción Encontrada:** {mejor['nombre']}")
                        st.info(f"**Score:** {mejor['score']:.2f} | **Mejora Throughput:** {mejor['mejora_throughput']:.1f}% | **Reducción TCT:** {mejor['reduccion_tct']:.1f}%")
        
        if 'resultados_optimizacion' in st.session_state:
            resultados_opt = st.session_state['resultados_optimizacion']
            mejor = resultados_opt['mejor_opcion']
            
            st.subheader("Mejor Configuración Encontrada")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Configuración", mejor['nombre'])
            with col2:
                st.metric("Throughput", f"{mejor['metricas'].get('throughput_dia', 0):.0f} piezas/día")
            with col3:
                st.metric("TCT Promedio", f"{mejor['metricas'].get('tct_promedio', 0):.1f} min")
            
            st.subheader("Comparación de Todas las Opciones")
            fig_comparacion = crear_grafico_comparacion_optimizaciones(resultados_opt)
            st.plotly_chart(fig_comparacion, use_container_width=True, key="grafico_comparacion_optimizaciones")
            
            # Tabla comparativa
            st.subheader("Tabla Comparativa")
            datos_comparacion = []
            for op in resultados_opt['todas_opciones']:
                datos_comparacion.append({
                    'Configuración': op['nombre'],
                    'Throughput (piezas/día)': f"{op['metricas'].get('throughput_dia', 0):.0f}",
                    'TCT Promedio (min)': f"{op['metricas'].get('tct_promedio', 0):.1f}",
                    'Mejora Throughput (%)': f"{op['mejora_throughput']:.1f}",
                    'Reducción TCT (%)': f"{op['reduccion_tct']:.1f}",
                    'Score': f"{op['score']:.2f}"
                })
            df_comparacion = pd.DataFrame(datos_comparacion)
            st.dataframe(df_comparacion, use_container_width=True)
    
    with sub_tab2:
        st.subheader("Análisis de Riesgos")
        st.markdown("Evalúa escenarios pesimistas y optimistas mediante múltiples simulaciones")
        
        num_sim = st.slider("Número de Simulaciones", 50, 200, 100, help="Más simulaciones = mayor precisión pero más tiempo")
        
        if st.button("Ejecutar Análisis de Riesgos", type="primary"):
            if 'metricas_base' not in st.session_state:
                st.warning("Primero ejecuta la simulación del modelo base.")
            else:
                with st.spinner(f"Ejecutando {num_sim} simulaciones para análisis de riesgos..."):
                    analisis_riesgos_result = analisis_riesgos(
                        metricas_base=st.session_state['metricas_base'],
                        horizonte_dias=horizonte_dias,
                        mix_estandar=mix_estandar,
                        mix_modelos=mix_modelos,
                        seed=seed,
                        num_simulaciones=num_sim
                    )
                    
                    if analisis_riesgos_result:
                        st.session_state['analisis_riesgos'] = analisis_riesgos_result
        
        if 'analisis_riesgos' in st.session_state:
            analisis = st.session_state['analisis_riesgos']
            
            st.subheader("Escenarios")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Escenario Pesimista", f"{analisis['escenario_pesimista']['throughput']:.0f} piezas/día", 
                         delta=f"TCT: {analisis['escenario_pesimista']['tct']:.1f} min", delta_color="inverse")
            with col2:
                st.metric("Escenario Promedio", f"{analisis['throughput']['promedio']:.0f} piezas/día",
                         delta=f"TCT: {analisis['tct']['promedio']:.1f} min")
            with col3:
                st.metric("Escenario Optimista", f"{analisis['escenario_optimista']['throughput']:.0f} piezas/día",
                         delta=f"TCT: {analisis['escenario_optimista']['tct']:.1f} min", delta_color="normal")
            
            st.subheader("Distribución de Resultados")
            fig_riesgos = crear_grafico_analisis_riesgos(analisis)
            st.plotly_chart(fig_riesgos, use_container_width=True, key="grafico_analisis_riesgos")
            
            st.subheader("Estadísticas Detalladas")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Throughput:**")
                st.write(f"- Promedio: {analisis['throughput']['promedio']:.0f} piezas/día")
                st.write(f"- Mínimo: {analisis['throughput']['min']:.0f} piezas/día")
                st.write(f"- Máximo: {analisis['throughput']['max']:.0f} piezas/día")
                st.write(f"- Desviación Estándar: {analisis['throughput']['std']:.2f}")
            with col2:
                st.write("**TCT:**")
                st.write(f"- Promedio: {analisis['tct']['promedio']:.1f} min")
                st.write(f"- Mínimo: {analisis['tct']['min']:.1f} min")
                st.write(f"- Máximo: {analisis['tct']['max']:.1f} min")
                st.write(f"- Desviación Estándar: {analisis['tct']['std']:.2f}")
    
    with sub_tab3:
        st.subheader("Análisis Predictivo")
        st.markdown("Predicciones basadas en datos históricos de simulaciones")
        
        horizonte_pred = st.slider("Horizonte de Predicción (días)", 7, 90, 30)
        
        if st.button("Generar Predicciones", type="primary"):
            historial = cargar_historial_simulaciones()
            if len(historial) < 3:
                st.warning("Se necesitan al menos 3 simulaciones en el historial para generar predicciones.")
            else:
                # Extraer métricas del historial
                metricas_historicas = [sim['metricas'] for sim in historial]
                analisis_pred = analisis_predictivo(metricas_historicas, horizonte_pred)
                
                if analisis_pred:
                    st.session_state['analisis_predictivo'] = analisis_pred
                    st.session_state['metricas_historicas'] = metricas_historicas
        
        if 'analisis_predictivo' in st.session_state:
            analisis_pred = st.session_state['analisis_predictivo']
            metricas_hist = st.session_state.get('metricas_historicas', [])
            
            st.subheader("Predicciones")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Throughput Futuro Promedio", f"{analisis_pred['throughput_futuro_promedio']:.0f} piezas/día",
                         delta=f"Tendencia: {analisis_pred['tendencia_throughput']}")
            with col2:
                st.metric("TCT Futuro Promedio", f"{analisis_pred['tct_futuro_promedio']:.1f} min",
                         delta=f"Tendencia: {analisis_pred['tendencia_tct']}")
            
            st.subheader("Gráfico de Predicción")
            fig_prediccion = crear_grafico_prediccion(analisis_pred, metricas_hist)
            st.plotly_chart(fig_prediccion, use_container_width=True, key="grafico_prediccion")

# PESTAÑA 7: IMPORTAR/EXPORTAR
with tab7:
    st.header("Importar y Exportar Datos")
    st.markdown("""
    <p class="lead">Importa datos desde Excel y exporta resultados de simulaciones</p>
    """, unsafe_allow_html=True)
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Importar Datos", "Exportar Resultados", "Historial de Simulaciones"])
    
    with sub_tab1:
        st.subheader("Importar Datos desde Excel")
        archivo_excel = st.file_uploader("Selecciona un archivo Excel", type=['xlsx', 'xls'])
        
        if archivo_excel:
            datos_importados = importar_datos_excel(archivo_excel)
            
            if datos_importados['exito']:
                st.success("Archivo importado exitosamente")
                st.write(f"**Filas:** {datos_importados['filas']}")
                st.write(f"**Columnas:** {', '.join(datos_importados['columnas'])}")
                
                st.subheader("Vista Previa de Datos")
                st.dataframe(datos_importados['dataframe'].head(20), use_container_width=True)
                
                # Guardar en session state
                st.session_state['datos_importados'] = datos_importados['dataframe']
            else:
                st.error(f"Error al importar: {datos_importados.get('error', 'Error desconocido')}")
    
    with sub_tab2:
        st.subheader("Exportar Resultados a Excel")
        
        if 'metricas_base' not in st.session_state:
            st.warning("No hay resultados de simulación para exportar. Ejecuta primero una simulación.")
        else:
            metricas_base = st.session_state['metricas_base']
            metricas_optimizado = st.session_state.get('metricas_optimizado', None)
            paneles_data = st.session_state.get('paneles_data', None)
            
            nombre_archivo = st.text_input("Nombre del archivo", value="resultados_spops.xlsx")
            
            if st.button("Generar Archivo Excel", type="primary"):
                with st.spinner("Generando archivo Excel..."):
                    excel_bytes = exportar_resultados_excel(
                        metricas_base=metricas_base,
                        metricas_optimizado=metricas_optimizado,
                        paneles_data=paneles_data,
                        nombre_archivo=nombre_archivo
                    )
                    
                    st.download_button(
                        label="Descargar Archivo Excel",
                        data=excel_bytes,
                        file_name=nombre_archivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("Archivo Excel generado exitosamente")
            
            # Análisis de costos detallado
            if metricas_optimizado:
                st.subheader("Análisis de Costos Detallado")
                costos = calcular_costos_detallados(metricas_optimizado, paneles_data)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Costo Unitario", f"${costos['costo_unitario']:.2f} MXN")
                with col2:
                    st.metric("Costo Diario", f"${costos['costo_diario']:.2f} MXN")
                with col3:
                    st.metric("Costo Mensual", f"${costos['costo_mensual']:.2f} MXN")
                
                st.subheader("Costos por Estación")
                df_costos_estacion = pd.DataFrame({
                    'Estación': list(costos['costo_por_estacion'].keys()),
                    'Costo (MXN)': list(costos['costo_por_estacion'].values())
                })
                st.dataframe(df_costos_estacion, use_container_width=True)
                
                if costos['costo_por_tipo_panel']:
                    st.subheader("Costos por Tipo de Panel")
                    datos_tipo = []
                    for tipo, info in costos['costo_por_tipo_panel'].items():
                        datos_tipo.append({
                            'Tipo': tipo,
                            'Cantidad': info['cantidad'],
                            'Costo Unitario (MXN)': f"{info['costo_unitario']:.2f}",
                            'Costo Total (MXN)': f"{info['costo_total']:.2f}"
                        })
                    df_costos_tipo = pd.DataFrame(datos_tipo)
                    st.dataframe(df_costos_tipo, use_container_width=True)
    
    with sub_tab3:
        st.subheader("Historial de Simulaciones")
        
        historial = cargar_historial_simulaciones()
        
        if not historial:
            st.info("No hay simulaciones guardadas en el historial.")
        else:
            st.write(f"**Total de simulaciones:** {len(historial)}")
            
            # Mostrar últimas 10 simulaciones
            st.subheader("Últimas Simulaciones")
            datos_historial = []
            for sim in historial[-10:]:
                datos_historial.append({
                    'Fecha/Hora': sim['timestamp'],
                    'Throughput': f"{sim['metricas'].get('throughput_dia', 0):.0f} piezas/día",
                    'TCT Promedio': f"{sim['metricas'].get('tct_promedio', 0):.1f} min",
                    'WIP Promedio': f"{sim['metricas'].get('wip_promedio', 0):.1f}"
                })
            df_historial = pd.DataFrame(datos_historial)
            st.dataframe(df_historial, use_container_width=True)
            
            if st.button("Limpiar Historial"):
                st.session_state['historial_simulaciones'] = []
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>SGPP</strong> - Sistema de Gestión y Programación de Proyectos</p>
    <p>Desarrollado con Streamlit, SimPy y Plotly</p>
</div>
""", unsafe_allow_html=True)


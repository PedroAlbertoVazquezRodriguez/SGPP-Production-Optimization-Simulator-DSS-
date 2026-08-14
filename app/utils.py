"""
Utilidades para visualización y análisis de métricas
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def crear_grafico_utilizacion(metricas: dict, titulo: str = "Utilización de Recursos") -> go.Figure:
    """Crea gráfico de barras de utilización de recursos"""
    if 'utilizacion' not in metricas:
        return go.Figure()
    
    estaciones = list(metricas['utilizacion'].keys())
    valores = list(metricas['utilizacion'].values())
    
    # Colores: Rojo para Ensamblaje (CPB), Verde para otros
    colores = ['#dc3545' if est == 'Ensamblaje' else '#28a745' for est in estaciones]
    
    fig = go.Figure(data=[
        go.Bar(
            x=estaciones,
            y=valores,
            marker_color=colores,
            text=[f'{v:.1f}%' for v in valores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Estación",
        yaxis_title="Utilización (%)",
        yaxis=dict(range=[0, 100]),
        template='plotly_white',
        height=400
    )
    
    return fig


def crear_grafico_wip(wip_historial: list) -> go.Figure:
    """Crea gráfico de línea para Inventario en Proceso (WIP)"""
    if not wip_historial:
        return go.Figure()
    
    df = pd.DataFrame(wip_historial)
    
    fig = go.Figure()
    
    # WIP total
    fig.add_trace(go.Scatter(
        x=df['tiempo'],
        y=df['wip'],
        mode='lines',
        name='WIP Total',
        line=dict(color='#007bff', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 123, 255, 0.1)'
    ))
    
    # Colas por estación
    fig.add_trace(go.Scatter(
        x=df['tiempo'],
        y=df['corte_cola'],
        mode='lines',
        name='Corte',
        line=dict(color='#ffc107', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['tiempo'],
        y=df['ensamblaje_cola'],
        mode='lines',
        name='Ensamblaje',
        line=dict(color='#dc3545', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['tiempo'],
        y=df['calidad_cola'],
        mode='lines',
        name='Calidad',
        line=dict(color='#28a745', width=1)
    ))
    
    fig.update_layout(
        title="Inventario en Proceso (WIP) - Acumulación de Lotes",
        xaxis_title="Tiempo (minutos)",
        yaxis_title="Número de Lotes",
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def crear_grafico_comparacion_throughput(metricas_base: dict, metricas_optimizado: dict) -> go.Figure:
    """Crea gráfico de barras comparativo de throughput"""
    fig = go.Figure(data=[
        go.Bar(
            name='Modelo Base',
            x=['Throughput'],
            y=[metricas_base.get('throughput_dia', 0)],
            marker_color='#dc3545',
            text=[f"{metricas_base.get('throughput_dia', 0):.0f} piezas/día"],
            textposition='auto',
        ),
        go.Bar(
            name='Configuración Óptima',
            x=['Throughput'],
            y=[metricas_optimizado.get('throughput_dia', 0)],
            marker_color='#28a745',
            text=[f"{metricas_optimizado.get('throughput_dia', 0):.0f} piezas/día"],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Comparación de Throughput",
        yaxis_title="Piezas por Día",
        template='plotly_white',
        height=400,
        barmode='group'
    )
    
    return fig


def crear_grafico_ahorro_economico(metricas_base: dict, metricas_optimizado: dict) -> go.Figure:
    """Crea gráfico de cascada para visualizar ahorro económico"""
    tct_base = metricas_base.get('tct_promedio', 0)
    tct_optimizado = metricas_optimizado.get('tct_promedio', 0)
    
    reduccion_tct = ((tct_base - tct_optimizado) / tct_base * 100) if tct_base > 0 else 0
    
    # Costo por unidad (asumiendo $5.00/minuto de mano de obra)
    costo_base = tct_base * 5.00
    costo_optimizado = tct_optimizado * 5.00
    ahorro_cpu = costo_base - costo_optimizado
    
    fig = go.Figure(go.Waterfall(
        name="Ahorro Económico",
        orientation="v",
        measure=["relative", "relative", "total"],
        x=["TCT Base", "Reducción TCT", "TCT Optimizado"],
        textposition="outside",
        text=[f"{tct_base:.1f} min", f"-{reduccion_tct:.1f}%", f"{tct_optimizado:.1f} min"],
        y=[tct_base, -tct_base + tct_optimizado, tct_optimizado],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title=f"Reducción de TCT: {reduccion_tct:.1f}% | Ahorro: ${ahorro_cpu:.2f} MXN/pieza",
        yaxis_title="Tiempo (minutos)",
        template='plotly_white',
        height=400
    )
    
    return fig


def crear_semaforo_operacional(metricas: dict) -> dict:
    """Crea indicadores de semáforo operacional para cada estación"""
    if 'utilizacion' not in metricas:
        return {}
    
    semaforos = {}
    utilizacion = metricas['utilizacion']
    
    for estacion, util in utilizacion.items():
        if estacion == 'Ensamblaje':
            # CPB: Rojo si > 80%, Amarillo si 60-80%, Verde si < 60%
            if util > 80:
                semaforos[estacion] = {'color': 'red', 'mensaje': 'Alta carga - Reducir velocidad'}
            elif util > 60:
                semaforos[estacion] = {'color': 'orange', 'mensaje': 'Carga moderada'}
            else:
                semaforos[estacion] = {'color': 'green', 'mensaje': 'Riesgo de inactividad - Aumentar ritmo'}
        else:
            # Otras estaciones: Verde si < 70%, Amarillo si 70-85%, Rojo si > 85%
            if util > 85:
                semaforos[estacion] = {'color': 'red', 'mensaje': 'Sobrecarga'}
            elif util > 70:
                semaforos[estacion] = {'color': 'orange', 'mensaje': 'Carga normal'}
            else:
                semaforos[estacion] = {'color': 'green', 'mensaje': 'Operación normal'}
    
    return semaforos


def calcular_recomendaciones(metricas_base: dict, metricas_optimizado: dict) -> list:
    """Genera recomendaciones operacionales basadas en la comparación"""
    recomendaciones = []
    
    if not metricas_base or not metricas_optimizado:
        return recomendaciones
    
    throughput_mejora = ((metricas_optimizado.get('throughput_dia', 0) - 
                          metricas_base.get('throughput_dia', 0)) / 
                         metricas_base.get('throughput_dia', 1)) * 100 if metricas_base.get('throughput_dia', 0) > 0 else 0
    
    tct_reduccion = ((metricas_base.get('tct_promedio', 0) - 
                     metricas_optimizado.get('tct_promedio', 0)) / 
                    metricas_base.get('tct_promedio', 1)) * 100 if metricas_base.get('tct_promedio', 0) > 0 else 0
    
    if throughput_mejora > 50:
        recomendaciones.append({
            'tipo': 'success',
            'titulo': 'Mejora Significativa de Throughput',
            'descripcion': f'El throughput aumentó {throughput_mejora:.1f}%, alcanzando {metricas_optimizado.get("throughput_dia", 0):.0f} piezas/día'
        })
    
    if tct_reduccion > 10:
        recomendaciones.append({
            'tipo': 'info',
            'titulo': 'Reducción de Tiempo de Ciclo',
            'descripcion': f'El TCT promedio se redujo {tct_reduccion:.1f}%, mejorando la eficiencia operacional'
        })
    
    if metricas_optimizado.get('perdida_capacidad', 0) < metricas_base.get('perdida_capacidad', 0):
        perdida_reducida = metricas_base.get('perdida_capacidad', 0) - metricas_optimizado.get('perdida_capacidad', 0)
        recomendaciones.append({
            'tipo': 'warning',
            'titulo': 'Mitigación de Retrabajo',
            'descripcion': f'La estrategia de aislamiento de retrabajo ha liberado {perdida_reducida:.1f}% de capacidad del sistema'
        })
    
    # Recomendaciones basadas en utilización
    if 'utilizacion' in metricas_optimizado:
        utilizacion = metricas_optimizado['utilizacion']
        for estacion, util in utilizacion.items():
            if util > 85:
                recomendaciones.append({
                    'tipo': 'warning',
                    'titulo': f'Sobrecarga en {estacion}',
                    'descripcion': f'{estacion} tiene una utilización del {util:.1f}%. Considerar redistribuir recursos o aumentar capacidad.'
                })
            elif util < 50 and estacion != 'Calidad':
                recomendaciones.append({
                    'tipo': 'info',
                    'titulo': f'Subutilización en {estacion}',
                    'descripcion': f'{estacion} tiene una utilización del {util:.1f}%. Puede reasignar operarios a estaciones con mayor carga.'
                })
    
    return recomendaciones


def calcular_estrategia_operarios(metricas: dict, flujo_paralelo: bool = False, 
                                  priorizar_setup: bool = False, 
                                  aislamiento_retrabajo: bool = False,
                                  mix_estandar: float = 0.6) -> dict:
    """Calcula la estrategia óptima de asignación de operarios basada en las métricas y configuración"""
    if not metricas or 'utilizacion' not in metricas:
        return {
            'ensamblaje': 8,
            'corte': 2,
            'tapizado': 2,
            'calidad': 2,
            'reserva': 1
        }
    
    utilizacion = metricas['utilizacion']
    total_operarios = 15
    
    # Calcular proporción de utilización
    ensamblaje_util = utilizacion.get('Ensamblaje', 70)
    corte_util = utilizacion.get('Corte', 50)
    tapizado_util = utilizacion.get('Tapizado', 50)
    calidad_util = utilizacion.get('Calidad', 40)
    
    # Factores de ajuste basados en configuración
    factor_ensamblaje = 1.5  # Base: Ensamblaje es CPB
    factor_corte = 0.8
    factor_tapizado = 0.8
    factor_calidad = 0.6
    
    # Ajustes según configuración
    
    # 1. Flujo Paralelo: Requiere más operarios en Ensamblaje y Tapizado (procesamiento paralelo)
    if flujo_paralelo:
        factor_ensamblaje *= 1.2  # Más operarios para manejar flujo paralelo
        factor_tapizado *= 1.1
        factor_corte *= 0.9  # Menos crítico en paralelo
    
    # 2. Priorización de Setup: Reduce necesidad en Corte (menos cambios)
    if priorizar_setup:
        factor_corte *= 0.85  # Menos operarios necesarios
        factor_ensamblaje *= 1.1  # Más operarios para mantener flujo continuo
    
    # 3. Aislamiento de Retrabajo: Requiere más reserva y operarios en Calidad
    if aislamiento_retrabajo:
        factor_calidad *= 1.3  # Más operarios para manejar retrabajo aislado
        # La reserva se ajustará después
    
    # 4. Mix de Demanda: Más paneles grandes = más tiempo en Ensamblaje y Tapizado
    if mix_estandar < 0.5:  # Más paneles grandes
        factor_ensamblaje *= 1.15
        factor_tapizado *= 1.1
    elif mix_estandar > 0.7:  # Más paneles estándar
        factor_corte *= 1.1  # Más operarios en corte para procesar más rápido
    
    # Calcular asignación basada en utilización y factores
    suma_util = ensamblaje_util + corte_util + tapizado_util + calidad_util
    
    if suma_util > 0:
        # Asignación proporcional con factores de configuración
        ensamblaje_ratio = (ensamblaje_util / suma_util) * factor_ensamblaje
        corte_ratio = (corte_util / suma_util) * factor_corte
        tapizado_ratio = (tapizado_util / suma_util) * factor_tapizado
        calidad_ratio = (calidad_util / suma_util) * factor_calidad
        
        total_ratio = ensamblaje_ratio + corte_ratio + tapizado_ratio + calidad_ratio
        
        # Calcular asignación base
        operarios_disponibles = total_operarios - 2  # Reservar 2 para reserva base
        
        ensamblaje = max(5, min(10, int((ensamblaje_ratio / total_ratio) * operarios_disponibles)))
        corte = max(2, min(5, int((corte_ratio / total_ratio) * operarios_disponibles)))
        tapizado = max(1, min(4, int((tapizado_ratio / total_ratio) * operarios_disponibles)))
        calidad = max(1, min(3, int((calidad_ratio / total_ratio) * operarios_disponibles)))
        
        # Ajustar reserva según configuración
        reserva_base = 2
        if aislamiento_retrabajo:
            reserva_base = 3  # Más reserva para retrabajo aislado
        if flujo_paralelo:
            reserva_base = max(reserva_base, 2)  # Mantener reserva para paralelo
        
        reserva = total_operarios - ensamblaje - corte - tapizado - calidad
        reserva = max(reserva_base, reserva)  # Mínimo según configuración
        
        # Ajustar si hay desbalance (redistribuir desde la estación menos crítica)
        if reserva < reserva_base:
            diferencia = reserva_base - reserva
            # Reducir de tapizado primero (menos crítico), luego calidad
            if tapizado > 1:
                reduccion = min(diferencia, tapizado - 1)
                tapizado -= reduccion
                diferencia -= reduccion
            if diferencia > 0 and calidad > 1:
                reduccion = min(diferencia, calidad - 1)
                calidad -= reduccion
                diferencia -= reduccion
            if diferencia > 0 and corte > 2:
                reduccion = min(diferencia, corte - 2)
                corte -= reduccion
            reserva = reserva_base
        
        # Asegurar que sumen 15
        total_asignado = ensamblaje + corte + tapizado + calidad + reserva
        if total_asignado != total_operarios:
            diferencia = total_operarios - total_asignado
            if diferencia > 0:
                # Agregar a ensamblaje (más crítico)
                ensamblaje = min(10, ensamblaje + diferencia)
            elif diferencia < 0:
                # Quitar de reserva primero
                reserva = max(reserva_base, reserva + diferencia)
    else:
        # Valores por defecto según configuración
        if flujo_paralelo:
            ensamblaje = 9
            corte = 2
            tapizado = 2
            calidad = 1
            reserva = 1
        elif aislamiento_retrabajo:
            ensamblaje = 8
            corte = 2
            tapizado = 2
            calidad = 2
            reserva = 1
        else:
            ensamblaje = 8
            corte = 2
            tapizado = 2
            calidad = 2
            reserva = 1
    
    return {
        'ensamblaje': ensamblaje,
        'corte': corte,
        'tapizado': tapizado,
        'calidad': calidad,
        'reserva': reserva,
        'razon': _generar_razon_asignacion(flujo_paralelo, priorizar_setup, aislamiento_retrabajo, mix_estandar)
    }


def _generar_razon_asignacion(flujo_paralelo: bool, priorizar_setup: bool, 
                              aislamiento_retrabajo: bool, mix_estandar: float) -> str:
    """Genera una explicación de por qué se asignaron los operarios de esta manera"""
    razones = []
    
    if flujo_paralelo:
        razones.append("Flujo paralelo requiere más operarios en Ensamblaje")
    if priorizar_setup:
        razones.append("Priorización de setup reduce necesidad en Corte")
    if aislamiento_retrabajo:
        razones.append("Aislamiento de retrabajo aumenta reserva y operarios en Calidad")
    if mix_estandar < 0.5:
        razones.append("Mayor proporción de paneles grandes aumenta necesidad en Ensamblaje")
    elif mix_estandar > 0.7:
        razones.append("Mayor proporción de paneles estándar requiere más operarios en Corte")
    
    if not razones:
        return "Asignación basada en utilización actual de cada estación"
    
    return " | ".join(razones)


def obtener_supuestos_modelo() -> pd.DataFrame:
    """Retorna tabla de supuestos del modelo"""
    supuestos = [
        {
            'Parámetro': 'Costo de Mano de Obra',
            'Valor': '$5.00 MXN/minuto',
            'Fuente': 'Estimación operacional'
        },
        {
            'Parámetro': 'Margen de Ganancia',
            'Valor': '60%',
            'Fuente': 'Análisis financiero'
        },
        {
            'Parámetro': 'Probabilidad de Retrabajo',
            'Valor': '15%',
            'Fuente': 'Datos históricos'
        },
        {
            'Parámetro': 'Pérdida de Capacidad por Retrabajo',
            'Valor': '7-8%',
            'Fuente': 'Análisis de capacidad'
        },
        {
            'Parámetro': 'Jornada Laboral',
            'Valor': '8 horas/día',
            'Fuente': 'Política de producción'
        },
        {
            'Parámetro': 'Número de Operarios',
            'Valor': '15 operarios',
            'Fuente': 'Recursos disponibles'
        },
        {
            'Parámetro': 'Distribución de Tiempos de Servicio',
            'Valor': 'Exponencial',
            'Fuente': 'Validación estadística'
        },
        {
            'Parámetro': 'Distribución de Defectos/Retrabajo',
            'Valor': 'Poisson (λ=0.15)',
            'Fuente': 'Análisis de calidad'
        }
    ]
    
    return pd.DataFrame(supuestos)


def crear_grafico_tct_por_modelo(paneles_data: list) -> go.Figure:
    """Crea gráfico de TCT por modelo de panel"""
    if not paneles_data:
        return go.Figure()
    
    df = pd.DataFrame(paneles_data)
    
    fig = go.Figure()
    
    modelos = df['modelo'].unique()
    for modelo in modelos:
        df_modelo = df[df['modelo'] == modelo]
        fig.add_trace(go.Box(
            y=df_modelo['tct_total'],
            name=modelo,
            boxmean='sd'
        ))
    
    fig.update_layout(
        title="Distribución de TCT por Modelo de Panel",
        xaxis_title="Modelo",
        yaxis_title="TCT (minutos)",
        template='plotly_white',
        height=400
    )
    
    return fig


def crear_grafico_throughput_tiempo(paneles_data: list) -> go.Figure:
    """Crea gráfico de throughput acumulado en el tiempo"""
    if not paneles_data:
        return go.Figure()
    
    df = pd.DataFrame(paneles_data)
    df = df.sort_values('tiempo_finalizacion')
    df['throughput_acumulado'] = range(1, len(df) + 1)
    df['tiempo_horas'] = df['tiempo_finalizacion'] / 60
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['tiempo_horas'],
        y=df['throughput_acumulado'],
        mode='lines',
        name='Throughput Acumulado',
        line=dict(color='#007bff', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 123, 255, 0.1)'
    ))
    
    fig.update_layout(
        title="Throughput Acumulado en el Tiempo",
        xaxis_title="Tiempo (horas)",
        yaxis_title="Piezas Completadas",
        template='plotly_white',
        height=400
    )
    
    return fig


def crear_visualizacion_linea_produccion(metricas: dict, wip_historial: list = None) -> go.Figure:
    """Crea visualización de la línea de producción con estado de cada estación"""
    if 'utilizacion' not in metricas:
        return go.Figure()
    
    estaciones = ['Corte', 'Ensamblaje', 'Tapizado', 'Calidad']
    utilizaciones = [metricas['utilizacion'].get(est, 0) for est in estaciones]
    
    # Crear gráfico de Gantt simplificado
    fig = go.Figure()
    
    # Barras horizontales para cada estación
    for i, (estacion, util) in enumerate(zip(estaciones, utilizaciones)):
        color = '#dc3545' if util > 80 else '#ffc107' if util > 60 else '#28a745'
        fig.add_trace(go.Bar(
            x=[util],
            y=[estacion],
            orientation='h',
            name=estacion,
            marker_color=color,
            text=[f'{util:.1f}%'],
            textposition='auto',
            width=0.6
        ))
    
    fig.update_layout(
        title="Estado de la Línea de Producción - Utilización por Estación",
        xaxis_title="Utilización (%)",
        yaxis_title="Estación",
        xaxis=dict(range=[0, 100]),
        template='plotly_white',
        height=300,
        showlegend=False
    )
    
    return fig


def crear_grafico_retrabajo(paneles_data: list) -> go.Figure:
    """Crea gráfico de análisis de retrabajo"""
    if not paneles_data:
        return go.Figure()
    
    df = pd.DataFrame(paneles_data)
    
    retrabajo_por_tipo = df.groupby('tipo')['requiere_retrabajo'].agg(['sum', 'count'])
    retrabajo_por_tipo['porcentaje'] = (retrabajo_por_tipo['sum'] / retrabajo_por_tipo['count'] * 100).round(2)
    
    fig = go.Figure(data=[
        go.Bar(
            x=retrabajo_por_tipo.index,
            y=retrabajo_por_tipo['porcentaje'],
            marker_color=['#dc3545', '#ffc107'],
            text=[f"{v:.1f}%" for v in retrabajo_por_tipo['porcentaje']],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Porcentaje de Retrabajo por Tipo de Panel",
        xaxis_title="Tipo de Panel",
        yaxis_title="Porcentaje de Retrabajo (%)",
        template='plotly_white',
        height=400
    )
    
    return fig


def crear_animacion_linea_produccion(estaciones_secuencial, estaciones_paralelo, 
                                     contador_secuencial, contador_paralelo, 
                                     paquetes_en_estacion_sec, paquetes_en_estacion_par):
    """Crea visualización HTML de las dos líneas de producción animadas"""
    # Esta función se usa en app.py pero no necesita implementación aquí
    # ya que la animación se genera directamente en app.py
    pass


def crear_animacion_banda_transportadora_html(num_productos: int, productos_entran: int, 
                                              productos_salen: int, tiempo_transcurrido: float,
                                              finalizado: bool = False, auto_refresh: bool = True,
                                              titulo: str = "Línea de Producción",
                                              color_cajas: str = "#0d6efd",
                                              mostrar_tiempo: bool = True) -> str:
    """Crea HTML con animación de banda transportadora"""
    
    # Calcular progreso
    progreso = (productos_salen / num_productos * 100) if num_productos > 0 else 0
    
    # Generar un ID único para esta línea para evitar conflictos de CSS
    import hashlib
    linea_id = hashlib.md5(titulo.encode()).hexdigest()[:8]
    
    # Generar cajas en la banda
    num_cajas_visibles = min(10, productos_entran - productos_salen)  # Máximo 10 cajas visibles
    posicion_base = max(0, productos_entran - productos_salen - num_cajas_visibles)
    
    cajas_html = ""
    for i in range(num_cajas_visibles):
        # Posición de la caja (0 a 90% de la banda)
        posicion = (i / max(1, num_cajas_visibles - 1)) * 90 if num_cajas_visibles > 1 else 45
        cajas_html += f'<div class="caja-{linea_id}" style="left: {posicion}%; animation-delay: {i * 0.2}s;"></div>'
    
    # No incluir mensaje finalizado en el HTML principal, se renderiza por separado en app.py
    mensaje_final = ""
    
    tiempo_html = f'<div style="text-align: center; color: #adb5bd; font-size: 1.1em; margin-top: 5px; margin-bottom: 10px;"><strong style="color: #ffffff;">Tiempo: {tiempo_transcurrido:.4f} s</strong></div>' if mostrar_tiempo else ''
    html = f"""<div style="margin-bottom: 10px;"><h4 style="color: #adb5bd; font-weight: 600; text-align: center; margin: 0;">{titulo}</h4>{tiempo_html}</div><div class="contenedor-linea-{linea_id}"><style>
        @keyframes moverBanda {{
            0% {{ background-position: 0 0; }}
            100% {{ background-position: 50px 0; }}
        }}
        
        @keyframes moverCaja {{
            0% {{ left: 0%; opacity: 1; }}
            100% {{ left: 90%; opacity: 1; }}
        }}
        
        @keyframes aparecer {{
            from {{
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.8);
            }}
            to {{
                opacity: 1;
                transform: translate(-50%, -50%) scale(1);
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        .contenedor-banda {{
            position: relative;
            width: 100%;
            height: 220px;
            background: linear-gradient(135deg, #212529 0%, #343a40 100%);
            border-radius: 12px;
            overflow: hidden;
            margin: 20px 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3), inset 0 2px 4px rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .banda-transportadora {{
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 70px;
            background: repeating-linear-gradient(
                90deg,
                #495057 0px,
                #495057 25px,
                #6c757d 25px,
                #6c757d 50px
            );
            background-size: 50px 70px;
            animation: moverBanda 2s linear infinite;
            transform: translateY(-50%);
            border-top: 4px solid #0d6efd;
            border-bottom: 4px solid #0d6efd;
            box-shadow: inset 0 4px 8px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .banda-transportadora::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(13, 110, 253, 0.1) 50%,
                transparent 100%
            );
            pointer-events: none;
        }}
        
        .contenedor-linea-{linea_id} .contenedor-banda .cajas-container {{
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 70px;
            transform: translateY(-50%);
            z-index: 2;
        }}
        
        .contenedor-linea-{linea_id} .contenedor-banda .caja-{linea_id} {{
            position: absolute;
            width: 45px;
            height: 45px;
            background: {color_cajas} !important;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.4), 0 0 20px {color_cajas} !important;
            animation: moverCaja 8s linear infinite, pulse 2s ease-in-out infinite;
            top: 12px;
            transition: all 0.3s ease;
        }}
        
        .contenedor-linea-{linea_id} .contenedor-banda .caja-{linea_id}:hover {{
            box-shadow: 0 6px 12px rgba(0,0,0,0.5), 0 0 24px {color_cajas} !important;
        }}
        
        .contenedor-linea-{linea_id} .contenedor-banda .caja-{linea_id}::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 24px;
            height: 24px;
            background: rgba(255,255,255,0.4);
            border-radius: 4px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .estaciones-linea {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: space-around;
            align-items: center;
            z-index: 1;
            pointer-events: none;
            padding: 10px;
        }}
        
        .estacion-marcador {{
            text-align: center;
            color: #fff;
            font-weight: 600;
            font-size: 0.85em;
            background: linear-gradient(135deg, rgba(13, 110, 253, 0.9) 0%, rgba(102, 16, 242, 0.9) 100%);
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .mensaje-finalizado {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #198754 0%, #20c997 100%);
            color: white;
            padding: 30px 50px;
            border-radius: 12px;
            text-align: center;
            z-index: 10;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4), 0 0 20px rgba(25, 135, 84, 0.5);
            animation: aparecer 0.5s ease-in;
            border: 2px solid rgba(255,255,255,0.3);
        }}
        
        .mensaje-finalizado h2 {{
            margin: 0 0 12px 0;
            font-size: 1.8em;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .mensaje-finalizado p {{
            margin: 0;
            font-size: 1.1em;
            opacity: 0.95;
        }}
        
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
            transition: all 0.3s ease;
        }}
        
        .contador-item:hover {{
            transform: translateY(-4px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4), inset 0 1px 2px rgba(255,255,255,0.15);
            border-color: rgba(13, 110, 253, 0.5);
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
            margin: 20px 0;
            box-shadow: inset 0 4px 8px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .barra-progreso-fill {{
            height: 100%;
            background: linear-gradient(90deg, #0d6efd 0%, #6610f2 50%, #0d6efd 100%);
            background-size: 200% 100%;
            width: {progreso}%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 1em;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            box-shadow: 0 0 20px rgba(13, 110, 253, 0.5), inset 0 2px 4px rgba(255,255,255,0.2);
            animation: shimmer 2s linear infinite;
        }}
        
        @keyframes shimmer {{
            0% {{ background-position: 0% 0%; }}
            100% {{ background-position: 200% 0%; }}
        }}
    </style>
<div class="contenedor-banda"><div class="banda-transportadora"></div><div class="cajas-container">{cajas_html}</div>{mensaje_final}</div></div>
"""
    
    return html


def crear_grafico_comparacion_tiempo_real(tiempos, contadores_sec, contadores_par):
    """Crea gráfico de comparación en tiempo real entre las dos líneas"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=tiempos,
        y=contadores_sec,
        mode='lines+markers',
        name='Línea Secuencial',
        line=dict(color='#007bff', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=tiempos,
        y=contadores_par,
        mode='lines+markers',
        name='Línea Paralela',
        line=dict(color='#28a745', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Comparación en Tiempo Real: Paquetes Completados",
        xaxis_title="Tiempo (segundos)",
        yaxis_title="Paquetes Completados",
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def crear_graficas_tiempo_real_produccion(historial: dict) -> dict:
    """Crea gráficas en tiempo real del tracking de producción de ambas líneas"""
    if not historial['tiempo'] or len(historial['tiempo']) == 0:
        # Retornar gráficas vacías si no hay datos
        fig_productos_salen = go.Figure()
        fig_productos_entran = go.Figure()
        fig_comparacion = go.Figure()
        
        for fig in [fig_productos_salen, fig_productos_entran, fig_comparacion]:
            fig.update_layout(
                template='plotly_dark',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=350
            )
        
        return {
            'productos_salen': fig_productos_salen,
            'productos_entran': fig_productos_entran,
            'comparacion': fig_comparacion
        }
    
    tiempos = historial['tiempo']
    productos_salen_sec = historial['productos_salen_secuencial']
    productos_salen_par = historial['productos_salen_parallel']
    productos_entran_sec = historial['productos_entran_secuencial']
    productos_entran_par = historial['productos_entran_parallel']
    
    # Gráfica 1: Productos que salen en tiempo real
    fig_productos_salen = go.Figure()
    
    fig_productos_salen.add_trace(go.Scatter(
        x=tiempos,
        y=productos_salen_sec,
        mode='lines+markers',
        name='Línea Secuencial',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=5, color='#dc3545'),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.2)'
    ))
    
    fig_productos_salen.add_trace(go.Scatter(
        x=tiempos,
        y=productos_salen_par,
        mode='lines+markers',
        name='Línea Paralelo (Pipeline)',
        line=dict(color='#28a745', width=3),
        marker=dict(size=5, color='#28a745'),
        fill='tozeroy',
        fillcolor='rgba(40, 167, 69, 0.2)'
    ))
    
    fig_productos_salen.update_layout(
        title="Productos Completados (Salen) en Tiempo Real",
        xaxis_title="Tiempo (segundos)",
        yaxis_title="Productos Completados",
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350,
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        )
    )
    
    # Gráfica 2: Productos que entran en tiempo real
    fig_productos_entran = go.Figure()
    
    fig_productos_entran.add_trace(go.Scatter(
        x=tiempos,
        y=productos_entran_sec,
        mode='lines+markers',
        name='Línea Secuencial',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=5, color='#dc3545'),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.2)'
    ))
    
    fig_productos_entran.add_trace(go.Scatter(
        x=tiempos,
        y=productos_entran_par,
        mode='lines+markers',
        name='Línea Paralelo (Pipeline)',
        line=dict(color='#28a745', width=3),
        marker=dict(size=5, color='#28a745'),
        fill='tozeroy',
        fillcolor='rgba(40, 167, 69, 0.2)'
    ))
    
    fig_productos_entran.update_layout(
        title="Productos que Entran en Tiempo Real",
        xaxis_title="Tiempo (segundos)",
        yaxis_title="Productos que Entran",
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350,
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        )
    )
    
    # Gráfica 3: Comparación de eficiencia (progreso porcentual)
    max_productos = max(
        max(productos_salen_sec) if productos_salen_sec else 0,
        max(productos_salen_par) if productos_salen_par else 0,
        max(productos_entran_sec) if productos_entran_sec else 0,
        max(productos_entran_par) if productos_entran_par else 0,
        1
    )
    
    progreso_sec = [(p / max_productos * 100) if max_productos > 0 else 0 for p in productos_salen_sec] if productos_salen_sec else []
    progreso_par = [(p / max_productos * 100) if max_productos > 0 else 0 for p in productos_salen_par] if productos_salen_par else []
    
    fig_comparacion = go.Figure()
    
    fig_comparacion.add_trace(go.Scatter(
        x=tiempos,
        y=progreso_sec,
        mode='lines+markers',
        name='Línea Secuencial',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=5, color='#dc3545')
    ))
    
    fig_comparacion.add_trace(go.Scatter(
        x=tiempos,
        y=progreso_par,
        mode='lines+markers',
        name='Línea Paralelo (Pipeline)',
        line=dict(color='#28a745', width=3),
        marker=dict(size=5, color='#28a745')
    ))
    
    fig_comparacion.update_layout(
        title="Comparación de Progreso (%)",
        xaxis_title="Tiempo (segundos)",
        yaxis_title="Progreso (%)",
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350,
        hovermode='x unified',
        yaxis=dict(range=[0, 100]),
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        )
    )
    
    return {
        'productos_salen': fig_productos_salen,
        'productos_entran': fig_productos_entran,
        'comparacion': fig_comparacion
    }


def crear_grafico_productos_completados(tiempos, productos_sec, productos_par):
    """Crea gráfico de productos completados vs tiempo"""
    fig = go.Figure()
    
    # Línea Secuencial (roja)
    fig.add_trace(go.Scatter(
        x=tiempos,
        y=productos_sec,
        mode='lines+markers',
        name='Secuencial',
        line=dict(color='#dc3545', width=2),
        marker=dict(size=5, color='#dc3545')
    ))
    
    # Línea Paralela (verde)
    fig.add_trace(go.Scatter(
        x=tiempos,
        y=productos_par,
        mode='lines+markers',
        name='Paralelo (Pipeline)',
        line=dict(color='#28a745', width=2),
        marker=dict(size=5, color='#28a745')
    ))
    
    fig.update_layout(
        title="Productos Completados vs Tiempo",
        xaxis_title="Tiempo (segundos)",
        yaxis_title="Productos Completados",
        template='plotly_dark',
        height=300,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig


def crear_grafico_velocidad_produccion(tiempos, velocidad_sec, velocidad_par):
    """Crea gráfico de velocidad de producción con áreas sombreadas"""
    fig = go.Figure()
    
    # Velocidad Paralela (verde sólido con área)
    fig.add_trace(go.Scatter(
        x=tiempos,
        y=velocidad_par,
        mode='lines',
        name='Velocidad Paralela',
        line=dict(color='#28a745', width=2),
        fill='tozeroy',
        fillcolor='rgba(40, 167, 69, 0.3)'
    ))
    
    # Velocidad Secuencial (roja punteada con área)
    fig.add_trace(go.Scatter(
        x=tiempos,
        y=velocidad_sec,
        mode='lines',
        name='Velocidad Secuencial',
        line=dict(color='#dc3545', width=2, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.3)'
    ))
    
    fig.update_layout(
        title="Velocidad de Producción (Productos/segundo)",
        xaxis_title="Tiempo (segundos)",
        yaxis_title="Productos por Segundo",
        template='plotly_dark',
        height=300,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(range=[0, 0.6])
    )
    
    return fig


# ==================== NUEVAS FUNCIONALIDADES ====================

def exportar_resultados_excel(metricas_base: dict, metricas_optimizado: dict = None, 
                               paneles_data: list = None, nombre_archivo: str = "resultados_spops.xlsx") -> bytes:
    """Exporta todos los resultados a un archivo Excel"""
    from io import BytesIO
    import streamlit as st
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Métricas Generales
        metricas_data = {
            'Métrica': ['Throughput (piezas/día)', 'TCT Promedio (min)', 'WIP Promedio', 
                       'Pérdida Capacidad Retrabajo (%)', 'Utilización Corte (%)', 
                       'Utilización Ensamblaje (%)', 'Utilización Tapizado (%)', 
                       'Utilización Calidad (%)'],
            'Modelo Base': [
                metricas_base.get('throughput_dia', 0),
                metricas_base.get('tct_promedio', 0),
                metricas_base.get('wip_promedio', 0),
                metricas_base.get('perdida_capacidad', 0),
                metricas_base.get('utilizacion', {}).get('Corte', 0),
                metricas_base.get('utilizacion', {}).get('Ensamblaje', 0),
                metricas_base.get('utilizacion', {}).get('Tapizado', 0),
                metricas_base.get('utilizacion', {}).get('Calidad', 0)
            ]
        }
        
        if metricas_optimizado:
            metricas_data['Modelo Optimizado'] = [
                metricas_optimizado.get('throughput_dia', 0),
                metricas_optimizado.get('tct_promedio', 0),
                metricas_optimizado.get('wip_promedio', 0),
                metricas_optimizado.get('perdida_capacidad', 0),
                metricas_optimizado.get('utilizacion', {}).get('Corte', 0),
                metricas_optimizado.get('utilizacion', {}).get('Ensamblaje', 0),
                metricas_optimizado.get('utilizacion', {}).get('Tapizado', 0),
                metricas_optimizado.get('utilizacion', {}).get('Calidad', 0)
            ]
            metricas_data['Mejora (%)'] = [
                ((metricas_data['Modelo Optimizado'][i] - metricas_data['Modelo Base'][i]) / 
                 metricas_data['Modelo Base'][i] * 100) if metricas_data['Modelo Base'][i] > 0 else 0
                for i in range(len(metricas_data['Modelo Base']))
            ]
        
        df_metricas = pd.DataFrame(metricas_data)
        df_metricas.to_excel(writer, sheet_name='Métricas Generales', index=False)
        
        # Hoja 2: Análisis de Costos
        if metricas_optimizado:
            costo_mano_obra = 5.0  # MXN por minuto
            tct_base = metricas_base.get('tct_promedio', 0)
            tct_opt = metricas_optimizado.get('tct_promedio', 0)
            throughput_base = metricas_base.get('throughput_dia', 0)
            throughput_opt = metricas_optimizado.get('throughput_dia', 0)
            
            costos_data = {
                'Concepto': ['Costo Unitario Base (MXN)', 'Costo Unitario Optimizado (MXN)', 
                           'Ahorro por Pieza (MXN)', 'Costo Diario Base (MXN)', 
                           'Costo Diario Optimizado (MXN)', 'Ahorro Diario (MXN)',
                           'Ahorro Mensual (MXN)', 'ROI (%)'],
                'Valor': [
                    tct_base * costo_mano_obra,
                    tct_opt * costo_mano_obra,
                    (tct_base - tct_opt) * costo_mano_obra,
                    tct_base * costo_mano_obra * throughput_base,
                    tct_opt * costo_mano_obra * throughput_opt,
                    (tct_base * throughput_base - tct_opt * throughput_opt) * costo_mano_obra,
                    (tct_base * throughput_base - tct_opt * throughput_opt) * costo_mano_obra * 30,
                    ((tct_base - tct_opt) / tct_base * 100) if tct_base > 0 else 0
                ]
            }
            df_costos = pd.DataFrame(costos_data)
            df_costos.to_excel(writer, sheet_name='Análisis de Costos', index=False)
        
        # Hoja 3: Datos de Paneles
        if paneles_data:
            df_paneles = pd.DataFrame(paneles_data)
            df_paneles.to_excel(writer, sheet_name='Datos de Paneles', index=False)
        
        # Hoja 4: Historial WIP
        if 'wip_historial' in metricas_base and metricas_base['wip_historial']:
            df_wip = pd.DataFrame(metricas_base['wip_historial'])
            df_wip.to_excel(writer, sheet_name='Historial WIP', index=False)
    
    output.seek(0)
    return output.getvalue()



def guardar_historial_simulacion(configuracion: dict, metricas: dict, timestamp: str = None):
    """Guarda una simulación en el historial"""
    import datetime
    import streamlit as st
    
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if 'historial_simulaciones' not in st.session_state:
        st.session_state['historial_simulaciones'] = []
    
    simulacion = {
        'timestamp': timestamp,
        'configuracion': configuracion,
        'metricas': metricas
    }
    
    st.session_state['historial_simulaciones'].append(simulacion)
    
    # Mantener solo las últimas 50 simulaciones
    if len(st.session_state['historial_simulaciones']) > 50:
        st.session_state['historial_simulaciones'] = st.session_state['historial_simulaciones'][-50:]


def cargar_historial_simulaciones():
    """Retorna el historial de simulaciones"""
    import streamlit as st
    return st.session_state.get('historial_simulaciones', [])


def calcular_costos_detallados(metricas: dict, paneles_data: list = None) -> dict:
    """Calcula análisis detallado de costos por estación y tipo de panel"""
    costo_mano_obra_min = 5.0  # MXN por minuto
    costo_mano_obra_hora = costo_mano_obra_min * 60
    
    costos = {
        'costo_total': 0,
        'costo_por_estacion': {},
        'costo_por_tipo_panel': {},
        'costo_unitario': 0,
        'costo_diario': 0,
        'costo_mensual': 0
    }
    
    # Costos por estación
    if 'utilizacion' in metricas:
        tiempo_simulacion_horas = metricas.get('tiempo_simulacion', 0) / 3600
        for estacion, util in metricas['utilizacion'].items():
            # Asumir 15 operarios distribuidos (4 por estación promedio)
            operarios_estacion = 4
            horas_ocupadas = tiempo_simulacion_horas * (util / 100)
            costos['costo_por_estacion'][estacion] = horas_ocupadas * operarios_estacion * costo_mano_obra_hora
            costos['costo_total'] += costos['costo_por_estacion'][estacion]
    
    # Costos por tipo de panel
    if paneles_data:
        df_paneles = pd.DataFrame(paneles_data)
        if 'tipo' in df_paneles.columns and 'tct' in df_paneles.columns:
            for tipo in df_paneles['tipo'].unique():
                paneles_tipo = df_paneles[df_paneles['tipo'] == tipo]
                tct_promedio = paneles_tipo['tct'].mean()
                cantidad = len(paneles_tipo)
                costos['costo_por_tipo_panel'][tipo] = {
                    'costo_total': tct_promedio * cantidad * costo_mano_obra_min,
                    'costo_unitario': tct_promedio * costo_mano_obra_min,
                    'cantidad': cantidad
                }
    
    # Costos agregados
    tct_promedio = metricas.get('tct_promedio', 0)
    throughput_dia = metricas.get('throughput_dia', 0)
    
    costos['costo_unitario'] = tct_promedio * costo_mano_obra_min
    costos['costo_diario'] = throughput_dia * costos['costo_unitario']
    costos['costo_mensual'] = costos['costo_diario'] * 30
    
    return costos


def optimizacion_automatica(metricas_base: dict, horizonte_dias: int, mix_estandar: float, 
                            mix_modelos: dict, seed: int) -> dict:
    """Ejecuta todas las combinaciones de optimización y encuentra la mejor"""
    from simulation import ejecutar_simulacion
    
    combinaciones = [
        {'nombre': 'Solo Priorización Setup', 'priorizar_setup': True, 'aislamiento_retrabajo': False, 'flujo_paralelo': False},
        {'nombre': 'Solo Aislamiento Retrabajo', 'priorizar_setup': False, 'aislamiento_retrabajo': True, 'flujo_paralelo': False},
        {'nombre': 'Solo Flujo Paralelo', 'priorizar_setup': False, 'aislamiento_retrabajo': False, 'flujo_paralelo': True},
        {'nombre': 'Setup + Retrabajo', 'priorizar_setup': True, 'aislamiento_retrabajo': True, 'flujo_paralelo': False},
        {'nombre': 'Setup + Paralelo', 'priorizar_setup': True, 'aislamiento_retrabajo': False, 'flujo_paralelo': True},
        {'nombre': 'Retrabajo + Paralelo', 'priorizar_setup': False, 'aislamiento_retrabajo': True, 'flujo_paralelo': True},
        {'nombre': 'Todas las Optimizaciones', 'priorizar_setup': True, 'aislamiento_retrabajo': True, 'flujo_paralelo': True}
    ]
    
    resultados = []
    
    for combo in combinaciones:
        try:
            metricas = ejecutar_simulacion(
                horizonte_dias=horizonte_dias,
                mix_estandar=mix_estandar,
                mix_modelos=mix_modelos,
                seed=seed,
                flujo_paralelo=combo['flujo_paralelo'],
                priorizar_setup=combo['priorizar_setup'],
                aislamiento_retrabajo=combo['aislamiento_retrabajo']
            )
            
            # Calcular score de optimización (throughput mejorado - costo adicional)
            mejora_throughput = ((metricas.get('throughput_dia', 0) - metricas_base.get('throughput_dia', 0)) / 
                                metricas_base.get('throughput_dia', 1)) * 100
            reduccion_tct = ((metricas_base.get('tct_promedio', 0) - metricas.get('tct_promedio', 0)) / 
                           metricas_base.get('tct_promedio', 1)) * 100
            
            # Score combinado (peso: 60% throughput, 40% TCT)
            score = (mejora_throughput * 0.6) + (reduccion_tct * 0.4)
            
            resultados.append({
                'nombre': combo['nombre'],
                'metricas': metricas,
                'mejora_throughput': mejora_throughput,
                'reduccion_tct': reduccion_tct,
                'score': score,
                'configuracion': combo
            })
        except Exception as e:
            continue
    
    # Encontrar la mejor opción
    if resultados:
        mejor_opcion = max(resultados, key=lambda x: x['score'])
        return {
            'mejor_opcion': mejor_opcion,
            'todas_opciones': resultados,
            'comparacion': resultados
        }
    
    return None


def crear_grafico_comparacion_optimizaciones(resultados_optimizacion: dict) -> go.Figure:
    """Crea gráfico comparativo de todas las opciones de optimización"""
    if not resultados_optimizacion or 'todas_opciones' not in resultados_optimizacion:
        return go.Figure()
    
    opciones = resultados_optimizacion['todas_opciones']
    nombres = [op['nombre'] for op in opciones]
    throughputs = [op['metricas'].get('throughput_dia', 0) for op in opciones]
    tcts = [op['metricas'].get('tct_promedio', 0) for op in opciones]
    scores = [op['score'] for op in opciones]
    
    fig = go.Figure()
    
    # Gráfico de barras agrupadas
    fig.add_trace(go.Bar(
        name='Throughput (piezas/día)',
        x=nombres,
        y=throughputs,
        yaxis='y',
        offsetgroup=1,
        marker_color='#28a745'
    ))
    
    fig.add_trace(go.Bar(
        name='TCT Promedio (min)',
        x=nombres,
        y=tcts,
        yaxis='y2',
        offsetgroup=2,
        marker_color='#dc3545'
    ))
    
    # Marcar la mejor opción
    mejor_idx = max(range(len(scores)), key=lambda i: scores[i])
    fig.add_trace(go.Scatter(
        x=[nombres[mejor_idx]],
        y=[max(throughputs) * 1.1],
        mode='markers+text',
        marker=dict(size=20, symbol='star', color='gold'),
        text=['⭐ MEJOR'],
        textposition='top center',
        showlegend=False
    ))
    
    fig.update_layout(
        title='Comparación de Todas las Opciones de Optimización',
        xaxis_title='Configuración',
        yaxis=dict(title='Throughput (piezas/día)', side='left'),
        yaxis2=dict(title='TCT Promedio (min)', overlaying='y', side='right'),
        template='plotly_white',
        height=500,
        barmode='group',
        hovermode='x unified'
    )
    
    return fig


def importar_datos_excel(archivo) -> dict:
    """Importa datos desde un archivo Excel"""
    try:
        df = pd.read_excel(archivo)
        
        datos_importados = {
            'dataframe': df,
            'columnas': list(df.columns),
            'filas': len(df),
            'exito': True
        }
        
        return datos_importados
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }


def analisis_riesgos(metricas_base: dict, horizonte_dias: int, mix_estandar: float, 
                    mix_modelos: dict, seed: int, num_simulaciones: int = 100) -> dict:
    """Realiza análisis de riesgos con múltiples simulaciones (escenarios pesimistas/optimistas)"""
    from simulation import ejecutar_simulacion
    
    resultados_throughput = []
    resultados_tct = []
    
    # Variar parámetros para crear escenarios
    variaciones = np.linspace(0.8, 1.2, num_simulaciones)  # ±20% de variación
    
    for var in variaciones:
        try:
            # Ajustar mix de demanda (escenario pesimista/optimista)
            mix_ajustado = max(0.1, min(0.9, mix_estandar * var))
            
            metricas = ejecutar_simulacion(
                horizonte_dias=int(horizonte_dias * var),
                mix_estandar=mix_ajustado,
                mix_modelos=mix_modelos,
                seed=seed + int(var * 100),
                flujo_paralelo=False,
                priorizar_setup=False,
                aislamiento_retrabajo=False
            )
            
            resultados_throughput.append(metricas.get('throughput_dia', 0))
            resultados_tct.append(metricas.get('tct_promedio', 0))
        except:
            continue
    
    if resultados_throughput:
        analisis = {
            'throughput': {
                'promedio': np.mean(resultados_throughput),
                'min': np.min(resultados_throughput),
                'max': np.max(resultados_throughput),
                'percentil_25': np.percentile(resultados_throughput, 25),
                'percentil_75': np.percentile(resultados_throughput, 75),
                'std': np.std(resultados_throughput)
            },
            'tct': {
                'promedio': np.mean(resultados_tct),
                'min': np.min(resultados_tct),
                'max': np.max(resultados_tct),
                'percentil_25': np.percentile(resultados_tct, 25),
                'percentil_75': np.percentile(resultados_tct, 75),
                'std': np.std(resultados_tct)
            },
            'escenario_pesimista': {
                'throughput': np.percentile(resultados_throughput, 10),
                'tct': np.percentile(resultados_tct, 90)
            },
            'escenario_optimista': {
                'throughput': np.percentile(resultados_throughput, 90),
                'tct': np.percentile(resultados_tct, 10)
            }
        }
        return analisis
    
    return None


def analisis_predictivo(metricas_historicas: list, horizonte_prediccion: int = 30) -> dict:
    """Realiza análisis predictivo usando datos históricos"""
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    
    if len(metricas_historicas) < 3:
        return None
    
    # Preparar datos
    df = pd.DataFrame(metricas_historicas)
    
    if 'throughput_dia' not in df.columns or 'tct_promedio' not in df.columns:
        return None
    
    # Crear índice de tiempo
    df['tiempo'] = range(len(df))
    
    # Predicción de Throughput
    X_throughput = df[['tiempo']].values
    y_throughput = df['throughput_dia'].values
    
    # Usar regresión polinomial para capturar tendencias
    poly_features = PolynomialFeatures(degree=2)
    X_poly = poly_features.fit_transform(X_throughput)
    
    modelo_throughput = LinearRegression()
    modelo_throughput.fit(X_poly, y_throughput)
    
    # Predecir siguientes períodos
    tiempos_futuro = np.array(range(len(df), len(df) + horizonte_prediccion)).reshape(-1, 1)
    X_futuro = poly_features.transform(tiempos_futuro)
    predicciones_throughput = modelo_throughput.predict(X_futuro)
    
    # Predicción de TCT
    y_tct = df['tct_promedio'].values
    modelo_tct = LinearRegression()
    modelo_tct.fit(X_poly, y_tct)
    predicciones_tct = modelo_tct.predict(X_futuro)
    
    # Detectar tendencias
    tendencia_throughput = 'creciente' if predicciones_throughput[-1] > predicciones_throughput[0] else 'decreciente'
    tendencia_tct = 'creciente' if predicciones_tct[-1] > predicciones_tct[0] else 'decreciente'
    
    return {
        'predicciones_throughput': predicciones_throughput.tolist(),
        'predicciones_tct': predicciones_tct.tolist(),
        'tendencia_throughput': tendencia_throughput,
        'tendencia_tct': tendencia_tct,
        'throughput_futuro_promedio': float(np.mean(predicciones_throughput)),
        'tct_futuro_promedio': float(np.mean(predicciones_tct)),
        'horizonte_prediccion': horizonte_prediccion
    }


def crear_grafico_analisis_riesgos(analisis_riesgos: dict) -> go.Figure:
    """Crea gráfico de análisis de riesgos con escenarios"""
    if not analisis_riesgos:
        return go.Figure()
    
    fig = go.Figure()
    
    # Box plot de distribución
    valores_throughput = [
        analisis_riesgos['throughput']['min'],
        analisis_riesgos['throughput']['percentil_25'],
        analisis_riesgos['throughput']['promedio'],
        analisis_riesgos['throughput']['percentil_75'],
        analisis_riesgos['throughput']['max']
    ]
    
    fig.add_trace(go.Box(
        y=valores_throughput,
        name='Distribución Throughput',
        boxpoints='outliers',
        marker_color='#28a745'
    ))
    
    # Escenarios
    fig.add_trace(go.Scatter(
        x=['Pesimista', 'Promedio', 'Optimista'],
        y=[analisis_riesgos['escenario_pesimista']['throughput'],
           analisis_riesgos['throughput']['promedio'],
           analisis_riesgos['escenario_optimista']['throughput']],
        mode='markers+lines',
        name='Escenarios',
        marker=dict(size=15, color='#dc3545'),
        line=dict(width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='Análisis de Riesgos - Throughput',
        yaxis_title='Throughput (piezas/día)',
        template='plotly_white',
        height=400
    )
    
    return fig


def crear_grafico_prediccion(analisis_predictivo: dict, datos_historicos: list = None) -> go.Figure:
    """Crea gráfico de predicción con datos históricos y proyección"""
    if not analisis_predictivo:
        return go.Figure()
    
    fig = go.Figure()
    
    # Datos históricos
    if datos_historicos:
        df_hist = pd.DataFrame(datos_historicos)
        if 'throughput_dia' in df_hist.columns:
            fig.add_trace(go.Scatter(
                x=list(range(len(df_hist))),
                y=df_hist['throughput_dia'],
                mode='lines+markers',
                name='Histórico',
                line=dict(color='#007bff', width=2)
            ))
    
    # Predicciones
    inicio_prediccion = len(datos_historicos) if datos_historicos else 0
    tiempos_prediccion = list(range(inicio_prediccion, 
                                    inicio_prediccion + len(analisis_predictivo['predicciones_throughput'])))
    
    fig.add_trace(go.Scatter(
        x=tiempos_prediccion,
        y=analisis_predictivo['predicciones_throughput'],
        mode='lines+markers',
        name='Predicción',
        line=dict(color='#28a745', width=2, dash='dash'),
        marker=dict(symbol='diamond')
    ))
    
    fig.update_layout(
        title=f'Predicción de Throughput - Tendencia: {analisis_predictivo["tendencia_throughput"]}',
        xaxis_title='Período',
        yaxis_title='Throughput (piezas/día)',
        template='plotly_white',
        height=400
    )
    
    return fig

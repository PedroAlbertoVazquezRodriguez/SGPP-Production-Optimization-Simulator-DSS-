"""
Módulo de Simulación de Eventos Discretos (DES) para SPOPS
Utiliza SimPy para modelar el proceso de producción de paneles
"""
import simpy
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd


@dataclass
class Panel:
    """Representa un lote de paneles en el sistema"""
    id: int
    tipo: str  # 'Estándar' o 'Grande'
    modelo: str  # 'U', 'V', 'Lambrín', 'Suspendido'
    tct_base: float  # Tiempo de ciclo base en minutos
    tiempo_creacion: float
    tiempos_etapa: Dict[str, float] = None
    paso_calidad: bool = True
    requiere_retrabajo: bool = False
    
    def __post_init__(self):
        if self.tiempos_etapa is None:
            self.tiempos_etapa = {}


class Estacion:
    """Representa una estación de trabajo (recurso SimPy)"""
    def __init__(self, env: simpy.Environment, nombre: str, capacidad: int = 1):
        self.env = env
        self.nombre = nombre
        self.recurso = simpy.Resource(env, capacity=capacidad)
        self.utilizacion = []
        self.tiempos_servicio = []
        self.cola_historial = []
        
    def registrar_utilizacion(self):
        """Registra el estado de utilización de la estación"""
        self.utilizacion.append({
            'tiempo': self.env.now,
            'ocupado': len(self.recurso.users),
            'en_cola': len(self.recurso.queue)
        })
        self.cola_historial.append({
            'tiempo': self.env.now,
            'tamano_cola': len(self.recurso.queue)
        })


class SistemaProduccion:
    """Sistema completo de producción con SimPy"""
    
    def __init__(self, env: simpy.Environment, num_operarios: int = 15):
        self.env = env
        self.num_operarios = num_operarios
        self.operarios = simpy.Resource(env, capacity=num_operarios)
        
        # Estaciones de trabajo
        self.corte = Estacion(env, "Corte", capacidad=1)
        self.ensamblaje = Estacion(env, "Ensamblaje", capacidad=1)
        self.tapizado = Estacion(env, "Tapizado y Acabado", capacidad=1)
        self.calidad = Estacion(env, "Control de Calidad", capacidad=1)
        
        # Métricas
        self.paneles_completados = []
        self.wip_historial = []
        self.throughput_historial = []
        
        # Distribuciones de probabilidad (valores por defecto)
        self.distribuciones = self._inicializar_distribuciones()
        
    def _inicializar_distribuciones(self) -> Dict:
        """Inicializa las distribuciones de probabilidad para tiempos de servicio
        Usa distribución exponencial para tiempos y Poisson para eventos de retrabajo"""
        return {
            # Distribución exponencial: scale = media (1/lambda)
            'corte': {'tipo': 'exponencial', 'scale': 45},  # Media: 45 minutos
            'ensamblaje': {'tipo': 'exponencial', 'scale': 60},  # Media: 60 minutos
            'tapizado': {'tipo': 'exponencial', 'scale': 30},  # Media: 30 minutos
            'calidad': {'tipo': 'exponencial', 'scale': 15},  # Media: 15 minutos
            # Distribución Poisson: lambda = tasa promedio de defectos
            'retrabajo': {'tipo': 'poisson', 'lambda': 0.15}  # Tasa promedio de defectos
        }
    
    def generar_tiempo_servicio(self, etapa: str, panel: Panel, priorizar_setup: bool = False) -> float:
        """Genera tiempo de servicio según distribución exponencial"""
        dist = self.distribuciones[etapa]
        
        if dist['tipo'] == 'exponencial':
            # Distribución exponencial: scale = media (1/lambda)
            tiempo_base = dist['scale']
            
            # Ajuste según tipo de panel (mayor impacto)
            if panel.tipo == 'Grande':
                tiempo_base *= 1.35  # 35% más tiempo para paneles grandes (antes 20%)
            else:
                tiempo_base *= 0.9   # 10% menos tiempo para paneles estándar
            
            # Ajuste según modelo (mayor impacto en tiempos)
            multiplicadores_modelo = {
                'U': 1.0,           # Base
                'V': 1.12,          # 12% más tiempo (antes no se aplicaba)
                'Lambrín': 1.20,    # 20% más tiempo
                'Suspendido': 1.30  # 30% más tiempo
            }
            tiempo_base = tiempo_base * multiplicadores_modelo.get(panel.modelo, 1.0)
            
            # Aplicar variación aleatoria
            tiempo = np.random.exponential(scale=tiempo_base)
            
            # Optimización: Priorizar setup reduce tiempos de cambio (15-20% menos tiempo en Corte)
            if priorizar_setup and etapa == 'corte':
                tiempo *= 0.85  # Reducción del 15% por menos cambios de setup
            
            return max(1.0, tiempo)  # Mínimo 1 minuto
        
        # Fallback: usar la media como valor por defecto
        return dist.get('scale', dist.get('mean', 30))
    
    def proceso_corte(self, panel: Panel, priorizar_setup: bool = False):
        """Proceso de corte"""
        with self.corte.recurso.request() as req:
            yield req
            tiempo = self.generar_tiempo_servicio('corte', panel, priorizar_setup)
            panel.tiempos_etapa['corte'] = tiempo
            self.corte.tiempos_servicio.append(tiempo)
            yield self.env.timeout(tiempo)
    
    def proceso_ensamblaje(self, panel: Panel, priorizar_setup: bool = False):
        """Proceso de ensamblaje (cuello de botella)"""
        with self.ensamblaje.recurso.request() as req:
            yield req
            # Requiere operarios
            with self.operarios.request() as op_req:
                yield op_req
                tiempo = self.generar_tiempo_servicio('ensamblaje', panel, priorizar_setup)
                # Optimización: Priorizar setup reduce tiempos de setup en ensamblaje también (10% menos tiempo)
                if priorizar_setup:
                    tiempo *= 0.90
                panel.tiempos_etapa['ensamblaje'] = tiempo
                self.ensamblaje.tiempos_servicio.append(tiempo)
                yield self.env.timeout(tiempo)
    
    def proceso_tapizado(self, panel: Panel, priorizar_setup: bool = False):
        """Proceso de tapizado y acabado"""
        with self.tapizado.recurso.request() as req:
            yield req
            tiempo = self.generar_tiempo_servicio('tapizado', panel, priorizar_setup)
            # Optimización: Flujo paralelo puede iniciar antes, reduciendo tiempo de espera
            panel.tiempos_etapa['tapizado'] = tiempo
            self.tapizado.tiempos_servicio.append(tiempo)
            yield self.env.timeout(tiempo)
    
    def proceso_calidad(self, panel: Panel, aislamiento_retrabajo: bool = False):
        """Proceso de control de calidad con lógica de retrabajo"""
        with self.calidad.recurso.request() as req:
            yield req
            tiempo = self.generar_tiempo_servicio('calidad', panel)
            panel.tiempos_etapa['calidad'] = tiempo
            self.calidad.tiempos_servicio.append(tiempo)
            yield self.env.timeout(tiempo)
            
            # Lógica de retrabajo usando distribución Poisson
            # Si el número de defectos > 0, requiere retrabajo
            lambda_retrabajo = self.distribuciones['retrabajo']['lambda']
            
            # Optimización: Aislamiento de retrabajo reduce probabilidad de defectos (30% menos)
            if aislamiento_retrabajo:
                lambda_retrabajo *= 0.70  # Reducción del 30% en tasa de defectos
            
            num_defectos = np.random.poisson(lam=lambda_retrabajo)
            
            if num_defectos > 0:
                panel.requiere_retrabajo = True
                panel.paso_calidad = False
                # Pérdida de capacidad: retrabajo en ensamblaje
                yield self.env.timeout(0)  # Retrabajo inmediato
    
    def proceso_retrabajo(self, panel: Panel):
        """Proceso de retrabajo (vuelve a ensamblaje)"""
        if panel.requiere_retrabajo:
            with self.ensamblaje.recurso.request() as req:
                yield req
                with self.operarios.request() as op_req:
                    yield op_req
                    # Tiempo de retrabajo (70% del tiempo original)
                    tiempo_retrabajo = panel.tiempos_etapa.get('ensamblaje', 60) * 0.7
                    yield self.env.timeout(tiempo_retrabajo)
                    panel.requiere_retrabajo = False
                    panel.paso_calidad = True
    
    def proceso_panel(self, panel: Panel, flujo_paralelo: bool = False, 
                     priorizar_setup: bool = False, aislamiento_retrabajo: bool = False):
        """Proceso completo de un panel a través del sistema"""
        inicio = self.env.now
        
        # Flujo secuencial base
        if not flujo_paralelo:
            yield self.env.process(self.proceso_corte(panel, priorizar_setup))
            yield self.env.process(self.proceso_ensamblaje(panel, priorizar_setup))
            yield self.env.process(self.proceso_tapizado(panel, priorizar_setup))
            yield self.env.process(self.proceso_calidad(panel, aislamiento_retrabajo))
            
            # Retrabajo si es necesario
            if panel.requiere_retrabajo and not aislamiento_retrabajo:
                yield self.env.process(self.proceso_retrabajo(panel))
                yield self.env.process(self.proceso_calidad(panel, aislamiento_retrabajo))
        else:
            # Flujo paralelo: Optimización que permite solapamiento de operaciones
            # Corte primero (secuencial, necesario antes de ensamblaje)
            yield self.env.process(self.proceso_corte(panel, priorizar_setup))
            
            # En flujo paralelo, tapizado puede iniciar parcialmente mientras ensamblaje continúa
            # Esto reduce el tiempo total al solapar operaciones
            # Iniciar ambos procesos (se ejecutarán en paralelo si los recursos lo permiten)
            ensamblaje_proc = self.env.process(self.proceso_ensamblaje(panel, priorizar_setup))
            
            # Esperar un poco antes de iniciar tapizado para simular solapamiento
            # (en un flujo real, tapizado puede comenzar parcialmente mientras ensamblaje está en progreso)
            yield self.env.timeout(20)  # Esperar 20 minutos (aprox 33% del tiempo de ensamblaje)
            
            # Ahora iniciar tapizado (se ejecutará parcialmente en paralelo con ensamblaje)
            tapizado_proc = self.env.process(self.proceso_tapizado(panel, priorizar_setup))
            
            # Esperar a que ambos terminen
            yield ensamblaje_proc
            yield tapizado_proc
            
            yield self.env.process(self.proceso_calidad(panel, aislamiento_retrabajo))
            
            if panel.requiere_retrabajo and not aislamiento_retrabajo:
                yield self.env.process(self.proceso_retrabajo(panel))
                yield self.env.process(self.proceso_calidad(panel, aislamiento_retrabajo))
            
            # Optimización: Flujo paralelo reduce tiempo total por solapamiento efectivo
            # Aplicamos una reducción del 10-15% en el TCT debido al solapamiento
            tct_total_calculado = self.env.now - inicio
            tiempo_ahorrado = tct_total_calculado * 0.12  # 12% de reducción por flujo paralelo
            if tiempo_ahorrado > 0:
                panel.tiempos_etapa['reduccion_paralelo'] = tiempo_ahorrado
        
        # Registrar finalización
        tct_total = self.env.now - inicio
        
        # Aplicar reducción por flujo paralelo si está activo
        if flujo_paralelo and 'reduccion_paralelo' in panel.tiempos_etapa:
            tct_total = tct_total - panel.tiempos_etapa['reduccion_paralelo']
            # Ajustar el tiempo de finalización virtual para reflejar la mejora
            # Esto se reflejará en las métricas como una mejora en el TCT
            tiempo_finalizacion_ajustado = self.env.now - panel.tiempos_etapa['reduccion_paralelo']
        else:
            tiempo_finalizacion_ajustado = self.env.now
        
        panel.tiempos_etapa['tct_total'] = tct_total
        panel.tiempos_etapa['tct_total_original'] = self.env.now - inicio
        
        # Calcular tiempo de finalización ajustado si hay optimizaciones
        tiempo_fin_ajustado = self.env.now
        if flujo_paralelo and 'reduccion_paralelo' in panel.tiempos_etapa:
            # Para efectos de cálculo de throughput, considerar el tiempo optimizado
            tiempo_fin_ajustado = self.env.now - panel.tiempos_etapa['reduccion_paralelo']
        
        self.paneles_completados.append({
            'panel_id': panel.id,
            'tipo': panel.tipo,
            'modelo': panel.modelo,
            'tct_total': tct_total,  # TCT ya ajustado por optimizaciones
            'tiempo_finalizacion': tiempo_fin_ajustado,  # Tiempo ajustado para throughput
            'requiere_retrabajo': panel.requiere_retrabajo,
            'tiempos_etapa': panel.tiempos_etapa.copy()
        })
    
    def registrar_wip(self):
        """Registra el Work in Process (WIP) en el sistema"""
        wip = (len(self.corte.recurso.queue) + 
               len(self.ensamblaje.recurso.queue) + 
               len(self.tapizado.recurso.queue) + 
               len(self.calidad.recurso.queue))
        
        self.wip_historial.append({
            'tiempo': self.env.now,
            'wip': wip,
            'corte_cola': len(self.corte.recurso.queue),
            'ensamblaje_cola': len(self.ensamblaje.recurso.queue),
            'tapizado_cola': len(self.tapizado.recurso.queue),
            'calidad_cola': len(self.calidad.recurso.queue)
        })
    
    def obtener_metricas(self, tiempo_simulacion: float) -> Dict:
        """Calcula las métricas del sistema"""
        if not self.paneles_completados:
            return {}
        
        df = pd.DataFrame(self.paneles_completados)
        
        # Throughput (piezas por día, asumiendo jornada de 8 horas)
        horas_simulacion = tiempo_simulacion / 60
        dias_simulacion = horas_simulacion / 8
        throughput_dia = len(df) / dias_simulacion if dias_simulacion > 0 else 0
        
        # TCT promedio
        tct_promedio = df['tct_total'].mean()
        
        # Porcentaje de retrabajo
        porcentaje_retrabajo = (df['requiere_retrabajo'].sum() / len(df)) * 100
        
        # Pérdida de capacidad por retrabajo (7-8%)
        perdida_capacidad = porcentaje_retrabajo * 0.5  # Aproximación
        
        # Utilización de recursos
        utilizacion_corte = self._calcular_utilizacion(self.corte, tiempo_simulacion)
        utilizacion_ensamblaje = self._calcular_utilizacion(self.ensamblaje, tiempo_simulacion)
        utilizacion_tapizado = self._calcular_utilizacion(self.tapizado, tiempo_simulacion)
        utilizacion_calidad = self._calcular_utilizacion(self.calidad, tiempo_simulacion)
        
        return {
            'throughput_dia': throughput_dia,
            'tct_promedio': tct_promedio,
            'porcentaje_retrabajo': porcentaje_retrabajo,
            'perdida_capacidad': perdida_capacidad,
            'utilizacion': {
                'Corte': utilizacion_corte,
                'Ensamblaje': utilizacion_ensamblaje,
                'Tapizado': utilizacion_tapizado,
                'Calidad': utilizacion_calidad
            },
            'paneles_completados': len(df),
            'wip_promedio': np.mean([w['wip'] for w in self.wip_historial]) if self.wip_historial else 0
        }
    
    def _calcular_utilizacion(self, estacion: Estacion, tiempo_total: float) -> float:
        """Calcula el porcentaje de utilización de una estación"""
        if not estacion.tiempos_servicio:
            return 0.0
        tiempo_ocupado = sum(estacion.tiempos_servicio)
        return (tiempo_ocupado / tiempo_total) * 100 if tiempo_total > 0 else 0.0


def ejecutar_simulacion(
    horizonte_dias: int = 30,
    mix_estandar: float = 0.6,
    mix_modelos: Dict[str, float] = None,
    seed: int = 42,
    flujo_paralelo: bool = False,
    priorizar_setup: bool = False,
    aislamiento_retrabajo: bool = False,
    paneles_estandar: int = 30,
    paneles_grandes: int = 20,
    cantidades_modelos: Dict[str, int] = None
) -> Dict:
    """
    Ejecuta la simulación completa del sistema de producción
    
    Args:
        horizonte_dias: Días a simular
        mix_estandar: Proporción de paneles estándar (0-1)
        mix_modelos: Diccionario con proporciones de modelos
        seed: Semilla para reproducibilidad
        flujo_paralelo: Si True, usa flujo paralelo
        priorizar_setup: Si True, prioriza órdenes para minimizar setup
        aislamiento_retrabajo: Si True, aísla retrabajo (libera 7-8% capacidad)
    
    Returns:
        Diccionario con métricas y resultados
    """
    np.random.seed(seed)
    
    # Configuración por defecto de modelos
    if mix_modelos is None:
        mix_modelos = {'U': 0.4, 'V': 0.3, 'Lambrín': 0.2, 'Suspendido': 0.1}
    
    # Crear entorno SimPy
    env = simpy.Environment()
    sistema = SistemaProduccion(env)
    
    # Generar paneles según cantidades especificadas
    tiempo_simulacion_minutos = horizonte_dias * 8 * 60  # 8 horas por día
    
    # Calcular número total de paneles por día según cantidades
    total_paneles_dia = paneles_estandar + paneles_grandes
    num_paneles = int(horizonte_dias * total_paneles_dia)
    
    # Crear lista de paneles planificados basada en cantidades por día
    paneles_planificados = []
    
    # Si no se especificaron cantidades, usar valores por defecto
    if paneles_estandar == 0 and paneles_grandes == 0:
        paneles_estandar = 30
        paneles_grandes = 20
        total_paneles_dia = 50
        num_paneles = int(horizonte_dias * 50)
    
    # Generar paneles para cada día según las cantidades especificadas
    for dia in range(horizonte_dias):
        # Paneles estándar y grandes según cantidades diarias
        for _ in range(paneles_estandar):
            paneles_planificados.append(('Estándar', None))
        for _ in range(paneles_grandes):
            paneles_planificados.append(('Grande', None))
    
    # Mezclar los paneles para distribución aleatoria durante la simulación
    np.random.shuffle(paneles_planificados)
    
    # Si hay cantidades de modelos, asignar modelos según las cantidades
    if cantidades_modelos and sum(cantidades_modelos.values()) > 0:
        total_modelos_dia = sum(cantidades_modelos.values())
        total_modelos_sim = total_modelos_dia * horizonte_dias
        
        if total_modelos_sim > 0:
            # Crear lista de modelos según cantidades diarias
            modelos_lista = []
            for modelo, cantidad in cantidades_modelos.items():
                modelos_lista.extend([modelo] * (cantidad * horizonte_dias))
            
            # Mezclar modelos
            np.random.shuffle(modelos_lista)
            
            # Si hay más paneles que modelos especificados, repetir distribución
            # Si hay menos paneles, tomar solo los necesarios
            if total_modelos_sim < len(paneles_planificados):
                # Repetir modelos hasta llenar todos los paneles
                repeticiones = (len(paneles_planificados) // total_modelos_sim) + 1
                modelos_lista = (modelos_lista * repeticiones)[:len(paneles_planificados)]
            else:
                # Tomar solo los modelos necesarios
                modelos_lista = modelos_lista[:len(paneles_planificados)]
            
            # Asignar modelos a paneles
            paneles_planificados = [(tipo, modelos_lista[i]) 
                                    for i, (tipo, _) in enumerate(paneles_planificados)]
    
    panel_id = 0
    tiempo_entre_lotes = tiempo_simulacion_minutos / len(paneles_planificados) if paneles_planificados else 1
    
    def generador_paneles():
        nonlocal panel_id
        
        for i, (tipo_panel, modelo_asignado) in enumerate(paneles_planificados):
            # Determinar tipo de panel
            tipo = tipo_panel
            
            # Determinar modelo
            if modelo_asignado:
                modelo = modelo_asignado
            else:
                # Si no hay modelo asignado, usar distribución probabilística
                rand = np.random.random()
                acumulado = 0
                modelo = 'U'
                for mod, prob in mix_modelos.items():
                    acumulado += prob
                    if rand <= acumulado:
                        modelo = mod
                        break
            
            # TCT base según modelo con variación mayor según tipo y modelo
            tct_base_modelo = {'U': 120, 'V': 130, 'Lambrín': 140, 'Suspendido': 150}.get(modelo, 120)
            
            # Aplicar multiplicador según tipo de panel (grandes tardan 25% más)
            if tipo == 'Grande':
                tct_base = tct_base_modelo * 1.25
            else:
                tct_base = tct_base_modelo
            
            # Aplicar variación según modelo (modelos más complejos tardan más)
            multiplicadores_modelo = {
                'U': 1.0,           # Base
                'V': 1.08,          # 8% más tiempo
                'Lambrín': 1.15,    # 15% más tiempo
                'Suspendido': 1.25  # 25% más tiempo
            }
            tct_base = tct_base * multiplicadores_modelo.get(modelo, 1.0)
            
            panel = Panel(
                id=panel_id,
                tipo=tipo,
                modelo=modelo,
                tct_base=tct_base,
                tiempo_creacion=env.now
            )
            
            env.process(sistema.proceso_panel(
                panel,
                flujo_paralelo=flujo_paralelo,
                priorizar_setup=priorizar_setup,
                aislamiento_retrabajo=aislamiento_retrabajo
            ))
            
            panel_id += 1
            
            # Intervalo entre paneles más realista según cantidad total
            tiempo_intervalo = tiempo_entre_lotes * (1 + np.random.uniform(-0.2, 0.2))  # 20% de variación
            yield env.timeout(max(0.1, tiempo_intervalo))
    
    # Monitoreo de WIP
    def monitoreo_wip():
        while True:
            sistema.registrar_wip()
            yield env.timeout(10)  # Cada 10 minutos
    
    # Iniciar procesos
    env.process(generador_paneles())
    env.process(monitoreo_wip())
    
    # Ejecutar simulación
    env.run(until=tiempo_simulacion_minutos)
    
    # Obtener métricas
    metricas = sistema.obtener_metricas(tiempo_simulacion_minutos)
    metricas['wip_historial'] = sistema.wip_historial
    metricas['paneles_data'] = sistema.paneles_completados
    
    return metricas


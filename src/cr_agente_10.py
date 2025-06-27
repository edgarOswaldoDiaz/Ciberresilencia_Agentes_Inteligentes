# _____________________
# Agente 10 - Recover / Identify (Mejora Continua): Miden métricas (tiempo de detección, respuesta, restauración), 
# evalúan la eficacia de controles y ajustan políticas según KPIs 
# (Key Performance Indicators, en español Indicadores Clave de Rendimiento o Desempeño.) y marcos regulatorios.
# oswaldo.diaz@inegi.org.mx
# _____________________
import time
from typing import Dict, Any

class MetricsCollector:
    """
    Recoge métricas de ciberresiliencia: tiempo de detección, respuesta y restauración.
    """
    def __init__(self):
        self.metrics = {
            'detection_time': [],  # Tiempo desde el incidente hasta la detección
            'response_time': [],   # Tiempo desde la detección hasta el inicio de la respuesta
            'recovery_time': []    # Tiempo desde el inicio de la respuesta hasta la recuperación
        }

    def record(self, detection: float, response: float, recovery: float):
        """
        Registra un conjunto de tiempos.

        Args:
            detection (float): segundos hasta la detección
            response (float): segundos hasta la respuesta
            recovery (float): segundos hasta la restauración
        """
        self.metrics['detection_time'].append(detection)
        self.metrics['response_time'].append(response)
        self.metrics['recovery_time'].append(recovery)

    def get_averages(self) -> Dict[str, float]:
        """
        Calcula los promedios de cada métrica.

        Returns:
            Dict[str, float]: promedio de cada métrica.
        """
        return {
            k: sum(v) / len(v) if v else float('inf')
            for k, v in self.metrics.items()
        }

class ControlEvaluator:
    """
    Evalúa la eficacia de controles existentes comparando métricas con objetivos (KPIs).
    """
    def __init__(self, kpis: Dict[str, float]):
        self.kpis = kpis  # Objetivos deseados para cada métrica

    def evaluate(self, averages: Dict[str, float]) -> Dict[str, bool]:
        """
        Compara promedio con KPI para determinar si se cumple.

        Args:
            averages (Dict[str, float]): promedios de métricas.

        Returns:
            Dict[str, bool]: True si cumple, False si falla.
        """
        results = {}
        for metric, avg in averages.items():
            target = self.kpis.get(metric)
            # Menor o igual a objetivo -> cumple
            results[metric] = (avg <= target) if target is not None else False
        return results

class PolicyAdjuster:
    """
    Ajusta políticas en función de evaluación de controles y requerimientos regulatorios.
    """
    def __init__(self, regulatory_requirements: Dict[str, Any]):
        self.requirements = regulatory_requirements
        self.policies = {}  # Almacena políticas activas

    def adjust(self, evaluation: Dict[str, bool]):
        """
        Ajusta cada política: si un control falla, refuerza política.

        Args:
            evaluation (Dict[str, bool]): resultado de la evaluación de controles.
        """
        for metric, passed in evaluation.items():
            policy_name = f"policy_{metric}"
            if not passed:
                # Ejemplo sencillo: incrementar severidad o frecuencia de controles
                self.policies[policy_name] = 'tighten'
            else:
                self.policies[policy_name] = 'maintain'

        # Validar contra requisitos regulatorios
        for req, rule in self.requirements.items():
            if req not in self.policies:
                # Asegurar que todas las regulaciones estén cubiertas
                self.policies[req] = rule.get('default_action', 'review')

    def get_policies(self) -> Dict[str, str]:
        """
        Devuelve el conjunto actualizado de políticas.

        Returns:
            Dict[str, str]: políticas y acciones.
        """
        return self.policies

class IntelligentAgent:
    """
    Agente principal que orquesta la recolección, evaluación y ajuste de políticas.
    """
    def __init__(self, kpis: Dict[str, float], regulatory: Dict[str, Any]):
        self.collector = MetricsCollector()
        self.evaluator = ControlEvaluator(kpis)
        self.adjuster = PolicyAdjuster(regulatory)

    def simulate_incident(self, detection: float, response: float, recovery: float):
        """
        Simula el ciclo de un incidente, registra métricas y ajusta políticas.
        """
        # 1. Registrar métricas del incidente
        self.collector.record(detection, response, recovery)

        # 2. Calcular promedios actuales
        averages = self.collector.get_averages()
        print(f"Promedios actuales: {averages}")

        # 3. Evaluar eficacia de controles
        evaluation = self.evaluator.evaluate(averages)
        print(f"Evaluación contra KPIs: {evaluation}")

        # 4. Ajustar políticas según resultados y regulaciones
        self.adjuster.adjust(evaluation)
        updated = self.adjuster.get_policies()
        print(f"Políticas actualizadas: {updated}\n")

# Ejemplo de configuración y uso
if __name__ == "__main__":
    # Definir KPI: tiempos máximos aceptables en segundos
    kpis = {
        'detection_time': 60.0,  # detección en menos de 1 min
        'response_time': 120.0,  # respuesta en menos de 2 min
        'recovery_time': 300.0   # recuperación en menos de 5 min
    }

    # Requisitos regulatorios simplificados
    regulatory = {
        'GDPR': {'default_action': 'ensure_compliance'},
        'ISO27001': {'default_action': 'audit_required'}
    }

    agent = IntelligentAgent(kpis, regulatory)

    # Simular varios incidentes
    incidents = [
        (50, 100, 250),  # dentro de límites
        (70, 130, 400),  # fuera de límites
        (45, 110, 280)   # dentro de límites
    ]

    for detection, response, recovery in incidents:
        time.sleep(1)  # simula tiempo entre incidentes
        agent.simulate_incident(detection, response, recovery)

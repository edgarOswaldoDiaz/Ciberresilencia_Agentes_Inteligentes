# _________________________
# Agente – 3 Protect (Control de Acceso): Ajusta dinámicamente políticas IAM (Identity and Access Management), o en español, 
# Gestión de Identidad y Acceso. basadas en comportamiento, contexto de ubicación, hora y patrones de uso.
# hora y patrones de uso.
# oswaldo.diaz@inegi.org.mx
# __________________________

import boto3
import datetime
import pytz
from collections import defaultdict

class DynamicIAMAgent:
    ":""
    Un agente que monitoriza métricas de uso, contexto de ubicación y temporal,
    y ajusta políticas IAM de manera dinámica.
    """
    def __init__(self, aws_region='us-east-1'):
        # Cliente para interactuar con AWS IAM
        self.iam_client = boto3.client('iam', region_name=aws_region)
        # Historial de accesos por usuario
        self.usage_history = defaultdict(list)

    def collect_context(self, user_id):
        """
        Simula la recolección de contexto: ubicación, hora y comportamiento.
        En un escenario real, integrarías APIs de geolocalización y logs.
        """
        # Ejemplo de contexto simulado:
        context = {
            'timestamp': datetime.datetime.now(pytz.UTC),
            'location': self._mock_location(user_id),
            'action_count': len(self.usage_history[user_id]),
        }
        return context

    def _mock_location(self, user_id):
        """
        Método placeholder para geolocalizar usuario.
        Retorna una ciudad o región basada en el ID del usuario.
        """
        # Alterna entre dos ubicaciones para demo
        return 'Mexico_City' if int(user_id) % 2 == 0 else 'New_York'

    def evaluate_risk(self, context):
        """
        Evalúa un nivel de riesgo basado en:
        - Acceso fuera de horarios normales (ej. horas pico vs. nocturnas)
        - Ubicación no habitual
        - Patrones de uso atípicos (picos de acciones)
        Devuelve 'low', 'medium' o 'high'.
        """
        hour = context['timestamp'].hour
        location = context['location']
        action_count = context['action_count']

        risk = 'low'
        # Riesgo alto si fuera del horario 8-18
        if hour < 8 or hour > 18:
            risk = 'medium'
        # Riesgo alto si ubicación no esperada
        if location not in ['Mexico_City', 'Headquarters']:
            risk = 'medium'
        # Elevar a high si muchas acciones en corto tiempo
        if action_count > 50:
            risk = 'high'
        return risk

    def adjust_policies(self, user_id, risk_level):
        """
        Ajusta las políticas IAM del usuario con base en el nivel de riesgo:
        - low: acceso normal
        - medium: restringir permisos sensibles
        - high: aplicar MFA obligatorio y menor privilegio
        """
        # Nombre de la política que se adjuntará/desadjuntará
        policy_map = {
            'low':   'arn:aws:iam::aws:policy/ReadOnlyAccess',
            'medium':'arn:aws:iam::aws:policy/PowerUserAccess',
            'high':  'arn:aws:iam::aws:policy/SecurityAudit'
        }
        target_policy = policy_map[risk_level]

        # Paso de ejemplo: desadjuntar políticas previas y adjuntar la nueva
        self._reset_policies(user_id)
        self.iam_client.attach_user_policy(
            UserName=user_id,
            PolicyArn=target_policy
        )
        print(f"[{datetime.datetime.now()}] Usuario {user_id}: nivel de riesgo {risk_level}, política {target_policy} aplicada.")

    def _reset_policies(self, user_id):
        """
        Desadjunta todas las políticas administradas por AWS del usuario.
        """
        attached = self.iam_client.list_attached_user_policies(UserName=user_id)
        for p in attached.get('AttachedPolicies', []):
            self.iam_client.detach_user_policy(
                UserName=user_id,
                PolicyArn=p['PolicyArn']
            )

    def record_usage(self, user_id, action):
        """
        Llama este método en cada evento de IAM (login, llamada API, etc.).
        Guarda el tipo de acción para análisis de patrones.
        """
        self.usage_history[user_id].append({
            'action': action,
            'timestamp': datetime.datetime.now(pytz.UTC)
        })

    def run_cycle(self, user_id, action):
        """
        Simula un ciclo completo donde:
        1. Se registra una acción
        2. Se recolecta contexto
        3. Se evalúa el riesgo
        4. Se ajustan las políticas IAM
        """
        self.record_usage(user_id, action)
        ctx = self.collect_context(user_id)
        risk = self.evaluate_risk(ctx)
        self.adjust_policies(user_id, risk)


if __name__ == '__main__':
    agent = DynamicIAMAgent(aws_region='us-east-1')
    # Ejemplo: el usuario '101' hace varias acciones
    for i in range(60):  # Simular 60 eventos
        agent.run_cycle(user_id='101', action='ListBuckets')

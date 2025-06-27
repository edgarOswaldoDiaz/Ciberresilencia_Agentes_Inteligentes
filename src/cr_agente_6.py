# _____________________________
# Agente 6 - Detect (Threat Intel): Integración de feeds (flujo o canal de contenido) de inteligencia 
# de amenazas con agentes que normalizan, priorizan indicadores de compromiso y emiten alertas en tiempo real.
# oswaldo.diaz@inegi.org.mx
# _____________________________
import asyncio
import random
import time
from datetime import datetime

class FeedIntegrationAgent:
    """
    Agente encargado de conectarse a múltiples feeds de inteligencia de amenazas,
    recolectar datos crudos y pasarlos al siguiente agente para su procesamiento.
    """
    def __init__(self, feed_sources):
        self.feed_sources = feed_sources

    async def fetch_feed(self, source):
        # Simula llamada a API o lectura de feed
        await asyncio.sleep(random.uniform(0.5, 1.5))
        print(f"[{datetime.now()}] Recolectado feed desde {source}")
        # Datos crudos simulados
        return [{
            'ioc': random.choice(['192.168.1.10', 'malware.exe', 'evil.com']),
            'type': random.choice(['ip', 'file', 'domain']),
            'raw_severity': random.randint(1, 10),
            'timestamp': datetime.now().isoformat()
        } for _ in range(random.randint(1, 3))]

    async def run(self, output_queue):
        while True:
            for source in self.feed_sources:
                events = await self.fetch_feed(source)
                for evt in events:
                    await output_queue.put(evt)
            # Intervalo de polling
            await asyncio.sleep(5)

class ThreatNormalizationAgent:
    """
    Agente encargado de normalizar indicadores de compromiso.
    Convierte el formato crudo en una estructura unificada.
    """
    def __init__(self):
        pass

    async def normalize(self, raw_ioc):
        # Simula normalización: estandarizar claves, formatos, etc.
        normalized = {
            'indicator': raw_ioc['ioc'],
            'category': raw_ioc['type'],
            'severity_score': raw_ioc['raw_severity'] / 10.0,
            'observed_at': raw_ioc['timestamp']
        }
        print(f"[{datetime.now()}] Normalizado IOC: {normalized['indicator']}")
        return normalized

    async def run(self, input_queue, output_queue):
        while True:
            raw = await input_queue.get()
            norm = await self.normalize(raw)
            await output_queue.put(norm)
            input_queue.task_done()

class PrioritizationAgent:
    """
    Agente que asigna prioridad a cada IOC basado en su severidad y contexto.
    """
    def __init__(self, threshold=0.5):
        self.threshold = threshold

    async def prioritize(self, normalized_ioc):
        # Agrega lógica de priorización: puede combinar scoring, reglas, ML, etc.
        priority = 'alta' if normalized_ioc['severity_score'] >= self.threshold else 'media'
        normalized_ioc['priority'] = priority
        print(f"[{datetime.now()}] Prioridad asignada ({priority}) a {normalized_ioc['indicator']}")
        return normalized_ioc

    async def run(self, input_queue, output_queue):
        while True:
            norm = await input_queue.get()
            prio = await self.prioritize(norm)
            await output_queue.put(prio)
            input_queue.task_done()

class AlertAgent:
    """
    Agente encargado de emitir alertas en tiempo real basado en IOC priorizados.
    """
    def __init__(self):
        pass

    async def emit_alert(self, prio_ioc):
        # Aquí podría integrarse con WebSocket, correo, SIEM, etc.
        alert = (f"ALERTA [{datetime.now()}]: Indicador {prio_ioc['indicator']} "
                 f"de categoría {prio_ioc['category']} con prioridad {prio_ioc['priority']}")
        print(alert)

    async def run(self, input_queue):
        while True:
            ioc = await input_queue.get()
            await self.emit_alert(ioc)
            input_queue.task_done()

async def main():
    # Definición de canales (colas) asincrónicas para comunicación entre agentes
    queue_raw = asyncio.Queue()
    queue_norm = asyncio.Queue()
    queue_prio = asyncio.Queue()

    # Instanciación de agentes con configuraciones
    feed_sources = ['feed_A', 'feed_B', 'feed_C']
    agent_feed = FeedIntegrationAgent(feed_sources)
    agent_norm = ThreatNormalizationAgent()
    agent_prio = PrioritizationAgent(threshold=0.7)
    agent_alert = AlertAgent()

    # Ejecución concurrente de agentes
    await asyncio.gather(
        agent_feed.run(queue_raw),
        agent_norm.run(queue_raw, queue_norm),
        agent_prio.run(queue_norm, queue_prio),
        agent_alert.run(queue_prio)
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Detenido por el usuario")

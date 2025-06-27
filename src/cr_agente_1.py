# _____________________
# Agente 1 - Identify (Inventario): Descubre y clasifica activos, sensores y servicios en tiempo real, 
# manteniendo un catálogo actualizado con metadatos, paradatos de riesgos y criticidad.
# oswaldo.diaz@inegi.org.mx
# _____________________
import time
import threading
import random
from datetime import datetime

class Asset:
    """
    Representa un activo, sensor o servicio en la red.
    """
    def __init__(self, identifier, kind, metadata=None):
        self.id = identifier                  # Identificador único (IP, MAC, nombre de servicio...)
        self.kind = kind                      # Tipo: 'asset', 'sensor', 'service'
        self.metadata = metadata or {}        # Información descriptiva (fabricante, versión, ubicación...)
        self.last_seen = datetime.utcnow()    # Fecha y hora del último descubrimiento
        self.risk_score = 0                   # Puntaje de riesgo asignado
        self.criticality = 'low'              # Nivel de criticidad: 'low', 'medium', 'high'

    def update(self, metadata_update):
        """Actualiza metadatos y la última vez visto."""
        self.metadata.update(metadata_update)
        self.last_seen = datetime.utcnow()

    def evaluate_risk(self, factors):
        """
        Calcula un puntaje de riesgo basado en factores de vulnerabilidad o amenazas.
        factors: dict con llaves como 'vulnerabilities', 'threat_level'
        """
        base = factors.get('vulnerabilities', 0) * 5
        threat = factors.get('threat_level', 0) * 10
        self.risk_score = min(base + threat, 100)
        self._assign_criticality()

    def _assign_criticality(self):
        """Asigna criticidad con base en el puntaje de riesgo."""
        if self.risk_score >= 75:
            self.criticality = 'high'
        elif self.risk_score >= 40:
            self.criticality = 'medium'
        else:
            self.criticality = 'low'

class Catalog:
    """
    Catálogo centralizado que mantiene los activos descubiertos.
    """
    def __init__(self):
        self._store = {}  # Diccionario: clave=id, valor=Asset
        self._lock = threading.Lock()

    def add_or_update(self, asset):
        """Agrega un nuevo activo o actualiza uno existente."""
        with self._lock:
            if asset.id in self._store:
                existing = self._store[asset.id]
                existing.update(asset.metadata)
            else:
                self._store[asset.id] = asset

    def list_assets(self):
        """Lista todos los activos en el catálogo."""
        with self._lock:
            return list(self._store.values())

    def print_summary(self):
        """Imprime un resumen de cada activo, con riesgo y criticidad."""
        with self._lock:
            for a in self._store.values():
                print(f"ID: {a.id} | Tipo: {a.kind} | Riesgo: {a.risk_score} | Criticidad: {a.criticality} | Última vez visto: {a.last_seen}")

class DiscoveryAgent(threading.Thread):
    """
    Agente que ejecuta descubrimiento periódico en red.
    """
    def __init__(self, catalog, interval=30):
        super().__init__(daemon=True)
        self.catalog = catalog
        self.interval = interval  # segundos entre descubrimientos
        self.running = True

    def run(self):
        while self.running:
            found = self._scan_network()
            for data in found:
                asset = self._make_asset(data)
                asset.evaluate_risk(data.get('factors', {}))
                self.catalog.add_or_update(asset)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def _scan_network(self):
        """
        Simulación de escaneo: devuelve lista de diccionarios con datos.
        """
        # En un entorno real, podrías usar nmap, SNMP, API de nube, etc.
        sample = []
        kinds = ['asset', 'sensor', 'service']
        # Simular entre 1 y 5 hallazgos
        count = random.randint(1,5)
        for _ in range(count):
            identifier = f"node-{random.randint(1,20)}"
            kind = random.choice(kinds)
            metadata = {
                'ip': f"192.168.1.{random.randint(1,254)}",
                'version': f"v{random.randint(1,3)}.{random.randint(0,9)}",
            }
            factors = {
                'vulnerabilities': random.randint(0,5),
                'threat_level': random.random()
            }
            sample.append({ 'id': identifier, 'kind': kind, 'metadata': metadata, 'factors': factors })
        return sample

    def _make_asset(self, data):
        """Construye un objeto Asset a partir de datos crudos."""
        a = Asset(data['id'], data['kind'], data['metadata'])
        return a

if __name__ == "__main__":
    # Ejecución de ejemplo
    catalog = Catalog()
    agent = DiscoveryAgent(catalog, interval=10)
    agent.start()

    try:
        # Ejecutar por un periodo limitado
        for _ in range(5):
            time.sleep(12)
            print("\n=== Resumen de catálogo ===")
            catalog.print_summary()
    except KeyboardInterrupt:
        pass
    finally:
        agent.stop()
        agent.join()
        print("Agente detenido. Estado final del catálogo:")
        catalog.print_summary()

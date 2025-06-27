# _____________________________
# Agente 9 - Recover (Plan de Recuperación): Valida la integridad de respaldos y orquestan restauraciones 
# (parciales o totales), priorizando servicios críticos según demanda y disponibilidad.
# oswaldo.diaz@inegi.org.mx
# _____________________________
import os
import hashlib
import json
import time
import shutil
from datetime import datetime
import threading
import queue

# ======================
# CONFIGURACIÓN DEL SISTEMA
# ======================
class BackupConfig:
    """Configuración del sistema de respaldos y prioridades"""
    def __init__(self):
        self.backup_dir = "backups"
        self.production_dir = "production"
        self.hash_db = "hash_db.json"
        self.critical_services = self.load_critical_services()
        
    def load_critical_services(self):
        """Carga la jerarquía de servicios críticos desde archivo"""
        try:
            with open("critical_services.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Servicios predeterminados (estructura ejemplo)
            return {
                "servicio_db": {"priority": 1, "demand_threshold": 100},
                "servicio_api": {"priority": 2, "demand_threshold": 80},
                "servicio_web": {"priority": 3, "demand_threshold": 50}
            }

# ======================
# AGENTE DE VALIDACIÓN
# ======================
class ValidationAgent:
    """Agente que verifica la integridad de los respaldos"""
    def __init__(self, config):
        self.config = config
        self.integrity_status = {}
        
    def calculate_hash(self, file_path):
        """Calcula hash SHA-256 para verificar integridad"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def verify_backup(self, backup_file):
        """Verifica la integridad de un respaldo específico"""
        backup_path = os.path.join(self.config.backup_dir, backup_file)
        
        if not os.path.exists(backup_path):
            return False, "Backup no encontrado"
        
        current_hash = self.calculate_hash(backup_path)
        
        # Cargar base de datos de hashes conocidos
        try:
            with open(self.config.hash_db, "r") as f:
                known_hashes = json.load(f)
        except FileNotFoundError:
            known_hashes = {}
        
        # Verificar contra hash conocido
        if backup_file in known_hashes:
            if known_hashes[backup_file] == current_hash:
                return True, "Integridad verificada"
            return False, "Hash no coincide"
        
        # Si es nuevo backup, registrar hash
        known_hashes[backup_file] = current_hash
        with open(self.config.hash_db, "w") as f:
            json.dump(known_hashes, f)
        
        return True, "Nuevo backup registrado"
    
    def full_validation_cycle(self):
        """Ejecuta verificación completa de todos los respaldos"""
        print("\n[Agente Validación] Iniciando verificación de integridad...")
        for backup in os.listdir(self.config.backup_dir):
            is_valid, message = self.verify_backup(backup)
            self.integrity_status[backup] = {
                "valid": is_valid,
                "message": message,
                "last_checked": datetime.now().isoformat()
            }
            status = "✓" if is_valid else "✗"
            print(f"  {status} {backup}: {message}")
        print("[Agente Validación] Verificación completada\n")
        return self.integrity_status

# ======================
# AGENTE DE ORQUESTACIÓN
# ======================
class OrchestrationAgent:
    """Agente que gestiona restauraciones priorizadas"""
    def __init__(self, config, validation_agent):
        self.config = config
        self.validation_agent = validation_agent
        self.restoration_queue = queue.PriorityQueue()
        self.current_demands = {}
        
    def evaluate_demands(self):
        """Evalúa la demanda actual de servicios (simulado)"""
        # En un sistema real esto vendría de métricas en tiempo real
        self.current_demands = {
            "servicio_db": 150,  # Alta demanda
            "servicio_api": 65,
            "servicio_web": 30
        }
        return self.current_demands
    
    def prioritize_services(self):
        """Prioriza servicios basado en criticidad y demanda actual"""
        demands = self.evaluate_demands()
        priority_list = []
        
        for service, data in self.config.critical_services.items():
            current_demand = demands.get(service, 0)
            demand_ratio = current_demand / data["demand_threshold"]
            
            # Fórmula de prioridad: (Prioridad base) * (Factor demanda)
            # Menor valor = mayor prioridad
            priority = data["priority"] * (1 / max(0.1, demand_ratio))
            
            priority_list.append((priority, service))
        
        # Ordenar por prioridad (menor primero)
        priority_list.sort(key=lambda x: x[0])
        return [service for _, service in priority_list]
    
    def restore_service(self, service, backup_file, partial=False):
        """Realiza la restauración de un servicio"""
        print(f"[Orquestador] Iniciando restauración de {service} ({'parcial' if partial else 'completa'})")
        
        # Validar backup antes de restaurar
        is_valid, _ = self.validation_agent.verify_backup(backup_file)
        if not is_valid:
            return False, "Backup inválido"
        
        source = os.path.join(self.config.backup_dir, backup_file)
        target = os.path.join(self.config.production_dir, service)
        
        try:
            # Simulación de restauración
            if not os.path.exists(target):
                os.makedirs(target)
                
            if partial:
                # Restauración parcial simulada
                shutil.copy(source, os.path.join(target, "partial_restore"))
            else:
                # Restauración completa simulada
                shutil.copy(source, os.path.join(target, "full_restore"))
            
            # Simular tiempo de restauración
            time.sleep(1)
            return True, "Restauración exitosa"
            
        except Exception as e:
            return False, str(e)
    
    def orchestrate_restorations(self, trigger_event=None):
        """Orquesta las restauraciones basado en prioridades"""
        print("\n[Agente Orquestación] Evaluando prioridades...")
        prioritized = self.prioritize_services()
        print(f"Orden de prioridad: {', '.join(prioritized)}")
        
        results = {}
        for service in prioritized:
            # Backup file naming convention: servicio_fecha.ext
            backup_file = f"{service}_backup_{datetime.now().strftime('%Y%m%d')}.bak"
            
            # Determinar tipo de restauración (parcial para demandas medias)
            current_demand = self.current_demands.get(service, 0)
            threshold = self.config.critical_services[service]["demand_threshold"]
            partial = current_demand < threshold * 1.5
            
            success, message = self.restore_service(service, backup_file, partial)
            results[service] = {"success": success, "message": message}
            
            # Solo restaurar servicios críticos necesarios
            if success and current_demand < threshold:
                break
        
        print("[Agente Orquestación] Proceso de restauración completado\n")
        return results

# ======================
# SISTEMA SUPERVISOR
# ======================
class CyberResilienceSystem:
    """Sistema principal de ciberresiliencia"""
    def __init__(self):
        self.config = BackupConfig()
        self.validation_agent = ValidationAgent(self.config)
        self.orchestration_agent = OrchestrationAgent(
            self.config, 
            self.validation_agent
        )
        self.monitor_active = False
        
    def start_monitoring(self, interval=60):
        """Inicia monitoreo continuo en segundo plano"""
        self.monitor_active = True
        print(f"🔍 Iniciando monitoreo de resiliencia (intervalo: {interval}s)")
        
        def monitoring_loop():
            while self.monitor_active:
                # Validar backups primero
                self.validation_agent.full_validation_cycle()
                
                # Verificar si se necesita restauración (simulado)
                if self.detect_incident():
                    self.orchestration_agent.orchestrate_restorations()
                
                time.sleep(interval)
        
        threading.Thread(target=monitoring_loop, daemon=True).start()
    
    def stop_monitoring(self):
        """Detiene el monitoreo continuo"""
        self.monitor_active = False
        print("⏹️ Monitoreo detenido")
    
    def detect_incident(self):
        """Detecta incidentes simulados (en implementación real usaría monitoreo real)"""
        # Simulación: 20% de probabilidad de incidente
        return True #random.random() < 0.2
    
    def manual_restoration(self):
        """Inicia restauración manual"""
        print("🛠️ Iniciando restauración manual...")
        return self.orchestration_agent.orchestrate_restorations()

# ======================
# EJECUCIÓN PRINCIPAL
# ======================
if __name__ == "__main__":
    # Inicializar sistema
    resilience_system = CyberResilienceSystem()
    
    # Ejecutar validación inicial
    resilience_system.validation_agent.full_validation_cycle()
    
    # Iniciar monitoreo continuo en segundo plano
    resilience_system.start_monitoring(interval=10)
    
    # Mantener el programa activo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        resilience_system.stop_monitoring()
        print("Sistema apagado")
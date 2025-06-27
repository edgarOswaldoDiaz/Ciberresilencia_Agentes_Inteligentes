# _____________________________
# Agente 4 - Protect (Seguridad Datos): Monitorea el ciclo de vida de datos, aplican cifrado y etiquetado automáticos, 
# y bloquean exfiltraciones mediante análisis de flujo de datos.
# Explicación:
# 1. watchdog: biblioteca usada para monitorear eventos de creación/modificación de archivos.
# 2. Fernet (cryptography): ofrece cifrado simétrico con autenticidad y confidencialidad.
# 3. Cada vez que se detecta un archivo nuevo o modificado, se cifra, se etiqueta y se analiza.
# 4. El etiquetado usa un fragmento de hash SHA-256 de la ruta para identificar archivos.
# 5. El análisis de flujo simula reglas (ej. tamaño y horario) y retorna alerta si coincide.
# 6. Si se detecta exfiltración, se bloquea eliminando el archivo original como respuesta inmediata.
# 7. Puede extenderse con reenvío a sistemas SIEM o integración con DLP reales.
# oswaldo.diaz@inegi.org.mx
# ______________________________
import os
import time
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cryptography.fernet import Fernet

class DataLifecycleHandler(FileSystemEventHandler):
    """
    Manejador que responde a eventos en el sistema de archivos:
      - creación y modificación de archivos
      - dispara cifrado, etiquetado y análisis de flujo
    """
    def __init__(self, agent):
        self.agent = agent

    def on_created(self, event):
        if not event.is_directory:
            self.agent.process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.agent.process_file(event.src_path)

class IntelligentAgent:
    def __init__(self, watch_dir, key=None):
        # Directorio a monitorear y clave de cifrado
        self.watch_dir = watch_dir
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        # Diccionario para etiquetas de archivos
        self.labels = {}

    def start(self):
        """Inicia el observador de filesystem"""
        event_handler = DataLifecycleHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.watch_dir, recursive=True)
        observer.start()
        print(f"[+] Agente iniciado. Monitoreando: {self.watch_dir}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def process_file(self, path):
        """Procesa cada archivo: cifrado, etiquetado y análisis de flujo"""
        print(f"[*] Detectado cambio: {path}")
        data = self._read_file(path)
        encrypted = self.encrypt_data(data)
        self._write_file(path + ".enc", encrypted)
        label = self.label_data(path)
        print(f"    Etiqueta asignada: {label}")
        if self.analyze_flow(path, encrypted):
            self.block_exfiltration(path)

    def _read_file(self, path):
        with open(path, 'rb') as f:
            return f.read()

    def _write_file(self, path, data):
        with open(path, 'wb') as f:
            f.write(data)

    def encrypt_data(self, data):
        """Aplica cifrado simétrico con Fernet"""
        token = self.cipher.encrypt(data)
        print("    [Cifrado] Datos cifrados correctamente en memoria")
        return token

    def label_data(self, path):
        """Genera etiqueta en base a hash y ruta"""
        hasher = hashlib.sha256()
        hasher.update(path.encode())
        tag = hasher.hexdigest()[:8]
        self.labels[path] = tag
        return tag

    def analyze_flow(self, path, encrypted_data):
        """
        Simula análisis de flujo de datos buscando patrones sospechosos.
        Retorna True si detecta posible exfiltración.
        """
        size = len(encrypted_data)
        # Ejemplo de regla: archivos grandes modificados fuera de horario laboral
        hour = time.localtime().tm_hour
        if size > 1_000_000 and (hour < 8 or hour > 18):
            print("    [Alerta] Flujo de datos sospechoso detectado")
            return True
        print("    [Análisis] Flujo de datos normal")
        return False

    def block_exfiltration(self, path):
        """Bloquea la exfiltración eliminando el archivo original como medida retractiva"""
        try:
            os.remove(path)
            print(f"    [Bloqueo] Archivo original {path} ha sido eliminado")
        except Exception as e:
            print(f"    [Error] No se pudo bloquear exfiltración: {e}")

if __name__ == "__main__":
    # Ejemplo de uso: ajustar ruta a monitorear
    ruta = "/ruta/a/monitorear"
    agente = IntelligentAgent(ruta)
    agente.start()


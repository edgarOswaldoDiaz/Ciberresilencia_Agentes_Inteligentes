# --------------------------------------------
# Agente 7 - Respond (Orquestación): Agentes RPA/IA (Robotic Process Automation (Automatización Robótica de Procesos con inteligencia artificial), 
# que ejecutan playbooks automáticos: aíslan sistemas, bloquean IPs, elaboran informes iniciales y notifican stakeholders (involucrados) sin intervención manual.
# Explicación:
# 1. Configuración y logging:
#    - Logging configurado en nivel INFO para seguimiento de pasos.
# 2. isolate_system():
#    - Simula aislamiento, en entornos reales se conectaría por SSH o API a firewalls.
# 3. block_ip():
#    - Simula bloqueo local, reemplazar con comandos de UFW, iptables o APIs de cloud.
# 4. generate_report():
#    - Usa pandas para estructurar datos de incidentes y exportar a CSV.
# 5. notify_stakeholders():
#    - Envía emails con SMTP, adjuntando el CSV generado.
#      Las credenciales se cargan de variables de entorno para seguridad.
# 6. run_playbook():
#    - Orquesta las funciones en secuencia, captura datos en 'incidents' para el informe.
# 7. Bloque main:
#    - Ejemplo de uso: define host, IP maliciosa y lista de correos.
#    - Permite ejecutar el playbook sin intervención manual.
# oswaldo.diaz@inegi.org.mx
# --------------------------------------------
import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import datetime

# Configure logging for the agent
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RPAAgent:
    """
    Un agente RPA/IA que ejecuta playbooks automáticos para:
    - Aislar sistemas comprometidos
    - Bloquear IPs maliciosas
    - Generar informes iniciales
    - Notificar automáticamente a los stakeholders
    """

    def __init__(self, report_dir="./reports"):
        # Directorio donde se guardarán los informes
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)
        logging.info(f"Directorio de informes configurado en: {self.report_dir}")

    def isolate_system(self, target_host):
        """
        Aísla el sistema comprometido.
        En un entorno real, aquí se podría usar SSH, APIs de firewall o herramientas de virtualización.
        """
        logging.info(f"Iniciando aislamiento del sistema: {target_host}")
        # Simulación de aislamiento
        # Por ejemplo: ejecutar un comando SSH que aplique políticas de red restrictivas
        # ssh_client.exec_command(f"sudo iptables -A INPUT -s {target_host} -j DROP")
        logging.info(f"Sistema {target_host} aislado exitosamente.")

    def block_ip(self, ip_address):
        """
        Bloquea una dirección IP en el firewall.
        """
        logging.info(f"Bloqueando IP maliciosa: {ip_address}")
        # Simulación de bloqueo de IP en firewall local
        # os.system(f"sudo ufw deny from {ip_address}")
        logging.info(f"IP {ip_address} bloqueada exitosamente.")

    def generate_report(self, incidents: list) -> str:
        """
        Genera un informe inicial en formato CSV a partir de una lista de incidentes.
        Cada incidente es un dict con claves: 'timestamp', 'host', 'ip', 'action'.
        Retorna la ruta al archivo generado.
        """
        logging.info("Generando informe inicial de incidentes...")
        df = pd.DataFrame(incidents)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.csv"
        filepath = os.path.join(self.report_dir, filename)
        df.to_csv(filepath, index=False)
        logging.info(f"Informe generado: {filepath}")
        return filepath

    def notify_stakeholders(self, report_path: str, stakeholders: list):
        """
        Notifica a los stakeholders vía email con el informe adjunto.
        stakeholders: lista de emails.
        Las credenciales SMTP deben estar seteadas en variables de entorno:
          SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS
        """
        logging.info("Enviando notificaciones a stakeholders...")
        # Configuración del servidor SMTP
        server = os.getenv('SMTP_SERVER')
        port = os.getenv('SMTP_PORT')
        user = os.getenv('SMTP_USER')
        password = os.getenv('SMTP_PASS')

        if not all([server, port, user, password]):
            logging.error("Credenciales SMTP incompletas. Abortando notificación.")
            return

        # Construcción del mensaje
        msg = MIMEMultipart()
        msg['From'] = user
        msg['Subject'] = "[Automático] Informe de Incidentes de Ciberseguridad"
        body = f"Adjunto encuentras el informe inicial generado automáticamente: {os.path.basename(report_path)}"
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar el archivo CSV
        with open(report_path, 'r') as f:
            attachment = MIMEText(f.read(), 'csv')
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(report_path))
            msg.attach(attachment)

        try:
            smtp = smtplib.SMTP(server, int(port))
            smtp.starttls()
            smtp.login(user, password)
            for recipient in stakeholders:
                msg['To'] = recipient
                smtp.sendmail(user, recipient, msg.as_string())
                logging.info(f"Notificación enviada a: {recipient}")
            smtp.quit()
            logging.info("Todas las notificaciones se enviaron correctamente.")
        except Exception as e:
            logging.error(f"Error al enviar notificaciones: {e}")

    def run_playbook(self, target_host, malicious_ip, stakeholders):
        """
        Orquesta la ejecución completa del playbook.
        1. Aislar sistema.
        2. Bloquear IP.
        3. Generar informe.
        4. Notificar stakeholders.
        """
        incidents = []

        # 1. Aislar sistema
        self.isolate_system(target_host)
        incidents.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'host': target_host,
            'ip': None,
            'action': 'isolate_system'
        })

        # 2. Bloquear IP
        self.block_ip(malicious_ip)
        incidents.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'host': target_host,
            'ip': malicious_ip,
            'action': 'block_ip'
        })

        # 3. Generar informe
        report_path = self.generate_report(incidents)

        # 4. Notificar stakeholders
        self.notify_stakeholders(report_path, stakeholders)

        logging.info("Playbook automatizado completado.")

if __name__ == "__main__":
    # Ejecución de ejemplo
    agent = RPAAgent()
    target = "192.168.1.100"      # Host comprometido
    bad_ip = "203.0.113.45"       # IP maliciosa detectada
    team = ["seguridad@empresa.com", "itops@empresa.com"]
    agent.run_playbook(target, bad_ip, team)



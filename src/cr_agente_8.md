## Agente 8 - Respond (Aprendizaje): Retroalimentación automática de datos de incidentes a los agentes para refinar reglas de detección, umbrales y estrategias defensivas basadas en lecciones aprendidas.


1. **Reglas de detección** (por ejemplo, patrones de eventos sospechosos).
2. **Umbrales** (por ejemplo, número de intentos de acceso fallidos).
3. **Estrategias defensivas** (por ejemplo, bloqueo temporal, notificación al SOC).

El código está dividido en tres partes:

1. **Definición de estructuras** (incidentes, reglas, etc.).
2. **Clase `FeedbackAgent`** con métodos para:

   * Ingestar incidentes.
   * Evaluar incidentes contra reglas actuales.
   * Ajustar reglas, umbrales y defensas según métricas de “éxito” o “fracaso”.
3. **Ejemplo de uso** con simulación de varios incidentes y refinamiento iterativo.

---

```python
import json
from collections import defaultdict
from statistics import mean

class DetectionRule:
    """
    Representa una regla de detección sencilla:
    - name: identificador
    - pattern: palabra clave o expresión
    - threshold: número mínimo de coincidencias para disparar alerta
    - action: estrategia defensiva a ejecutar
    """
    def __init__(self, name, pattern, threshold, action):
        self.name = name
        self.pattern = pattern
        self.threshold = threshold
        self.action = action

    def matches(self, incident):
        """
        Comprueba cuántas veces aparece el patrón en la descripción del incidente.
        """
        count = incident['description'].lower().count(self.pattern.lower())
        return count >= self.threshold, count

    def to_dict(self):
        return {
            'name': self.name,
            'pattern': self.pattern,
            'threshold': self.threshold,
            'action': self.action
        }


class FeedbackAgent:
    """
    Agente que:
    1. Almacena reglas de detección.
    2. Procesa incidentes, registra métricas (TP, FP, FN).
    3. Ajusta thresholds y acciones en función de rendimiento histórico.
    """
    def __init__(self, rules=None):
        # Reglas iniciales
        self.rules = rules or []
        # Métricas históricas: regla -> {'tp':…, 'fp':…, 'fn':…}
        self.metrics = defaultdict(lambda: {'tp':0, 'fp':0, 'fn':0})

    def ingest_incident(self, incident):
        """
        Recibe un incidente con:
        - description (texto libre)
        - is_true_threat (bool): si realmente fue amenaza
        """
        for rule in self.rules:
            fired, count = rule.matches(incident)
            # Si la regla disparó alerta…
            if fired:
                if incident['is_true_threat']:
                    self.metrics[rule.name]['tp'] += 1
                else:
                    self.metrics[rule.name]['fp'] += 1
            else:
                if incident['is_true_threat']:
                    # No detectó algo que era amenaza
                    self.metrics[rule.name]['fn'] += 1
        # Podríamos almacenar el incidente en una base de datos para auditoría
        # Aquí solo imprimimos para ilustrar
        print(f"[Incidente procesado] desc='{incident['description'][:30]}...' "
              f"verdadero={incident['is_true_threat']}")

    def refine_rules(self, min_improvement=0.05):
        """
        Ajusta thresholds y, si es necesario, cambia la acción.
        - Si demasiados FP: sube threshold en 1.
        - Si demasiados FN: baja threshold en 1 (pero al menos 1).
        - También se podrían cambiar 'action' según gravedad.
        """
        for rule in self.rules:
            m = self.metrics[rule.name]
            tp, fp, fn = m['tp'], m['fp'], m['fn']
            total = tp + fp + fn
            if total == 0:
                continue  # Sin datos, no ajustar
            precision = tp / (tp + fp) if (tp+fp)>0 else 0
            recall = tp / (tp + fn) if (tp+fn)>0 else 0

            print(f"\n[Refinamiento de regla '{rule.name}']")
            print(f"  Metrics => precision={precision:.2f}, recall={recall:.2f}")

            # Ajuste de threshold
            if precision < 0.8:
                old = rule.threshold
                rule.threshold += 1
                print(f"  • Alta tasa de falsos positivos → subimos umbral "
                      f"{old}→{rule.threshold}")
            elif recall < 0.7:
                old = rule.threshold
                rule.threshold = max(1, rule.threshold - 1)
                print(f"  • Alta tasa de falsos negativos → bajamos umbral "
                      f"{old}→{rule.threshold}")
            else:
                print("  • Rendimiento aceptable: no se cambian umbrales")

            # Ejemplo de ajuste de estrategia defensiva
            if fp > tp:
                old_action = rule.action
                rule.action = "log_and_notify"  # menos agresiva
                print(f"  • Muchos FP → cambiamos acción {old_action}→{rule.action}")
            elif fn > fp:
                old_action = rule.action
                rule.action = "block_and_isolate"  # más agresiva
                print(f"  • Muchos FN → cambiamos acción {old_action}→{rule.action}")

            # Reiniciar métricas tras refinamiento
            self.metrics[rule.name] = {'tp':0, 'fp':0, 'fn':0}

    def export_rules(self, filepath):
        """
        Guarda las reglas actuales en JSON para persistencia.
        """
        data = [r.to_dict() for r in self.rules]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[Reglas exportadas] {filepath}")


# ===== Ejemplo de uso =====

if __name__ == "__main__":
    # 1. Definimos reglas iniciales:
    rules = [
        DetectionRule("BruteForceLogin", "failed login", threshold=3, action="alert_admin"),
        DetectionRule("DataExfil", "download", threshold=5, action="block_ip")
    ]

    agent = FeedbackAgent(rules=rules)

    # 2. Simulamos llegada de varios incidentes:
    incidents = [
        {"description": "User had 1 failed login attempt", "is_true_threat": False},
        {"description": "failed login failed login failed login", "is_true_threat": True},
        {"description": "download download download download", "is_true_threat": False},
        {"description": "download download download download download download", "is_true_threat": True},
        {"description": "failed login failed login", "is_true_threat": True},
    ]

    for inc in incidents:
        agent.ingest_incident(inc)

    # 3. Refinamos reglas según métricas acumuladas:
    agent.refine_rules()

    # 4. Exportamos la nueva configuración:
    agent.export_rules("reglas_actualizadas.json")
```

---

## Explicación paso a paso

1. **`DetectionRule`**

   * Cada regla tiene un `pattern` (cadena que buscamos en la descripción del incidente), un `threshold` (umbral de repeticiones para disparar la alerta) y una `action` (por ejemplo, notificar, bloquear IP, aislar máquina).
   * El método `matches()` cuenta apariciones y determina si supera el umbral.

2. **`FeedbackAgent`**

   * Mantiene una lista de reglas y un diccionario `metrics` que lleva conteos de:

     * **TP** (True Positives): regla disparó y realmente fue amenaza.
     * **FP** (False Positives): regla disparó pero no era amenaza.
     * **FN** (False Negatives): regla no disparó pero sí era amenaza.
   * **`ingest_incident()`** aplica cada regla al incidente, actualiza métricas según el campo `is_true_threat`.
   * **`refine_rules()`** calcula *precisión* y *recall* para cada regla:

     * Si la **precisión** baja (muchos FP), **incrementa** el umbral para ser más “selectivo”.
     * Si el **recall** baja (muchos FN), **disminuye** el umbral para atrapar más casos.
     * Ajusta la **acción defensiva** si predominan FP (menos agresiva) o FN (más agresiva).
     * Finalmente, reinicia las métricas para la próxima ronda de aprendizaje.

3. **Flujo de trabajo típico**

   1. El agente corre en producción escuchando incidentes en tiempo real.
   2. Cada N incidentes (o cada cierto período) invocas `refine_rules()` para auto-ajuste.
   3. Persistes las reglas refinadas (`export_rules()`) y las recargas en el sistema central.

Con este esqueleto puedes ampliar los componentes para incluir:

* Persistencia en base de datos (en lugar de `print`).
* Métricas más avanzadas (F1-score, curvas ROC).
* Reglas basadas en expresiones regulares complejas o patrones de comportamiento.
* Integración con APIs de firewall, SIEM o SOAR para aplicar `action` automáticamente.

> oswaldo.diaz@inegi.org.mx

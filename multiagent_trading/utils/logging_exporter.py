import json
import time

class LoggingExporter:
    """
    Exportador de logs estruturados para sistemas externos (ELK, Grafana Loki).
    """
    def __init__(self, endpoint=None):
        self.endpoint = endpoint # URL do colector

    def export_batch(self, logs: list):
        """Simula o envio de um lote de logs via HTTP POST."""
        if not self.endpoint:
            # print(f"[DEBUG-LOGS] A exportar {len(logs)} registos para o console.")
            return True

        try:
            # requests.post(self.endpoint, json=logs)
            return True
        except Exception:
            return False

    def format_for_loki(self, log_record: dict):
        """Formata o log para o formato esperado pelo Grafana Loki."""
        return {
            "streams": [
                {
                    "stream": {"job": "matf-trading", "agent": log_record.get("name")},
                    "values": [[str(int(time.time() * 1e9)), json.dumps(log_record)]]
                }
            ]
        }

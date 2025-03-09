import logging
import sys
import requests
import json

class Logger:
    def __init__(self, module_name):
        self.logger = logging.getLogger(module_name)
        self.logger.setLevel(logging.DEBUG)

        # Formato del log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Loki (Promtail)
        self.loki_url = "http://localhost:3100/loki/api/v1/push"  # Cambia si usas otro host

    def log(self, level, message, extra_fields=None):
        """ Registra un mensaje en la consola y en Loki """
        if extra_fields is None:
            extra_fields = {}

        log_entry = {"module": self.logger.name, **extra_fields}
        formatted_message = f"{message} | {json.dumps(log_entry)}"

        if level == "debug":
            self.logger.debug(formatted_message)
        elif level == "info":
            self.logger.info(formatted_message)
        elif level == "warning":
            self.logger.warning(formatted_message)
        elif level == "error":
            self.logger.error(formatted_message)
        elif level == "critical":
            self.logger.critical(formatted_message)

        # Enviar log a Loki
        self.send_to_loki(level, message, log_entry)

    def send_to_loki(self, level, message, log_entry):
        """ Envía los logs a Loki en formato JSON """
        payload = {
            "streams": [
                {
                    "stream": {"level": level, "module": self.logger.name},
                    "values": [[str(int(1e9 * logging.time.time())), message]]
                }
            ]
        }
        try:
            requests.post(self.loki_url, json=payload)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error enviando log a Loki: {e}")

# Inicialización para módulos específicos
trading_logger = Logger("trading")
backtest_logger = Logger("backtesting")

# Compatibilidad con módulos existentes
def get_logger(module_name):
    """ Devuelve un logger según el módulo """
    if module_name == "trading":
        return trading_logger
    elif module_name == "backtesting":
        return backtest_logger
    else:
        return Logger(module_name)

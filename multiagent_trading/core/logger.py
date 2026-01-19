import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add extra fields if available
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields)

        return json.dumps(log_record)

class Logger:
    def __init__(self, name="MATF", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid adding multiple handlers if the logger is already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JsonFormatter())
            self.logger.addHandler(handler)

    def info(self, msg, **kwargs):
        self.logger.info(msg, extra={"extra_fields": kwargs} if kwargs else None)

    def error(self, msg, **kwargs):
        self.logger.error(msg, extra={"extra_fields": kwargs} if kwargs else None)

    def warning(self, msg, **kwargs):
        self.logger.warning(msg, extra={"extra_fields": kwargs} if kwargs else None)

    def debug(self, msg, **kwargs):
        self.logger.debug(msg, extra={"extra_fields": kwargs} if kwargs else None)

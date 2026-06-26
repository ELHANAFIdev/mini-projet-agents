import logging
import json
import sys

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log(self, level: int, event: str, **kwargs):
        if self.logger.isEnabledFor(level):
            log_dict = {"event": event, **kwargs}
            self.logger.log(level, json.dumps(log_dict))

    def info(self, event: str, **kwargs):
        self._log(logging.INFO, event, **kwargs)

    def error(self, event: str, **kwargs):
        self._log(logging.ERROR, event, **kwargs)

    def warning(self, event: str, **kwargs):
        self._log(logging.WARNING, event, **kwargs)

    def debug(self, event: str, **kwargs):
        self._log(logging.DEBUG, event, **kwargs)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)

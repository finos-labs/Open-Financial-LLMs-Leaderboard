import logging
import sys
from tqdm import tqdm

def get_tqdm_handler():
    """
    Creates a special handler for tqdm that doesn't interfere with other logs.
    """
    class TqdmLoggingHandler(logging.Handler):
        def emit(self, record):
            try:
                msg = self.format(record)
                tqdm.write(msg)
                self.flush()
            except Exception:
                self.handleError(record)

    return TqdmLoggingHandler()

def setup_service_logger(service_name: str) -> logging.Logger:
    """
    Configure a specific logger for a given service.
    """
    logger = logging.getLogger(f"app.services.{service_name}")
    
    # If the logger already has handlers, don't reconfigure it
    if logger.handlers:
        return logger
    
    # Add tqdm handler for this service
    tqdm_handler = get_tqdm_handler()
    tqdm_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(tqdm_handler)
    
    # Don't propagate logs to parent loggers
    logger.propagate = False
    
    return logger
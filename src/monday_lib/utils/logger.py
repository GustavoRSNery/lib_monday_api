import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from ..infra.settings import get_settings

def setup_logger(name: str, log_file: Path, level=logging.ERROR) -> logging.Logger:
    """Função para configurar um logger que escreve em um arquivo."""
    
    # Garante que o diretório de logs exista
    log_dir = log_file.parent
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


settings = get_settings()

LOG_FILE_PATH = settings.LOGS_PATH / "api_errors.log"

api_logger = setup_logger('api_error_logger', LOG_FILE_PATH)
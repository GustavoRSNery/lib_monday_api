import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.ERROR):
    """
    Configura um logger específico para escrever em um arquivo, com rotação.
    """
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)

    # Cria o handler para o arquivo
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Pega o logger e configura
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # IMPORTANTE: Propagate = False
    # Impede que as mensagens de erro deste logger sejam enviadas para o logger raiz (console)
    # Isso evita que a mesma mensagem de erro apareça duas vezes no terminal.
    logger.propagate = False
    
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# Arquivo de log
LOG_FILE_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'logs', 'api_errors.log'
)

api_logger = setup_logger('api_error_logger', LOG_FILE_PATH)
import logging
import shutil
from pathlib import Path
from ..infra.settings import get_settings
from ..utils.decorators import log_api_errors
settings = get_settings()

@log_api_errors
def copy_log_file(destination_path: str) -> bool:
    """
    Copia o arquivo de log de erros da API para um diretório especificado pelo usuário.

    Args:
        destination_path (str): O caminho completo da pasta de destino onde o 
                                arquivo 'api_errors.log' será copiado.

    Returns:
        True se a cópia for bem-sucedida, False caso contrário.
    
    Raises:
        Qualquer exceção durante a operação será capturada e logada pelo
        decorador @log_api_errors.
    """
    source_log_file = settings.LOGS_PATH / "api_errors.log"
    
    if not source_log_file.is_file():
        logging.warning(f"Arquivo de log de origem não encontrado em: {source_log_file}")
        return False

    try:
        dest_path = Path(destination_path)
        # Garante que o diretório de destino exista
        dest_path.mkdir(parents=True, exist_ok=True)
        
        destination_file = dest_path / "api_errors.log"
        
        logging.info(f"Copiando arquivo de log de '{source_log_file}' para '{destination_file}'...")
        
        # shutil.copy2 copia o arquivo e preserva os metadados (como data de modificação)
        shutil.copy2(source_log_file, destination_file)
        
        logging.info("Cópia do arquivo de log concluída com sucesso.")
        return True

    except (PermissionError, IOError) as e:
        logging.error(f"Erro de permissão ou de I/O ao copiar o arquivo de log: {e}")
        # O decorador também irá capturar e logar isso.
        raise
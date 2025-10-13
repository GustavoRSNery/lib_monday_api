import logging
import functools
from ..utils.logger import api_logger

def log_api_errors(func):
    """
    Um decorador que envolve uma função em um bloco try...except.

    Se a função decorada levantar qualquer exceção, este decorador irá
    capturá-la, logar uma mensagem de erro contextualizada (incluindo o nome
    da função que falhou) no logger de persistência 'api_logger', e então
    re-levantar a exceção para não interromper o fluxo de erro.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # A lógica de tratamento de erro que queremos reutilizar
        try:
            # Tenta executar a função original e retornar seu resultado
            return func(*args, **kwargs)
        except Exception as e:
            # Se uma exceção ocorrer, loga com o nome da função que falhou
            error_message = f"Falha na execução de '{func.__name__}'."
            
            # Loga a mensagem de alto nível no console (via logger raiz)
            logging.error(error_message)
            # Loga a mensagem de alto nível + causa no arquivo de persistência
            api_logger.error(f"{error_message} Causa: {e}")
            
            # Re-levanta a exceção para que o programa principal saiba que a falha ocorreu
            raise
    return wrapper
import os
import json
import inspect
import logging
import requests
from datetime import datetime
from infra.settings import get_settings
from ..utils.logger import api_logger
from .exceptions import APIError, APITimeoutError
settings = get_settings()


def call_monday_api(query: str, variables: dict) -> dict:
    """
    Função centralizada para fazer chamadas à API GraphQL do Monday.com.

    :param query: A string da query/mutation GraphQL.
    :param variables: Um dicionário com as variáveis para a query.
    :return: O dicionário 'data' da resposta JSON da API.
    :raises Exception: Se a chamada HTTP ou a query GraphQL retornarem erros.
    """
    if not settings.MONDAY_API_TOKEN.get_secret_value() or not settings.MONDAY_API_TOKEN.get_secret_value():
        raise EnvironmentError("API_KEY ou MONDAY_API_URL não foram definidos no .env")

    headers = {
        "Authorization": f"Bearer {settings.MONDAY_API_TOKEN.get_secret_value()}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "variables": variables}
    try:
        response = requests.post(
            url=settings.MONDAY_API_URL,
            headers=headers,
            json=payload,
            verify=str(settings.PEM_PATH) if settings.PEM_PATH else True
        )
        
        response.raise_for_status()
        logging.info(f"Status: {response.status_code}. Chamada API bem-sucedida. Tempo: {response.elapsed}")

        result = response.json()
        
        # Verificacao de erros especificos do GraphQL
        if "errors" in result:
            raise Exception(f"Erro na consulta GraphQL: {result['errors']}")
        
        if not result.get("data"):
            raise Exception(f"Resposta inesperada da API: {result}")
        
        return result.get("data", {})
    

    # novo
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 504:
            raise APITimeoutError(f"Gateway Timeout (504) na chamada para {e.request.url}") from e
        else:
            raise APIError(f"Erro de HTTP: {e}") from e
        
        
        
    except Exception as e:
        caller_frame = inspect.stack()[1]
        caller_filename = os.path.basename(caller_frame.filename)
        caller_function = caller_frame.function
        caller_lineno = caller_frame.lineno

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "called_from": f"{caller_filename} -> {caller_function}() na linha {caller_lineno}",
            "status_code": response.status_code if response is not None else "N/A",
            "elapsed_time": str(response.elapsed) if response is not None else "N/A",
            "error_type": type(e).__name__,
            "error_message": str(e),
            # "request_body": payload 
        }
        log_message = json.dumps(log_data, indent=4, ensure_ascii=False)
        api_logger.error(log_message)
        logging.error(f"Falha na chamada da API. Detalhes salvos em 'logs/api_errors.log'")
        raise APIError(f"Erro inesperado na chamada da API: {e}") from e
            
import logging
from ..api_client.call_api import call_monday_api
from ..queries.templates import QUERY_GET_COLUMN_METADATA


def chamada_api_get_ids(board_id: str) -> dict:
    """
    Chama a API para buscar os METADADOS das colunas de um quadro.
    Retorna o dicionário 'data' da resposta.
    """
    return call_monday_api(QUERY_GET_COLUMN_METADATA, {"boardId": board_id})


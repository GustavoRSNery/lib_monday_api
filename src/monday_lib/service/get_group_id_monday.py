import logging
from ..api_client.call_api import call_monday_api
from ..queries.templates import QUERY_GET_GROUP_ID
from ..utils.logger import api_logger
from ..utils.decorators import log_api_errors

@log_api_errors
def get_group_id(board_id: int, group_name: str) -> str | None:
    """
    Busca o ID de um grupo em um quadro específico pelo seu nome.

    Args:
        board_id: O ID do quadro onde o grupo será procurado.
        group_name: O nome exato (case-sensitive) do grupo a ser encontrado.

    Returns:
        A string do ID do grupo se encontrado, caso contrário, None.
    """
    logging.info(f"Buscando ID do grupo '{group_name}' no quadro ID: {board_id}...")
    
    try:
        variables = {"boardId": board_id}
        
        response_data = call_monday_api(QUERY_GET_GROUP_ID, variables)
        
        groups_list = response_data.get('boards', [{}])[0].get('groups', [])
        
        for group in groups_list:
            if group.get('title') == group_name:
                group_id_found = group.get('id')
                logging.info(f"Grupo '{group_name}' encontrado com o ID: {group_id_found}.")
                return group_id_found
        
        logging.warning(f"Grupo com o nome '{group_name}' não foi encontrado no quadro {board_id}.")
        return None

    except Exception as e:
        error_message = f"Falha ao buscar grupos para o quadro {board_id}."
        api_logger.error(f"{error_message} Causa: {e}")
        raise
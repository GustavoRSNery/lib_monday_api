import logging
from ..utils.logger import api_logger
from ..api_client.call_api import call_monday_api
from ..queries.templates import QUERY_CREATE_GROUP


def create_monday_group(board_id: int, group_name: str) -> str:
    """
    Cria um novo grupo em um quadro específico do Monday.com.

    :param board_id: ID do quadro onde o grupo será criado.
    :param group_name: Nome do novo grupo.
    :return: O ID do grupo recém-criado.
    """
    try:
        logging.info(f"Criando grupo '{group_name}' no quadro {board_id}...")
        group_vars = {"boardId": board_id, "groupName": group_name}
        
        response_data = call_monday_api(QUERY_CREATE_GROUP, group_vars)
        new_group_id = response_data.get('create_group', {}).get('id')

        if not new_group_id:
            raise Exception("API retornou sucesso, mas o ID do grupo não foi encontrado.")
        
        logging.info(f"Grupo '{group_name}' (ID: {new_group_id}) criado com sucesso!")
        
        return new_group_id
    
    except Exception as e:
        logging.error(f"Erro inesperado {e}!")
        api_logger.error(e)
        
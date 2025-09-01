# Em: src/extracao_monday/service/delete_group_monday.py

import logging
from ..api_client.call_api import call_monday_api
from ..queries.templates import QUERY_DELETE_GROUP
from ..utils.logger import api_logger

def delete_monday_group(board_id: int, group_id: str) -> bool:
    """
    Deleta um grupo de um quadro específico do Monday.com.

    Args:
        board_id: O ID do quadro de onde o grupo será deletado.
        group_id: O ID do grupo a ser deletado.

    Returns:
        True se o grupo foi deletado com sucesso, False caso contrário.
    """
    logging.info(f"Tentando deletar o grupo ID '{group_id}' do quadro ID: {board_id}...")
    
    try:
        variables = {
            "boardId": board_id,
            "groupId": group_id
        }
        
        response_data = call_monday_api(QUERY_DELETE_GROUP, variables)
        
        # Verificação da resposta para confirmar a exclusão
        deleted_id = response_data.get('delete_group', {}).get('id')
        
        if deleted_id == group_id:
            logging.info(f"Grupo ID '{group_id}' deletado com sucesso do quadro {board_id}.")
            return True
        else:
            logging.warning(f"A API não confirmou a exclusão do grupo '{group_id}'. Resposta: {response_data}")
            return False

    except Exception as e:
        error_message = f"Falha ao tentar deletar o grupo '{group_id}' do quadro {board_id}."
        logging.error(error_message)
        api_logger.error(f"{error_message} Causa: {e}")
        raise
import logging
from ..api_client.call_api import call_monday_api
from ..queries.templates import QUERY_BOARD_ITEM_COUNT
from ..utils.decorators import log_api_errors

@log_api_errors
def get_board_item_count(board_id: int) -> int:
    """
    Busca o número de itens em um quadro específico.

    Args:
        board_id: O ID do quadro.

    Returns:
        O número de itens no quadro, ou 'raise' em caso de erro.
    """
    logging.info(f"Verificando a contagem de itens no quadro ID '{board_id}'...")
    try:
        variables = {"boardId": board_id}
        response_data = call_monday_api(QUERY_BOARD_ITEM_COUNT, variables)
        
        count = response_data.get('boards', [{}])[0].get('items_count', 0)
        logging.info(f"O quadro contém {count} itens.")
        return count
    
    except Exception:
        logging.error(f"Não foi possível obter a contagem de itens para o quadro {board_id}.")
        raise
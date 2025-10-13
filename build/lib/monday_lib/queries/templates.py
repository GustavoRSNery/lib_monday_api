import os
import logging
from ..utils.logger import api_logger

def load_queries_from_directory(directory_path: str) -> dict:
    """
    Varre um diretório, encontra todos os arquivos .gql e os carrega em um dicionário.
    A chave do dicionário é o nome do arquivo (sem a extensão .gql) em maiúsculas.
    """
    queries = {}
    # print(f"Carregando queries do diretório: {directory_path}")
    try:
        for filename in os.listdir(directory_path):
            if filename.endswith(".gql"):
                query_name = os.path.splitext(filename)[0].upper()
                file_path = os.path.join(directory_path, filename)
                
                with open(file_path, "r", encoding="utf-8") as file:
                    queries[query_name] = file.read()

    except FileNotFoundError:
        error_message = f"Diretório de templates GQL não foi encontrado no caminho esperado: '{directory_path}'"
        logging.critical(error_message)
        api_logger.error(error_message)
        raise
    
    return queries

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templ')
_queries_dict = load_queries_from_directory(TEMPLATES_DIR)

QUERY_DELETE_GROUP = _queries_dict.get('DELETE_GROUP', None)
QUERY_CREATE_GROUP = _queries_dict.get('CREATE_GROUP', None)   
QUERY_GET_GROUP_ID = _queries_dict.get('GET_BOARD_GROUPS', None)
QUERY_INITIAL_REQUEST = _queries_dict.get('INITIAL_REQUEST', None)
QUERY_PAGINATED_REQUEST = _queries_dict.get('PAGINATED_REQUEST', None)
QUERY_BOARD_ITEM_COUNT = _queries_dict.get('GET_BOARD_ITEM_COUNT', None)
QUERY_GET_COLUMN_METADATA = _queries_dict.get('GET_COLUMN_METADATA', None)
import logging
import sys

# --- CONFIGURAÇÃO CENTRAL DE LOGGING PARA A BIBLIOTECA ---
# Esta configuração será executada UMA VEZ, na primeira vez que
# qualquer parte do pacote 'extracao_monday' for importada.

logging.basicConfig(
    level=logging.INFO, # Define o nível mínimo de log a ser exibido (INFO e acima)
    stream=sys.stdout,  # Direciona a saída para o terminal (console)
    format="%(asctime)s - [%(levelname)s] - [%(filename)s -> %(funcName)s()] - %(message)s"
)
# para usuario final
from .main import extrair_dados_monday
from .service.data_import_monday import create_items_in_group
from .service.creat_group_monday import create_monday_group
from .service.get_group_id_monday import get_group_id
from .service.delete_group_monday import delete_monday_group
from .service.get_board_item_count import get_board_item_count
from .service.log_management import copy_log_file
from .infra.settings import load_settings

# uso pesquisador/interno_do_software
from .service.data_export_monday import extrair_dados_paginados
from .api_client.call_api import call_monday_api
from .service.get_id_column_monday import chamada_api_get_ids
from .infra.settings import get_settings
from .mapper.column_map import ColunaIDMapper

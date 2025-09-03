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

from .main import extrair_dados_monday                                                                       # para usuario final
from .service.data_import_monday import create_items_in_group                                                # para usuario final
from .service.creat_group_monday import create_monday_group                                                  # para usuario final
from .service.data_export_monday import extrair_dados_paginados # uso pesquisador/interno_do_software
from .api_client.call_api import call_monday_api                # uso pesquisador/interno_do_software
from .service.get_id_column_monday import chamada_api_get_ids   # uso pesquisador/interno_do_software
from .service.get_group_id_monday import get_group_id                                                        # para usuario final
from .service.delete_group_monday import delete_monday_group                                                 # para usuario final
from .mapper.column_map import ColunaIDMapper                   # uso pesquisador/interno_do_software

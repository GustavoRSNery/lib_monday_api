import logging
import os
import pickle
from infra.settings import settings
from ..utils.logger import api_logger
from ..service.get_id_column_monday import chamada_api_get_ids


class ColunaIDMapper:
    """Gerencia o mapeamento entre nomes de colunas e seus metadados (ID, tipo).

    Esta classe atua como uma interface para um quadro (board) específico do 
    Monday.com, facilitando a obtenção de informações de colunas de forma eficiente.

    A principal funcionalidade é o sistema de cache (persistência). Na primeira
    vez que a classe é instanciada para um determinado quadro, ela faz uma chamada
    à API do Monday.com, busca os metadados de todas as colunas e salva
    essas informações localmente em um arquivo `.pkl`. Em inicializações futuras,
    ela carrega o mapa diretamente do arquivo, evitando chamadas desnecessárias à API
    e tornando o processo muito mais rápido.

    Além disso, a classe possui uma lógica de atualização dinâmica: se um método
    como `get_column_info` for chamado com um nome de coluna que não está no
    cache, ela automaticamente força uma nova busca na API, atualiza o mapa
    local e tenta encontrar a coluna novamente.

    Atributos:
        board_id (str): O ID do quadro do Monday.com que está sendo gerenciado.
        coluna_map (dict): O dicionário principal que armazena o mapeamento.
            O formato é: `{'Nome da Coluna': {'id': 'id_da_coluna', 'type': 'tipo_da_coluna'}}`

    Exemplo de Uso:
        ## Instancia o mapper para um quadro específico
        mapper = ColunaIDMapper(board_id="1234567890", board_name="projetos_ti")

        ### get_column_info -> `dict`
        info_status = mapper.get_column_info("Status")
         info_status -> {'id': 'status', 'type': 'status'}

        ### get_id -> `str`
        id_prazo = mapper.get_id("Prazo")
         id_prazo -> 'date'

        ### get_type -> `str`
        tipo_responsavel = mapper.get_type("Responsável")
         tipo_responsavel -> 'people'
    """
    def __init__(self, board_id: str = None, board_name: str = None):

        if not (board_id and board_name):
            raise ValueError("É obrigatório informar board_id e board_name.")
        
        self.board_id = board_id
        self.persist_path = settings.PERSIST_PATH / board_name / f"{self.board_id}.pkl"
        self.coluna_map = {}
        
        if os.path.exists(self.persist_path):
            self._load()
        else:
            self.refresh_map() 
    
    def _create_map(self, api_response_data: dict):
        """
        Cria o mapa {'Nome': {'id': ID, 'type': TIPO}} a partir da resposta da 
        query de metadados do quadro.
        """
        board_data = api_response_data.get("boards", [{}])[0]

        if not board_data:
            raise ValueError(f"Nenhum item encontrado no quadro {self.board_id} para mapear colunas.")
        
        main_columns = board_data.get("main_columns", [])
        sub_columns = board_data.get("sub_columns", [])
        coluna_map_temp = {}
        
        # Items
        for coluna in main_columns:
            titulo = coluna.get("title")
            id_col = coluna.get("id")
            type_col = coluna.get("type")
            if titulo and id_col and type_col:
                coluna_map_temp[titulo] = {'id': id_col, 'type': type_col}

        # Subitens
        for coluna in sub_columns:
            titulo = coluna.get("column", {}).get("title")
            id_col = coluna.get("id")
            type_col = coluna.get("type")
            if titulo and id_col and type_col:
                coluna_map_temp[titulo] = {'id': id_col, 'type': type_col}

        self.coluna_map = coluna_map_temp

    def _save(self):
        """Cria o arquivo de persistência e salva os dados"""
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
        with open(self.persist_path, 'wb') as f:
            pickle.dump(self.coluna_map, f)

    def _load(self):
        """Carrega os dados do arquivo de persistência"""
        with open(self.persist_path, 'rb') as f:
            self.coluna_map = pickle.load(f)

    def refresh_map(self):
        """Força a atualização do mapa de colunas a partir da API e salva em disco."""
        logging.info(f"Buscando metadados das colunas para o quadro {self.board_id}...")
        api_data = chamada_api_get_ids(self.board_id)
        self._create_map(api_data)
        self._save()
        logging.info(f"Mapeamento de colunas para o quadro {self.board_id} foi atualizado e salvo com sucesso.")

    def get_column_info(self, nome_coluna: str) -> dict:
        """
        Retorna um dicionário com {'id': ..., 'type': ...} para a coluna, se existente.
        Atualiza o mapa se a coluna não for encontrada na primeira tentativa.
        """
        try:
            info: dict = self.coluna_map.get(nome_coluna)
            if not info:
                self.refresh_map()
                info = self.coluna_map.get(nome_coluna)
                if not info:
                    raise ValueError(f"Coluna '{nome_coluna}' não foi encontrada no quadro {self.board_id} mesmo após a atualização.")
                
        except Exception as e:
            # Se qualquer parte do processo falhar, loga o erro e re-levanta a exceção
            error_message = f"Falha ao atualizar o mapa de colunas para o quadro {self.board_id}."
            
            # Loga a mensagem de alto nível no console
            logging.error(error_message)
            # Loga a mensagem detalhada no arquivo de persistência
            api_logger.error(f"{error_message} Causa: {e}")
            raise 
            
        return info
    
    def get_id(self, nome_coluna: str) -> str:
        """
        Retorna apenas o ID da coluna para manter a compatibilidade com o código antigo.
        """
        # Este método agora usa o novo get_column_info
        return self.get_column_info(nome_coluna)['id']
    
    def get_type(self, nome_coluna: str) -> str:
        """
        Retorna apenas o TIPO da coluna.
        """
        return self.get_column_info(nome_coluna)['type']
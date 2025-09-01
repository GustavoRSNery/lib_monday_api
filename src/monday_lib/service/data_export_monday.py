import logging
from ..utils.logger import api_logger
from ..utils.get_last_date import get_date
from ..mapper.column_map import ColunaIDMapper
from ..api_client.call_api import call_monday_api
from ..queries.templates import QUERY_INITIAL_REQUEST, QUERY_PAGINATED_REQUEST

def extrair_dados_paginados(board_id: str, 
                            subsetor: str, 
                            filtrar_por_data: bool = True,
                            column_name: str = None, 
                            init_date: str = None, 
                            end_date: str = None) -> list:
    """
    Chamada API para o servidor da Monday com a query de 'request.gql', 
    aqui extrai os elementos e sub_elementos.

    Recebe obrigatoriamente: 
        board_id= format:"8585814551" -> str
        column_name= format:"Prazo Inicial" -> str
        nome_subsetor= format:"CRI" -> str

        OBS: Em nome_subsetor passar apenas a 
            abreviação do subsetor para padronização,
            como 'CRI' para 'Criação', 'ARQ' para 'Design de Ambientes'...

    Opcionais:
        init_date= format:"AAAA-MM-DD" -> str
        end_date= format:"AAAA-MM-DD" -> str
    
    Se não passar os opcionais, será definido pelo codigo:
        init_date= "primeiro_dia_mes_anterior" -> str
        end_date= "ultimo_dia_mes_anterior" -> str

    Se {filtrar_por_data: bool = False} & '{init_date} and {end_date} and {column_name} = None' -> os items não sao filtrados por data.
        (Não recomendado, pois escala 'N+D' .:.(dias corridos do ano em atividades))

    'raise' caso fortuito.
    """

    all_items = []
    variables = {
        "boardId": board_id,
    }

    if filtrar_por_data:
        if init_date is None and end_date is None:
            init_date, end_date = get_date()
        if not column_name:
            raise Exception("Não foi passado o Nome da Coluna de Data a ser filtrada.")     

        mapper = ColunaIDMapper(board_id, subsetor)
        id_date_col = mapper.get_id(column_name)

        regras_de_filtro = [{
            "column_id": id_date_col,
            "compare_value": [init_date, end_date],
            "operator": "between"
        }]
        variables["rules"] = regras_de_filtro
        logging.info(f"Filtro de data ativado. Buscando primeira página COM FILTRO...")
        # Chamada API
        response_data = call_monday_api(QUERY_INITIAL_REQUEST, variables)
    else:
        logging.info("Busca SEM FILTRO. Buscando primeira página...")
        # Chamada API
        response_data = call_monday_api(QUERY_PAGINATED_REQUEST, variables)

    page_data = response_data.get("boards", [{}])[0].get("items_page", {})
    items = page_data.get("items", [])
    if items:
        all_items.extend(items)
    
    cursor = page_data.get("cursor")
    logging.info(f"Primeira página buscada. Itens até agora: {len(all_items)}. Contém mais items? - {"Sim" if bool(cursor)==True else "Não"}")

    while cursor is not None:

        variables_paginadas = {
            "boardId": board_id,
            "cursor": cursor
        }

        # Chamada API
        response_data = call_monday_api(QUERY_PAGINATED_REQUEST, variables_paginadas)

        page_data = response_data.get("boards", [{}])[0].get("items_page", {})
        if not page_data:
            break

        items = page_data.get("items", [])
        if items:
            all_items.extend(items)
        
        cursor = page_data.get("cursor")
        if cursor is None:
            break

        logging.info(f"Itens até agora: {len(all_items)}. Contém mais items? - Sim")

    if all_items:
        logging.info(f"Busca concluída. Total de itens encontrados: {len(all_items)}. Contém mais items? - Não")
    return all_items
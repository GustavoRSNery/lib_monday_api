import pandas as pd
import json
import time
import logging

import requests
from ..api_client.call_api import call_monday_api
from .get_board_item_count import get_board_item_count
from ..mapper.column_map import ColunaIDMapper
from ..utils.formatters import DEFAULT_FORMATTER, COLUMN_FORMATTERS, ID_SPECIFIC_FORMATTERS
from ..utils.logger import api_logger

def create_items_in_group(board_id: int, 
                          group_id: str, 
                          df: pd.DataFrame, 
                          board_name: str,
                          batch_size: int = 100,
                          column_map: dict = None) -> dict: 
    """
    Cria múltiplos itens em um grupo em lotes (batches) para otimizar a performance,
    respeitando os limites da API e pausando entre os lotes.

    Args:
        board_id: ID do quadro onde os itens serão criados.
        group_id: ID do grupo que receberá os novos itens.
        df: DataFrame com os dados dos itens.
        subsetor: Nome do subsetor, necessário para o ColunaIDMapper.
        column_map: (Opcional) Dicionário para forçar mapeamentos específicos
                    onde o nome da coluna do DF é diferente do nome no Monday.
                    Se for passar, {coluna DF: coluna Monday}
        batch_size: O número de itens a serem criados em cada chamada à API.

    Returns:
        Um dicionário com o resumo da operação de upload.
    """




#----------------------------------------------------------------VALIDAR EXISTENCIA DE DADOS NO DF------------------------------------------------------------------------------------------------
    if df.empty or len(df.columns) == 0:
        raise ValueError("O DataFrame está vazio ou não possui colunas.")
    if column_map is None:
        column_map = {}
#----------------------------------------------------------------VALIDAR EXISTENCIA DE DADOS NO DF------------------------------------------------------------------------------------------------
    
    logging.info(f"Iniciando upload de {len(df)} itens em lotes de {batch_size} para o grupo '{group_id}'...")

#----------------------------------------------------------------MAPEAMENTO DE COLUNA------------------------------------------------------------------------------------------------
    try:
        mapper = ColunaIDMapper(board_id, board_name)
    except Exception as e:
        api_logger.error(f"Falha ao inicializar ColunaIDMapper para o quadro {board_id}. Erro: {e}")
        raise

    auto_column_map = {}
    item_name_col_df = None
    first_col_df = df.columns[0].lower().strip() # A primeira coluna é o nome do item.
    df_columns = list(df.columns)
    monday_columns_info = mapper.coluna_map

    for df_col in df_columns: # percorrendo as colunas do DF
        normalized_df_col = df_col.lower().strip()
        found_match = False

        for monday_title, monday_info in monday_columns_info.items(): # percorrendo as colunas do Monday
            normalized_monday_title = monday_title.lower().strip()

            is_override_match = df_col in column_map and column_map[df_col] == monday_title
            is_direct_match = df_col not in column_map and normalized_df_col == normalized_monday_title
            
            if is_override_match or is_direct_match or (first_col_df==normalized_df_col): # Deu Match
                auto_column_map[df_col] = monday_title
                logging.info(f"Auto-map: Coluna do DF '{df_col}' -> Coluna Monday '{monday_title}'.")
                
                if monday_info.get('id') == 'name': # Se deu Match, ja proveita e faz o rastreio da coluna de nome do DF no Monday
                    item_name_col_df = df_col       # Se deu Match, e no match o id da coluna do monday é 'name' entao provavelmente é o primeiro loop, consequentemente o 'item name' esta aqui
                
                found_match = True
                break
        
        if not found_match and df_col not in column_map:
            logging.warning(f"AVISO: Nenhuma coluna correspondente no Monday foi encontrada para a coluna do DataFrame: '{df_col}'. Ela será ignorada.")
            
    if not item_name_col_df:
        raise ValueError("Mapeamento automático falhou: Não foi possível identificar a coluna de nome do item.")
    
    logging.info(f"Coluna de nome do item auto-detectada: '{item_name_col_df}'")
#----------------------------------------------------------------MAPEAMENTO DE COLUNA------------------------------------------------------------------------------------------------    

#----------------------------------------------------------------CRIAR BATH QUERY PARA SUBIR OS ITENS NO QUADRO------------------------------------------------------------------------------------------------
    created_item_ids = []
    batches_with_504_timeout = []
    failed_critical_batches = []

    # Divide o DF em uma lista de lotes
    list_of_batches = [df.iloc[i:i + batch_size] for i in range(0, len(df), batch_size)]
    total_batches = len(list_of_batches)

    for i, batch_df in enumerate(list_of_batches):

        batch_mutation_parts = []
        batch_vars_definition = []
        batch_vars_values = {"boardId": board_id, "groupId": group_id}
        batch_start_time = time.monotonic()

        for index, row in batch_df.iterrows():
            _item_alias = f"item_{index}"
            _item_name_var = f"itemName_{index}"
            _column_values_var = f"columnValues_{index}"

            batch_vars_definition.extend([
                f"${_item_name_var}: String!",
                f"${_column_values_var}: JSON!"
            ])

            item_name = str(row.get(item_name_col_df, f'Item da Linha {index}'))

            column_values_dict = {}
            for df_col_name, monday_col_name in auto_column_map.items():
                if df_col_name == item_name_col_df or pd.isna(row.get(df_col_name)):
                    continue

                value = row[df_col_name]
                column_info = mapper.get_column_info(monday_col_name)
                if not column_info:
                    continue
                
                monday_col_id = column_info['id']
                column_type = column_info['type']
                formatter = None
                # 1. Tenta encontrar um formatador específico para este ID de coluna
                if monday_col_id in ID_SPECIFIC_FORMATTERS:
                    formatter = ID_SPECIFIC_FORMATTERS[monday_col_id]
                else:
                # 2. Se não tiver usa str
                    formatter = COLUMN_FORMATTERS.get(column_type, DEFAULT_FORMATTER)
                
                formatted_value = formatter(value)
                column_values_dict[monday_col_id] = formatted_value

            batch_vars_values[_item_name_var] = item_name
            batch_vars_values[_column_values_var] = json.dumps(column_values_dict)

            # E adicionamos a parte da query para este item à nossa lista de partes da query
            batch_mutation_parts.append(f"""
                {_item_alias}: create_item(
                    board_id: $boardId,
                    group_id: $groupId,
                    item_name: ${_item_name_var},
                    column_values: ${_column_values_var}
                ) {{ id }}
            """)
        
        full_mutation_str = f"""
            mutation createMultipleItems({', '.join(batch_vars_definition)}, $boardId: ID!, $groupId: String!) {{
                {' '.join(batch_mutation_parts)}
            }}
        """

            # ----- AQUI SE FAZ A CHAMADA API -----
        try:
            logging.info(f"Enviando lote {i+1}/{total_batches} com {len(batch_df)} itens...")
            response_data = call_monday_api(full_mutation_str, batch_vars_values)
            
            for item_alias, result in response_data.items():
                if result and 'id' in result:
                    created_item_ids.append(result['id'])
            # --- exception da chamada api ---
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 504:
                logging.warning(f"Lote {i+1} encontrou um Timeout (504). Os itens podem ter sido criados. Verificação será feita no final.")
                batches_with_504_timeout.append({"batch_number": i+1, "item_count": len(batch_df)})
            else:
                # É outro erro de HTTP (4xx, 5xx), tratamos como ERRO crítico
                error_info = f"Falha crítica de HTTP no lote {i+1}. Causa: {e}"
                api_logger.error(error_info)
                failed_critical_batches.append({"batch_number": i+1, "error": str(e)})
            # --- exception da chamada api ---
        except Exception as e:
            # É um erro de GraphQL ou de conexão, tratamos como ERRO crítico
            error_info = f"Falha crítica no lote {i+1}. Causa: {e}"
            api_logger.error(error_info)
            failed_critical_batches.append({"batch_number": i+1, "error": str(e)})
            
            # ----- TERMINO DA CHAMADA API -----

        # Se este NÃO for o ultimo lote, espere 60 segundos.
        if i < total_batches - 1:
            batch_duration = time.monotonic() - batch_start_time
            pause_duration = 60 - batch_duration
            
            if pause_duration > 0:
                logging.info(f"Lote processado em {batch_duration:.2f}s. Pausando por {pause_duration:.2f}s para renovar o orçamento da API...")
                time.sleep(pause_duration)
            else:
                logging.info(f"Lote processado em {batch_duration:.2f}s. Orçamento da API já renovado. Prosseguindo imediatamente.")
            
    
#----------------------------------------------------------------CRIAR BATH QUERY PARA SUBIR OS ITENS NO QUADRO------------------------------------------------------------------------------------------------

#----------------------------------------------------------------ENVIAR SUMARIO DOS ITENS CRIADOS------------------------------------------------------------------------------------------------

    # --- VERIFICAÇÃO PÓS-EXECUÇÃO PARA ERROS 504 ---
    try:
        total_items_failed_in_504 = 0
        if batches_with_504_timeout:
            logging.info("\n--- Verificando a quantidade de itens recebidos pelo Monday (erros: 504) ---")
            
            # Conta quantos itens deveriam ter sido criados nos lotes que NÃO falharam criticamente
            items_in_critical_failed_batches = sum(batch['item_count'] for batch in failed_critical_batches)
            
            # Chama a API para ver quantos itens realmente existem no grupo agora
            items_on_monday = get_board_item_count(board_id)
            
            total_items_failed_in_504 = len(df) - items_on_monday - items_in_critical_failed_batches
            
            if total_items_failed_in_504 > 0:
                logging.error(f"Verificação indica que {total_items_failed_in_504} itens de lotes com Timeout (504) realmente não foram criados.")
            else:
                logging.info("Verificação indica que todos os itens de lotes com Timeout (504) foram criados com sucesso no Monday.")
                total_items_failed_in_504 = 0

    except Exception:
        logging.error(f"Erro na verificação de quantidade de itens recebidos.")
        raise
             

    total_failed_critical = sum(batch['item_count'] for batch in failed_critical_batches)
    total_failed = total_failed_critical + total_items_failed_in_504

    summary = {
        "total_rows": len(df),
        "success_count": len(df) - total_failed,
        "failed_count": total_failed,
        "created_ids": created_item_ids,
        "critical_errors": failed_critical_batches,
        "timeout_batches": batches_with_504_timeout,
        "uncreated_items_after_timeout": total_items_failed_in_504
    }
    
    logging.info(f"Upload concluído. {summary['success_count']} itens criados, {summary['failed_count']} falhas.")
    return summary
#----------------------------------------------------------------ENVIAR SUMARIO DOS ITENS CRIADOS------------------------------------------------------------------------------------------------

import pandas as pd
import json
import time
import logging
import requests
from ..api_client.call_api import call_monday_api, APITimeoutError, APIError
from .get_board_item_count import get_board_item_count
from ..mapper.column_map import ColunaIDMapper
from ..utils.formatters import DEFAULT_FORMATTER, COLUMN_FORMATTERS, ID_SPECIFIC_FORMATTERS
from ..utils.decorators import log_api_errors

@log_api_errors
def _build_auto_column_map(df: pd.DataFrame, mapper: ColunaIDMapper, column_map: dict) -> tuple[dict, str]:
    """
    Constrói o mapa de colunas automático e identifica a coluna de nome do item.
    Retorna o mapa e o nome da coluna do item no DataFrame.
    """
    auto_map = {}
    item_name_col_df = df.columns[0] # Convenção: primeira coluna do DF é o nome.
    logging.info(f"Convenção adotada: a coluna '{item_name_col_df}' será usada como nome do item.")

    monday_columns = mapper.coluna_map
    for df_col in df.columns:
        normalized_df_col = df_col.lower().strip()
        found_match = False
        for monday_title in monday_columns.keys():
            is_override = df_col in column_map and column_map[df_col] == monday_title
            is_direct_match = df_col not in column_map and normalized_df_col == monday_title.lower().strip()
            
            if is_override or is_direct_match:
                auto_map[df_col] = monday_title
                # logging.info(f"Auto-map: Coluna do DF '{df_col}' -> Coluna Monday '{monday_title}'.")
                found_match = True
                break
        
        if not found_match and df_col not in column_map:
            logging.warning(f"AVISO: Nenhuma coluna correspondente no Monday para '{df_col}'. Será ignorada.")
    
    logging.info(f"Auto-map: Todas as colunas mapeadas'.")
    return auto_map, item_name_col_df

@log_api_errors
def _prepare_batch_request(batch_df: pd.DataFrame, board_id: int, group_id: str, auto_map: dict, item_name_col: str, mapper: ColunaIDMapper) -> tuple[str, dict]:
    """Prepara a string da query GraphQL e o dicionário de variáveis para um lote."""
    parts = []
    defs = []
    vals = {"boardId": board_id, "groupId": group_id}

    for index, row in batch_df.iterrows():
        item_alias = f"item_{index}"
        item_name_var = f"itemName_{index}"
        col_vals_var = f"columnValues_{index}"
        
        defs.extend([f"${item_name_var}: String!", f"${col_vals_var}: JSON!"])
        
        vals[item_name_var] = str(row.get(item_name_col, f'Item Linha {index}'))
        
        col_vals_dict = {}
        for df_col, mon_col in auto_map.items():
            if df_col == item_name_col or pd.isna(row.get(df_col)):
                continue
            
            value = row[df_col]
            info = mapper.get_column_info(mon_col)
            if not info: continue
            
            col_id, col_type = info['id'], info['type']
            formatter = ID_SPECIFIC_FORMATTERS.get(col_id) or COLUMN_FORMATTERS.get(col_type, DEFAULT_FORMATTER)
            col_vals_dict[col_id] = formatter(value)
        
        vals[col_vals_var] = json.dumps(col_vals_dict)
        
        parts.append(f"""
            {item_alias}: create_item(
                board_id: $boardId, group_id: $groupId,
                item_name: ${item_name_var}, column_values: ${col_vals_var}
            ) {{ id }}
        """)
        
    query_str = f"""
        mutation createMultipleItems({', '.join(defs)}, $boardId: ID!, $groupId: String!) {{
            {' '.join(parts)}
        }}
    """
    return query_str, vals

@log_api_errors
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
        board_name: Nome do quadro, necessário para o ColunaIDMapper.
        column_map: (Opcional) Dicionário para forçar mapeamentos específicos
                    onde o nome da coluna do DF é diferente do nome no Monday.
                    Se for passar, {coluna DF: coluna Monday}
        batch_size: O número de itens a serem criados em cada chamada à API.

    Returns:
        Um dicionário com o resumo da operação de upload.
    """
    if df.empty or len(df.columns) == 0:
        raise ValueError("O DataFrame está vazio ou não possui colunas.")

    logging.info(f"Iniciando upload de {len(df)} itens em lotes de {batch_size} para o grupo '{group_id}'...")
    
    # Prepara o mapper e o mapa de colunas uma única vez
    mapper = ColunaIDMapper(board_id, board_name)
    auto_map, item_name_col = _build_auto_column_map(df, mapper, column_map or {})
    
    # Prepara as listas de resultados
    created_item_ids = []
    batches_with_504_timeout = []
    failed_critical_batches = []

    list_of_batches = [df.iloc[i:i + batch_size] for i in range(0, len(df), batch_size)]
    total_batches = len(list_of_batches)

    for i, batch_df in enumerate(list_of_batches):
        batch_start_time = time.monotonic()
        
        try:
            full_mutation_str, batch_vars = _prepare_batch_request(batch_df, board_id, group_id, auto_map, item_name_col, mapper)
            
            logging.info(f"Enviando lote {i+1}/{total_batches} com {len(batch_df)} itens...")
            response_data = call_monday_api(full_mutation_str, batch_vars)
            
            for item_alias, result in response_data.items():
                if result and 'id' in result:
                    created_item_ids.append(result['id'])

            # --- exception da chamada api ---
        except APITimeoutError as e:
            logging.warning(f"Lote {i+1} encontrou um Timeout (504). Os itens podem ter sido criados. Verificação será feita no final.")
            batches_with_504_timeout.append({"batch_number": i+1, "item_count": len(batch_df)})

            # --- exception da chamada api ---
        except APIError as e:
            logging.error(f"Falha crítica no lote {i+1}. O lote não foi processado.")
            failed_critical_batches.append({"batch_number": i+1, "error": str(e), "item_count": len(batch_df)})
            
            # ----- TERMINO DA CHAMADA API -----
        # Pausa dinâmica
        if i < total_batches - 1:
            batch_duration = time.monotonic() - batch_start_time
            pause_duration = 60 - batch_duration
            if pause_duration > 0:
                logging.info(f"Lote processado em {batch_duration:.2f}s. Pausando por {pause_duration:.2f}s...")
                time.sleep(pause_duration)
            else:
                logging.info(f"Lote processado em {batch_duration:.2f}s. Prosseguindo imediatamente.")

    # --- VERIFICAÇÃO PÓS-EXECUÇÃO ---
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
                logging.info("Verificação indica que todos os itens foram criados com SUCESSO no Monday.")
                total_items_failed_in_504 = 0

        total_failed_critical = sum(batch['item_count'] for batch in failed_critical_batches)
        total_failed = total_failed_critical + total_items_failed_in_504

    except Exception:
        logging.error(f"Erro na verificação de quantidade de itens recebidos.")
        raise
             
    
    summary = {
        "total_rows": len(df),
        "success_count": len(df) - total_failed,
        "failed_count": total_failed,
        "created_ids": created_item_ids,
        "critical_erros_count": total_failed_critical,
        "critical_errors": failed_critical_batches,
        "timeout_batches": batches_with_504_timeout,
        "uncreated_items_after_timeout": total_items_failed_in_504
    }
    
    logging.info(f"Upload concluído. {summary['success_count']} itens criados, {summary['failed_count']} falhas, {summary['critical_erros_count']} erros criticos.")
    return summary
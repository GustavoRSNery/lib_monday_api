from monday_lib import create_monday_group, create_items_in_group
import pandas as pd
### ALGUNS TESTES QUE ESTAVA FAZENDO PARA A IMPORTAÇÃO DE DADOS E CRIAÇÃO DE GRUPOS NO MONDAY###
# --- DADOS DE EXEMPLO ---
data = {
    'Elemento': ['Desenvolver_API_v2', 'Criar_UI/UX_v2', 'Testar_Módulo_B_v2'],
    'Pessoa': [61907099, 61907099, 61907099], # Note: ID deve ser número
    'Data': ['2025-08-26', '2025-09-10', '2025-09-01'],
    'Status': ['Feito', 'Travado', 'Em andamento']
}
df = pd.DataFrame(data)

# --- MAPEAMENTO DAS COLUNAS ---
column_mapping = {
    'Elemento': 'Elemento',
    'Pessoa': 'Pessoa',
    'Data': 'Data', # Ajuste para 'date' se o ID da sua coluna for 'date'
    'Status': 'Status'
}

BOARD_ID = 9382957552 # Substitua pelo seu ID de quadro

current_date = pd.to_datetime('today').strftime('%Y-%m-%d %H:%M')
new_group_title = f"Upload Modularizado - {current_date}"

try:
    # --- ORQUESTRANDO AS DUAS FUNÇÕES ---
    # Passo 1: Use a primeira função para criar um novo grupo.
    current_date = pd.to_datetime('today').strftime('%Y-%m-%d %H:%M')
    new_group_title = f"Teste de {current_date}"
    
    new_group_id = create_monday_group(board_id=BOARD_ID, group_name=new_group_title)
    #ATÉ AQUI FUNCIONANDO PERFEITAMENTE

    # Passo 2: Use a segunda função para popular o grupo que acabamos de criar.
    if new_group_id:
        create_items_in_group(
            board_id=BOARD_ID,
            group_id=new_group_id,
            df=df,
            column_map=column_mapping,
            board_name="GEP_TESTE"
        )

    # --- EXEMPLO DE COMO USAR A SEGUNDA FUNÇÃO SEPARADAMENTE ---
    # Se você já sabe o ID de um grupo e quer apenas adicionar itens a ele:
    #
    # print("\n--- Adicionando itens a um grupo existente ---")
    # existing_group_id = "topics" # Substitua pelo ID real do grupo
    # create_items_in_group(
    #     board_id=BOARD_ID,
    #     group_id=existing_group_id,
    #     df=df,
    #     column_map=column_mapping
    # )

except Exception as e:
    print(f"Ocorreu um erro geral durante a execução: {e}")
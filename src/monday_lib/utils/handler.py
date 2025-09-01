import pandas as pd
"""
Este arquivo é usado apenas para tratar a lista recebida da chamada API, portanto não suporta outra estrutura de dados.
"""

def _obter_valor_coluna(columns: list, title: str = None) -> dict | str | None:
    """ 
    Recebe uma lista de todas as colunas de um json, no modelo de requisição 'gql' presente nos arquivos.
    Retorna um dicionario contendo o nome e valor de todas as colunas:
     dict -> {"nome_colune": "_obter_valor_coluna"}
    Ou se passar o título da coluna desejada:
     str -> "_obter_valor_coluna"
    

    Se str"coluna_desejada".strip.lower != str"coluna_existente".strip.lower:
     -> None
    Else, quer dizer que a coluna existe porem está vazia, então é trago:
     str -> ''

     
    'raise' caso fortuito.
    """
    if title is None:
        coluna_dict = {}
        for col in columns:
            nome_coluna = col['column']['title']
            valor_coluna = col.get('text') or col.get('display_value') or ''
            coluna_dict[nome_coluna] = valor_coluna
        return coluna_dict
    for col in columns:
        if title and str(str(col['column']['title']).strip).lower == str(title.strip).lower:
            return col.get('text') or col.get('display_value') or ''
    return None

def filtrar_itens_grupo(data: list, grupo: str= None) -> list:
    """
    Recebe a lista de retorno da função 'chamada_api()', e com base no modelo de requisição 'gql' presente nos arquivos.
    Filtra todos os itens a partir do groupe_title,
     list -> itens_por_grupo
    
    Se não for passado o nome do grupo:
     None -> "mensagem: Não foi passado um nome de grupo para filtrar"

    'raise' caso fortuito.
    """
    itens_por_grupo = []
    if grupo is None:
        print("Não foi passado um nome de grupo para filtrar")
        return None   
    for item in data:
        group_title = item['group']['title']
        if grupo and group_title != grupo:
            continue
        itens_por_grupo.append(item)
    return itens_por_grupo

def list2dfs(_items: list) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    [ Elementos, Sub Elementos ]

    Itera sobre os elementos da lista recebida de "filrar_itens_grupo" 
    e cria DataFrame's dos elementos e sub elementos.
    
    Entrada -> List

    Saida -> Tuple (pd.DataFrame)
    """
    element_rows = []
    for item in _items:
        row = {
            "id": item['id'],
            "grupo": item['group']['title'],
            "nome": item['name'],
        }                                                       
        row.update(_obter_valor_coluna(item['columns']))   # Atualiza o dicionario com todos os campos das colunas daquele item
        element_rows.append(row)

    sub_itens =_list2df_subitems(_items)
    itens = pd.DataFrame(element_rows)

    return itens, sub_itens

def _list2df_subitems(_items: list) -> pd.DataFrame:
    """ 
    Cria DataFrame dos subelementos
    Entrada -> List
    Saida -> pd.DataFrame
    """
    subelements_rows = []
    for item in _items:
        for sub_item in item.get("subitems", []):
            sub_row = {
                "item_pai_id": item['id'],
                "item_pai_nome": item['name'],
                "subitem_id": sub_item['id'],
                "subitem_nome": sub_item['name'],
            }
            sub_row.update(_obter_valor_coluna(sub_item['columns']))    # Atualiza o dicionario com todos os campos das colunas daquele sub_item
            subelements_rows.append(sub_row)

    return pd.DataFrame(subelements_rows)
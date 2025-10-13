from .service.data_export_monday import extrair_dados_paginados
from .utils.handler import filtrar_itens_grupo, list2dfs
import pandas as pd
import os

def extrair_dados_monday(   
        nome_subsetor: str,
        id_board: str,
        nome_coluna_data: str,
        caminho_arquivos: str,
        data_inicio: str = None,
        data_fim: str = None,
        filtrar_grupo: str = None,
        filtrar_por_data: bool = True
        ) -> tuple[pd.DataFrame | pd.DataFrame | str | str]:
    """Extrai, processa e salva itens e subitens de um quadro do Monday.com.

Esta função orquestra o processo completo de extração de dados. Ela se conecta
a um quadro específico do Monday, busca os itens (e seus respectivos subitens)
com base em filtros de data e/ou grupo, processa esses dados e os salva
localmente em dois arquivos .xlsx separados (um para itens principais e outro
para subitens).

Args:
    nome_subsetor (str): Nome do subsetor, usado tanto para organizar o arquivo
        de cache de metadados (.pkl) quanto o arquivo Excel de saída.
    id_board (str): O ID do quadro no Monday.com de onde os itens serão extraídos.
    nome_coluna_data (str): Nome da coluna de data a ser usada para o filtro
        temporal. Essencial para otimizar a performance da busca.
    caminho_arquivos (str): Caminho da pasta onde os arquivos Excel gerados
        serão salvos.
    data_inicio (str, optional): Data de início do filtro ("AAAA-MM-DD").
        Se não fornecida, o padrão é o primeiro dia do mês anterior.
    data_fim (str, optional): Data de fim do filtro ("AAAA-MM-DD").
        Se não fornecida, o padrão é o último dia do mês anterior.
    filtrar_grupo (str, optional): Nome exato de um grupo para filtrar os resultados.
        Se não fornecido, a busca será feita em todos os grupos do quadro.
    filtrar_por_data (bool, optional): Se True (padrão), aplica o filtro de data.
        Se False, busca todos os itens do quadro, ignorando as datas.

Returns:
    tuple[pd.DataFrame, str, pd.DataFrame, str]: Uma tupla contendo quatro elementos:
    - pd.DataFrame: Um DataFrame com os dados dos itens principais (elementos).
    - str: O caminho completo para o arquivo Excel dos elementos salvo.
    - pd.DataFrame: Um DataFrame com os dados de todos os subitens encontrados.
    - str: O caminho completo para o arquivo Excel dos subitens salvo.

Exemplo de Uso:
    
    # Parâmetros para a extração
    nome_subsetor = "teste_gep"
    id_board = "9382984170"
    nome_coluna_data = "Data de Entrega"
    caminho_arquivos = r"C:\Projetos\extracao_monday\data" # Corrigido: sem `
    data_inicio = "2025-06-01"
    data_fim = "2025-06-24"
    filtrar_grupo = "Feito"
    
    # Supondo que a biblioteca foi instalada com "pip install -e ."
    from extracao_monday import extrair_dados_monday
    
    elementos_df, arq_elem, subelementos_df, arq_sub = extrair_dados_monday(
        nome_subsetor=nome_subsetor,
        id_board=id_board,
        nome_coluna_data=nome_coluna_data,
        caminho_arquivos=caminho_arquivos,
        data_inicio=data_inicio,
        data_fim=data_fim,
        filtrar_grupo=filtrar_grupo
    )
    
    print(f"Extração concluída. Arquivos salvos em: {arq_elem} e {arq_sub}")

Nota sobre o Ambiente:
    Para que a importação `from extracao_monday import ...` funcione, o pacote
    deve ser instalado em modo editável a partir da raiz do projeto:
    $ pip install -e .
"""
    
    # 1 Requisição API para o Monday, puxando os itens do quadro, e filtrando os elementos por data de inicio e fim.
    dados = extrair_dados_paginados(board_id=id_board, column_name=nome_coluna_data, subsetor=nome_subsetor, init_date=data_inicio, end_date=data_fim, filtrar_por_data=filtrar_por_data)

    # 1.1 se necessário, filtrar os elementos por grupo.
    itens = filtrar_itens_grupo(dados, filtrar_grupo) if filtrar_grupo else dados

    # 2 Transforma a lista para Data Frames
    elemento, subelemento = list2dfs(itens)

    pasta_subsetor = os.path.join(caminho_arquivos, nome_subsetor)
    os.makedirs(pasta_subsetor, exist_ok=True)

    arquivo_elementos = os.path.join(caminho_arquivos, nome_subsetor,f"{nome_subsetor}_elementos.xlsx")
    arquivo_subelementos = os.path.join(caminho_arquivos, nome_subsetor, f"{nome_subsetor}_subelementos.xlsx")

    # 3 Pronto!
    elemento.to_excel(arquivo_elementos, index=False)
    print(f"Arquivo Elementos salvo em: {arquivo_elementos}")

    subelemento.to_excel(arquivo_subelementos, index=False)
    print(f"Arquivo Subelementos salvo em: {arquivo_subelementos}")

    return elemento, subelemento, arquivo_elementos, arquivo_subelementos

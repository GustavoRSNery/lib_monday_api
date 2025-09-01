# venv activate 
# cd C:\Projetos\PythonProjects\extracao_monday
# pip install -e .
# cd C:\Projetos\YOUR_CURRENTLY_PROJECT

# Importação da Lib de extracao_dados_monday
import sys

from monday_lib import extrair_dados_monday
### ALGUNS TESTES QUE ESTAVA FAZENDO PARA A EXTRAÇÃO DE DADOS DO MONDAY###
# Importações locais
from utils.handler import atualiza_elementos
from tratar_entregas_finais.filtrar_items import filtrar_atividades_unicas
"""CONCLUIDO"""

# Instancia de Variaveis
nome_subsetor = "CRI"
id_board = "8235017384"
nome_coluna_data = "Data de Entrega"
data_inicio = "2025-06-01"
data_fim = "2025-06-30"
filtrar_grupo = "Feito"
caminho_arquivos = r"C:\Projetos\entregas_finais\criacao"
data_obj = pd.to_datetime(data_inicio)
periodo_formatado = data_obj.strftime('%b/%y').lower()
path_atividades_unicas = fr'C:\Projetos\entregas_finais\criacao\CRI\entregas_finais\CRI_elementos_formatado_{data_inicio[:-3]}.xlsx' # [:-3] tira os 3 ultimos caracteres da str data_inicio 

# Chamada de funções
elementos, subelementos, arquivo_elementos, arquivo_subelementos = extrair_dados_monday(
    nome_subsetor,
    id_board,
    nome_coluna_data,
    caminho_arquivos,
    data_inicio,
    data_fim,
    filtrar_grupo,
)
df_elemento_ajustado = atualiza_elementos(df_elementos=elementos)
df_atividades_unicas = filtrar_atividades_unicas(df_elemento_ajustado, periodo_formatado)

# Criação e atualização dos arquivos
df_elemento_ajustado.to_excel(arquivo_elementos, index=False)
df_atividades_unicas.to_excel(path_atividades_unicas, index=False)

"""CONCLUIDO"""
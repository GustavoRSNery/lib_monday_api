# Lib. para *Extrator* e *Importador* de itens para o site Monday.com

Uma biblioteca Python robusta e performática para extrair e importar dados da API v2 do Monday.com, com *foco* em *automação de processos* e manipulação de *grandes volumes de dados*.

Foi criada para a extração massiva de dados de varios quadros diferentes e com modelos de estrutura diferentes. Tratar e processar estes dados de forma eficaz, sem a necessidade de várias chamadas APIs.
Com a eficiência e refinamento das querys para as chamadas, complementando com a persistencia dos metadados das colunas dos quadros já percorridos, isto facilita a manipulação para extração e importação futuras.
Em quesito importação, também foi pensado para grandes quantidades de itens, não extrapolando a complexidade de query por minuto, para isto é realizado o cacheamento dos itens de um DataFrame (por padrão 100), aonde ele envia dados em batches para controle, e no final faz uma checagem para saber se todos os itens subiram de fato para o quadro & grupo em questão. 

Este pacote foi desenvolvido para simplificar a interação com a API do Monday, abstraindo a complexidade da paginação, limites de taxa (rate limits), mapeamento de colunas e tratamento de erros.

## Principais Funcionalidades

  - **Extração de Dados Paginada:** Busca de forma inteligente todos os itens de um quadro, lidando automaticamente com a paginação da API.
  - **Filtragem Avançada:** Permite a filtragem de itens por data ou outros critérios.
  - **Criação de Itens em Lote (Batch):** Importa milhares de linhas de um DataFrame do Pandas de forma otimizada, respeitando os limites de complexidade da API através de lotes e pausas estratégicas.
  - **Gerenciamento de Grupos:** Funções utilitárias para criar, deletar e buscar o ID de grupos pelo nome.
  - **Mapeamento de Colunas Inteligente:** Sistema para mapear colunas de um DataFrame para colunas do Monday, com detecção automática das colunas de um quadro, mas também tem suporte para overrides(mapeamentos) manuais assim como mostra nos arquivos em /_testes.
  - **Cache de Metadados:** Armazena os metadados das colunas localmente (`.pkl`) para acelerar inicializações futuras.
  - **Logging Profissional:** Sistema de log de dois níveis:
      - Logs de progresso (`INFO`, `WARNING`) são exibidos no terminal durante a execução.
      - Logs de erro (`ERROR`) são salvos com detalhes completos (incluindo o corpo da requisição) em um arquivo `logs/api_errors.log` para auditoria.

  *Confira o arquivo CHANGE.md para obter mais funcionalidades e adições*

## Instalação

1.  **Clone o repositório:**

    ```bash
    git clone [https://lib_monday_api/extracao_monday.git](https://github.com/GustavoRSNery/lib_monday_api)
    cd extracao_monday
    ```

2.  **Crie e ative um ambiente virtual:**

    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\Activate.ps1
    # Linux/macOS
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Instale o pacote em modo editável:**
    Este passo é crucial. Ele torna seu pacote `extracao_monday` importável em todo o projeto.

    ```bash
    pip install -e .
    ```

## Configuração

Altere no arquivo dentro da pasta to projeto `.env` na raiz do projeto e preencha com suas credenciais e configurações. **Alterar metodo, vamos colocar instancia de classe para infra**

```dotenv
# .env

# (Obrigatório) Token de API do Monday.com (Pessoal ou de App)
TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJ0..."

# (Opcional) Caminho para o bundle de certificados .pem (necessário em redes corporativas com proxy/firewall)
PEM="C:/caminho/completo/para/seu/certificado.pem"
```

## Exemplos de Uso

Abaixo estão exemplos de como usar as principais funcionalidades da biblioteca a partir de um script (ex: na sua pasta `scripts/`).

### Exemplo 1: Extraindo Itens de um Quadro com Filtro de Data

```python
from monday_lib import extrair_dados_monday

# Instancia de Variaveis
nome_subsetor = "CRI" # Apenas para criar um arquivo.pkl que irá salvar os dados dos grupos e colunas existentes no quadro para usar futuramente, sem fazer outra chamada API

# Obrigatorio
id_board = "0123456789" 

# Opicional, apenas se você quiser extrair os itens filtrados pela data
nome_coluna_data = "Data de Entrega" 
data_inicio = "2025-06-01"
data_fim = "2025-06-30"

# Opicional, apenas se quiser extrair os itens de apenas um grupo expecifico
filtrar_grupo = "Feito" 

# caminho aonde será salvo o arquivo Excel dos elementos e outro dos subelementos
caminho_arquivos = r"C:\Projetos\entregas_finais\criacao" 


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

print(f"Total de {len(itens_encontrados)} itens encontrados.")
```

### Exemplo 2: Gerenciando Grupos (Buscar, Criar, Deletar)

```python
from extracao_monday import get_group_id, create_monday_group, delete_monday_group

BOARD_ID = 1234567890
NOME_DO_GRUPO = "Novas Demandas Q4 2025"

# 1. Tenta encontrar o grupo
id_grupo = get_group_id(board_id=BOARD_ID, group_name=NOME_DO_GRUPO)

if not id_grupo:
    # 2. Se não encontrar, cria o grupo
    print(f"Grupo '{NOME_DO_GRUPO}' não encontrado. Criando...")
    id_grupo = create_monday_group(board_id=BOARD_ID, group_name=NOME_DO_GRUPO)

if id_grupo:
    print(f"Trabalhando com o grupo ID: {id_grupo}")
    
    # 3. (Exemplo) Deleta o grupo
    # sucesso = delete_monday_group(board_id=BOARD_ID, group_id=id_grupo)
    # if sucesso:
    #     print("Grupo deletado com sucesso.")
```

### Exemplo 3: Importando Dados de um DataFrame em Lote

```python
import pandas as pd
from extracao_monday import create_items_in_batches, get_group_id

# Dados e configurações
BOARD_ID = 9382957552
NOME_DO_GRUPO = "Importação em Lote"
SUBSETOR = "projetos_ti"

# 1. DataFrame com os dados a serem importados
# A primeira coluna ('Atividade') será usada como o nome do item.
data = {
    'Atividade': ['Planejamento do Sprint 10', 'Reunião de Kick-off do Projeto Phoenix'],
    'Responsável': [61907099, 61907099], # Use IDs de usuário
    'Prazo': ['2025-09-15', '2025-09-18'],
    'Progresso': ['A fazer', 'A fazer']
}
df_para_importar = pd.DataFrame(data)

# 2. Mapeamento para colunas com nomes diferentes entre o DataFrame e o Monday
# A automação cuidará das colunas com nomes iguais (ex: 'Responsável', 'Prazo').
mapa_de_excecoes = {
    'Atividade': 'Nome', # DF 'Atividade' -> Monday 'Nome'
    'Progresso': 'Status'  # DF 'Progresso' -> Monday 'Status'
}

# 3. Garante que o grupo de destino existe
id_grupo_destino = get_group_id(board_id=BOARD_ID, group_name=NOME_DO_GRUPO)
if not id_grupo_destino:
    # Lide com o caso de o grupo não existir (crie-o, pare o script, etc.)
    raise Exception(f"Grupo de destino '{NOME_DO_GRUPO}' não encontrado.")

# 4. Chama a função de importação em lote
relatorio = create_items_in_batches(
    board_id=BOARD_ID,
    group_id=id_grupo_destino,
    df=df_para_importar,
    subsetor=SUBSETOR,
    column_map_override=mapa_de_excecoes,
    batch_size=200 # Tamanho do lote otimizado
)

print("\n--- Relatório Final da Importação ---")
print(f"Sucesso: {relatorio['success_count']}")
print(f"Falhas: {relatorio['failed_count']}")
print(f"IDs Criados: {relatorio['created_ids']}")
if relatorio['errors']:
    print(f"Erros: {relatorio['errors']}")
```
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
    git clone https://github.com/GustavoRSNery/lib_monday_api.git
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
Após a inicialização com `load_settings`, você pode usar as funções da biblioteca.

## Passo 1: Inicialize a Bilioteca no seu Script

No início do seu script Python, você deve chamar a função `load_settings` e passar o caminho para o seu arquivo `.env` antes de usar qualquer outra função da biblioteca.

```python
from monday_lib import load_settings

# Caminho para o seu arquivo de configuração
caminho_do_env = "C:/configuracoes/meu_projeto.env"

# Inicializa a biblioteca com as suas configurações
load_settings(caminho_do_env)

# A partir daqui, a biblioteca está pronta para ser usada.
from monday_lib import extrair_dados_monday
# ... codigo abaixo
```

### Exemplo 1: Extraindo Itens de um Quadro com Filtro de Data

```python
from monday_lib import extrair_dados_monday

# 1. Configuração
load_settings("caminho/para/seu/.env")

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
from monday_lib import load_settings, get_group_id, create_monday_group

load_settings("caminho/para/seu/.env")

board_id = 1234567890
nome_do_grupo = "Novas Demandas Q4 2025"

id_grupo = get_group_id(board_id=board_id, group_name=nome_do_grupo)
if not id_grupo:
    print(f"Grupo '{nome_do_grupo}' não encontrado. Criando...")
    id_grupo = create_monday_group(board_id=board_id, group_name=nome_do_grupo)

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
from monday_lib import load_settings, create_items_in_batches, get_group_id

load_settings("caminho/para/seu/.env")

# Dados e configurações
board_id = 1234567890
nome_do_grupo = "Importação em Lote"
subsetor = "projetos_ti"

# DataFrame com os dados a serem importados
data = {
    'Atividade': ['Planejamento do Sprint 10', 'Reunião de Kick-off'],
    'Responsável': [12345678, 12345678],
    'Prazo': ['2025-09-15', '2025-09-18'],
    'Progresso': ['A fazer', 'A fazer']
}
df_para_importar = pd.DataFrame(data)

# Mapeamento para colunas com nomes diferentes
mapa_de_excecoes = {
    'Atividade': 'Nome',
    'Progresso': 'Status'
}

id_grupo_destino = get_group_id(board_id=board_id, group_name=nome_do_grupo)
if not id_grupo_destino:
    raise Exception(f"Grupo de destino '{nome_do_grupo}' não encontrado.")

relatorio = create_items_in_batches(
    board_id=board_id,
    group_id=id_grupo_destino,
    df=df_para_importar,
    subsetor=subsetor,
    column_map_override=mapa_de_excecoes,
    batch_size=75
)

print("\n--- Relatório Final da Importação ---")
print(f"Sucesso: {relatorio['success_count']}")
print(f"Falhas: {relatorio['failed_count']}")
```
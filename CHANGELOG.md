# Changelog

Todo o histórico de mudanças notáveis neste projeto será documentado neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.2] - 2025-09-09

Versão focada na refatoração completa do sistema de configurações para tornar a biblioteca portátil, segura e fácil de ser utilizada por outros projetos.

### Added
- **Gerenciamento de Configurações com Pydantic:** Introduzido um módulo `core/settings.py` que utiliza Pydantic para carregar, validar e gerenciar todas as configurações da aplicação.
- **Inicialização Explícita:** Adicionada a função pública `load_settings(env_path)`, que torna obrigatória a inicialização da biblioteca pelo usuário, garantindo que a configuração seja fornecida de forma explícita e controlada.
- **Caminhos de Arquivo Seguros e Dinâmicos:** Implementada a biblioteca `appdirs` para criar as pastas de `logs` e `persist` em diretórios de dados padrão do usuário (ex: `AppData` no Windows, `~/.local/share` no Linux), resolvendo problemas de permissão e tornando a biblioteca compatível com qualquer sistema operacional.
- **Exceção de Configuração:** Criada a exceção customizada `ConfigurationError` para fornecer feedback claro ao usuário caso a biblioteca seja utilizada sem a devida inicialização.

### Changed
- **Desacoplamento da Configuração:** Todo o código da biblioteca foi refatorado para obter suas configurações através da função `get_settings()`, eliminando completamente o uso de `os.getenv` e a dependência de um arquivo `.env` com caminho fixo.
- **Simplificação do `.env`:** O arquivo `.env` esperado pelo usuário agora só precisa conter segredos (`MONDAY_API_TOKEN`) e configurações específicas do ambiente (`PEM_PATH`), pois os caminhos de dados são gerenciados pela biblioteca.

### Fixed
- **Problema de Portabilidade:** Corrigido o problema fundamental que impedia a biblioteca de ser instalada e utilizada em outras máquinas, removendo todos os caminhos de arquivo fixos (hardcoded) do código-fonte e da configuração padrão.


## [0.2.1] - 2025-09-04

Versão focada em adicionar funcionalidades de importação de dados, otimização de performance e no tratamento de erros.

### Added
- **Criação de Itens em Lote:** Implementada a função `create_items_in_batches` que constrói e envia queries GraphQL dinâmicas para criar múltiplos itens em uma única chamada à API, aumentando drasticamente a performance de importação.
- **Gerenciamento de Grupos:** Adicionadas funções de serviço para `create_monday_group` (criar), `delete_monday_group` (deletar) e `get_group_id` (buscar ID por nome).
- **Logging Profissional:** Configurado o módulo `logging` do Python para exibir logs de progresso (`INFO`) no console e salvar logs de erro (`ERROR`) detalhados em formato JSON no arquivo `logs/api_errors.log`.
- **Decorador de Erros:** Criado o decorador `@log_api_errors` para padronizar o tratamento de exceções em funções de serviço, mantendo o código mais limpo (DRY).
- **Retentativas de API:** A função `call_monday_api` foi aprimorada com uma lógica de retentativa (retry) com backoff exponencial para lidar automaticamente com erros de rede transitórios como `504 Gateway Timeout`.
- **Verificação Pós-Timeout:** Implementada uma rotina de verificação que, após um erro 504, consulta a API para confirmar quantos itens foram de fato criados, garantindo a integridade do relatório final.
- **Formatadores de Coluna Avançados:** O sistema de formatadores foi expandido para lidar com tipos de dados complexos, como strings de data com horário e durações formatadas (ex: "1h 30m").

### Changed
- **Otimização de Limites da API:** A lógica de importação em lote agora inclui uma pausa dinâmica de 60 segundos entre os lotes, calculada a partir do tempo de resposta da chamada anterior, para gerenciar o orçamento de complexidade da API de forma eficiente.

### Fixed
- Corrigido o erro `maxComplexityExceeded` através do cálculo de um `batch_size` seguro com base no custo real de complexidade medido.
- Resolvido o erro `504 Gateway Timeout` ajustando o `batch_size` para garantir que as requisições sejam concluídas em menos de 60 segundos.
- Corrigidos múltiplos erros de validação de dados (`ColumnValueException`) para colunas de Status, Cor e Data, através de formatadores de dados mais inteligentes.

## [0.2.0] - 2025-08-29

Grande refatoração arquitetural, transformando o projeto de scripts para um pacote Python instalável e robusto.

### Added
- **`setup.py`:** O projeto agora é um pacote instalável.
- **`README.md`:** Documentação inicial do projeto.
- **Cliente de API Central (`call_monday_api`):** Toda a lógica de comunicação com a API foi centralizada em uma única função.
- **Carregador de Queries (`queries.py`):** Sistema para carregar dinamicamente queries de arquivos `.gql` externos.
- **`ColunaIDMapper`:** Classe para mapear nomes de colunas para metadados da API, com um sistema de cache em arquivo (`.pkl`) para performance.

### Changed
- **Arquitetura `src-layout`:** Todo o código-fonte foi movido para uma estrutura `src/extracao_monday`, seguindo as melhores práticas para pacotes Python.
- **Queries com Variáveis:** Todas as queries foram refatoradas para usar variáveis GraphQL, eliminando a injeção de strings com `.format()` e aumentando a segurança.
- **Mapeamento de Colunas:** O `ColunaIDMapper` foi aprimorado para buscar metadados diretamente do quadro, resolvendo o problema de mapeamento em quadros vazios.

### Fixed
- **Paginação com Filtros:** Corrigido o bug onde filtros de data eram perdidos nas páginas 2 em diante.
- **Erros de Importação:** Resolvidos todos os erros de `ImportError` e `ModuleNotFoundError` decorrentes da nova arquitetura de pacotes.
- **Erros de Tipo do GraphQL:** Corrigidos os tipos de variáveis nas queries (`ItemsPageByColumnValuesRule` vs `ItemsQueryRule`).

## [0.1.3] - [Data Aprox. 27/08/2025]
### Changed
- Melhorado o tratamento inicial de erros para inspecionar a chave `errors` na resposta da API, em vez de depender apenas do status HTTP.

## [0.1.2] - [Data Aprox. 26/08/2025]
### Changed
- Adicionada a capacidade de desativar o filtro de data na função de extração principal.

## [0.1.1] - [Data Aprox. 25/08/2025]
### Added
- Versão inicial do script, com a funcionalidade básica de extrair itens de um quadro do Monday com filtro de data, usando `.format()` para montar a query.
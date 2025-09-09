import logging
from pydantic import SecretStr, FilePath, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
from appdirs import user_data_dir

APP_NAME = "extracao_monday"

class ConfigurationError(Exception):
    """Erro lançado quando a biblioteca é usada sem ser configurada."""
    pass


class Settings(BaseSettings):
    """
    Classe de configuração central que carrega variáveis de ambiente de um arquivo .env.
    """
    # --- Variáveis lidas do .env (permanecem as mesmas) ---
    MONDAY_API_TOKEN: SecretStr
    MONDAY_API_URL: HttpUrl = "https://api.monday.com/v2"
    PEM_PATH: Optional[FilePath] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

    @property
    def PERSIST_PATH(self) -> Path:
        """
        Retorna o caminho para a pasta 'persist' na raiz do projeto.
        """
        # Cria o caminho: /raiz_do_projeto/persist
        path = Path(user_data_dir(appname=APP_NAME, appauthor=False)) / "persist"
        path.mkdir(parents=True, exist_ok=True)
        return path
    @property
    def LOGS_PATH(self) -> Path:
        """
        Retorna o caminho para a pasta 'logs' na raiz do projeto.
        """
        # Cria o caminho: /raiz_do_projeto/logs
        path = Path(user_data_dir(appname=APP_NAME, appauthor=False)) / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
_settings_instance: Optional[Settings] = None

def load_settings(env_path: str):
    """
    Inicializa as configurações globais da biblioteca a partir de um arquivo .env específico.
    Esta função DEVE ser chamada pelo usuário no início de seu script.
    """
    global _settings_instance
    if _settings_instance is not None:
        logging.warning("As configurações já foram carregadas. Ignorando chamada duplicada.")
        return

    try:
        # Pydantic carrega e valida as configurações do arquivo .env especificado
        config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8", extra='ignore')
        _settings_instance = Settings.model_validate({}, _env_file=env_path)

        # Garante que os diretórios existam após o carregamento
        _settings_instance.LOGS_PATH.mkdir(parents=True, exist_ok=True)
        _settings_instance.PERSIST_PATH.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Configurações da biblioteca 'extracao_monday' carregadas com sucesso de: {env_path}")
    except Exception as e:
        raise ConfigurationError(f"Falha ao carregar as configurações de '{env_path}'. Erro: {e}") from e

def get_settings() -> Settings:
    """
    Retorna a instância de configurações. Falha se a inicialização não tiver sido feita.
    Esta é a função que o resto da sua biblioteca usará.
    """
    if _settings_instance is None:
        raise ConfigurationError(
            "As configurações não foram inicializadas. "
            "Chame a função 'load_settings(caminho_do_env)' no início do seu script."
        )
    return _settings_instance
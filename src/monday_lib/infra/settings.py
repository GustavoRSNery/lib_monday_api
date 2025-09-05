from pydantic import SecretStr, FilePath, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
from appdirs import user_data_dir
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Define o nome da nossa aplicação para ser usado na criação de pastas
APP_NAME = "extracao_monday"

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
        path = PROJECT_ROOT / "persist"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def LOGS_PATH(self) -> Path:
        """
        Retorna o caminho para a pasta 'logs' na raiz do projeto.
        """
        # Cria o caminho: /raiz_do_projeto/logs
        path = PROJECT_ROOT / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
settings = Settings()
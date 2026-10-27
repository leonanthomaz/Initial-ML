# app/core/config/settings.py
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Carrega variáveis de ambiente
load_dotenv(dotenv_path=".env", encoding="utf-8")


class Configuration:
    """Configuração centralizada - Singleton"""
    
    _instance: Optional['Configuration'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evita reinicialização
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._setup_logging()
        self._load_environment_variables()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"✅ Configuration inicializada - Ambiente: {self.environment}")
    
    def _setup_logging(self):
        """Configura logging básico"""
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"app_{datetime.now():%Y%m%d}.log"
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.handlers.clear()
        root.addHandler(console_handler)
        root.addHandler(file_handler)
    
    def _load_environment_variables(self):
        """Carrega variáveis de ambiente"""
        # Ambiente
        self.environment = os.getenv("APP_ENVIRONMENT", "development").upper()
        
        # Configurações do Groq
        self.groq_url = os.getenv("GROQ_URL")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL")
        
        # Configurações do Banco de Dados
        self.db_type = os.getenv("DB_TYPE", "sqlite")
        self.db_populate = os.getenv("DB_POPULATE", "true").lower() == "true"
        self.db_path = os.getenv("DB_PATH", "assistente.db")
        
        # PostgreSQL (para produção)
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "assistente")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "")
    
    def get_database_url(self) -> str:
        """Retorna a URL de conexão com o banco de dados"""
        if self.environment == "PRODUCAO" or self.db_type.lower() == "postgresql":
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            # SQLite para desenvolvimento
            db_path = Path(self.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"

_config: Optional[Configuration] = None

def get_config() -> Configuration:
    """Obtém a instância única do Configuration"""
    global _config
    if _config is None:
        _config = Configuration()
    return _config
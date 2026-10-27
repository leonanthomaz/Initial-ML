# app/shared/database/connection.py
import logging
from contextlib import contextmanager
from typing import Generator
from sqlmodel import create_engine, SQLModel, Session
from app.core.config.settings import Configuration

# Configuração global já carregada
configuration = Configuration()

# Variável global para armazenar o engine
_engine = None

def get_engine():
    """Retorna o engine do banco de dados (singleton)"""
    global _engine
    
    if _engine is None:
        try:
            db_url = configuration.get_database_url()
            
            # Configurações específicas para SQLite
            connect_args = {}
            if "sqlite" in db_url:
                connect_args = {"check_same_thread": False}
            
            # Criação do engine para a conexão com o banco de dados
            _engine = create_engine(
                db_url, 
                echo=False,
                connect_args=connect_args
            )
            
            # Importa os modelos para garantir que as tabelas sejam criadas
            from app.modules.assistente.models.database_models import Master, User, Assistant
            
            # Criando as tabelas no banco de dados (caso não existam)
            SQLModel.metadata.create_all(bind=_engine)
            
            logging.info(f"Engine criado com sucesso para: {configuration.environment}")
            logging.info(f"Banco de dados: {db_url}")
            
        except Exception as e:
            logging.error(f"Erro ao criar engine do banco de dados: {e}")
            raise
    
    return _engine

def get_session() -> Session:
    """Cria e retorna uma sessão para interação com o banco de dados."""
    try:
        engine = get_engine()
        session = Session(engine)
        return session
    except Exception as e:
        logging.error(f"Erro ao criar sessão do banco de dados: {e}")
        raise

@contextmanager
def session_scope():
    """Context manager para sessão do banco de dados"""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def init_database():
    """Inicializa o banco de dados"""
    try:
        get_engine()
        logging.info("Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        logging.error(f"Erro ao inicializar banco de dados: {e}")
        return False
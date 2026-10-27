# app/shared/database/__init__.py
import logging
from app.shared.database.connection import get_engine, get_session, session_scope, init_database
from app.shared.database.populate import populate_database
from app.core.config.settings import Configuration

config = Configuration()

def init_db():
    """Inicializa o banco de dados e popula com dados iniciais se configurado."""
    try:
        # Inicializa o banco
        if init_database():
            # Popula com dados iniciais (controlado por flag DB_POPULATE)
            populate_database()
            return True
        return False
    except Exception as e:
        logging.error(f"Erro ao inicializar banco de dados: {e}")
        return False
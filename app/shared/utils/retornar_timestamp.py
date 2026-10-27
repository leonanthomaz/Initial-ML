from datetime import datetime

def get_current_timestamp() -> str:
    """Retorna timestamp atual formatado"""
    return datetime.now().isoformat()
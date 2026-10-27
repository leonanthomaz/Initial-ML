from fastapi import Header, status
from typing import Optional

from app.core.config.settings import Configuration
from app.core.exceptions.auth_exception import AuthException

config = Configuration()

def validate_internal_api_key(
    x_application_key: Optional[str] = Header(None)
):
    if not x_application_key:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="[ERRO DE AUTORIZAÇÃO - CÓDIGO 401] - Não autorizado.",
            
        )

    if x_application_key != config.x_application_key:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="[ERRO DE AUTORIZAÇÃO - CÓDIGO 401] - Não autorizado.",
        )

    return True
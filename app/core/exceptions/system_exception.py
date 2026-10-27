# src/modules/firebird/exceptions/faturas_exception.py
from fastapi import HTTPException, status
from typing import Any, Optional
from datetime import datetime

class SystemException(HTTPException):
    """
    Exceção base para erros do sistema
    Estrutura padronizada para respostas de erro
    """
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "[ERRO SISTEMA - CÓDIGO 500] - Erro interno no servidor",
        details: Optional[Any] = None
    ):
        # Corpo da exceção estruturado
        error_response = {
            "status": status_code,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Adiciona details se existir
        if details is not None:
            error_response["details"] = details
        
        super().__init__(
            status_code=status_code,
            detail=error_response
        )
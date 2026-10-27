# app/shared/utils/password_utils.py
import bcrypt
import logging
from typing import Tuple


class PasswordUtils:
    """Utilitário para gerenciamento de senhas com bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash de uma senha usando bcrypt
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha como string
        """
        try:
            # Gera salt e hash
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logging.error(f"Erro ao gerar hash da senha: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash
        
        Args:
            password: Senha em texto plano
            password_hash: Hash da senha armazenado
            
        Returns:
            True se a senha corresponde ao hash, False caso contrário
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logging.error(f"Erro ao verificar senha: {e}")
            return False
    
    @staticmethod
    def generate_password_hash(password: str) -> Tuple[str, str]:
        """
        Gera hash e retorna também a senha original (útil para testes)
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Tupla (hash, senha_original)
        """
        hash_password = PasswordUtils.hash_password(password)
        return hash_password, password


# Funções de conveniência para uso direto
def hash_password(password: str) -> str:
    """Função de conveniência para gerar hash"""
    return PasswordUtils.hash_password(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Função de conveniência para verificar senha"""
    return PasswordUtils.verify_password(password, password_hash)
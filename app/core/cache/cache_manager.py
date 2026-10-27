# src/cache/cache_manager.py

import logging
from typing import Optional

from app.core.cache.cache import Cache

cache = Cache()

class CacheManager:
    _cache_key_prefix = "fedcorp-pay_"
    
    def __init__(self):
        self.cache = cache

    def get_cache_key(self, key: str) -> str:
        """Gera a chave de cache completa com o prefixo"""
        return f"{self._cache_key_prefix}{key}"

    async def load_cached_data(self, key: str) -> Optional[dict]:
        """Carrega dados do cache"""
        cache_key = self.get_cache_key(key)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logging.info(f"Dados encontrados no cache para a chave: {cache_key}")
        return cached_data

    async def cache_data(self, key: str, data: dict) -> None:
        """Armazena dados no cache"""
        cache_key = self.get_cache_key(key)
        self.cache.set(cache_key, data, ttl=900)
        logging.info(f"Dados armazenados no cache com a chave: {cache_key}")

    
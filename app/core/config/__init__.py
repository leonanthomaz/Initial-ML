# # app/core/config/__init__.py

# # Singleton global

# from app.core.config.settings import Configuration


# _config = None

# def get_config() -> Configuration:
#     """Obtém instância singleton do Configuration"""
#     global _config
#     if _config is None:
#         _config = Configuration()
#     return _config
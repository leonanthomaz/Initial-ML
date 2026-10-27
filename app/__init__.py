# app/__init__.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config.settings import Configuration
from app.modules import register_routes
# from app.shared.database import init_db

# Chama configuração
configuration = Configuration()

def create_app():
    logging.info("SISTEMA >>> Inicializando...")
    logging.info(f"AMBIENTE >>> {configuration.environment.upper()}")

    app = FastAPI(
        title="Analysis API",
        version="1.0.0",
        redirect_slashes=False,
        docs_url="/api/analysis/docs" if configuration.environment == "production" else "/docs",
        openapi_url="/api/analysis/openapi.json" if configuration.environment == "production" else "/openapi.json",
    )
    logging.info("SISTEMA >>> Inicializando o banco de dados...")
    # init_db()
    logging.info("SISTEMA >>> Banco de dados carregado.")
    
    origins = (
        [
            "http://127.0.0.1:8000",
        ]
        if configuration.environment == "production"
        else [
            "http://127.0.0.1:8000", 
        ]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Filename"],
    )

    register_routes(app)
    return app

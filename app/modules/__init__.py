# src/modules/__init__.py

# Controllers
from app.modules.analysis.controllers.analysis_controller import AnalysisController
from app.modules.analysis.controllers.chat_controlller import ChatController
from app.modules.analysis.controllers.ml_controller import MLController

def register_routes(app):
    # Rotas
    app.include_router(AnalysisController(), prefix="/api/analysis", tags=["Rota Análise"])
    app.include_router(ChatController(), prefix="/api/analysis", tags=["Rota Chat"])
    app.include_router(MLController(), prefix="/api/analysis", tags=["Rota ML"])
 
  

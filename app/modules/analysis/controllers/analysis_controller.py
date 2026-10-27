# app/modules/analysis/controller/analysis_controller.py

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import httpx
from app.core.config.settings import Configuration
from app.modules.analysis.services.stock_service import StockService
from app.shared.utils.retornar_timestamp import get_current_timestamp

class AnalysisController(APIRouter):
    """Controller para operações com Análise"""
    
    def __init__(self):
        super().__init__()
        self.config = Configuration()
        self.logger = logging.getLogger(__name__)
        
        self.service = StockService()

        self.add_api_route("/stock/{ticker}", self.get_stock, methods=["GET"])
        self.add_api_route("/stock/{ticker}/summary", self.get_summary, methods=["GET"])

        # Health check
        self.add_api_route(
            path="/health",
            endpoint=self.health_check,
            methods=["GET"],
            summary="Health check"
        )
    
    # ============ HEALTH ============
    def health_check(self) -> Dict[str, str]:
        return {
            "status": "ONLINE",
            "service": "API ANÁLISE",
            "timestamp": get_current_timestamp()
        }
        
    async def get_stock(self, ticker: str, period: str = "6mo", interval: str = "1d") -> dict:
        try:
            df = self.service.get_history(ticker, period, interval)
            return {
                "success": True,
                "ticker": ticker.upper(),
                "data": df.reset_index().to_dict(orient="records"),
                "timestamp": get_current_timestamp(),
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_summary(self, ticker: str) -> dict:
        try:
            return {"success": True, **self.service.get_summary(ticker),
                    "timestamp": get_current_timestamp()}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    
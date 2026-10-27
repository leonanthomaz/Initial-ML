# app/modules/analysis/controllers/ml_controller.py
import logging
from typing import Dict
from fastapi import APIRouter, HTTPException

from app.modules.analysis.services.stock_service import StockService
from app.modules.analysis.ml.features import build_features, build_inference_features
from app.modules.analysis.ml import trainer
from app.shared.utils.retornar_timestamp import get_current_timestamp


class MLController(APIRouter):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.stock = StockService()

        self.add_api_route("/ml/train/{ticker}",   self.train,   methods=["POST"])
        self.add_api_route("/ml/predict/{ticker}", self.predict, methods=["GET"])

    async def train(self, ticker: str) -> Dict:
        try:
            df = self.stock.get_history(ticker, period="5y")
            feats = build_features(df)
            if len(feats) < 100:
                raise ValueError(f"Poucos dados ({len(feats)} amostras).")
            result = trainer.train(feats, ticker)
            return {
                "success": True,
                "ticker": ticker.upper(),
                **result,
                "timestamp": get_current_timestamp(),
            }
        except Exception as e:
            self.logger.exception("Erro no treino")
            raise HTTPException(status_code=400, detail=str(e))

    async def predict(self, ticker: str) -> Dict:
        try:
            bundle = trainer.load(ticker)
            df = self.stock.get_history(ticker, period="6mo")
            feats = build_inference_features(df)

            if feats.empty:
                raise ValueError("Sem features válidas para predição.")

            candle_date = feats.index[-1]                 # o dia que embasa a predição
            X_last = feats.tail(1)[bundle["features"]]    # garante ordem das colunas

            proba = bundle["model"].predict_proba(X_last)[0]
            pred = int(bundle["model"].predict(X_last)[0])

            return {
                "success": True,
                "ticker": ticker.upper(),
                "prediction": "UP" if pred == 1 else "DOWN",
                "confidence": round(float(max(proba)), 4),
                "probabilities": {
                    "DOWN": round(float(proba[0]), 4),
                    "UP":   round(float(proba[1]), 4),
                },
                "based_on_candle": str(candle_date.date()),
                "timestamp": get_current_timestamp(),
            }
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            self.logger.exception("Erro na predição")
            raise HTTPException(status_code=400, detail=str(e))
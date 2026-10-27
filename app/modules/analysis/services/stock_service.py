# app/modules/analysis/services/stock_service.py
import logging
from typing import List
import yfinance as yf
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class StockService:
    """Serviço responsável por buscar e processar dados de ações via yfinance."""

    def get_history(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Retorna o histórico OHLCV de um ticker."""
        try:
            df = yf.Ticker(ticker).history(period=period, interval=interval)
            if df.empty:
                raise ValueError(f"Sem dados para {ticker}")
            df.index = df.index.tz_localize(None)  # remove timezone
            logger.info(f"{ticker}: {len(df)} candles carregados")
            return df
        except Exception as e:
            logger.error(f"Erro ao buscar {ticker}: {e}")
            raise

    def get_summary(self, ticker: str) -> dict:
        """Resumo estatístico simples: preço atual, variação, volatilidade."""
        df = self.get_history(ticker, period="1mo")
        close = df["Close"]
        return {
            "ticker": ticker.upper(),
            "last_price": round(float(close.iloc[-1]), 2),
            "month_return_pct": round(float((close.iloc[-1] / close.iloc[0] - 1) * 100), 2),
            "volatility_pct": round(float(close.pct_change().std() * 100), 2),
            "high_1m": round(float(close.max()), 2),
            "low_1m": round(float(close.min()), 2),
            "candles": len(df),
        }
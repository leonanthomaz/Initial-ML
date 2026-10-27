# app/modules/analysis/ml/features.py
import pandas as pd

# Lista única de features — evita divergência entre treino e predição.
FEATURE_COLS = [
    "return_1d",
    "return_5d",
    "ma_5",
    "ma_20",
    "volatility",
    "volume_norm",
]


def _base_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria as features a partir do OHLCV.
    NÃO cria target nem remove NaN — só as colunas de entrada do modelo.
    """
    out = pd.DataFrame(index=df.index)
    out["return_1d"]   = df["Close"].pct_change()              # variação % vs ontem
    out["return_5d"]   = df["Close"].pct_change(5)             # variação % vs 5 dias atrás
    out["ma_5"]        = df["Close"].rolling(5).mean() / df["Close"] - 1   # distância da média de 5d
    out["ma_20"]       = df["Close"].rolling(20).mean() / df["Close"] - 1  # distância da média de 20d
    out["volatility"]  = df["Close"].pct_change().rolling(10).std()        # volatilidade 10d
    out["volume_norm"] = df["Volume"] / df["Volume"].rolling(20).mean()    # volume vs média 20d
    return out


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    TREINO: features + target (sobe amanhã?).
    Remove linhas com NaN — inclusive o último dia, que não tem target.
    """
    out = _base_features(df)
    out["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    return out.dropna()


def build_inference_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    PREDIÇÃO: só features.
    O último candle SOBREVIVE — é ele que queremos prever.
    """
    return _base_features(df).dropna()
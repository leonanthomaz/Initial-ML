# app/modules/analysis/ml/trainer.py
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODEL_DIR = Path("data/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train(df_features, ticker: str) -> dict:
    X = df_features.drop(columns=["target"])
    y = df_features["target"]

    # shuffle=False: ESSENCIAL em séries temporais.
    # Senão o modelo "vê o futuro" no treino e mente no teste.
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=42,
        n_jobs=-1,
    )
    
    # model = LogisticRegression(max_iter=1000, random_state=42)
    
    model.fit(X_tr, y_tr)

    # Baseline honesto: "sempre UP" (ou sempre o mais frequente)
    y_pred = model.predict(X_te)
    acc = accuracy_score(y_te, y_pred)
    baseline = max(y_te.mean(), 1 - y_te.mean())

    path = MODEL_DIR / f"{ticker.upper()}.pkl"
    joblib.dump({"model": model, "features": list(X.columns)}, path)

    return {
        "accuracy":     round(float(acc), 4),
        "baseline":     round(float(baseline), 4),   # "sempre UP/DOWN"
        "edge":         round(float(acc - baseline), 4),  # ganho real do modelo
        "train_samples": int(len(X_tr)),
        "test_samples":  int(len(X_te)),
        "model_path":   str(path),
        "samples":      int(len(X)),
    }


def load(ticker: str):
    path = MODEL_DIR / f"{ticker.upper()}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Modelo {ticker} não treinado.")
    return joblib.load(path)
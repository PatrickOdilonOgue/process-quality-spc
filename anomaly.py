"""Isolation Forest als Ergänzung zu den Regeln: findet auffällige Gruppen anhand von Mittelwert und Spannweite."""
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def isolation_flags(stats: pd.DataFrame, contamination: float = 0.05, seed: int = 42) -> pd.Series:
    X = StandardScaler().fit_transform(stats[["mean", "range"]])
    pred = IsolationForest(contamination=contamination, random_state=seed).fit_predict(X)
    return pd.Series(pred == -1, index=stats.index, name="iforest_anomaly")

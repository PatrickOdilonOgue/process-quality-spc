"""Alarmregeln nach Nelson (Regeln 1–8) auf Mittellinie `cl` und Standardabweichung `sigma`."""
import numpy as np
import pandas as pd

DESCRIPTIONS = {
    1: "1 Punkt jenseits 3σ", 2: "9 Punkte auf einer Seite der Mittellinie", 3: "6 Punkte steigend oder fallend",
    4: "14 Punkte alternierend", 5: "2 von 3 Punkten jenseits 2σ (gleiche Seite)",
    6: "4 von 5 Punkten jenseits 1σ (gleiche Seite)", 7: "15 Punkte innerhalb 1σ", 8: "8 Punkte außerhalb 1σ",
}


def nelson(values, cl: float, sigma: float) -> pd.DataFrame:
    """Gibt je ausgelöstem Alarm die Position (0-basiert) und die Regelnummer zurück."""
    x = np.asarray(values, float)
    z = (x - cl) / sigma
    d = np.diff(x)
    hits = []
    for i in range(len(x)):
        if abs(z[i]) > 3: hits.append((i, 1))
        if i >= 8 and (np.all(z[i - 8:i + 1] > 0) or np.all(z[i - 8:i + 1] < 0)): hits.append((i, 2))
        if i >= 5 and (np.all(d[i - 5:i] > 0) or np.all(d[i - 5:i] < 0)): hits.append((i, 3))
        if i >= 13 and np.all(d[i - 13:i][1:] * d[i - 13:i][:-1] < 0): hits.append((i, 4))
        if i >= 2:
            w = z[i - 2:i + 1]
            if (z[i] > 2 and (w > 2).sum() >= 2) or (z[i] < -2 and (w < -2).sum() >= 2): hits.append((i, 5))
        if i >= 4:
            w = z[i - 4:i + 1]
            if (z[i] > 1 and (w > 1).sum() >= 4) or (z[i] < -1 and (w < -1).sum() >= 4): hits.append((i, 6))
        if i >= 14 and np.all(np.abs(z[i - 14:i + 1]) < 1): hits.append((i, 7))
        if i >= 7 and np.all(np.abs(z[i - 7:i + 1]) > 1): hits.append((i, 8))
    out = pd.DataFrame(hits, columns=["position", "rule"])
    out["description"] = out["rule"].map(DESCRIPTIONS)
    return out

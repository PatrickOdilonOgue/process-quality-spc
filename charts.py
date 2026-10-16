"""Regelkarten: X̄-R (Gruppen) und I-MR (Einzelwerte). Grenzen werden aus einer Referenzphase berechnet."""
import numpy as np
import pandas as pd

# Standardkonstanten für Gruppengröße n: d2, A2, D3, D4
CONST = {2: (1.128, 1.880, 0.0, 3.267), 3: (1.693, 1.023, 0.0, 2.574), 4: (2.059, 0.729, 0.0, 2.282),
         5: (2.326, 0.577, 0.0, 2.114), 6: (2.534, 0.483, 0.0, 2.004), 7: (2.704, 0.419, 0.076, 1.924),
         8: (2.847, 0.373, 0.136, 1.864), 9: (2.970, 0.337, 0.184, 1.816), 10: (3.078, 0.308, 0.223, 1.777)}


def subgroup_stats(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("subgroup")["value"]
    return pd.DataFrame({"mean": g.mean(), "range": g.max() - g.min(), "n": g.size()}).reset_index()


def xbar_r_limits(stats: pd.DataFrame, n: int, baseline: int = 20) -> dict:
    """Eingriffsgrenzen aus den ersten `baseline` Gruppen (Phase I), nicht aus der Spezifikation."""
    d2, a2, d3, d4 = CONST[n]
    ref = stats.iloc[:baseline]
    xbb, rbar = ref["mean"].mean(), ref["range"].mean()
    return {"xbar": (xbb - a2 * rbar, xbb, xbb + a2 * rbar), "r": (d3 * rbar, rbar, d4 * rbar),
            "sigma_xbar": a2 * rbar / 3, "sigma_within": rbar / d2}


def imr_limits(values) -> dict:
    """I-MR-Karte für Einzelwerte: Grenzen = Mittelwert ± 2,66 · MR̄, MR-Obergrenze = 3,267 · MR̄."""
    v = np.asarray(values, float)
    mr = np.abs(np.diff(v)); mrbar, m = mr.mean(), v.mean()
    return {"i": (m - 2.66 * mrbar, m, m + 2.66 * mrbar), "mr": (0.0, mrbar, 3.267 * mrbar), "sigma": mrbar / 1.128}

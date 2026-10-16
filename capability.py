"""Prozessfähigkeit: Cp/Cpk (innerhalb der Gruppen) und Pp/Ppk (Gesamtstreuung)."""
import numpy as np
from scipy.stats import norm

from .charts import CONST


def cp(lsl: float, usl: float, sigma: float) -> float:
    return (usl - lsl) / (6 * sigma)


def cpk(mean: float, sigma: float, lsl: float, usl: float) -> float:
    return min(usl - mean, mean - lsl) / (3 * sigma)


def capability(values, rbar: float, n: int, lsl: float, usl: float) -> dict:
    v = np.asarray(values, float)
    s_within, s_overall, m = rbar / CONST[n][0], v.std(ddof=1), v.mean()
    ppm = (norm.cdf(lsl, m, s_overall) + norm.sf(usl, m, s_overall)) * 1e6
    return {"mean": round(m, 4), "Cp": round(cp(lsl, usl, s_within), 2), "Cpk": round(cpk(m, s_within, lsl, usl), 2),
            "Pp": round(cp(lsl, usl, s_overall), 2), "Ppk": round(cpk(m, s_overall, lsl, usl), 2),
            "ppm_expected": round(ppm, 0)}

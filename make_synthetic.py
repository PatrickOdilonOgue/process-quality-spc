"""Erzeugt synthetische Produktionsdaten (Soll 10,00 mm) für drei Maschinen mit eingebauten Prozessstörungen.

Maschine A: stabil | Maschine B: schleichender Drift ab Gruppe 26 (z. B. Werkzeugverschleiß)
Maschine C: Mittelwertsprung ab Gruppe 21 und ein einzelner Ausreißer in Gruppe 33.
Die Daten sind frei erfunden (Seed 42).
"""
import numpy as np
import pandas as pd
from pathlib import Path

N_SUB, N = 40, 5          # Anzahl Stichprobengruppen, Gruppengröße
TARGET, SD = 10.00, 0.05


def generate(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for machine in "ABC":
        for g in range(1, N_SUB + 1):
            mu = TARGET
            if machine == "B" and g > 25:
                mu += 0.006 * (g - 25)
            if machine == "C" and g > 20:
                mu += 0.07
            vals = rng.normal(mu, SD, N)
            if machine == "C" and g == 33:
                vals[2] += 0.25
            ts = pd.Timestamp("2025-03-03 06:00") + pd.Timedelta(hours=g - 1)
            for k, v in enumerate(vals, 1):
                rows.append((machine, g, k, ts, round(float(v), 4)))
    return pd.DataFrame(rows, columns=["machine", "subgroup", "sample", "timestamp", "value"])


def main(out: str = "data/raw/measurements_synthetic.csv") -> None:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df = generate(); df.to_csv(out, index=False); print(f"{len(df)} Zeilen -> {out}")


if __name__ == "__main__":
    main()

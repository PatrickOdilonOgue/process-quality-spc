"""Pipeline: Rohdaten -> Regelkarten -> Prozessfähigkeit -> Alarme -> Bericht."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .anomaly import isolation_flags
from .capability import capability
from .charts import subgroup_stats, xbar_r_limits
from .rules import nelson


def md_table(df: pd.DataFrame) -> str:
    head = "| " + " | ".join(df.columns) + " |\n|" + "|".join("---" for _ in df.columns) + "|\n"
    return head + "\n".join("| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)) + "\n"


def plot_machine(machine, stats, lim, alarm_groups, r_alarm_groups, baseline, path):
    fig, (a, b) = plt.subplots(2, 1, figsize=(8, 5.2), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    x = stats["subgroup"]
    for ax, col, key in ((a, "mean", "xbar"), (b, "range", "r")):
        lo, cl, hi = lim[key]
        ax.axvspan(1, baseline, color="#DCEAE5", alpha=.5, lw=0)
        ax.plot(x, stats[col], marker="o", ms=3.5, lw=1, color="#0E6B5E")
        for v, ls in ((hi, "--"), (cl, "-"), (lo, "--")):
            ax.axhline(v, color="#B3261E" if ls == "--" else "#5D6D70", ls=ls, lw=.9)
    hit = stats["subgroup"].isin(alarm_groups); a.plot(x[hit], stats["mean"][hit], "o", ms=7, mfc="none", mec="#B3261E", mew=1.5)
    hit = stats["subgroup"].isin(r_alarm_groups); b.plot(x[hit], stats["range"][hit], "o", ms=7, mfc="none", mec="#B3261E", mew=1.5)
    a.set_title(f"Maschine {machine} – X̄-R-Karte (Grenzen aus Gruppen 1–{baseline}, grün hinterlegt)")
    a.set_ylabel("X̄ (mm)"); b.set_ylabel("R (mm)"); b.set_xlabel("Stichprobengruppe")
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def run(raw: str, out_dir: str = "reports", lsl: float = 9.80, usl: float = 10.20, n: int = 5, baseline: int = 20):
    df = pd.read_csv(raw, parse_dates=["timestamp"])
    out = Path(out_dir); (out / "figures").mkdir(parents=True, exist_ok=True)
    rows, all_alarms = [], []
    for m, d in df.groupby("machine"):
        stats = subgroup_stats(d)
        lim = xbar_r_limits(stats, n, baseline)
        al = nelson(stats["mean"], lim["xbar"][1], lim["sigma_xbar"])
        al["machine"] = m; al["subgroup"] = stats["subgroup"].iloc[al["position"]].values
        r_out = stats.loc[stats["range"] > lim["r"][2], "subgroup"].tolist()
        flags = isolation_flags(stats)
        cap = capability(d["value"], stats["range"].mean(), n, lsl, usl)
        plot_machine(m, stats, lim, al["subgroup"].unique(), r_out, baseline, out / "figures" / f"xbar_r_machine_{m}.png")
        rows.append({"Maschine": m, **{k: cap[k] for k in ("Cp", "Cpk", "Pp", "Ppk")},
                     "erwartete ppm außerhalb Spez.": int(cap["ppm_expected"]),
                     "erster Alarm (Gruppe)": int(al["subgroup"].min()) if len(al) else "–",
                     "Regeln ausgelöst": ", ".join(str(r) for r in sorted(al["rule"].unique())) or "–",
                     "R-Karte Alarme": len(r_out), "Isolation Forest": int(flags.sum())})
        all_alarms.append(al)
    summary = pd.DataFrame(rows)
    alarms = pd.concat(all_alarms, ignore_index=True)[["machine", "subgroup", "rule", "description"]]
    summary.to_csv(out / "spc_summary.csv", index=False); alarms.to_csv(out / "alarms.csv", index=False)
    (out / "quality_report.md").write_text(
        f"# Qualitätsbericht SPC\n\nSpezifikation: {lsl:.2f} – {usl:.2f} mm, Gruppengröße n = {n}, "
        f"Regelgrenzen aus den Gruppen 1–{baseline} (Phase I).\n\n{md_table(summary)}\n"
        f"Cp/Cpk nutzen die Streuung innerhalb der Gruppen, Pp/Ppk die Gesamtstreuung. "
        f"Ein großer Abstand zwischen beiden weist auf instabile Lage hin.\n", encoding="utf-8")
    return summary, alarms


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw/measurements_synthetic.csv")
    ap.add_argument("--lsl", type=float, default=9.80); ap.add_argument("--usl", type=float, default=10.20)
    a = ap.parse_args()
    s, al = run(a.raw, lsl=a.lsl, usl=a.usl)
    print(s.to_string(index=False)); print(); print(al.groupby(["machine", "rule"]).size().to_string())

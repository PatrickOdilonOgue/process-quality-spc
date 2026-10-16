import numpy as np
import pandas as pd
import pytest
from src.capability import capability, cp, cpk
from src.charts import imr_limits, subgroup_stats, xbar_r_limits
from src.make_synthetic import generate
from src.pipeline import run
from src.rules import nelson


def rules_at(values, cl=0.0, sigma=1.0):
    r = nelson(values, cl, sigma)
    return {(int(p), int(k)) for p, k in zip(r["position"], r["rule"])}


# --- Fähigkeitskennzahlen gegen von Hand gerechnete Beispiele --------------------
def test_cp_cpk_centered_process():
    assert cp(9.8, 10.2, 0.05) == pytest.approx(1.3333, abs=1e-4)
    assert cpk(10.0, 0.05, 9.8, 10.2) == pytest.approx(1.3333, abs=1e-4)


def test_cpk_off_center_process():
    assert cpk(10.05, 0.05, 9.8, 10.2) == pytest.approx(1.0, abs=1e-9)      # (10,2 - 10,05) / (3 · 0,05)


def test_capability_uses_within_and_overall_sigma():
    v = np.tile([9.95, 10.05], 10)
    c = capability(v, rbar=0.1, n=5, lsl=9.8, usl=10.2)
    assert c["Cp"] == pytest.approx((10.2 - 9.8) / (6 * 0.1 / 2.326), abs=0.01)
    assert c["Pp"] < c["Cp"] * 2


# --- Regelkartengrenzen --------------------------------------------------------------
def test_xbar_r_limits_with_textbook_constants():
    stats = pd.DataFrame({"subgroup": range(1, 21), "mean": [10.0] * 20, "range": [0.1] * 20, "n": [5] * 20})
    lim = xbar_r_limits(stats, n=5, baseline=20)
    assert lim["xbar"][2] == pytest.approx(10.0 + 0.577 * 0.1)
    assert lim["r"][2] == pytest.approx(2.114 * 0.1) and lim["r"][0] == 0.0


def test_imr_limits():
    lim = imr_limits([10.0, 10.2, 9.9, 10.1, 10.0])
    assert lim["i"][1] == pytest.approx(10.04)
    assert lim["i"][2] == pytest.approx(10.04 + 2.66 * 0.2)


# --- Nelson-Regeln ----------------------------------------------------------------------
def test_rule1_point_beyond_3_sigma():
    assert (3, 1) in rules_at([0, 0.2, -0.1, 3.5, 0])


def test_rule2_nine_points_one_side():
    assert (8, 2) in rules_at([0.1] * 9) and (7, 2) not in rules_at([0.1] * 9)


def test_rule3_six_points_trend():
    assert (5, 3) in rules_at([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
    assert (5, 3) not in rules_at([0.0, 0.1, 0.2, 0.3, 0.4, 0.3])


def test_rule4_fourteen_alternating():
    v = [0.1 if i % 2 else -0.1 for i in range(14)]
    assert (13, 4) in rules_at(v)


def test_rule5_two_of_three_beyond_2_sigma():
    assert (2, 5) in rules_at([2.5, 0.0, 2.4])


def test_rule6_four_of_five_beyond_1_sigma():
    assert (4, 6) in rules_at([1.2, 1.3, 0.0, 1.1, 1.4])


def test_rule7_fifteen_within_1_sigma():
    assert (14, 7) in rules_at([0.2, -0.3, 0.1] * 5)


def test_rule8_eight_outside_1_sigma():
    assert (7, 8) in rules_at([1.5, -1.5] * 4)


# --- Gesamtpipeline -------------------------------------------------------------------------
def test_pipeline_detects_built_in_disturbances(tmp_path):
    raw = tmp_path / "raw.csv"; generate().to_csv(raw, index=False)
    summary, alarms = run(str(raw), str(tmp_path / "rep"))
    s = summary.set_index("Maschine")
    assert s.loc["A", "Cpk"] > 1.33 > s.loc["C", "Cpk"]                       # A fähig, C nicht
    assert s.loc["C", "Ppk"] < s.loc["C", "Cpk"]                              # Lageverschiebung drückt Ppk
    c = alarms[(alarms.machine == "C") & (alarms.subgroup >= 21)].subgroup.min()
    assert c <= 23                                                              # Sprung ab Gruppe 21 schnell erkannt
    assert alarms[(alarms.machine == "B") & (alarms.subgroup >= 26)].subgroup.min() <= 36   # Drift erkannt

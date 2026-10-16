# Process Quality SPC

Statistische Prozesslenkung in Python: Regelkarten, Prozessfähigkeit und Alarmregeln auf Produktionsmesswerten.
*Maîtrise statistique des procédés en Python : cartes de contrôle, capabilité et règles d'alarme.*

> **Hinweis zu den Daten:** Der mitgelieferte Datensatz ist **synthetisch** (frei erfunden, Seed 42). Drei Maschinen
> mit bewusst eingebauten Störungen zeigen, ob die Methoden sie erkennen.

## Die Frage

Jedes Qualitätsmanagement stellt dieselbe Frage: **Läuft der Prozess noch, oder driftet er?** Ein Mittelwert
allein beantwortet sie nicht. Dieses Projekt beantwortet sie mit einer Karte und mit Kennzahlen.

## Was berechnet wird

- **X̄-R-Karte** für Stichprobengruppen. Die Eingriffsgrenzen werden aus einer Referenzphase (Gruppen 1–20) mit den
  Standardkonstanten A2, D3, D4 berechnet, **nicht** aus der Spezifikation abgeleitet. **I-MR-Grenzen** für Einzelwerte sind ebenfalls enthalten.
- **Prozessfähigkeit:** Cp/Cpk (Streuung innerhalb der Gruppen, R̄/d2) und Pp/Ppk (Gesamtstreuung) plus erwarteter ppm-Anteil außerhalb der Spezifikation.
- **Alarmregeln nach Nelson (1–8)** auf der X̄-Karte.
- **Isolation Forest** als Ergänzung: markiert auffällige Gruppen anhand von Mittelwert und Spannweite.

| Regel | Muster | Deutung |
|---|---|---|
| 1 | 1 Punkt jenseits 3σ | grober Ausreißer |
| 2 | 9 Punkte auf einer Seite der Mittellinie | Mittelwertverschiebung |
| 3 | 6 Punkte steigend oder fallend | Trend, z. B. Werkzeugverschleiß |
| 4 | 14 Punkte alternierend | zwei überlagerte Quellen |
| 5 | 2 von 3 Punkten jenseits 2σ | beginnende Instabilität |
| 6 | 4 von 5 Punkten jenseits 1σ | kleine Verschiebung |
| 7 | 15 Punkte innerhalb 1σ | zu geringe Streuung (Schichtung) |
| 8 | 8 Punkte außerhalb 1σ | Mischung zweier Prozesse |

## Ergebnisse (auf den synthetischen Daten)

Spezifikation 9,80–10,20 mm, Gruppengröße n = 5, 40 Gruppen je Maschine.

| Maschine | Eingebaute Störung | Cp | Cpk | Pp | Ppk | Erster Alarm nach Störungsbeginn |
|---|---|---:|---:|---:|---:|---|
| A | keine | 1,53 | 1,52 | 1,51 | 1,50 | – (ein einzelner Fehlalarm, Regel 1, Gruppe 28) |
| B | Drift ab Gruppe 26 | 1,29 | 1,17 | 1,15 | 1,04 | Gruppe 33 (Regeln 5 und 6) |
| C | Sprung ab Gruppe 21, Ausreißer in Gruppe 33 | 1,29 | 1,08 | 1,04 | 0,87 | Gruppe 22 (Regeln 1 und 5) |

Lesehilfe: Maschine A ist stabil und fähig (Cpk > 1,33). Bei B und C liegt Ppk deutlich unter Cpk, ein Zeichen für instabile Lage; C ist laut Cpk nicht fähig.
Der einzelne Alarm bei A ist ein typischer **Fehlalarm** der 3σ-Regel und gehört zur ehrlichen Auswertung dazu.

![Maschine B](reports/figures/xbar_r_machine_B.png)
![Maschine C](reports/figures/xbar_r_machine_C.png)

Weitere Ausgaben: `reports/quality_report.md`, `reports/spc_summary.csv` und `reports/alarms.csv` (zum Weiterverarbeiten in Tableau oder Power BI).

## Projektstruktur

```
process-quality-spc/
├── data/raw/measurements_synthetic.csv
├── src/                 # make_synthetic, charts, capability, rules, anomaly, pipeline
├── reports/             # Bericht, Kennzahlen, Alarme, Abbildungen
├── tests/test_spc.py    # 14 Tests (pytest)
└── requirements.txt
```

## Verwendung

```bash
git clone https://github.com/PatrickOdilonOgue/process-quality-spc.git
cd process-quality-spc
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m src.make_synthetic
python -m src.pipeline --lsl 9.80 --usl 10.20
python -m pytest -q
```

Eigene Daten: CSV mit den Spalten `machine, subgroup, sample, timestamp, value` verwenden.

## Warum die Tests zählen

`tests/test_spc.py` prüft die Kennzahlen gegen von Hand gerechnete Beispiele (z. B. Cp = Cpk = 1,333 bei zentriertem
Prozess mit σ = 0,05 und Spezifikation 9,8–10,2) und jede der acht Nelson-Regeln mit konstruierten Folgen. Bei einer Kennzahl,
auf der eine Freigabeentscheidung beruht, ist eine still falsche Formel schlimmer als gar keine.

## Technik

Python 3.11 · pandas · NumPy · SciPy · scikit-learn · Matplotlib · pytest

## Kontakt

Patrick Odilon Ogue, Data Analyst (IHK), Leipzig ·
[LinkedIn](https://www.linkedin.com/in/odilon-patrick-ogue/) · [GitHub](https://github.com/PatrickOdilonOgue)

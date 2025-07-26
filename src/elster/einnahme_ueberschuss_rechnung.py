import pandas as pd
from src.elster.umsatz_steuererklaerung import BRUTTO_TO_UST
from src.elster.utils import sum_of_category_abs, load_elster_schema, load_processed_transactions

df = load_processed_transactions()
results = load_elster_schema()


### Ausgaben
leistungen = results["EÜR"]["4 - 2. Betriebsausgaben"]["Betriebsausgaben"]
leistungen["Bezogene Leistungen"] = sum_of_category_abs(df, "Bezogene Leistungen")
leistungen_sum = sum(leistungen.values())


afa = results["EÜR"]["4 - 2. Betriebsausgaben"]["Absetzung für Abnutzung (AfA)"]
for category in afa.keys():
    afa[category] = sum_of_category_abs(df, category)
afa_sum = sum(afa.values())


sonstige = results["EÜR"]["4 - 2. Betriebsausgaben"][
    "Sonstige unbeschränkt abziehbare Betriebsausgaben"
]
for category in sonstige.keys():
    if category == "Gezahlte Vorsteuerbeträge":
        continue  # this is handled separately
    sonstige[category] = sum_of_category_abs(df, category)
sonstige["Gezahlte Vorsteuerbeträge"] = abs(
    (
        df[
            (df["Amount (EUR)"] > 0)
            & (df["Brutto / Netto"] == "Brutto")
            & (df["Country"] == "GER")
        ]["Amount (EUR)"]
        * BRUTTO_TO_UST
    ).sum()
)
sonstige_sum = sum(sonstige.values())


### Einnahmen
refunds = results["EÜR"]["3 - 1. Betriebseinnahmen"]["Sonstige Betriebseinnahmen"][
    "Sonstige Sach- Nutzungs- und Leistungsentnahmen"
]
refunds = sum_of_category_abs(df, "Sonstige Sach- Nutzungs- und Leistungsentnahmen")


### Bilanz
gewinn = refunds - (
    leistungen_sum + afa_sum + sonstige_sum
)  # (how do i count refunded VAT? e.g. from adobe)


### Transfers
privat_entnahme = sum_of_category_abs(df, "Privateentnahme")
privat_einlage = sum_of_category_abs(df, "Privateinlage")
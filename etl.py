import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from notion2pandas import Notion2PandasClient

load_dotenv()

UST_SATZ = 0.19
BRUTTO_TO_UST = UST_SATZ / (1 + UST_SATZ)

KV_BASISSATZ = 0.14
KV_BKK_ZUSATZ = 0.0299
KV_SATZ = KV_BASISSATZ + KV_BKK_ZUSATZ
PV_SATZ = 0.034

CUSTOM_N26_COLS = [
    "ELSTER Kategorie",
    "Brutto / Netto",
    "Country",
    "Reverse Charge Remark",
]

N26_COLS = [
    "Name",
    "Amount (EUR)",
]

PSD_COLS = [
    "Name Zahlungsbeteiligter",
    "Betrag",
]

CUSTOM_PSD_COLS = [
    "Count as Business",
    "Business Related",
    "ELSTER Kategorie",
    "Letztes Jahr verwendet"
]


def to_float(col: pd.Series) -> pd.Series:
    col = col.str.replace(r"\.", "", regex=True)  # remove thousand‐sep dots
    col = col.str.replace(",", ".", regex=False)  # comma → dot
    return col.astype(float)


def process_n26(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    df_out = df_out[N26_COLS + CUSTOM_N26_COLS]
    df_out = df.rename(columns={"Name": "Name Zahlungsbeteiligter"})
    # achtung,
    return df_out


def process_psd(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    df_out = df_out[PSD_COLS + CUSTOM_PSD_COLS]
    df_out["Betrag"] = to_float(df_out["Betrag"])
    df_out = df_out.rename(columns={"Betrag": "Amount (EUR)"})
    df_out = df_out[
        (df_out["Business Related"] == "business")
        & (df_out["Count as Business"] != "Personal")
    ]
    df_out = df_out.drop(columns=["Count as Business", "Business Related"])
    return df_out


def process_stripe(df: pd.DataFrame) -> pd.DataFrame: # TODO (only 2EUR so maybe not worth time)
    df_out = df.copy()
    df_out["Amount"] = to_float(df_out["Amount"])
    df_out["Fee"] = to_float(df_out["Fee"])
    df_out["Net"] = to_float(df_out["Net"])
    return df_out

     
    
 

# Get environment variables with validation
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_PSD = os.getenv("DB_PSD")
DB_N26 = os.getenv("DB_N26")
PARTIES = os.getenv("PARTIES")

# Validate that all required environment variables are set
if not all([NOTION_TOKEN, DB_PSD, DB_N26, PARTIES]):
    raise ValueError(
        "Missing required environment variables. Please check your .env file."
    )

# Type assertions to help the type checker understand these are non-None
assert NOTION_TOKEN is not None
assert DB_PSD is not None
assert DB_N26 is not None
assert PARTIES is not None

# Initialize Notion client
n2p = Notion2PandasClient(auth=NOTION_TOKEN)

# Load data from Notion databases
df_psd = n2p.from_notion_DB_to_dataframe(DB_PSD)
df_psd = process_psd(df_psd)
df_n26 = n2p.from_notion_DB_to_dataframe(DB_N26)
df_n26 = process_n26(df_n26)

df = pd.concat([df_psd, df_n26], ignore_index=True, axis=0)

df_parties = n2p.from_notion_DB_to_dataframe(PARTIES)

# - Alle werte 1zu1 übernommen, aber muss eigentlich noch auf netto/brutto/reverse charge anpassen


results = {
    "EÜR": {
        "3 - 1. Betriebseinnahmen": {
            "Umsatzsteuerlicher Kleinunternehmer": {
                "Betriebseinnahmen als umsatzsteuerlicher Kleinunternehmer": 0,
                "Betriebseinnahmen als umsatzsteuerlicher Kleinunternehmer: davon nicht steuerbare Umsätze sowie Umsätze nach § 19 Abs. 3 Satz 1 Nr. 1 und 2 UStG": 0,
                "Betriebseinnahmen als umsatzsteuerlicher Kleinunternehmer: davon steuerbar": 0,
            },
            "Umsatzsteuerliche Regelbesteuerung": {
                "Betriebseinnahmen, die umsatzsteuerfrei oder nicht umsatzsteuerbar sind": 0,
                "Umsatzsteuerpflichtige Betriebseinnahmen": 0,
                "Vereinnahmte Umsatzsteuer sowie Umsatzsteuer auf unentgeltliche Wertabgaben": 0,
            },
            "Sonstige Betriebseinnahmen": {
                "Vom Finanzamt erstattete und ggf. verrechnete Umsatzsteuer": 0,
                "Sonstige Sach- Nutzungs- und Leistungsentnahmen": 0,  # ADOBE here
            },
        },
        "4 - 2. Betriebsausgaben": {
            "Betriebsausgaben": {
                "Bezogene Leistungen": 0,
            },
            "Absetzung für Abnutzung (AfA)": {
                "Anlage AVEÜR": 0,
                "geringwertige Wirtschaftsgüter": 0,
            },
            "Sonstige unbeschränkt abziehbare Betriebsausgaben": {
                "Aufwendungen für Telekommunikation": 0,
                "Fortbildungskosten": 0,
                "Gebühren": 0,
                "Rechts- und Steuerberatung, Buchführung": 0,
                "Laufende EDV-Kosten": 0,
                "Arbeitsmittel": 0,
                "Werbekosten": 0,
                "Gezahlte Vorsteuerbeträge": 0,
                "An das Finanzamt gezahlte und ggf. verrechnete Umsatzsteuer": 0,
            },
        },
    },
    "USt": {
        "3 - B. Angaben zur Besteuerung der Kleinunternehmer (§ 19 Absatz 1 UStG)": 0,
        "9 - H. Leistungsempfänger als Steuerschuldner (§ 13b UStG)": 0,
    },
}


def sum_of_category_abs(df: pd.DataFrame, category: str) -> float:
    """
    Sums the absolute values of the 'Amount (EUR)' column for a given ELSTER category.
    """
    return abs(df[df["ELSTER Kategorie"].str.contains(category)]["Amount (EUR)"].sum())


### EÜR
#########################################################################################

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


### Einkommensteuer
#################################################################################################
ESt = {
    "Beiträge anderer Personen": {
        "Krankenversicherungen": 0,
        "Pflegeversicherungen": 0,
    },
    "Gewinn als Einzelunternehmer": 0
}

kv_und_pv = sum_of_category_abs(df[df["Letztes Jahr verwendet"] == "Nein"], "Krankenversicherungen")
ESt["Gewinn als Einzelunternehmer"] = gewinn
ESt["Beiträge anderer Personen"]["Krankenversicherungen"] = kv_und_pv * KV_SATZ / (KV_SATZ + PV_SATZ)
ESt["Beiträge anderer Personen"]["Pflegeversicherungen"] = kv_und_pv * PV_SATZ / (KV_SATZ + PV_SATZ)






### USt Erklärung
#################################################################################################
legit_rc = abs(
    df[(df["Country"].isin(["USA", "EU"])) & (df["Brutto / Netto"] == "Netto")]["Amount (EUR)"].sum()
)
double_rc = abs(
    df[(df["Country"].isin(["USA", "EU"])) & (df["Brutto / Netto"] == "Brutto")]["Amount (EUR)"].sum()
)
reverse_charge_soll = legit_rc + double_rc
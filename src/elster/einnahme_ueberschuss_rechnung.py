"""Calculation helpers for the Einnahmen-Überschuss-Rechnung."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

import pandas as pd

from src.elster.umsatz_steuererklaerung import BRUTTO_TO_UST
from src.elster.utils import sum_of_category_abs


def label_vat_paid_transactions(df):
    is_negative_brutto_in_germany = (
        (df["Amount (EUR)"] < 0)
        & (df["Brutto / Netto"] == "Brutto")
        & (df["Country"] == "GER")
    )
    vorsteuer_col = "Gezahlte Vorsteuerbeträge"
    df[vorsteuer_col] = False
    df.loc[is_negative_brutto_in_germany, vorsteuer_col] = True


def calculate_eur(df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate the EÜR section of the ELSTER schema.

    Parameters
    ----------
    df:
        Processed transactions.
    schema:
        Base ELSTER schema to be populated.

    Returns
    -------
    Tuple[Dict[str, Any], float, float, float]
        The updated schema, the calculated profit (``gewinn``), the value of
        ``privat_entnahme`` and ``privat_einlage``.
    """

    results = deepcopy(schema)
    label_vat_paid_transactions(df)

    # Initialize the EÜR section
    ausgaben = results["EÜR"]["4 - 2. Betriebsausgaben"]
    leistungen = ausgaben["Betriebsausgaben"]
    afa = ausgaben["Absetzung für Abnutzung (AfA)"]
    sonstige = ausgaben["Sonstige unbeschränkt abziehbare Betriebsausgaben"]

    # Ausgaben
    # TODO: fix hädlerbund (steuerberatung kosten), auch related zu dem brutto bug
    # TODO: handle business expenses for EDV from personal accounts (psd / advancia) properly
    # TODO: Gebühren N26 Zahlung fehlt hier (wahrscheinlich selber bug bezogen auf Brutto vorsteuer)
    for ausgaben_kategorie in ausgaben.keys():
        for subcategory in ausgaben[ausgaben_kategorie].keys():
            pointer = ausgaben[ausgaben_kategorie][subcategory]

            # TODO: fix bug: Afa gehört nicht zur gezahlte Vorsteuerbeträge
            if subcategory == "Gezahlte Vorsteuerbeträge":
                column = "ELSTER Kategorie"
                multiplier = BRUTTO_TO_UST
            pointer = sum_of_category_abs(df, category=subcategory)

    # Einnahmen
    einnahmen = results["EÜR"]["3 - 1. Betriebseinnahmen"]["Sonstige Betriebseinnahmen"]
    refund_key = "Sonstige Sach- Nutzungs- und Leistungsentnahmen"

    einnahmen[refund_key] = sum_of_category_abs(df, category=refund_key)

    # Bilanz
    bilanz = results["EÜR"]["Bilanz"]
    bilanz["Einnahmen"] = einnahmen[refund_key]
    bilanz["Ausgaben"] = round(
        sum(leistungen.values()) + sum(afa.values()) + sum(sonstige.values()), 2
    )
    bilanz["Gewinn"] = round(bilanz["Einnahmen"] - bilanz["Ausgaben"], 2)

    # Transfers
    bilanz["Privateentnahme"] = sum_of_category_abs(df, category="Privateentnahme")
    bilanz["Privateinlage"] = sum_of_category_abs(df, category="Privateinlage")
    return results

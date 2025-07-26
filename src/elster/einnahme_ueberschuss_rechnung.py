"""Calculation helpers for the Einnahmen-Überschuss-Rechnung."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple

import pandas as pd

from src.elster.umsatz_steuererklaerung import BRUTTO_TO_UST
from src.elster.utils import sum_of_category_abs


def label_vat_paid_transactions(df):
    is_negative_brutto_in_germany = (
        (df["Amount (EUR)"] < 0)
        & (df["Brutto / Netto"] == "Brutto")
        & (df["Country"] == "GER")
    )
    df.loc[is_negative_brutto_in_germany, "ELSTER Kategorie"] = (
        "Gezahlte Vorsteuerbeträge"
    )


def calculate_eur(
    df: pd.DataFrame, schema: Dict[str, Any]
) -> Tuple[Dict[str, Any], float, float, float]:
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
    for ausgaben_kategorie in ausgaben.keys():
        for subcategory in ausgaben[ausgaben_kategorie].keys():
            multiplier = (
                BRUTTO_TO_UST if subcategory == "Gezahlte Vorsteuerbeträge" else 1
            )
            ausgaben[ausgaben_kategorie][subcategory] = (
                multiplier
                * sum_of_category_abs(df, ausgaben[ausgaben_kategorie][subcategory])
            )

    # Einnahmen
    einnahmen = results["EÜR"]["3 - 1. Betriebseinnahmen"]
    refunds = einnahmen["Sonstige Sach- Nutzungs- und Leistungsentnahmen"]
    refunds = sum_of_category_abs(df, "Sonstige Sach- Nutzungs- und Leistungsentnahmen")


    # Bilanz
    gewinn = refunds - (
        sum(leistungen.values()) + sum(afa.values()) + sum(sonstige.values())
    )

    # Transfers
    privat_entnahme = sum_of_category_abs(df, "Privateentnahme")
    privat_einlage = sum_of_category_abs(df, "Privateinlage")

    return results, gewinn, privat_entnahme, privat_einlage

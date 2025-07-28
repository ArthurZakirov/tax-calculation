"""Calculation helpers for the Einnahmen-Überschuss-Rechnung."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

import pandas as pd

from src.elster.utils import sum_of_category_abs
from src.tax.tax import TaxAlias


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

    # Initialize the EÜR section
    ausgaben = results["EÜR"]["4 - 2. Betriebsausgaben"]
    leistungen = ausgaben["Betriebsausgaben"]
    afa = ausgaben["Absetzung für Abnutzung (AfA)"]
    sonstige = ausgaben["Sonstige unbeschränkt abziehbare Betriebsausgaben"]

    # Ausgaben
    # TODO: fix hädlerbund (steuerberatung kosten), auch related zu dem brutto bug
    # TODO: handle business expenses for EDV from personal accounts (psd / advancia) properly
    # TODO: Gebühren N26 Zahlung fehlt hier (wahrscheinlich selber bug bezogen auf Brutto vorsteuer)
    # TODO: alle expenses wo ich brutto für vorsteuer angebe, muss ich auf netto umrechnen für EÜR
    for kategorie in ausgaben.keys():
        for subcategory in ausgaben[kategorie].keys():
            if subcategory == TaxAlias.VORSTEUER:
                continue
            ausgaben[kategorie][subcategory] = sum_of_category_abs(
                df, category=subcategory
            )

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

"""Calculation helpers for the Einnahmen-Überschuss-Rechnung."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple

import pandas as pd

from src.elster.umsatz_steuererklaerung import BRUTTO_TO_UST
from src.elster.utils import sum_of_category_abs


def calculate_eur(df: pd.DataFrame, schema: Dict[str, Any]) -> Tuple[Dict[str, Any], float, float, float]:
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

    # Ausgaben
    leistungen = results["EÜR"]["4 - 2. Betriebsausgaben"]["Betriebsausgaben"]
    leistungen["Bezogene Leistungen"] = sum_of_category_abs(df, "Bezogene Leistungen")
    leistungen_sum = sum(leistungen.values())

    afa = results["EÜR"]["4 - 2. Betriebsausgaben"]["Absetzung für Abnutzung (AfA)"]
    for category in list(afa.keys()):
        afa[category] = sum_of_category_abs(df, category)
    afa_sum = sum(afa.values())

    sonstige = results["EÜR"]["4 - 2. Betriebsausgaben"][
        "Sonstige unbeschränkt abziehbare Betriebsausgaben"
    ]
    for category in list(sonstige.keys()):
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

    # Einnahmen
    refunds = sum_of_category_abs(df, "Sonstige Sach- Nutzungs- und Leistungsentnahmen")

    # Bilanz
    gewinn = refunds - (leistungen_sum + afa_sum + sonstige_sum)

    # Transfers
    privat_entnahme = sum_of_category_abs(df, "Privateentnahme")
    privat_einlage = sum_of_category_abs(df, "Privateinlage")

    return results, gewinn, privat_entnahme, privat_einlage